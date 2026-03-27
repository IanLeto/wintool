# -*- coding: utf-8 -*-
"""
工具：体重管理 - BodyOS 个人减脂管理系统
"""
import json
from datetime import datetime, date, timedelta
from flask import Blueprint, request, jsonify
from .base import BaseTool
from . import body_weight_db as db


class BodyWeightTool(BaseTool):
    TOOL_ID = "body_weight"
    TOOL_NAME = "体重管理"

    @classmethod
    def get_form_html(cls) -> str:
        return """
        <div class="tool-form body-weight-form" data-body-weight data-tool-id="body_weight">
            <div class="body-weight-tabs">
                <button type="button" class="body-tab active" data-tab="dashboard">仪表盘</button>
                <button type="button" class="body-tab" data-tab="daily">每日记录</button>
                <button type="button" class="body-tab" data-tab="trend">趋势图表</button>
                <button type="button" class="body-tab" data-tab="strategy">策略版本</button>
                <button type="button" class="body-tab" data-tab="export">数据导出</button>
            </div>
            
            <!-- 仪表盘 -->
            <div class="body-panel" data-panel="dashboard">
                <div class="dashboard-grid">
                    <div class="dash-card">
                        <h3>当前体重</h3>
                        <div class="dash-value" id="current-weight">--</div>
                        <div class="dash-sub">7日均线: <span id="ma7-weight">--</span></div>
                    </div>
                    <div class="dash-card">
                        <h3>当前阶段</h3>
                        <div class="dash-value phase-badge" id="current-phase">--</div>
                        <div class="dash-sub" id="phase-reason">--</div>
                    </div>
                    <div class="dash-card">
                        <h3>本周执行率</h3>
                        <div class="dash-value" id="week-compliance">--</div>
                        <div class="dash-sub">暴食次数: <span id="week-binge">--</span></div>
                    </div>
                    <div class="dash-card">
                        <h3>当前策略</h3>
                        <div class="dash-value small" id="current-strategy">--</div>
                        <div class="dash-sub" id="strategy-days">--</div>
                    </div>
                </div>
                <div class="dash-chart">
                    <canvas id="dashboard-chart"></canvas>
                </div>
            </div>
            
            <!-- 每日记录 -->
            <div class="body-panel" data-panel="daily" style="display:none;">
                <div class="daily-form">
                    <div class="form-row">
                        <label>日期：</label>
                        <input type="date" id="log-date" class="form-input" />
                        <button type="button" class="btn-secondary" id="copy-yesterday">复制昨日</button>
                        <button type="button" class="btn-secondary" id="load-date">加载</button>
                    </div>
                    <div class="form-row">
                        <label>体重 (kg)：</label>
                        <input type="number" step="0.1" id="log-weight" class="form-input" placeholder="70.5" />
                    </div>
                    <div class="form-row">
                        <label>睡眠时长 (h)：</label>
                        <input type="number" step="0.5" id="log-sleep" class="form-input" placeholder="7.5" />
                    </div>
                    <div class="form-row">
                        <label>步数：</label>
                        <input type="number" id="log-steps" class="form-input" placeholder="8000" />
                    </div>
                    <div class="form-row">
                        <label>运动时长 (min)：</label>
                        <input type="number" id="log-exercise" class="form-input" placeholder="30" />
                    </div>
                    <div class="form-row checkbox-row">
                        <label><input type="checkbox" id="log-fasting" /> 16:8 断食</label>
                        <label><input type="checkbox" id="log-sugar-free" /> 戒糖</label>
                        <label><input type="checkbox" id="log-binge" /> 暴食</label>
                    </div>
                    <div class="form-row">
                        <label>精力水平 (1-10)：</label>
                        <input type="range" min="1" max="10" id="log-energy" class="form-range" value="5" />
                        <span id="energy-val">5</span>
                    </div>
                    <div class="form-row">
                        <label>饥饿水平 (1-10)：</label>
                        <input type="range" min="1" max="10" id="log-hunger" class="form-range" value="5" />
                        <span id="hunger-val">5</span>
                    </div>
                    <div class="form-row">
                        <label>心情水平 (1-10)：</label>
                        <input type="range" min="1" max="10" id="log-mood" class="form-range" value="5" />
                        <span id="mood-val">5</span>
                    </div>
                    <div class="form-row">
                        <label>备注：</label>
                        <textarea id="log-notes" class="form-textarea" rows="3"></textarea>
                    </div>
                    <div class="form-actions">
                        <button type="button" class="btn-primary" id="save-log">保存记录</button>
                        <button type="button" class="btn-secondary" id="clear-form">清空</button>
                    </div>
                    <div id="daily-result" class="result-msg"></div>
                </div>
            </div>
            
            <!-- 趋势图表 -->
            <div class="body-panel" data-panel="trend" style="display:none;">
                <div class="trend-controls">
                    <label>时间范围：</label>
                    <select id="trend-range" class="form-select">
                        <option value="7">最近7天</option>
                        <option value="14">最近14天</option>
                        <option value="30" selected>最近30天</option>
                        <option value="90">最近90天</option>
                    </select>
                    <button type="button" class="btn-secondary" id="refresh-trend">刷新</button>
                </div>
                <div class="trend-chart">
                    <canvas id="trend-chart"></canvas>
                </div>
            </div>
            
            <!-- 策略版本 -->
            <div class="body-panel" data-panel="strategy" style="display:none;">
                <div class="strategy-current">
                    <h3>当前策略</h3>
                    <div id="current-strategy-detail">加载中...</div>
                </div>
                <div class="strategy-new">
                    <h3>创建新策略</h3>
                    <div class="form-row">
                        <label>版本名称：</label>
                        <input type="text" id="strategy-name" class="form-input" placeholder="v1.1 - 增加运动" />
                    </div>
                    <div class="form-row">
                        <label>开始日期：</label>
                        <input type="date" id="strategy-start" class="form-input" />
                    </div>
                    <div class="form-row">
                        <label>核心策略：</label>
                        <textarea id="strategy-core" class="form-textarea" rows="3" placeholder="16:8断食 + 戒糖 + 每日运动30分钟"></textarea>
                    </div>
                    <div class="form-row">
                        <label>变更变量：</label>
                        <input type="text" id="strategy-vars" class="form-input" placeholder="运动时长从20分钟增加到30分钟" />
                    </div>
                    <div class="form-row">
                        <label>预期效果：</label>
                        <textarea id="strategy-effect" class="form-textarea" rows="2" placeholder="预计每周减重0.5-1kg"></textarea>
                    </div>
                    <button type="button" class="btn-primary" id="create-strategy">创建策略</button>
                    <div id="strategy-result" class="result-msg"></div>
                </div>
                <div class="strategy-history">
                    <h3>历史版本</h3>
                    <div id="strategy-list">加载中...</div>
                </div>
            </div>
            
            <!-- 数据导出 -->
            <div class="body-panel" data-panel="export" style="display:none;">
                <div class="export-section">
                    <h3>导出诊断数据</h3>
                    <p class="desc">导出最近14天数据，可复制给 GPT 进行分析</p>
                    <button type="button" class="btn-primary" id="export-data">生成导出数据</button>
                    <div class="export-result">
                        <textarea id="export-json" class="export-textarea" readonly></textarea>
                        <button type="button" class="btn-secondary" id="copy-export">复制到剪贴板</button>
                    </div>
                </div>
            </div>
        </div>
        """

    @classmethod
    def register_routes(cls, bp: Blueprint):
        
        @bp.route("/init", methods=["POST"])
        def init_db():
            """初始化数据库"""
            try:
                db.init_tables()
                return jsonify({"ok": True, "message": "数据库初始化成功"})
            except Exception as e:
                return jsonify({"ok": False, "error": str(e)})
        
        @bp.route("/dashboard", methods=["GET"])
        def get_dashboard():
            """获取仪表盘数据"""
            try:
                today = date.today()
                
                # 当前体重和7日均线
                recent_logs = db.get_daily_logs(limit=1)
                current_weight = recent_logs[0]['weight'] if recent_logs and recent_logs[0].get('weight') else None
                ma7 = db.calculate_ma7()
                
                # 当前阶段
                phase_info = db.get_phase_status()
                
                # 本周执行率
                week_start = today - timedelta(days=6)
                week_logs = db.get_daily_logs(start_date=week_start, end_date=today)
                compliance_scores = [db.calculate_compliance_score(l) for l in week_logs]
                avg_compliance = sum(compliance_scores) / len(compliance_scores) if compliance_scores else 0
                binge_count = sum(1 for l in week_logs if l.get('binge'))
                
                # 当前策略
                strategy = db.get_active_strategy()
                strategy_info = None
                if strategy:
                    days_running = (today - strategy['start_date']).days if strategy.get('start_date') else 0
                    strategy_info = {
                        'name': strategy['version_name'],
                        'days': days_running
                    }
                
                # 最近30天体重数据（用于图表）
                chart_logs = db.get_daily_logs(start_date=today - timedelta(days=29), end_date=today)
                chart_data = {
                    'dates': [str(l['date']) for l in reversed(chart_logs)],
                    'weights': [float(l['weight']) if l.get('weight') else None for l in reversed(chart_logs)]
                }
                
                return jsonify({
                    "ok": True,
                    "current_weight": float(current_weight) if current_weight else None,
                    "ma7": float(ma7) if ma7 else None,
                    "phase": phase_info,
                    "compliance": round(avg_compliance, 3),
                    "binge_count": binge_count,
                    "strategy": strategy_info,
                    "chart": chart_data
                })
            except Exception as e:
                return jsonify({"ok": False, "error": str(e)})
        
        @bp.route("/daily-log", methods=["GET"])
        def get_daily_log():
            """获取指定日期的记录"""
            log_date = request.args.get('date')
            if not log_date:
                return jsonify({"ok": False, "error": "缺少日期参数"})
            
            try:
                logs = db.get_daily_logs(start_date=log_date, end_date=log_date)
                log = logs[0] if logs else None
                
                # 转换日期为字符串
                if log and log.get('date'):
                    log['date'] = str(log['date'])
                
                return jsonify({"ok": True, "log": log})
            except Exception as e:
                return jsonify({"ok": False, "error": str(e)})
        
        @bp.route("/daily-log", methods=["POST"])
        def save_daily_log():
            """保存每日记录"""
            data = request.get_json() or {}
            log_date = data.get('date')
            
            if not log_date:
                return jsonify({"ok": False, "error": "缺少日期"})
            
            try:
                # 准备数据
                log_data = {}
                if 'weight' in data and data['weight']:
                    log_data['weight'] = float(data['weight'])
                if 'sleep_hours' in data and data['sleep_hours']:
                    log_data['sleep_hours'] = float(data['sleep_hours'])
                if 'steps' in data and data['steps']:
                    log_data['steps'] = int(data['steps'])
                if 'exercise_minutes' in data and data['exercise_minutes']:
                    log_data['exercise_minutes'] = int(data['exercise_minutes'])
                
                log_data['fasting_168'] = 1 if data.get('fasting_168') else 0
                log_data['sugar_free'] = 1 if data.get('sugar_free') else 0
                log_data['binge'] = 1 if data.get('binge') else 0
                
                if 'energy_level' in data:
                    log_data['energy_level'] = int(data['energy_level'])
                if 'hunger_level' in data:
                    log_data['hunger_level'] = int(data['hunger_level'])
                if 'mood_level' in data:
                    log_data['mood_level'] = int(data['mood_level'])
                if 'notes' in data:
                    log_data['notes'] = data['notes']
                
                db.save_daily_log(log_date, **log_data)
                
                return jsonify({"ok": True, "message": "保存成功"})
            except Exception as e:
                return jsonify({"ok": False, "error": str(e)})
        
        @bp.route("/trend", methods=["GET"])
        def get_trend():
            """获取趋势数据"""
            days = int(request.args.get('days', 30))
            
            try:
                today = date.today()
                start_date = today - timedelta(days=days-1)
                
                logs = db.get_daily_logs(start_date=start_date, end_date=today)
                logs = list(reversed(logs))
                
                dates = [str(l['date']) for l in logs]
                weights = [float(l['weight']) if l.get('weight') else None for l in logs]
                
                # 计算7日移动平均
                ma7_values = []
                for i, log in enumerate(logs):
                    if log.get('weight'):
                        ma7 = db.calculate_ma7(log['date'])
                        ma7_values.append(ma7)
                    else:
                        ma7_values.append(None)
                
                return jsonify({
                    "ok": True,
                    "dates": dates,
                    "weights": weights,
                    "ma7": ma7_values
                })
            except Exception as e:
                return jsonify({"ok": False, "error": str(e)})
        
        @bp.route("/strategy/current", methods=["GET"])
        def get_current_strategy():
            """获取当前策略"""
            try:
                strategy = db.get_active_strategy()
                if strategy and strategy.get('start_date'):
                    strategy['start_date'] = str(strategy['start_date'])
                if strategy and strategy.get('end_date'):
                    strategy['end_date'] = str(strategy['end_date'])
                
                return jsonify({"ok": True, "strategy": strategy})
            except Exception as e:
                return jsonify({"ok": False, "error": str(e)})
        
        @bp.route("/strategy/history", methods=["GET"])
        def get_strategy_history():
            """获取策略历史"""
            try:
                strategies = db.get_all_strategies()
                for s in strategies:
                    if s.get('start_date'):
                        s['start_date'] = str(s['start_date'])
                    if s.get('end_date'):
                        s['end_date'] = str(s['end_date'])
                
                return jsonify({"ok": True, "strategies": strategies})
            except Exception as e:
                return jsonify({"ok": False, "error": str(e)})
        
        @bp.route("/strategy", methods=["POST"])
        def create_new_strategy():
            """创建新策略"""
            data = request.get_json() or {}
            
            required = ['version_name', 'start_date', 'core_strategy', 'variables_changed', 'expected_effect']
            for field in required:
                if not data.get(field):
                    return jsonify({"ok": False, "error": f"缺少字段: {field}"})
            
            try:
                db.create_strategy(
                    data['version_name'],
                    data['start_date'],
                    data['core_strategy'],
                    data['variables_changed'],
                    data['expected_effect']
                )
                return jsonify({"ok": True, "message": "策略创建成功"})
            except Exception as e:
                return jsonify({"ok": False, "error": str(e)})
        
        @bp.route("/export", methods=["GET"])
        def export_data():
            """导出诊断数据"""
            try:
                today = date.today()
                start_14 = today - timedelta(days=13)
                
                # 最近14天数据
                logs = db.get_daily_logs(start_date=start_14, end_date=today)
                logs_data = []
                for l in logs:
                    log_dict = dict(l)
                    if log_dict.get('date'):
                        log_dict['date'] = str(log_dict['date'])
                    if log_dict.get('created_at'):
                        log_dict['created_at'] = str(log_dict['created_at'])
                    logs_data.append(log_dict)
                
                # 当前策略
                strategy = db.get_active_strategy()
                if strategy:
                    if strategy.get('start_date'):
                        strategy['start_date'] = str(strategy['start_date'])
                    if strategy.get('end_date'):
                        strategy['end_date'] = str(strategy['end_date'])
                    if strategy.get('created_at'):
                        strategy['created_at'] = str(strategy['created_at'])
                
                # 阶段信息
                phase_info = db.get_phase_status()
                
                # 趋势数据
                ma7 = db.calculate_ma7()
                
                export_obj = {
                    "export_date": str(today),
                    "current_version": strategy,
                    "last_14_days": list(reversed(logs_data)),
                    "phase": phase_info,
                    "trend": {
                        "ma7": float(ma7) if ma7 else None
                    }
                }
                
                return jsonify({"ok": True, "data": export_obj})
            except Exception as e:
                return jsonify({"ok": False, "error": str(e)})
