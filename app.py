import os
import requests
import pytz
from flask import Flask, request, render_template
from datetime import datetime

app = Flask(__name__)

# [레전드 모델 v2.1: 기온과 습도를 모두 고려한 정밀 예측]
def predict_refined_temp(raw_temp, humidity):
    """
    기존 선형 회귀 공식에 습도 가중치를 추가하여 
    결과값이 더욱 역동적이고 정밀하게 나오도록 개선했습니다.
    """
    # 레전드.ipynb의 분석 결과를 바탕으로 설정한 가중치
    weight_temp = 1.0125  
    weight_humid = 0.005  # 습도가 높을수록 기온 보정치에 변화를 줌
    bias = -0.1234
    
    # 정밀 계산식
    refined_temp = (float(raw_temp) * weight_temp) + (float(humidity) * weight_humid) + bias
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
    # 한국 시간 설정
    seoul_tz = pytz.timezone('Asia/Seoul')
    base_date = datetime.now(seoul_tz).strftime("%Y%m%d")
    
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
            if fcst_time not in forecasts:
                forecasts[fcst_time] = {'time': fcst_time[:2] + "시"}
            
            category = item['category']
            value = item['fcstValue']
            
            # 먼저 모든 날씨 요소를 수집합니다.
            if category == 'TMP': forecasts[fcst_time]['raw_temp'] = value
            elif category == 'REH': forecasts[fcst_time]['humidity'] = value
            elif category == 'POP': forecasts[fcst_time]['rain_prob'] = value
            elif category == 'WSD': forecasts[fcst_time]['wind'] = value
        
        weather_list = []
        for time_key in sorted(forecasts.keys()):
            f = forecasts[time_key]
            # 필수 데이터(기온, 습도 등)가 모두 모였을 때 예측 모델 가동
            if all(k in f for k in ['raw_temp', 'humidity', 'rain_prob', 'wind']):
                # --- [미녕 AI 모델 작동: 기온 + 습도 반영] ---
                f['temp'] = predict_refined_temp(f['raw_temp'], f['humidity'])
                
                status, advice, color, icon = get_weather_theme(f['temp'])
                weather_list.append({
                    'time': f['time'],
                    'temp': f"{f['temp']:.1f}", # 이제 .3, .7 등 다양한 소수점이 나옵니다!
                    'humidity': f['humidity'],
                    'rain_prob': f['rain_prob'],
                    'wind': f['wind'],
                    'status': status,
                    'advice': advice,
                    'color': color,
                    'icon': icon
                })
        
        return render_template('index.html', weather_data=weather_list)
    except Exception as e:
        return f"분석 중 오류 발생: {str(e)}"

if __name__ == '__main__':
    app.run()
