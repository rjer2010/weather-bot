from flask import Flask, render_template, request, redirect
import requests
import json

app = Flask(__name__)

# 설정값 (본인의 것으로 채우세요)
REST_API_KEY = '내_REST_API_키'
REDIRECT_URI = 'http://localhost:5000/callback' # 테스트용 주소

@app.route('/')
def index():
    # 메인 페이지: 로그인 버튼을 보여줍니다.
    kakao_auth_url = f"https://kauth.kakao.com/oauth/authorize?client_id={REST_API_KEY}&redirect_uri={REDIRECT_URI}&response_type=code"
    return f'''
        <h1>☀️ 미녕예보 웹사이트</h1>
        <p>오늘의 날씨 브리핑을 확인하려면 로그인하세요.</p>
        <a href="{kakao_auth_url}">
            <img src="https://k.kakaocdn.net/14/dn/btroDszwNrM/3v5MvOf0PEw8HSnSKeyqK1/o.jpg" width="222" alt="카카오 로그인 버튼">
        </a>
    '''

@app.route('/callback')
def callback():
    # 카카오가 로그인 성공 후 보내주는 코드를 받는 곳입니다.
    code = request.args.get('code')
    
    # 1. 인가 코드로 토큰 받기
    token_url = "https://kauth.kakao.com/oauth/token"
    token_data = {
        "grant_type": "authorization_code",
        "client_id": REST_API_KEY,
        "redirect_uri": REDIRECT_URI,
        "code": code
    }
    token_res = requests.post(token_url, data=token_data).json()
    
    # 2. 날씨 정보 가져오기 (기존 로직 활용)
    # (여기서는 간단하게 결과만 출력하는 예시입니다)
    return f'''
        <h2>✅ 로그인 성공!</h2>
        <p>방금 발급된 액세스 토큰: {token_res.get('access_token')[:20]}...</p>
        <p>이제 이 토큰을 활용해 실시간 날씨 정보를 화면에 그려줄 수 있습니다!</p>
        <a href="/">홈으로 돌아가기</a>
    '''

if __name__ == '__main__':
    app.run(port=5000, debug=True)
