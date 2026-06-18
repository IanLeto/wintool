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
    except Exception as e:
        print(f"加载数据失败: {e}")
        return []


def save_snippets(snippets):
    """保存代码片段到文件"""
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(snippets, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"保存数据失败: {e}")
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
        snippets = load_snippets()
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
    # 查找可用端口
    port = find_available_port(8080)
    
    if port is None:
        print("=" * 50)
        print("  错误: 无法找到可用端口（尝试了 8080-8089）")
        print("  请手动停止占用端口的程序，或修改代码指定其他端口")
        print("=" * 50)
        exit(1)
    
    print("=" * 50)
    print("  Wintool 代码片段库 - Python 后端")
    print(f"  访问地址: http://localhost:{port}")
    if port != 8080:
        print(f"  注意: 8080 端口被占用，已自动切换到 {port} 端口")
    print("  数据文件: code_snippets/snippets.json")
    
    if FRONTEND_DIST.exists():
        print("  前端模式: 生产环境（静态文件）")
        print("  前端目录:", FRONTEND_DIST)
    else:
        print("  前端模式: 开发环境（需单独启动）")
        print("  提示: 运行 'cd frontend && npm run build' 生成静态文件")
    
    print("=" * 50)
    print()
    
    app.run(host='0.0.0.0', port=port, debug=False)
