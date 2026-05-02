import os
import requests
import json
from datetime import datetime
import pytz

# 1. 설정 (주소 부분을 본인의 Vercel 주소로 확인해 주세요)
NOTI_TIME = "08:00"
LOCATION_NAME = "서울"
NX = '55' 
NY = '127'
# 여기에 본인의 Vercel 사이트 주소를 넣으세요 (끝에 /는 빼는 것이 깔끔합니다)
MY_WEBSITE_URL = "https://weather-e96931yx6-rjer2010s-projects.vercel.app"

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
    url = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"
    
    now = datetime.now(pytz.timezone('Asia/Seoul'))
    base_date = now.strftime("%Y%m%d")
    
    params = {
        'serviceKey': WEATHER_KEY,
        'dataType': 'JSON',
        'base_date': base_date,
        'base_time': '0500',
        'nx': NX, 'ny': NY,
        'numOfRows': 290
    }
    
    try:
        res = requests.get(url, params=params).json()
        items = res['response']['body']['items']['item']
        
        temps = []
        rain_probs = []
        
        for item in items:
            if item['fcstDate'] == base_date:
                if item['category'] == 'TMP':
                    temps.append(int(item['fcstValue']))
                if item['category'] == 'POP':
                    rain_probs.append(int(item['fcstValue']))

        if not temps: return "날씨 데이터를 가져오지 못했습니다."

        avg_temp = sum(temps) / len(temps)
        max_temp = max(temps)
        min_temp = min(temps)
        max_rain = max(rain_probs)

        # 평균 기온 소수점 출력 오류 수정 (.1;f -> .1f)
        briefing = (
            f"✨ {LOCATION_NAME} 날씨 브리핑\n\n"
            f"🌡 평균 기온: {avg_temp:.1f}도\n"
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
    except Exception as e:
        return f"날씨 분석 중 오류 발생: {str(e)}"

def send_kakao(message):
    token = get_access_token()
    url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
    headers = {"Authorization": f"Bearer {token}"}
    
    # [수정 포인트] 링크 주소를 localhost에서 실제 Vercel 주소로 변경
    template = {
        "object_type": "text",
        "text": message,
        "link": {
            "web_url": MY_WEBSITE_URL,
            "mobile_web_url": MY_WEBSITE_URL
        },
        "button_title": "미녕예보 상세 확인" # 버튼 문구도 예쁘게 수정
    }
    
    res = requests.post(url, headers=headers, data={"template_object": json.dumps(template)})
    return res.status_code

if __name__ == "__main__":
    seoul_tz = pytz.timezone('Asia/Seoul')
    now_seoul = datetime.now(seoul_tz)
    current_time = now_seoul.strftime("%H:%M")
    
    print(f"현재 시각(KST): {current_time} / 설정 시각: {NOTI_TIME}")

    if current_time.split(':')[0] == NOTI_TIME.split(':')[0]:
        print("브리핑 전송을 시작합니다.")
        content = get_weather_briefing()
        send_kakao(content)
    else:
        print("설정된 시간이 아니므로 종료합니다.")
