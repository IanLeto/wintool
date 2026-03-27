# -*- coding: utf-8 -*-
"""
体重管理工具 - 数据库连接和初始化
"""
import pymysql
from datetime import datetime, date, timedelta
from contextlib import contextmanager

# 数据库配置
DB_CONFIG = {
    'host': '121.4.210.42',
    'port': 3306,
    'user': 'testuser',
    'password': 'testpassword',
    'database': 'testdlb',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}


@contextmanager
def get_db():
    """获取数据库连接的上下文管理器"""
    conn = pymysql.connect(**DB_CONFIG)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_tables():
    """初始化数据库表"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 用户配置表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_profile (
                id INT PRIMARY KEY AUTO_INCREMENT,
                height DECIMAL(5,2),
                initial_weight DECIMAL(5,2),
                target_weight DECIMAL(5,2),
                start_date DATE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        
        # 每日记录表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_logs (
                id INT PRIMARY KEY AUTO_INCREMENT,
                date DATE UNIQUE,
                weight DECIMAL(5,2),
                sleep_hours DECIMAL(3,1),
                steps INT,
                fasting_168 TINYINT DEFAULT 0,
                sugar_free TINYINT DEFAULT 0,
                exercise_minutes INT,
                binge TINYINT DEFAULT 0,
                energy_level INT,
                hunger_level INT,
                mood_level INT,
                notes TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_date (date)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        
        # 策略版本表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS strategy_versions (
                id INT PRIMARY KEY AUTO_INCREMENT,
                version_name VARCHAR(100),
                start_date DATE,
                end_date DATE,
                core_strategy TEXT,
                variables_changed TEXT,
                expected_effect TEXT,
                result_summary TEXT,
                active TINYINT DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_active (active)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        
        # 周报表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS weekly_reviews (
                id INT PRIMARY KEY AUTO_INCREMENT,
                week_start DATE,
                week_end DATE,
                avg_weight DECIMAL(5,2),
                weight_change DECIMAL(5,2),
                compliance_rate DECIMAL(4,3),
                binge_count INT,
                avg_sleep DECIMAL(3,1),
                phase VARCHAR(50),
                summary TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_week (week_start)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        
        conn.commit()
        return True


def get_user_profile():
    """获取用户配置"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user_profile LIMIT 1")
        return cursor.fetchone()


def save_user_profile(height, initial_weight, target_weight, start_date):
    """保存或更新用户配置"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM user_profile LIMIT 1")
        existing = cursor.fetchone()
        
        if existing:
            cursor.execute("""
                UPDATE user_profile 
                SET height=%s, initial_weight=%s, target_weight=%s, start_date=%s
                WHERE id=%s
            """, (height, initial_weight, target_weight, start_date, existing['id']))
        else:
            cursor.execute("""
                INSERT INTO user_profile (height, initial_weight, target_weight, start_date)
                VALUES (%s, %s, %s, %s)
            """, (height, initial_weight, target_weight, start_date))
        
        conn.commit()
        return True


def get_daily_logs(start_date=None, end_date=None, limit=None):
    """获取每日记录"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        sql = "SELECT * FROM daily_logs WHERE 1=1"
        params = []
        
        if start_date:
            sql += " AND date >= %s"
            params.append(start_date)
        
        if end_date:
            sql += " AND date <= %s"
            params.append(end_date)
        
        sql += " ORDER BY date DESC"
        
        if limit:
            sql += " LIMIT %s"
            params.append(limit)
        
        cursor.execute(sql, params)
        return cursor.fetchall()


def save_daily_log(log_date, **kwargs):
    """保存或更新每日记录"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 检查是否已存在
        cursor.execute("SELECT id FROM daily_logs WHERE date=%s", (log_date,))
        existing = cursor.fetchone()
        
        fields = ['weight', 'sleep_hours', 'steps', 'fasting_168', 'sugar_free', 
                  'exercise_minutes', 'binge', 'energy_level', 'hunger_level', 
                  'mood_level', 'notes']
        
        if existing:
            # 更新
            set_clause = ', '.join([f"{f}=%s" for f in fields if f in kwargs])
            values = [kwargs[f] for f in fields if f in kwargs]
            values.append(existing['id'])
            
            cursor.execute(f"UPDATE daily_logs SET {set_clause} WHERE id=%s", values)
        else:
            # 插入
            insert_fields = ['date'] + [f for f in fields if f in kwargs]
            placeholders = ', '.join(['%s'] * len(insert_fields))
            values = [log_date] + [kwargs[f] for f in fields if f in kwargs]
            
            cursor.execute(
                f"INSERT INTO daily_logs ({', '.join(insert_fields)}) VALUES ({placeholders})",
                values
            )
        
        conn.commit()
        return True


def get_active_strategy():
    """获取当前活跃策略"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM strategy_versions WHERE active=1 LIMIT 1")
        return cursor.fetchone()


def get_all_strategies():
    """获取所有策略版本"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM strategy_versions ORDER BY start_date DESC")
        return cursor.fetchall()


def create_strategy(version_name, start_date, core_strategy, variables_changed, expected_effect):
    """创建新策略版本"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 关闭所有旧版本
        cursor.execute("UPDATE strategy_versions SET active=0, end_date=%s WHERE active=1", (start_date,))
        
        # 创建新版本
        cursor.execute("""
            INSERT INTO strategy_versions 
            (version_name, start_date, core_strategy, variables_changed, expected_effect, active)
            VALUES (%s, %s, %s, %s, %s, 1)
        """, (version_name, start_date, core_strategy, variables_changed, expected_effect))
        
        conn.commit()
        return True


def calculate_ma7(target_date=None):
    """计算7日移动平均体重"""
    if target_date is None:
        target_date = date.today()
    elif isinstance(target_date, str):
        target_date = datetime.strptime(target_date, '%Y-%m-%d').date()
    
    start = target_date - timedelta(days=6)
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT AVG(weight) as ma7
            FROM daily_logs
            WHERE date BETWEEN %s AND %s AND weight IS NOT NULL
        """, (start, target_date))
        
        result = cursor.fetchone()
        return round(result['ma7'], 2) if result and result['ma7'] else None


def calculate_compliance_score(log):
    """计算单日执行率得分"""
    score = 0.0
    
    # 16:8 断食 30%
    if log.get('fasting_168'):
        score += 0.3
    
    # 戒糖 30%
    if log.get('sugar_free'):
        score += 0.3
    
    # 睡眠 ≥7h 20%
    if log.get('sleep_hours') and log['sleep_hours'] >= 7:
        score += 0.2
    
    # 运动 ≥20min 20%
    if log.get('exercise_minutes') and log['exercise_minutes'] >= 20:
        score += 0.2
    
    return score


def get_phase_status():
    """判断当前阶段"""
    today = date.today()
    start_14 = today - timedelta(days=13)
    start_7 = today - timedelta(days=6)
    
    logs = get_daily_logs(start_date=start_14, end_date=today)
    
    if len(logs) < 7:
        return {
            'phase': 'building',
            'reason': '数据不足7天',
            'suggestion': '继续记录数据'
        }
    
    # 计算最近7天数据
    recent_7 = [l for l in logs if datetime.strptime(str(l['date']), '%Y-%m-%d').date() >= start_7]
    
    # 失控期判断
    binge_count = sum(1 for l in recent_7 if l.get('binge'))
    if binge_count >= 3:
        return {
            'phase': 'unstable',
            'reason': f'最近7天暴食{binge_count}次',
            'suggestion': '需要调整策略，关注情绪管理'
        }
    
    poor_sleep_days = sum(1 for l in recent_7 if l.get('sleep_hours') and l['sleep_hours'] < 6)
    if poor_sleep_days >= 5:
        return {
            'phase': 'unstable',
            'reason': f'最近7天有{poor_sleep_days}天睡眠不足6小时',
            'suggestion': '优先改善睡眠质量'
        }
    
    # 计算执行率
    compliance_scores = [calculate_compliance_score(l) for l in recent_7]
    avg_compliance = sum(compliance_scores) / len(compliance_scores) if compliance_scores else 0
    
    # 计算体重变化
    weights_14 = [l['weight'] for l in logs if l.get('weight')]
    if len(weights_14) >= 14:
        first_7_avg = sum(weights_14[-14:-7]) / 7
        last_7_avg = sum(weights_14[-7:]) / 7
        weight_change = first_7_avg - last_7_avg
        
        # 平台期
        if abs(weight_change) < 0.5 and avg_compliance >= 0.75:
            return {
                'phase': 'plateau',
                'reason': f'14天体重波动仅{abs(weight_change):.2f}kg，执行率{avg_compliance:.1%}',
                'suggestion': '考虑调整策略变量'
            }
        
        # 加速期
        if weight_change > 1.0:
            avg_hunger = sum(l.get('hunger_level', 10) for l in recent_7) / len(recent_7)
            avg_energy = sum(l.get('energy_level', 0) for l in recent_7) / len(recent_7)
            
            if avg_hunger <= 6 and avg_energy >= 6:
                return {
                    'phase': 'accelerating',
                    'reason': f'周下降{weight_change:.2f}kg，饥饿度{avg_hunger:.1f}，精力{avg_energy:.1f}',
                    'suggestion': '当前策略效果良好，保持'
                }
    
    # 建立期
    return {
        'phase': 'building',
        'reason': f'执行率{avg_compliance:.1%}，持续观察中',
        'suggestion': '继续执行当前策略'
    }
