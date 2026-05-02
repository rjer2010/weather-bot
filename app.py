@app.route('/callback')
def callback():
    weather_url = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"
    base_date = datetime.now().strftime("%Y%m%d")
    params = {
        'serviceKey': os.environ.get('WEATHER_KEY'),
        'dataType': 'JSON', 'base_date': base_date, 'base_time': '0500', 
        'nx': '55', 'ny': '127', 'numOfRows': 500  # 데이터 종류가 많아지므로 넉넉히 가져옵니다.
    }
    
    try:
        res = requests.get(weather_url, params=params).json()
        items = res['response']['body']['items']['item']
        
        # 시간대별로 데이터를 묶기 위한 작업
        forecasts = {}
        for item in items:
            fcst_time = item['fcstTime']
            if fcst_time not in forecasts:
                forecasts[fcst_time] = {'time': fcst_time[:2] + "시"}
            
            # 카테고리별 데이터 저장
            category = item['category']
            value = item['fcstValue']
            
            if category == 'TMP': forecasts[fcst_time]['temp'] = float(value) # 기온(소수점)
            elif category == 'REH': forecasts[fcst_time]['humidity'] = value  # 습도
            elif category == 'POP': forecasts[fcst_time]['rain_prob'] = value # 강수확률
            elif category == 'WSD': forecasts[fcst_time]['wind'] = value      # 풍속
        
        weather_list = []
        # 정렬된 시간 순서대로 리스트 생성
        for time_key in sorted(forecasts.keys()):
            f = forecasts[time_key]
            # 필요한 모든 데이터가 있는지 확인
            if all(k in f for k in ['temp', 'humidity', 'rain_prob', 'wind']):
                status, advice, color, icon = get_weather_theme(f['temp'])
                weather_list.append({
                    'time': f['time'],
                    'temp': f"{f['temp']:.1f}", # 소수점 첫째 자리까지 표시
                    'humidity': f['humidity'],
                    'rain_prob': f['rain_prob'],
                    'wind': f['wind'],
                    'status': status,
                    'advice': advice,
                    'color': color,
                    'icon': icon
                })
        
        return render_template('index.html', weather_data=weather_list)
    except Exception as e:
        return f"상세 에러 내용: {str(e)}"
