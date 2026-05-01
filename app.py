from flask import Flask, request
import requests
from datetime import datetime

app = Flask(__name__)

# ================= [설정 구역] =================
REST_API_KEY = '168466c7fc817cdaa624d8d743054b4d' 
SERVICE_KEY = '04c962ef8ad36d2e639dd73ce8774a570cfb2e0ae8f243022b01a670faf440fa'
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
    code = request.args.get('code')
    if not code:
        return "인가 코드가 없습니다. 다시 시도해주세요."
    
    token_url = "https://kauth.kakao.com/oauth/token"
    # 중괄호를 하나로 수정했습니다!
    token_data = {
        "grant_type": "authorization_code",
        "client_id": REST_API_KEY,
        "redirect_uri": REDIRECT_URI,
        "code": code
    }
    
    token_res = requests.post(token_url, data=token_data).json()
    if 'access_token' not in token_res:
        return f"토큰 발급 실패: {token_res.get('error_description', '키 설정을 확인하세요.')}"

    weather_url = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"
    base_date = datetime.now().strftime("%Y%m%d")
    
    # 중괄호를 하나로 수정했습니다!
    weather_params = {
        'serviceKey': SERVICE_KEY,
        'dataType': 'JSON',
        'base_date': base_date,
        'base_time': '0500', 
        'nx': '55', 'ny': '127',
        'numOfRows': 200
    }

    try:
        weather_res = requests.get(weather_url, params=weather_params).json()
        items = weather_res['response']['body']['items']['item']
        
        weather_table = """
        <table border="1" style="margin: 20px auto; border-collapse: collapse; width: 300px; text-align: center;">
            <tr style="background-color: #f2f2f2;">
                <th>시간</th>
                <th>기온(℃)</th>
            </tr>
        """
        
        for item in items:
            if item.get('fcstDate') == base_date and item.get('category') == 'TMP':
                time = item['fcstTime'][:2] + "시"
                temp = item['fcstValue']
                weather_table += f"<tr><td>{time}</td><td>{temp}도</td></tr>"
        
        weather_table += "</table>"
        
    except Exception as e:
        weather_table = f"<p style='color:red;'>데이터 처리 중 오류: {e}</p>"

    return f'''
        <div style="text-align: center; font-family: sans-serif; padding: 20px;">
            <h2 style="color: #2d89ef;">✅ 로그인 및 날씨 조회 성공!</h2>
            <hr style="width: 50%;">
            {weather_table}
            <br>
            <a href="/" style="text-decoration: none; color: white; background: #333; padding: 10px 20px; border-radius: 5px;">홈으로 돌아가기</a>
        </div>
    '''

if __name__ == '__main__':
    app.run(port=5000, debug=True)
