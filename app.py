from flask import Flask, render_template, request, redirect
import requests
import json

app = Flask(__name__)

# [꼭 확인!] 본인의 REST API 키를 여기에 입력하세요
REST_API_KEY = '168466c7fc817cdaa624d8d743054b4d' 
REDIRECT_URI = 'http://localhost:5000/callback'

@app.route('/')
def index():
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
        
        if 'access_token' not in token_res:
            error_msg = token_res.get('error_description', '알 수 없는 오류')
            return f"<h2>❌ 토큰 발급 실패</h2><p>이유: {error_msg}</p><a href='/'>홈으로 돌아가기</a>"

        access_token = token_res.get('access_token')
        return f'''
            <h2>✅ 로그인 성공!</h2>
            <p>방금 발급된 액세스 토큰: {access_token[:20]}...</p>
            <p>이제 이 토큰을 활용해 실시간 날씨 정보를 화면에 그려줄 수 있습니다!</p>
            <a href="/">홈으로 돌아가기</a>
        '''
    except Exception as e:
        return f"<h2>❌ 시스템 에러</h2><p>{str(e)}</p><a href='/'>홈으로 돌아가기</a>"

if __name__ == '__main__':
    app.run(port=5000, debug=True)
