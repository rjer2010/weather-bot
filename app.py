import os
import requests
from flask import Flask, request
from datetime import datetime

app = Flask(__name__)

# [환경 변수 설정]
REST_API_KEY = os.environ.get('KAKAO_KEY')
SERVICE_KEY = os.environ.get('WEATHER_KEY')

# [레전드 모델 로직 - 순수 파이썬 버전]
def minyoung_analysis(temp):
    # Colab에서 정의했던 판단 로직을 그대로 가져왔습니다.
    if temp <= 5:
        return "⚠️ 매우 추움", "내복과 두꺼운 패딩 필수!", "#0050ef"
    elif temp <= 12:
        return "🍂 쌀쌀함", "코트나 경량 패딩이 적당해요.", "#e3a21a"
    elif temp <= 19:
        return "⛅ 선선함", "가디건이나 얇은 재킷을 추천해요.", "#2d89ef"
    else:
        return "☀️ 따뜻함", "가벼운 셔츠 차림이 좋겠네요.", "#60a917"

@app.route('/')
def index():
    actual_host = request.host
    REDIRECT_URI = f"https://{actual_host}/callback"
    kakao_auth_url = f"https://kauth.kakao.com/oauth/authorize?client_id={REST_API_KEY}&redirect_uri={REDIRECT_URI}&response_type=code"
    return f'''
        <div style="text-align: center; margin-top: 50px; font-family: sans-serif;">
            <h1>☀️ 미녕예보 AI (Light 버전)</h1>
            <p>메모리 최적화를 마친 '레전드' 분석 모델입니다.</p>
            <a href="{kakao_auth_url}"><img src="https://k.kakaocdn.net/14/dn/btroDszwNrM/3v5MvOf0PEw8HSnSKeyqK1/o.jpg" width="222"></a>
        </div>
    '''

@app.route('/callback')
def callback():
    weather_url = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"
    base_date = datetime.now().strftime("%Y%m%d")
    params = {
        'serviceKey': SERVICE_KEY,
        'dataType': 'JSON', 'base_date': base_date, 'base_time': '0500', 
        'nx': '55', 'ny': '127', 'numOfRows': 100
    }
    
    try:
        res = requests.get(weather_url, params=params).json()
        items = res['response']['body']['items']['item']
        
        table_rows = ""
        for item in items:
            if item['category'] == 'TMP':
                temp = int(item['fcstValue'])
                time = item['fcstTime'][:2] + "시"
                
                # --- 미녕 AI 분석 실행 ---
                status, advice, color = minyoung_analysis(temp)
                
                table_rows += f"""
                <tr>
                    <td style="padding: 10px;">{time}</td>
                    <td>{temp}도</td>
                    <td style="font-weight: bold; color: {color};">{status}</td>
                    <td style="font-size: 0.9em;">{advice}</td>
                </tr>"""
        
        return f'''
            <h2 style="text-align:center;">✅ 분석 완료</h2>
            <table border="1" style="margin: auto; border-collapse: collapse; width: 90%; text-align: center;">
                <tr style="background: #eee;"><th>시간</th><th>기온</th><th>AI분석</th><th>추천복장</th></tr>
                {table_rows}
            </table>
        '''
    except Exception as e:
        return f"분석 오류: {str(e)}"

if __name__ == '__main__':
    app.run()
