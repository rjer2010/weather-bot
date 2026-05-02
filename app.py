import os
import requests
from flask import Flask, request, render_template
from datetime import datetime

app = Flask(__name__)

# [1. 분석 로직] 반드시 상단에 위치해야 합니다!
def get_weather_theme(temp):
    if temp <= 5:
        return "🥶 매우 추움", "내복과 두꺼운 패딩 필수!", "#0050ef", "https://cdn-icons-png.flaticon.com/512/2322/2322701.png"
    elif temp <= 12:
        return "🍂 쌀쌀함", "코트나 경량 패딩이 적당해요.", "#e3a21a", "https://cdn-icons-png.flaticon.com/512/2204/2204342.png"
    elif temp <= 19:
        return "⛅ 선선함", "가디건이나 얇은 재킷을 추천!", "#2d89ef", "https://cdn-icons-png.flaticon.com/512/1163/1163661.png"
    else:
        return "☀️ 따뜻함", "가벼운 셔츠 차림이 좋겠네요.", "#60a917", "https://cdn-icons-png.flaticon.com/512/869/869869.png"

@app.route('/')
def index():
    REDIRECT_URI = f"https://{request.host}/callback"
    auth_url = f"https://kauth.kakao.com/oauth/authorize?client_id={os.environ.get('KAKAO_KEY')}&redirect_uri={REDIRECT_URI}&response_type=code"
    # index.html로 auth_url 변수를 전달합니다.
    return render_template('index.html', auth_url=auth_url)

@app.route('/callback')
def callback():
    weather_url = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"
    base_date = datetime.now().strftime("%Y%m%d")
    params = {
        'serviceKey': os.environ.get('WEATHER_KEY'),
        'dataType': 'JSON', 'base_date': base_date, 'base_time': '0500', 
        'nx': '55', 'ny': '127', 'numOfRows': 100
    }
    
    try:
        res = requests.get(weather_url, params=params).json()
        items = res['response']['body']['items']['item']
        
        weather_list = []
        for item in items:
            if item['category'] == 'TMP':
                temp = int(item['fcstValue'])
                status, advice, color, icon = get_weather_theme(temp)
                weather_list.append({
                    'time': item['fcstTime'][:2] + "시",
                    'temp': temp,
                    'status': status,
                    'advice': advice,
                    'color': color,
                    'icon': icon
                })
        
        # templates/index.html에 weather_data라는 이름으로 리스트를 넘깁니다.
        return render_template('index.html', weather_data=weather_list)
    except Exception as e:
        # 에러 발생 시 어떤 에러인지 화면에 출력해 줍니다 (디버깅용)
        return f"상세 에러 내용: {str(e)}"
