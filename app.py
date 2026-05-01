from flask import Flask, request
import requests
from datetime import datetime

app = Flask(__name__)

# ================= [설정 구역] =================
# 1. 카카오 REST API 키
REST_API_KEY = '168466c7fc817cdaa624d8d743054b4d' 
# 2. 기상청 서비스 키 (Encoding 또는 Decoding 키 중 맞는 것을 사용)
SERVICE_KEY = '04c962ef8ad36d2e639dd73ce8774a570cfb2e0ae8f243022b01a670faf440fa'
# 3. 리다이렉트 URI (카카오 설정과 동일해야 함)
REDIRECT_URI = 'http://localhost:5000/callback'
# ==============================================

@app.route('/')
def index():
    kakao_auth_url = f"https://kauth.kakao.com/oauth/authorize?client_id={REST_API_KEY}&redirect_uri={REDIRECT_URI}&response_type=code"
    return f'''
        <div style="text-align: center; margin-top: 50px; font-family: sans-serif;">
            <h1>☀️ 미녕예보 웹사이트</h1>
            <p>오늘의 실시간 날씨 정보를 확인하려면 아래 버튼을 눌러주세요.</p>
            <div style="margin-top: 20px;">
                <a href="{kakao_auth_url}">
                    <img src="https://k.kakaocdn.net/14/dn/btroDszwNrM/3v5MvOf0PEw8HSnSKeyqK1/o.jpg" width="222" alt="카카오 로그인">
                </a>
            </div>
        </div>
    '''

@app.route('/callback')
def callback():
    # 1. 카카오로부터 인가 코드 받기
    code = request.args.get('code')
    if not code:
        return "인가 코드가 없습니다. 다시 시도해주세요."
    
    # 2. 인가 코드로 액세스 토큰 요청하기
    token_url = "https://kauth.kakao.com/oauth/token"
    token_data = {{
        "grant_type": "authorization_code",
        "client_id": REST_API_KEY,
        "redirect_uri": REDIRECT_URI,
        "code": code
    }}
    
    token_res = requests.post(token_url, data=token_data).json()
    if 'access_token' not in token_res:
        return f"토큰 발급 실패: {token_res.get('error_description', '키 설정을 확인하세요.')}"

    # 3. 기상청 API를 통해 오늘 날씨 가져오기
    weather_url = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"
    base_date = datetime.now().strftime("%Y%m%d")
    
    weather_params = {{
        'serviceKey': SERVICE_KEY,
        'dataType': 'JSON',
        'base_date': base_date,
        'base_time': '0500',  # 새벽 5시 예보 기준
        'nx': '55', 'ny': '127',
        'numOfRows': 200
    }}

    try:
        weather_res = requests.get(weather_url, params=weather_params).json()
        items = weather_res['response']['body']['items']['item']
        
        # HTML 표 만들기
        weather_table = """
        <table border="1" style="margin: 20px auto; border-collapse: collapse; width: 300px; text-align: center;">
            <tr style="background-color: #f2f2f2;">
                <th>시간</th>
                <th>기온(℃)</th>
            </tr>
        """
        
        for item in items:
            # 오늘 날짜의 기온(TMP) 데이터만 추출
            if item['fcstDate'] == base_date and item['category'] == 'TMP':
                time = item['fcstTime'][:2] + "시"
                temp = item['fcstValue']
                weather_table += f"<tr><td>{time}</td><td>{temp}도</td></tr>"
        
        weather_table += "</table>"
        
    except Exception as e:
        weather_table = f"<p style='color:red;'>날씨 데이터를 가져오는 중 오류가 발생했습니다: {e}</p>"

    # 4. 최종 화면 출력
    return f'''
        <div style="text-align: center; font-family: sans-serif; padding: 20px;">
            <h2 style="color: #2d89ef;">✅ 로그인 및 본인인증 성공!</h2>
            <p>카카오 계정으로 인증되었습니다.</p>
            <hr style="width: 50%;">
            {weather_table}
            <br>
            <a href="/" style="text-decoration: none; color: white; background: #333; padding: 10px 20px; border-radius: 5px;">홈으로 돌아가기</a>
        </div>
    '''

if __name__ == '__main__':
    # debug=True는 코드 수정 시 자동으로 서버를 재시작해줍니다.
    app.run(port=5000, debug=True)
