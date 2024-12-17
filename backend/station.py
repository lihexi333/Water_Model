from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import urllib.parse
import urllib3

app = Flask(__name__)
CORS(app) # 启用跨域支持

@app.route('/api/stations', methods=['GET'])
def find_reservoir_stations():
    try:
        # 从请求参数获取输入
        province = request.args.get('province', '')
        valley = request.args.get('valley', '')
        target_station = request.args.get('target_station', '')
        queried_variable = request.args.get('queried_variable', '')

        print(f"接收到的参数: province={province}, valley={valley}, target_station={target_station}, queried_variable={queried_variable}")

        # 原有的API调用逻辑
        host = 'https://hydrology.market.alicloudapi.com'
        path = '/api/water_rain/reservoir_stations'
        appcode = '2e3185ab512b49c5b0b0a42044341dc4'

        querys = 'province=' + urllib.parse.quote(province) + '&valley=' + urllib.parse.quote(valley)
        url = host + path + '?' + querys
        
        print(f"请求URL: {url}")

        http = urllib3.PoolManager()
        headers = {
            'Authorization': 'APPCODE ' + appcode
        }
        
        print("发送API请求...")
        response = http.request('GET', url, headers=headers)
        print(f"API响应状态码: {response.status}")
        
        content = response.data.decode('utf-8')
        print(f"API响应内容: {content}")

        if content:
            data = json.loads(content)
            # 查找匹配的站点
            result = []
            if 'data' in data:
                for station in data['data']:
                    if not target_station or station.get(queried_variable, '') == target_station:
                        result.append(station)
            
            print(f"找到 {len(result)} 个匹配结果")
            return jsonify({
                'success': True,
                'data': result
            })
        else:
            return jsonify({
                'success': False,
                'error': 'No content received from API'
            }), 500

    except Exception as e:
        print(f"发生错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/reservoir', methods=['GET']) 
def find_reservoir_data():
    try:
        # 从请求参数获取输入
        pubtime = request.args.get('pubtime', '')
        river = request.args.get('river', '')
        station_name = request.args.get('station_name', '')
        target_station = request.args.get('target_station', '')

        # 原有的API调用逻辑
        host = 'https://hydrology.market.alicloudapi.com'
        path = '/api/water_rain/station/reservoir'
        appcode = '2e3185ab512b49c5b0b0a42044341dc4'

        querys = 'pubtime='+pubtime+'&river='+urllib.parse.quote(river)+'&station_name='+urllib.parse.quote(station_name)
        url = host + path + '?' + querys

        http = urllib3.PoolManager()
        headers = {
            'Authorization': 'APPCODE ' + appcode
        }
        response = http.request('GET', url, headers=headers)
        content = response.data.decode('utf-8')
        
        return jsonify(json.loads(content))

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)