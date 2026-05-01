import os
import requests
import json
from datetime import datetime

# 깃허브 금고(Secrets)에서 꺼내올 열쇠들
REST_KEY = os.environ.get('KAKAO_REST_KEY')
REFRESH_TOKEN = os.environ.get('KAKAO_REFRESH_TOKEN')
WEATHER_KEY = os.environ.get('WEATHER_SERVICE_KEY')

def get_access_token():
    url = "https://kauth.kakao.com/oauth/token"
    data = {"grant_type": "refresh_token", "client_id": REST_KEY, "refresh_token": REFRESH_TOKEN}
    return requests.post(url, data=data).json().get("access_token")

def main():
    # 기상청 데이터 가져오기 (서울 기준)
    w_url = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst"
    params = {'serviceKey': WEATHER_KEY, 'dataType': 'JSON', 'base_date': datetime.now().strftime("%Y%m%d"), 'base_time': datetime.now().strftime("%H00"), 'nx': '55', 'ny': '127'}
    
    res = requests.get(w_url, params=params).json()
    items = res['response']['body']['items']['item']
    temp = next(i['obsrValue'] for i in items if i['category'] == 'T1H')

    # 카톡 보내기 (예: 5도 이하일 때)
    if float(temp) <= 5.0:
        token = get_access_token()
        msg = {"object_type": "text", "text": f"🌡 현재 기온 {temp}도! 추워요!", "link": {"web_url": "https://localhost:3000"}}
        requests.post("https://kapi.kakao.com/v2/api/talk/memo/default/send", headers={"Authorization": f"Bearer {token}"}, data={"template_object": json.dumps(msg)})

if __name__ == "__main__":
    main()
