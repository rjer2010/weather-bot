import os

# 코드 상단에 이렇게 적어주면 GitHub Secrets 값을 가져옵니다.
REST_API_KEY = os.environ.get('KAKAO_REST_KEY')
REFRESH_TOKEN = os.environ.get('KAKAO_REFRESH_TOKEN')
WEATHER_KEY = os.environ.get('WEATHER_SERVICE_KEY')
import base64
import requests
import json
from datetime import datetime

# --- 설정 정보 ---
REST_API_KEY = "168466c7fc817cdaa624d8d743054b4d"
REFRESH_TOKEN = "내_카카오_REFRESH_TOKEN"
WEATHER_SERVICE_KEY = "기상청_DECODING_키"

def get_new_access_token():
    """만료된 토큰을 대비해 항상 새 토큰을 받아옵니다."""
    url = "https://kauth.kakao.com/oauth/token"
    data = {
        "grant_type": "refresh_token",
        "client_id": REST_API_KEY,
        "refresh_token": REFRESH_TOKEN
    }
    response = requests.post(url, data=data)
    return response.json().get("access_token")

def get_weather():
    """기상청 실황 데이터를 가져옵니다."""
    url = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst"
    now = datetime.now()
    params = {
        'serviceKey': WEATHER_SERVICE_KEY,
        'dataType': 'JSON',
        'base_date': now.strftime("%Y%m%d"),
        'base_time': now.strftime("%H00"),
        'nx': '55', 'ny': '127'
    }
    res = requests.get(url, params=params)
    items = res.json()['response']['body']['items']['item']
    # 기온(T1H) 추출
    temp = next(item['obsrValue'] for item in items if item['category'] == 'T1H')
    return float(temp)

def main_handler(event, context):
    """구글 클라우드가 실행하는 메인 함수"""
    current_temp = get_weather()
    
    # 예: 영하로 떨어지면 알림
    if current_temp <= 0:
        token = get_new_access_token()
        message = f"🚨 [미녕예보] 현재 기온 {current_temp}°C! 동파에 주의하세요."
        
        headers = {"Authorization": f"Bearer {token}"}
        post_data = {
            "template_object": json.dumps({
                "object_type": "text",
                "text": message,
                "link": {"web_url": "https://localhost:3000"}
            })
        }
        requests.post("https://kapi.kakao.com/v2/api/talk/memo/default/send", headers=headers, data=post_data)
        
    return "OK"
