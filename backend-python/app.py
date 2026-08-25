#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
代码片段库 - Python Flask 后端
用于内网环境，无需 JDK/Maven
支持静态文件服务（前端构建产物）
"""

import sys
from pathlib import Path

# 添加 libs 目录到 Python 路径（内网环境，无 pip）
SCRIPT_DIR = Path(__file__).parent
LIBS_DIR = SCRIPT_DIR.parent / "libs"

if LIBS_DIR.exists():
    sys.path.insert(0, str(LIBS_DIR))

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import os
from datetime import datetime

# 前端构建产物目录
# 优先使用同级目录的 frontend/dist（内网打包后的结构）
FRONTEND_DIST_INNER = Path(__file__).parent / "frontend" / "dist"
# 其次使用上级目录的 frontend/dist（开发环境）
FRONTEND_DIST_DEV = Path(__file__).parent.parent / "frontend" / "dist"

# 选择存在的目录
if FRONTEND_DIST_INNER.exists():
    FRONTEND_DIST = FRONTEND_DIST_INNER
elif FRONTEND_DIST_DEV.exists():
    FRONTEND_DIST = FRONTEND_DIST_DEV
else:
    FRONTEND_DIST = FRONTEND_DIST_DEV  # 默认使用开发环境路径

# 如果存在 dist 目录，则提供静态文件服务
if FRONTEND_DIST.exists():
    app = Flask(__name__, static_folder=str(FRONTEND_DIST), static_url_path='')
else:
    app = Flask(__name__)

CORS(app)  # 允许跨域

# 数据文件路径
DATA_DIR = Path("code_snippets")
DATA_FILE = DATA_DIR / "snippets.json"

# 确保数据目录存在
DATA_DIR.mkdir(exist_ok=True)


def load_snippets():
    """从文件加载代码片段"""
    if not DATA_FILE.exists():
        return []
    
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []


def save_snippets(snippets):
    """保存代码片段到文件"""
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(snippets, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False


def get_next_id(snippets):
    """获取下一个ID"""
    if not snippets:
        return 1
    return max(s['id'] for s in snippets) + 1


@app.route('/api/code-snippets', methods=['GET'])
def get_all_snippets():
    """获取所有代码片段"""
    try:
        snippets = load_snippets()
        
        # 搜索关键词
        keyword = request.args.get('keyword', '').lower()
        if keyword:
            snippets = [
                s for s in snippets
                if keyword in s['title'].lower() or
                   keyword in s['language'].lower() or
                   keyword in s['code'].lower() or
                   any(keyword in tag.lower() for tag in s.get('tags', []))
            ]
        
        # 语言筛选
        language = request.args.get('language', '')
        if language:
            snippets = [s for s in snippets if s['language'].lower() == language.lower()]
        
        return jsonify({
            'success': True,
            'data': snippets,
            'total': len(snippets)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取代码片段失败: {str(e)}'
        }), 500


@app.route('/api/code-snippets/<int:snippet_id>', methods=['GET'])
def get_snippet_by_id(snippet_id):
    """根据ID获取代码片段"""
    try:
        snippets = load_snippets()
        snippet = next((s for s in snippets if s['id'] == snippet_id), None)
        
        if not snippet:
            return jsonify({
                'success': False,
                'message': '代码片段不存在'
            }), 404
        
        return jsonify({
            'success': True,
            'data': snippet
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取代码片段失败: {str(e)}'
        }), 500


@app.route('/api/code-snippets', methods=['POST'])
def create_snippet():
    """创建代码片段"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        if not data.get('title') or not data.get('title').strip():
            return jsonify({
                'success': False,
                'message': '标题不能为空'
            }), 400
        
        if not data.get('code') or not data.get('code').strip():
            return jsonify({
                'success': False,
                'message': '代码不能为空'
            }), 400
        
        snippets = load_snippets()
        
        # 创建新片段
        new_snippet = {
            'id': get_next_id(snippets),
            'title': data['title'].strip(),
            'language': data.get('language', 'Other'),
            'code': data['code'],
            'tags': data.get('tags', []),
            'createdAt': datetime.now().isoformat(),
            'updatedAt': datetime.now().isoformat()
        }
        
        snippets.insert(0, new_snippet)  # 添加到开头
        
        if save_snippets(snippets):
            return jsonify({
                'success': True,
                'data': new_snippet,
                'message': '创建成功'
            }), 201
        else:
            return jsonify({
                'success': False,
                'message': '保存失败'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'创建代码片段失败: {str(e)}'
        }), 500


@app.route('/api/code-snippets/<int:snippet_id>', methods=['PUT'])
def update_snippet(snippet_id):
    """更新代码片段"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        if not data.get('title') or not data.get('title').strip():
            return jsonify({
                'success': False,
                'message': '标题不能为空'
            }), 400
        
        if not data.get('code') or not data.get('code').strip():
            return jsonify({
                'success': False,
                'message': '代码不能为空'
            }), 400
        
        snippets = load_snippets()
        
        # 查找并更新
        for i, snippet in enumerate(snippets):
            if snippet['id'] == snippet_id:
                snippets[i] = {
                    'id': snippet_id,
                    'title': data['title'].strip(),
                    'language': data.get('language', 'Other'),
                    'code': data['code'],
                    'tags': data.get('tags', []),
                    'createdAt': snippet.get('createdAt', datetime.now().isoformat()),
                    'updatedAt': datetime.now().isoformat()
                }
                
                if save_snippets(snippets):
                    return jsonify({
                        'success': True,
                        'data': snippets[i],
                        'message': '更新成功'
                    })
                else:
                    return jsonify({
                        'success': False,
                        'message': '保存失败'
                    }), 500
        
        return jsonify({
            'success': False,
            'message': '代码片段不存在'
        }), 404
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'更新代码片段失败: {str(e)}'
        }), 500


@app.route('/api/code-snippets/<int:snippet_id>', methods=['DELETE'])
def delete_snippet(snippet_id):
    """删除代码片段"""
    try:
        snippets = load_snippets()
        original_length = len(snippets)
        
        snippets = [s for s in snippets if s['id'] != snippet_id]
        
        if len(snippets) == original_length:
            return jsonify({
                'success': False,
                'message': '代码片段不存在'
            }), 404
        
        if save_snippets(snippets):
            return jsonify({
                'success': True,
                'message': '删除成功'
            })
        else:
            return jsonify({
                'success': False,
                'message': '保存失败'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'删除代码片段失败: {str(e)}'
        }), 500


@app.route('/api/code-snippets/languages', methods=['GET'])
def get_languages():
    """获取所有语言列表"""
    try:
        languages = sorted(set(s['language'] for s in snippets))
        
        return jsonify({
            'success': True,
            'data': languages
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取语言列表失败: {str(e)}'
        }), 500


@app.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        'status': 'ok',
        'message': 'Wintool Python Backend is running',
        'version': '1.0.0',
        'frontend': 'dist' if FRONTEND_DIST.exists() else 'dev'
    })


# ==================== K8s 集群管理 API ====================

import subprocess
import time
from pathlib import Path as PathLib

# K8s 配置文件路径（与启动脚本在同一目录）
KUBECONFIG_PATH = PathLib(__file__).parent.parent / "kubeconfig"


def run_kubectl_command(command, context=None):
    """
    执行 kubectl 命令
    
    Args:
        command: kubectl 命令（不包含 kubectl 前缀）
        context: 集群上下文名称（可选）
    
    Returns:
        dict: {success: bool, output: str, duration: int}
    """
    start_time = time.time()
    
    try:
        # 构建完整命令
        cmd = ['kubectl']
        
        # 如果指定了 kubeconfig 文件
        if KUBECONFIG_PATH.exists():
            cmd.extend(['--kubeconfig', str(KUBECONFIG_PATH)])
        
        # 如果指定了上下文
        if context:
            cmd.extend(['--context', context])
        
        # 添加用户命令
        cmd.extend(command.split())
        
        # 执行命令
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30  # 30秒超时
        )
        
        duration = int((time.time() - start_time) * 1000)
        
        if result.returncode == 0:
            return {
                'success': True,
                'output': result.stdout.strip(),
                'duration': duration
            }
        else:
            return {
                'success': False,
                'output': result.stderr.strip() or result.stdout.strip(),
                'duration': duration
            }
    
    except subprocess.TimeoutExpired:
        duration = int((time.time() - start_time) * 1000)
        return {
            'success': False,
            'output': '命令执行超时（30秒）',
            'duration': duration
        }
    except Exception as e:
        duration = int((time.time() - start_time) * 1000)
        return {
            'success': False,
            'output': f'执行错误: {str(e)}',
            'duration': duration
        }


@app.route('/api/k8s/clusters', methods=['GET'])
def get_k8s_clusters():
    """获取所有 K8s 集群列表"""
    try:
        # 构建命令
        cmd = ['kubectl', 'config', 'get-contexts', '--no-headers']
        
        # 如果指定了 kubeconfig 文件
        if KUBECONFIG_PATH.exists():
            cmd.extend(['--kubeconfig', str(KUBECONFIG_PATH)])
        
        # 执行命令
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode != 0:
            return jsonify({
                'success': False,
                'message': f'获取集群列表失败: {result.stderr}'
            }), 500
        
        # 解析输出
        clusters = []
        lines = result.stdout.strip().split('\n')
        
        for line in lines:
            if not line.strip():
                continue
            
            parts = line.split()
            if len(parts) < 3:
                continue
            
            # 格式: [*] NAME CLUSTER AUTHINFO NAMESPACE
            is_current = parts[0] == '*'
            offset = 1 if is_current else 0
            
            cluster = {
                'name': parts[offset],
                'cluster': parts[offset + 1] if len(parts) > offset + 1 else '',
                'user': parts[offset + 2] if len(parts) > offset + 2 else '',
                'namespace': parts[offset + 3] if len(parts) > offset + 3 else '',
                'current': is_current
            }
            clusters.append(cluster)
        
        return jsonify({
            'success': True,
            'data': clusters,
            'total': len(clusters)
        })
    
    except subprocess.TimeoutExpired:
        return jsonify({
            'success': False,
            'message': '获取集群列表超时'
        }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取集群列表失败: {str(e)}'
        }), 500


@app.route('/api/k8s/execute', methods=['POST'])
def execute_k8s_command():
    """在多个集群上批量执行 kubectl 命令"""
    try:
        data = request.get_json()
        
        # 验证参数
        if not data.get('clusters') or not isinstance(data['clusters'], list):
            return jsonify({
                'success': False,
                'message': '请选择至少一个集群'
            }), 400
        
        if not data.get('command') or not data['command'].strip():
            return jsonify({
                'success': False,
                'message': '命令不能为空'
            }), 400
        
        clusters = data['clusters']
        command = data['command'].strip()
        
        # 在每个集群上执行命令
        results = []
        for cluster_name in clusters:
            result = run_kubectl_command(command, context=cluster_name)
            results.append({
                'cluster': cluster_name,
                'command': command,
                'success': result['success'],
                'output': result['output'],
                'duration': result['duration']
            })
        
        return jsonify({
            'success': True,
            'data': results,
            'total': len(results)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'执行命令失败: {str(e)}'
        }), 500


@app.route('/api/k8s/switch-context', methods=['POST'])
def switch_k8s_context():
    """切换当前 K8s 上下文"""
    try:
        data = request.get_json()
        
        if not data.get('context'):
            return jsonify({
                'success': False,
                'message': '上下文名称不能为空'
            }), 400
        
        context = data['context']
        
        # 构建命令
        cmd = ['kubectl', 'config', 'use-context', context]
        
        # 如果指定了 kubeconfig 文件
        if KUBECONFIG_PATH.exists():
            cmd.extend(['--kubeconfig', str(KUBECONFIG_PATH)])
        
        # 执行命令
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            return jsonify({
                'success': True,
                'message': f'已切换到上下文: {context}'
            })
        else:
            return jsonify({
                'success': False,
                'message': f'切换上下文失败: {result.stderr}'
            }), 500
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'切换上下文失败: {str(e)}'
        }), 500


# ==================== 原型预览 API ====================

# 原型文件目录
PROTOTYPES_DIR = Path(__file__).parent.parent / "prototypes"

@app.route('/api/prototypes/list', methods=['GET'])
def list_prototypes():
    """获取所有原型文件列表"""
    try:
        # 确保目录存在
        if not PROTOTYPES_DIR.exists():
            PROTOTYPES_DIR.mkdir(parents=True, exist_ok=True)
            return jsonify({
                'success': True,
                'prototypes': [],
                'message': '原型目录已创建，请添加 HTML 文件'
            })
        
        # 扫描 HTML 文件
        prototypes = []
        for file_path in PROTOTYPES_DIR.rglob('*.html'):
            if file_path.is_file():
                # 获取相对路径
                rel_path = file_path.relative_to(PROTOTYPES_DIR)
                
                # 获取文件信息
                stat = file_path.stat()
                
                prototypes.append({
                    'name': file_path.name,
                    'path': str(rel_path),
                    'size': stat.st_size,
                    'modified': int(stat.st_mtime)
                })
        
        # 按修改时间倒序排序
        prototypes.sort(key=lambda x: x['modified'], reverse=True)
        
        return jsonify({
            'success': True,
            'prototypes': prototypes,
            'total': len(prototypes)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取原型列表失败: {str(e)}'
        }), 500


@app.route('/api/prototypes/view/<path:file_path>', methods=['GET'])
def view_prototype(file_path):
    """预览原型文件"""
    try:
        # 安全检查：防止路径遍历攻击
        safe_path = Path(file_path).resolve()
        prototypes_abs = PROTOTYPES_DIR.resolve()
        
        # 确保文件在 prototypes 目录内
        full_path = (prototypes_abs / file_path).resolve()
        
        if not str(full_path).startswith(str(prototypes_abs)):
            return jsonify({
                'success': False,
                'message': '非法的文件路径'
            }), 403
        
        # 检查文件是否存在
        if not full_path.exists() or not full_path.is_file():
            return jsonify({
                'success': False,
                'message': '文件不存在'
            }), 404
        
        # 返回 HTML 文件
        return send_from_directory(str(PROTOTYPES_DIR), file_path)
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'预览失败: {str(e)}'
        }), 500


# ==================== Kafka 消费工具 API ====================

@app.route('/api/kafka/test', methods=['POST'])
def kafka_test_connection():
    """测试 Kafka 连接"""
    try:
        data = request.get_json()
        brokers = data.get('brokers', '').strip()
        topic = data.get('topic', '').strip()
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        
        if not brokers or not topic:
            return jsonify({
                'success': False,
                'message': 'Broker 和 Topic 不能为空'
            }), 400
        
        # 导入 kafka-python
        try:
            from kafka import KafkaConsumer
        except ImportError:
            return jsonify({
                'success': False,
                'message': 'kafka-python 未安装，请先解压依赖'
            }), 500
        
        # 解析 brokers
        broker_list = [b.strip() for b in brokers.split(',') if b.strip()]
        
        # 极简配置 - 只保留必需参数
        config = {
            'bootstrap_servers': broker_list,
        }
        
        # 如果有用户名密码，添加 SASL 认证
        if username and password:
            config.update({
                'security_protocol': 'SASL_PLAINTEXT',
                'sasl_mechanism': 'PLAIN',
                'sasl_plain_username': username,
                'sasl_plain_password': password,
            })
        
        # 创建消费者测试连接
        consumer = KafkaConsumer(**config)
        
        # 获取 topic 分区信息
        partitions = consumer.partitions_for_topic(topic)
        consumer.close()
        
        if partitions is not None:
            return jsonify({
                'success': True,
                'message': f'连接成功！Topic 有 {len(partitions)} 个分区',
                'partitions': sorted(list(partitions))
            })
        else:
            return jsonify({
                'success': False,
                'message': f'Topic "{topic}" 不存在'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'连接失败: {str(e)}'
        }), 500


@app.route('/api/kafka/consume', methods=['POST'])
def kafka_consume_messages():
    """消费 Kafka 消息"""
    try:
        data = request.get_json()
        brokers = data.get('brokers', '').strip()
        topic = data.get('topic', '').strip()
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        offset = data.get('offset', 'latest')
        limit = int(data.get('limit', 10))
        timeout_sec = int(data.get('timeout', 30))
        
        if not brokers or not topic:
            return jsonify({
                'success': False,
                'message': 'Broker 和 Topic 不能为空'
            }), 400
        
        # 导入 kafka-python
        try:
            from kafka import KafkaConsumer
        except ImportError:
            return jsonify({
                'success': False,
                'message': 'kafka-python 未安装，请先解压依赖'
            }), 500
        
        # 解析 brokers
        broker_list = [b.strip() for b in brokers.split(',') if b.strip()]
        
        # 极简配置 - 只保留必需参数
        config = {
            'bootstrap_servers': broker_list,
            'auto_offset_reset': offset,
            'enable_auto_commit': False,
            'value_deserializer': lambda m: m.decode('utf-8', errors='ignore'),
            'consumer_timeout_ms': timeout_sec * 1000,
        }
        
        # 如果有用户名密码，添加 SASL 认证
        if username and password:
            config.update({
                'security_protocol': 'SASL_PLAINTEXT',
                'sasl_mechanism': 'PLAIN',
                'sasl_plain_username': username,
                'sasl_plain_password': password,
            })
        
        # 创建消费者
        consumer = KafkaConsumer(topic, **config)
        
        messages = []
        import time
        start_time = time.time()
        
        try:
            for message in consumer:
                # 解析消息
                try:
                    msg_data = json.loads(message.value)
                except:
                    msg_data = {'_raw': message.value}
                
                # 添加元数据
                msg_data['_partition'] = message.partition
                msg_data['_offset'] = message.offset
                msg_data['_timestamp'] = message.timestamp
                
                messages.append(msg_data)
                
                # 达到限制
                if len(messages) >= limit:
                    break
                
                # 超时
                if time.time() - start_time > timeout_sec:
                    break
                    
        except StopIteration:
            pass  # 超时正常退出
        
        consumer.close()
        
        return jsonify({
            'success': True,
            'message': f'消费成功，共 {len(messages)} 条消息',
            'count': len(messages),
            'messages': messages
        })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'消费失败: {str(e)}'
        }), 500


# ==================== 时间戳转换工具 API ====================

@app.route('/api/timestamp/convert', methods=['POST'])
def convert_timestamp():
    """时间戳转换"""
    try:
        data = request.get_json()
        input_value = data.get('value', '')
        
        if not input_value:
            return jsonify({
                'success': False,
                'message': '输入值不能为空'
            }), 400
        
        # 尝试解析输入
        try:
            # 如果是数字字符串，转换为整数
            if isinstance(input_value, str) and input_value.isdigit():
                timestamp = int(input_value)
            elif isinstance(input_value, (int, float)):
                timestamp = int(input_value)
            else:
                # 尝试解析为日期字符串
                from dateutil import parser
                dt = parser.parse(input_value)
                timestamp = int(dt.timestamp())
        except:
            # 如果解析失败，尝试作为时间戳处理
            try:
                timestamp = int(float(input_value))
            except:
                return jsonify({
                    'success': False,
                    'message': '无法解析输入值'
                }), 400
        
        # 自动判断时间戳精度（秒/毫秒/微秒/纳秒）
        if timestamp > 1e17:  # 纳秒 (> 100,000,000,000,000,000)
            dt = datetime.fromtimestamp(timestamp / 1e9)
            precision = 'nanosecond'
        elif timestamp > 1e13:  # 微秒 (> 10,000,000,000,000)
            dt = datetime.fromtimestamp(timestamp / 1e6)
            precision = 'microsecond'
        elif timestamp > 1e10:  # 毫秒 (> 10,000,000,000)
            dt = datetime.fromtimestamp(timestamp / 1000)
            precision = 'millisecond'
        else:  # 秒
            dt = datetime.fromtimestamp(timestamp)
            precision = 'second'
        
        # 生成各种格式
        result = {
            'success': True,
            'precision': precision,
            'formats': {
                'timestamp_second': int(dt.timestamp()),
                'timestamp_millisecond': int(dt.timestamp() * 1000),
                'timestamp_microsecond': int(dt.timestamp() * 1e6),
                'timestamp_nanosecond': int(dt.timestamp() * 1e9),
                'iso8601': dt.isoformat(),
                'iso8601_utc': dt.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                'rfc2822': dt.strftime('%a, %d %b %Y %H:%M:%S'),
                'date_cn': dt.strftime('%Y年%m月%d日'),
                'datetime_cn': dt.strftime('%Y年%m月%d日 %H:%M:%S'),
                'date_us': dt.strftime('%m/%d/%Y'),
                'datetime_us': dt.strftime('%m/%d/%Y %H:%M:%S'),
                'date_standard': dt.strftime('%Y-%m-%d'),
                'datetime_standard': dt.strftime('%Y-%m-%d %H:%M:%S'),
                'time_only': dt.strftime('%H:%M:%S'),
                'year_month': dt.strftime('%Y-%m'),
                'weekday_cn': ['周一', '周二', '周三', '周四', '周五', '周六', '周日'][dt.weekday()],
                'weekday_en': dt.strftime('%A'),
            }
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'转换失败: {str(e)}'
        }), 500


# 原型文件静态服务
@app.route('/prototypes/<path:filename>')
def serve_prototype(filename):
    """直接提供原型 HTML 文件"""
    prototypes_dir = Path(__file__).parent.parent / "prototypes"
    return send_from_directory(str(prototypes_dir), filename)


# 前端路由支持（SPA）
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    """提供前端静态文件服务"""
    if not FRONTEND_DIST.exists():
        return jsonify({
            'error': '前端构建产物不存在',
            'message': '请先运行: cd frontend && npm run build'
        }), 404
    
    # API 路由不处理
    if path.startswith('api/'):
        return jsonify({'error': 'API endpoint not found'}), 404
    
    # 如果是文件请求，直接返回
    if path and (FRONTEND_DIST / path).exists():
        return send_from_directory(str(FRONTEND_DIST), path)
    
    # SPA 路由，返回 index.html
    return send_from_directory(str(FRONTEND_DIST), 'index.html')


def find_available_port(start_port=8080, max_attempts=10):
    """查找可用端口"""
    import socket
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('0.0.0.0', port))
                return port
        except OSError:
            continue
    return None


if __name__ == '__main__':
    port = find_available_port(8080)
    if port is None:
        exit(1)
    app.run(host='0.0.0.0', port=port, debug=False)
