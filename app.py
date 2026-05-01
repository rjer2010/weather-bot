import os
from flask import Flask, request
import requests
from datetime import datetime

app = Flask(__name__)

# ================= [보안 설정 구역] =================
# Vercel 환경 변수에서 가져오기 (이미 설정하신 이름 그대로!)
REST_API_KEY = os.environ.get('KAKAO_KEY') 
SERVICE_KEY = os.environ.get('WEATHER_KEY')
# Redirect URI는 현재 Vercel 주소로 자동 설정 (수동 입력 필요 없음)
REDIRECT_URI = f"https://{os.environ.get('VERCEL_URL')}/callback" if os.environ.get('VERCEL_URL') else 'http://localhost:5000/callback'
# ===================================================

@app.route('/')
def index():
    if not REST_API_KEY:
        return "<h2>환경 설정 오류</h2><p>Vercel Settings에서 KAKAO_KEY를 등록해주세요.</p>"
        
    kakao_auth_url = f"https://kauth.kakao.com/oauth/authorize?client_id={REST_API_KEY}&redirect_uri={REDIRECT_URI}&response_type=code"
    return f'''
        <div style="text-align: center; margin-top: 50px; font-family: sans-serif;">
            <h1>☀️ 미녕예보 웹사이트</h1>
            <p>보안 연결이 준비되었습니다. 로그인을 눌러 날씨를 확인하세요.</p>
            <a href="{kakao_auth_url}">
                <img src="https://k.kakaocdn.net/14/dn/btroDszwNrM/3v5MvOf0PEw8HSnSKeyqK1/o.jpg" width="222" alt="카카오 로그인">
            </a>
        </div>
    '''

@app.route('/callback')
def callback():
    code = request.args.get('code')
    token_url = "https://kauth.kakao.com/oauth/token"
    token_data = {
        "grant_type": "authorization_code",
        "client_id": REST_API_KEY,
        "redirect_uri": REDIRECT_URI,
        "code": code
    }
    
    try:
        # 1. 토큰 가져오기
        token_res = requests.post(token_url, data=token_data).json()
        access_token = token_res.get('access_token')
        
        if not access_token:
            return f"로그인 실패: {token_res.get('error_description', '키 설정을 확인하세요.')}"

        # 2. 기상청 날씨 데이터 가져오기
        weather_url = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"
        base_date = datetime.now().strftime("%Y%m%d")
        weather_params = {
            'serviceKey': SERVICE_KEY,
            'dataType': 'JSON',
            'base_date': base_date,
            'base_time': '0500', 
            'nx': '55', 'ny': '127',
            'numOfRows': 200
        }

        weather_res = requests.get(weather_url, params=weather_params).json()
        items = weather_res['response']['body']['items']['item']
        
        weather_table = """
        <table border="1" style="margin: 20px auto; border-collapse: collapse; width: 300px; text-align: center;">
            <tr style="background-color: #f2f2f2;"><th>시간</th><th>기온(℃)</th></tr>
        """
        
        for item in items:
            if item.get('fcstDate') == base_date and item.get('category') == 'TMP':
                weather_table += f"<tr><td>{item['fcstTime'][:2]}시</td><td>{item['fcstValue']}도</td></tr>"
        weather_table += "</table>"

        # 3. 결과 화면 출력
        return f'''
            <div style="text-align: center; font-family: sans-serif; padding: 20px;">
                <h2 style="color: #2d89ef;">✅ 보안 연결 및 날씨 조회 성공!</h2>
                <p>실시간 기상청 정보를 불러왔습니다.</p>
                <hr style="width: 50%;">
                {weather_table}
                <br>
                <a href="/" style="text-decoration: none; color: white; background: #333; padding: 10px 20px; border-radius: 5px;">홈으로 돌아가기</a>
            </div>
        '''
        
    except Exception as e:
        return f"<h2>❌ 데이터 처리 중 오류 발생</h2><p>{str(e)}</p>"

if __name__ == '__main__':
    app.run()
