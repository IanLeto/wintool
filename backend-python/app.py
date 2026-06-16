#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
代码片段库 - Python Flask 后端
用于内网环境，无需 JDK/Maven
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime
from pathlib import Path

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
        'version': '1.0.0'
    })


if __name__ == '__main__':
    print("=" * 50)
    print("  Wintool 代码片段库 - Python 后端")
    print("  访问地址: http://localhost:8080")
    print("  数据文件: code_snippets/snippets.json")
    print("=" * 50)
    print()
    
    app.run(host='0.0.0.0', port=8080, debug=False)
