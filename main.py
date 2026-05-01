import os
import requests
import json
from datetime import datetime
import pytz # 시간대 설정을 위해 필요 (requirements.txt에 추가 필요)

# 1. 설정 (이 부분만 수정하세요)
NOTI_TIME = "08:00"  # 브리핑을 받고 싶은 시간 (24시간 형식)
LOCATION_NAME = "서울"
NX = '55' 
NY = '127'

# 깃허브 금고에서 키 가져오기
REST_KEY = os.environ.get('KAKAO_REST_KEY')
REFRESH_TOKEN = os.environ.get('KAKAO_REFRESH_TOKEN')
WEATHER_KEY = os.environ.get('WEATHER_SERVICE_KEY')

def get_access_token():
    url = "https://kauth.kakao.com/oauth/token"
    data = {"grant_type": "refresh_token", "client_id": REST_KEY, "refresh_token": REFRESH_TOKEN}
    res = requests.post(url, data=data).json()
    return res.get("access_token")

def get_weather_briefing():
    # 단기예보 API (오늘 하루의 예보를 가져옴)
    url = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"
    
    # 오늘 날짜 구하기
    now = datetime.now(pytz.timezone('Asia/Seoul'))
    base_date = now.strftime("%Y%m%d")
    
    params = {
        'serviceKey': WEATHER_KEY,
        'dataType': 'JSON',
        'base_date': base_date,
        'base_time': '0500', # 새벽 5시 발표 직후 데이터가 가장 정확함
        'nx': NX, 'ny': NY,
        'numOfRows': 290 # 하루치(TMP, POP 등)를 다 가져오기 위한 넉넉한 양
    }
    
    res = requests.get(url, params=params).json()
    items = res['response']['body']['items']['item']
    
    temps = []
    rain_probs = []
    
    for item in items:
        # 오늘 날짜에 해당하는 데이터만 추출
        if item['fcstDate'] == base_date:
            if item['category'] == 'TMP': # 기온
                temps.append(int(item['fcstValue']))
            if item['category'] == 'POP': # 강수확률
                rain_probs.append(int(item['fcstValue']))

    if not temps: return "날씨 데이터를 가져오지 못했습니다."

    avg_temp = sum(temps) / len(temps)
    max_temp = max(temps)
    min_temp = min(temps)
    max_rain = max(rain_probs)

    briefing = (
        f"✨ {LOCATION_NAME} 날씨 브리핑\n\n"
        f"🌡 평균 기온: {avg_temp:.1;f}도\n"
        f"🌡 최고/최저: {max_temp}도 / {min_temp}도\n"
        f"☔ 최고 강수확률: {max_rain}%\n\n"
    )

    if max_rain >= 50:
        briefing += "📢 오늘은 비 소식이 있어요. 우산을 꼭 챙기세요!"
    elif max_temp - min_temp >= 10:
        briefing += "📢 일교차가 커요. 겉옷을 챙기시면 좋겠어요."
    else:
        briefing += "📢 오늘도 즐거운 하루 보내세요!"
        
    return briefing

def send_kakao(message):
    token = get_access_token()
    url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
    headers = {"Authorization": f"Bearer {token}"}
    template = {
        "object_type": "text",
        "text": message,
        "link": {"web_url": "https://www.weather.go.kr"}
    }
    res = requests.post(url, headers=headers, data={"template_object": json.dumps(template)})
    return res.status_code

if __name__ == "__main__":
    # 한국 시간 설정
    seoul_tz = pytz.timezone('Asia/Seoul')
    now_seoul = datetime.now(seoul_tz)
    current_time = now_seoul.strftime("%H:%M")
    
    print(f"현재 시각(KST): {current_time} / 설정 시각: {NOTI_TIME}")

    # 설정한 시간과 현재 시간이 일치할 때만 실행
    # (GitHub Actions가 1시간마다 실행되므로 '시'만 체크하거나 범위를 줍니다)
    if current_time.split(':')[0] == NOTI_TIME.split(':')[0]:
        print("브리핑 전송을 시작합니다.")
        content = get_weather_briefing()
        send_kakao(content)
    else:
        print("설정된 시간이 아니므로 종료합니다.")
