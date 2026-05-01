import os
from flask import Flask, request
import requests
from datetime import datetime

app = Flask(__name__)

# ================= [보안 설정 구역] =================
# Vercel 환경 변수에서 값을 가져옵니다. 
# 만약 값이 없으면 None을 반환합니다.
REST_API_KEY = os.environ.get('KAKAO_KEY') 
SERVICE_KEY = os.environ.get('WEATHER_KEY')
REDIRECT_URI = 'https://weather-bot-git-main-rjer2010s-projects.vercel.app/callback' 
# ===================================================

@app.route('/')
def index():
    # 보안 체크: 키가 설정되지 않았을 때 에러 메시지 출력
    if not REST_API_KEY:
        return "<h2>환경 설정 오류</h2><p>Vercel에서 KAKAO_KEY를 설정해주세요.</p>"
        
    kakao_auth_url = f"https://kauth.kakao.com/oauth/authorize?client_id={REST_API_KEY}&redirect_uri={REDIRECT_URI}&response_type=code"
    return f'''
        <div style="text-align: center; margin-top: 50px; font-family: sans-serif;">
            <h1>☀️ 미녕예보 웹사이트</h1>
            <p>보안 모드가 활성화되었습니다.</p>
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
        token_res = requests.post(token_url, data=token_data).json()
        access_token = token_res.get('access_token')
        
        if not access_token:
            return f"로그인 실패: {token_res.get('error_description', '토큰을 가져올 수 없습니다.')}"

        # 날씨 정보 가져오기 로직 (중략 - 기존과 동일)
        return "<h2>✅ 보안 연결 성공!</h2><p>날씨 정보를 불러오는 중...</p>" # 테스트용 메시지
        
    except Exception as e:
        return f"에러 발생: {str(e)}"

if __name__ == '__main__':
    app.run()
