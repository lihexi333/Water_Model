from flask import Flask, request, jsonify
from flask_cors import CORS
from GLM_api2 import run_conversation, functions
import json
import uuid  # 添加这行导入

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

def convert_message(msg):
    """转换消息对象为可序列化的字典"""
    print(f"Converting message: {msg}")
    
    # 生成唯一id
    message_id = str(uuid.uuid4())
    
    if hasattr(msg, 'model_dump'):
        result = msg.model_dump()
        result['id'] = message_id
        return result
    elif hasattr(msg, '__dict__'):
        message_dict = {
            'id': message_id,
            'role': msg.role if hasattr(msg, 'role') else 'assistant',
            'content': msg.content if hasattr(msg, 'content') else str(msg)
        }
        if hasattr(msg, 'function_call'):
            message_dict['function_call'] = {
                'name': msg.function_call.name,
                'arguments': msg.function_call.arguments
            }
        return message_dict
    elif isinstance(msg, dict):
        if msg.get('role') == 'function':
            result = {
                'id': message_id,
                'role': 'assistant',
                'content': f"函数 {msg.get('name')} 的查询结果:\n{json.dumps(msg.get('content'), ensure_ascii=False, indent=2)}"
            }
            return result
        msg['id'] = message_id  # 为已有的dict添加id
        return msg
    else:
        return {
            'id': message_id,
            'role': 'assistant',
            'content': str(msg)
        }

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        query = data.get('message')
        messages = data.get('history', [])
        
        # 记录输出信息
        output_log = []

        response_messages = run_conversation(
            query=query,
            messages=messages,
            functions=functions,
            stream=False,
            max_retry=5
        )
        
        if response_messages is None:
            return jsonify({
                'success': True,
                'messages': [{
                    'role': 'assistant',
                    'content': '抱歉，我暂时无法处理您的请求，请稍后再试。'
                }]
            })
        
        try:
            converted_messages = [convert_message(msg) for msg in response_messages]
            
            # 将输出信息添加到消息中
            for msg in converted_messages:
                output_log.append(msg['content'])

            filtered_messages = [
                msg for msg in converted_messages 
                if msg['role'] in ['assistant', 'function']
            ]
            
            if not filtered_messages:
                return jsonify({
                    'success': True,
                    'messages': [{
                        'role': 'assistant',
                        'content': '抱歉，没有得到有效的回复'
                    }]
                })
            
            # 将输出日志也返回
            return jsonify({
                'success': True,
                'messages': filtered_messages,
                'output_log': output_log  # 返回输出日志
            })
            
        except Exception as e:
            print(f"Error in message conversion: {str(e)}")
            return jsonify({
                'success': True,
                'messages': [{
                    'role': 'assistant',
                    'content': '消息处理过程中出现错误，请重试。'
                }]
            })
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)  # 开启调试模式