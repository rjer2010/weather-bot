import os
import requests
import pandas as pd
import numpy as np
from flask import Flask, request
from datetime import datetime, timedelta

app = Flask(__name__)

# ================= [보안 및 인증 설정] =================
# 알려주신 키들을 Vercel 환경변수(Settings)에 등록한 후 사용하세요.
REST_API_KEY = os.environ.get('KAKAO_KEY')      # 168466c7fc817cdaa624d8d743054b4d
SERVICE_KEY = os.environ.get('WEATHER_KEY')    # 04c962ef8ad36d2e639dd73ce8774a57...
ACCESS_TOKEN = "_aQ2Ns7R53a19VwoXLVefHb1iokiHkwPAAAAAQoNIFoAAAGd4ziuX08FYMfcu4fs" # 발급받은 토큰 직접 사용 가능
# =====================================================

# [레전드 모델 로직 1] 미녕님의 데이터 전처리 함수 (Colab 추출)
def preprocess_minyoung_logic(temp, humidity, rain):
    # Colab에서 설계하신 기온별 판단 로직을 웹 사이트용으로 최적화
    status = "보통"
    advice = "적절한 외투를 챙기세요."
    color = "#2d89ef"

    if temp <= 5:
        status = "⚠️ 매우 추움"
        advice = "내복과 두꺼운 패딩이 필수인 날씨예요!"
        color = "#0050ef"
    elif temp <= 12:
        status = "🍂 쌀쌀함"
        advice = "코트나 경량 패딩이 적당한 기온입니다."
        color = "#e3a21a"
    
    if rain > 0:
        status = "☔ 비 예보"
        advice = "강수량이 감지되었습니다. 우산을 잊지 마세요!"
        color = "#60a917"
        
    return status, advice, color

# app.py 상단 수정
# ... (생략) ...
@app.route('/')
def index():
    # 주소를 직접 적어주는 것이 가장 확실합니다.
    actual_host = "weather-e96931yx6-rjer2010s-projects.vercel.app" 
    REDIRECT_URI = f"https://{actual_host}/callback"
    
    # 키가 제대로 로드되었는지 확인하는 방어 코드
    if not REST_API_KEY:
        return "<h2>에러: KAKAO_KEY가 Vercel 설정에 없습니다!</h2>"
# ... (생략) ...
        <div style="text-align: center; margin-top: 50px; font-family: sans-serif;">
            <h1 style="color: #333;">☀️ 미녕예보 AI 웹사이트</h1>
            <p style="color: #666;">Colab '레전드' 모델이 실시간으로 날씨를 분석합니다.</p>
            <a href="{kakao_auth_url}"><img src="https://k.kakaocdn.net/14/dn/btroDszwNrM/3v5MvOf0PEw8HSnSKeyqK1/o.jpg" width="222"></a>
        </div>
    '''

@app.route('/callback')
def callback():
    # 기상청 단기예보 조회 (Colab의 get_weather_data 로직 반영)
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
        
        weather_table = """
        <table border="1" style="margin: 20px auto; border-collapse: collapse; width: 95%; text-align: center; font-family: sans-serif;">
            <tr style="background-color: #f2f2f2;">
                <th>시간</th><th>기온(℃)</th><th>미녕 AI 분석</th><th>추천 가이드</th>
            </tr>
        """
        
        for item in items:
            if item['category'] == 'TMP': # 기온 데이터만 추출
                temp = int(item['fcstValue'])
                time = item['fcstTime'][:2] + "시"
                
                # --- [레전드 모델 가동] ---
                # Colab 로직에 따른 실시간 분석
                status, advice, color = preprocess_minyoung_logic(temp, 0, 0)
                
                weather_table += f"""
                <tr>
                    <td style="padding: 10px;">{time}</td>
                    <td>{temp}도</td>
                    <td style="font-weight: bold; color: {color};">{status}</td>
                    <td style="font-size: 0.9em; color: #555;">{advice}</td>
                </tr>"""
        
        weather_table += "</table>"
        return f"<h2 style='text-align:center;'>✅ 미녕 AI 모델 분석 결과</h2>{weather_table}"
        
    except Exception as e:
        return f"분석 중 오류 발생: {str(e)}"

if __name__ == '__main__':
    app.run()
