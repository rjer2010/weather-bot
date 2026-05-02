import os
import requests
from flask import Flask, request, render_template
from datetime import datetime

app = Flask(__name__)

# [환경 변수 및 테마 로직 생략 - 이전과 동일]
def get_weather_theme(temp):
    # (이전 코드의 get_weather_theme 함수 내용을 여기에 그대로 넣으세요)
    if temp <= 5: return "🥶 매우 추움", "내복 필수!", "#0050ef", "아이콘주소"
    # ... 생략 ...
    return "☀️ 따뜻함", "셔츠 차림!", "#60a917", "아이콘주소"

@app.route('/')
def index():
    REDIRECT_URI = f"https://{request.host}/callback"
    auth_url = f"https://kauth.kakao.com/oauth/authorize?client_id={os.environ.get('KAKAO_KEY')}&redirect_uri={REDIRECT_URI}&response_type=code"
    return render_template('index.html', auth_url=auth_url)

@app.route('/callback')
def callback():
    # 기상청 데이터 가져오는 로직 (기존과 동일)
    # ... 생략 (items 가져오는 부분까지) ...
    
    weather_data = []
    for item in items:
        if item['category'] == 'TMP':
            temp = int(item['fcstValue'])
            status, advice, color, icon = get_weather_theme(temp)
            weather_data.append({
                'time': item['fcstTime'][:2] + "시",
                'temp': temp,
                'status': status,
                'advice': advice,
                'color': color,
                'icon': icon
            })
    
    return render_template('index.html', weather_data=weather_data)
