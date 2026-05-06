import os
import requests
import pytz
from flask import Flask, request, render_template
from datetime import datetime

app = Flask(__name__)

# [레전드 모델: 선형 회귀 공식]
def predict_refined_temp(raw_temp):
    weight = 1.0125  # 미녕님 모델 가중치
    bias = -0.1234   # 미녕님 모델 절편
    refined_temp = (raw_temp * weight) + bias
    return round(refined_temp, 1)

def get_weather_theme(temp):
    temp_float = float(temp)
    if temp_float <= 5:
        return "🥶 매우 추움", "내복과 두꺼운 패딩 필수!", "#0050ef", "https://cdn-icons-png.flaticon.com/512/2322/2322701.png"
    elif temp_float <= 12:
        return "🍂 쌀쌀함", "코트나 경량 패딩이 적당해요.", "#e3a21a", "https://cdn-icons-png.flaticon.com/512/2204/2204342.png"
    elif temp_float <= 19:
        return "⛅ 선선함", "가디건이나 얇은 재킷을 추천!", "#2d89ef", "https://cdn-icons-png.flaticon.com/512/1163/1163661.png"
    else:
        return "☀️ 따뜻함", "가벼운 셔츠 차림이 좋겠네요.", "#60a917", "https://cdn-icons-png.flaticon.com/512/869/869869.png"

@app.route('/')
def index():
    actual_host = request.host
    REDIRECT_URI = f"https://{actual_host}/callback"
    auth_url = f"https://kauth.kakao.com/oauth/authorize?client_id={os.environ.get('KAKAO_KEY')}&redirect_uri={REDIRECT_URI}&response_type=code"
    return render_template('index.html', auth_url=auth_url)

@app.route('/callback')
def callback():
    weather_url = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"
    base_date = datetime.now(pytz.timezone('Asia/Seoul')).strftime("%Y%m%d")
    params = {
        'serviceKey': os.environ.get('WEATHER_KEY'),
        'dataType': 'JSON', 'base_date': base_date, 'base_time': '0500', 
        'nx': '55', 'ny': '127', 'numOfRows': 500 
    }
    
    try:
        res = requests.get(weather_url, params=params).json()
        items = res['response']['body']['items']['item']
        forecasts = {}
        for item in items:
            fcst_time = item['fcstTime']
            if fcst_time not in forecasts: forecasts[fcst_time] = {'time': fcst_time[:2] + "시"}
            category = item['category']
            value = item['fcstValue']
            if category == 'TMP':
                forecasts[fcst_time]['temp'] = predict_refined_temp(float(value))
            elif category == 'REH': forecasts[fcst_time]['humidity'] = value
            elif category == 'POP': forecasts[fcst_time]['rain_prob'] = value
            elif category == 'WSD': forecasts[fcst_time]['wind'] = value
        
        weather_list = []
        for time_key in sorted(forecasts.keys()):
            f = forecasts[time_key]
            if all(k in f for k in ['temp', 'humidity', 'rain_prob', 'wind']):
                status, advice, color, icon = get_weather_theme(f['temp'])
                weather_list.append({
                    'time': f['time'], 'temp': f"{f['temp']:.1f}", 'humidity': f['humidity'],
                    'rain_prob': f['rain_prob'], 'wind': f['wind'], 'status': status,
                    'advice': advice, 'color': color, 'icon': icon
                })
        return render_template('index.html', weather_data=weather_list)
    except Exception as e:
        return f"분석 오류: {str(e)}"
