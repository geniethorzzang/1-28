import streamlit as st
import os
from dotenv import load_dotenv
import streamlit.components.v1 as components
import json
import requests
from streamlit_sortables import sort_items

# 1. 환경변수 로드 (클라우드 & 로컬 호환)
load_dotenv()

try:
    # 스트림릿 클라우드 설정(Secrets)에서 먼저 찾기
    kakao_api_key = st.secrets["KAKAO_MAP_API_KEY"]
    weather_api_key = st.secrets["WEATHER_API_KEY"]
    exchange_api_key = st.secrets["EXCHANGE_API_KEY"]
except:
    # 없으면 로컬 .env 파일에서 찾기
    kakao_api_key = os.getenv("KAKAO_MAP_API_KEY")
    weather_api_key = os.getenv("WEATHER_API_KEY")
    exchange_api_key = os.getenv("EXCHANGE_API_KEY")

# 페이지 설정
st.set_page_config(layout="wide", page_title="Korea Travel Guide: Classic Red")

# [CSS 스타일 적용] 사이드바 태그: 다시 빨간색 + 하얀 글씨
st.markdown(
    """
    <style>
    /* 선택된 태그(버튼) 스타일 변경: 초기 빨간색으로 복구 */
    span[data-baseweb="tag"] {
        background-color: #FF4B4B !important; /* 스트림릿 기본 레드 계열 */
        color: white !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- API 호출 함수들 ---
def get_weather(lat, lng):
    if not weather_api_key: return None
    # 보안 에러 방지를 위해 https 사용
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lng}&appid={weather_api_key}&units=metric"
    try:
        response = requests.get(url)
        return response.json() if response.status_code == 200 else None
    except: return None

def get_exchange_rate():
    if not exchange_api_key: return None
    url = f"https://v6.exchangerate-api.com/v6/{exchange_api_key}/latest/USD"
    try:
        response = requests.get(url)
        return response.json()['conversion_rates']['KRW'] if response.status_code == 200 else None
    except: return None

# 2. 데이터 준비 (전국 10개 도시, 관광지/맛집 각 5개씩)
city_data = {
    "서울 (Seoul)": {"lat": 37.5665, "lng": 126.9780, 
        "spots": [
            {"name": "경복궁 (Gyeongbokgung Palace)", "lat": 37.5796, "lng": 126.9770, "type": "역사/문화"},
            {"name": "N서울타워 (N Seoul Tower)", "lat": 37.5511, "lng": 126.9882, "type": "야경/뷰"},
            {"name": "북촌 한옥마을 (Bukchon Hanok Village)", "lat": 37.5826, "lng": 126.9830, "type": "역사/문화"},
            {"name": "더현대 서울 (The Hyundai Seoul)", "lat": 37.5259, "lng": 126.9284, "type": "쇼핑/핫플"},
            {"name": "반포 한강공원 (Banpo Hangang Park)", "lat": 37.5098, "lng": 126.9947, "type": "힐링/자연"}
        ],
        "food": [
            {"name": "명동교자 (Myeongdong Kyoja)", "lat": 37.5625, "lng": 126.9856, "rating": 4.2, "type": "국수/면"},
            {"name": "우래옥 (Woo Lae Oak)", "lat": 37.5683, "lng": 126.9987, "rating": 4.5, "type": "전통한식"},
            {"name": "광장시장 (Gwangjang Market)", "lat": 37.5701, "lng": 126.9997, "rating": 4.3, "type": "길거리음식"},
            {"name": "어니언 안국 (Onion Anguk)", "lat": 37.5778, "lng": 126.9866, "rating": 4.0, "type": "카페/디저트"},
            {"name": "금돼지식당 (Gold Pig BBQ)", "lat": 37.5555, "lng": 127.0108, "rating": 4.6, "type": "바베큐/고기"}
        ]
    },
    "부산 (Busan)": {"lat": 35.1796, "lng": 129.0756, 
        "spots": [
            {"name": "해운대 해수욕장 (Haeundae Beach)", "lat": 35.1587, "lng": 129.1603, "type": "힐링/자연"},
            {"name": "감천문화마을 (Gamcheon Culture Village)", "lat": 35.0975, "lng": 129.0106, "type": "체험/액티비티"},
            {"name": "광안리 해수욕장 (Gwangalli Beach)", "lat": 35.1532, "lng": 129.1186, "type": "야경/뷰"},
            {"name": "해동용궁사 (Haedong Yonggungsa)", "lat": 35.1883, "lng": 129.2233, "type": "역사/문화"},
            {"name": "스카이캡슐 (Sky Capsule)", "lat": 35.1605, "lng": 129.1666, "type": "체험/액티비티"}
        ],
        "food": [
            {"name": "본전돼지국밥 (Bonjeon Pork Soup)", "lat": 35.1152, "lng": 129.0422, "rating": 4.1, "type": "전통한식"},
            {"name": "해운대암소갈비 (Haeundae Ribs)", "lat": 35.1633, "lng": 129.1666, "rating": 4.3, "type": "바베큐/고기"},
            {"name": "초량밀면 (Choryang Milmyeon)", "lat": 35.1187, "lng": 129.0396, "rating": 4.0, "type": "국수/면"},
            {"name": "옵스 해운대점 (OPS Bakery)", "lat": 35.1623, "lng": 129.1601, "rating": 4.2, "type": "카페/디저트"},
            {"name": "이재모피자 (Lee Jaemo Pizza)", "lat": 35.1021, "lng": 129.0306, "rating": 4.4, "type": "쇼핑/핫플"}
        ]
    },
    "제주 (Jeju)": {"lat": 33.3616, "lng": 126.5116, 
        "spots": [
            {"name": "성산일출봉 (Seongsan Ilchulbong)", "lat": 33.4580, "lng": 126.9425, "type": "힐링/자연"},
            {"name": "협재 해수욕장 (Hyeopjae Beach)", "lat": 33.3938, "lng": 126.2396, "type": "힐링/자연"},
            {"name": "아르떼뮤지엄 (Arte Museum)", "lat": 33.3986, "lng": 126.3468, "type": "체험/액티비티"},
            {"name": "오설록 티뮤지엄 (Osulloc Tea Museum)", "lat": 33.3060, "lng": 126.2895, "type": "쇼핑/핫플"},
            {"name": "사려니숲길 (Saryeoni Forest)", "lat": 33.4077, "lng": 126.6425, "type": "힐링/자연"}
        ],
        "food": [
            {"name": "자매국수 (Jamae Guksu)", "lat": 33.5008, "lng": 126.5284, "rating": 4.0, "type": "국수/면"},
            {"name": "돈사돈 (Donsadon BBQ)", "lat": 33.4795, "lng": 126.4745, "rating": 4.4, "type": "바베큐/고기"},
            {"name": "우진해장국 (Ujin Haejangguk)", "lat": 33.5115, "lng": 126.5201, "rating": 4.5, "type": "전통한식"},
            {"name": "랜디스도넛 (Randy's Donuts)", "lat": 33.4627, "lng": 126.3095, "rating": 4.2, "type": "카페/디저트"},
            {"name": "오는정김밥 (Oneunjeong Gimbap)", "lat": 33.2498, "lng": 126.5638, "rating": 4.3, "type": "길거리음식"}
        ]
    },
    "경주 (Gyeongju)": {"lat": 35.8562, "lng": 129.2247, 
        "spots": [
            {"name": "불국사 (Bulguksa Temple)", "lat": 35.7905, "lng": 129.3321, "type": "역사/문화"},
            {"name": "동궁과 월지 (Donggung Palace)", "lat": 35.8341, "lng": 129.2266, "type": "야경/뷰"},
            {"name": "황리단길 (Hwangnidan-gil)", "lat": 35.8385, "lng": 129.2096, "type": "쇼핑/핫플"},
            {"name": "첨성대 (Cheomseongdae)", "lat": 35.8347, "lng": 129.2190, "type": "역사/문화"},
            {"name": "대릉원 (Daereungwon Tomb Complex)", "lat": 35.8391, "lng": 129.2120, "type": "힐링/자연"}
        ],
        "food": [
            {"name": "황남빵 (Hwangnam Bread)", "lat": 35.8385, "lng": 129.2117, "rating": 4.2, "type": "카페/디저트"},
            {"name": "함양집 (Hamyangjip)", "lat": 35.8540, "lng": 129.2220, "rating": 4.1, "type": "전통한식"},
            {"name": "료코 (Ryoko)", "lat": 35.8378, "lng": 129.2099, "rating": 4.3, "type": "쇼핑/핫플"},
            {"name": "도솔마을 (Dosol Maeul)", "lat": 35.8380, "lng": 129.2105, "rating": 4.0, "type": "전통한식"},
            {"name": "숙영식당 (Sukyoung Sikdang)", "lat": 35.8362, "lng": 129.2085, "rating": 4.2, "type": "전통한식"}
        ]
    },
     "전주 (Jeonju)": {"lat": 35.8242, "lng": 127.1480, 
        "spots": [
            {"name": "전주 한옥마을 (Hanok Village)", "lat": 35.8147, "lng": 127.1526, "type": "역사/문화"},
            {"name": "전동성당 (Jeondong Cathedral)", "lat": 35.8133, "lng": 127.1492, "type": "역사/문화"},
            {"name": "경기전 (Gyeonggijeon Shrine)", "lat": 35.8150, "lng": 127.1490, "type": "역사/문화"},
            {"name": "자만벽화마을 (Jaman Mural Village)", "lat": 35.8155, "lng": 127.1565, "type": "체험/액티비티"},
            {"name": "남부시장 (Nambu Market)", "lat": 35.8118, "lng": 127.1475, "type": "쇼핑/핫플"}
        ], 
        "food": [
            {"name": "한국집 (Hankook Jip)", "lat": 35.8152, "lng": 127.1495, "rating": 4.0, "type": "전통한식"},
            {"name": "PNB 풍년제과 (PNB Bakery)", "lat": 35.8155, "lng": 127.1497, "rating": 4.2, "type": "카페/디저트"},
            {"name": "조점례 남문피순대 (Sundae)", "lat": 35.8130, "lng": 127.1477, "rating": 4.3, "type": "전통한식"},
            {"name": "가족회관 (Gajok Hoegwan)", "lat": 35.8170, "lng": 127.1445, "rating": 4.1, "type": "전통한식"},
            {"name": "베테랑 칼국수 (Veteran Kalguksu)", "lat": 35.8135, "lng": 127.1505, "rating": 4.4, "type": "국수/면"}
        ]
    },
    "수원 (Suwon)": {"lat": 37.2636, "lng": 127.0286, 
        "spots": [
            {"name": "수원화성 (Suwon Hwaseong)", "lat": 37.2851, "lng": 127.0197, "type": "역사/문화"},
            {"name": "방화수류정 (Banghwasuryujeong)", "lat": 37.2889, "lng": 127.0199, "type": "힐링/자연"},
            {"name": "스타필드 수원 (Starfield Suwon)", "lat": 37.2922, "lng": 126.9934, "type": "쇼핑/핫플"},
            {"name": "화성행궁 (Hwaseong Haenggung)", "lat": 37.2825, "lng": 127.0163, "type": "역사/문화"},
            {"name": "플라잉수원 (Flying Suwon)", "lat": 37.2905, "lng": 127.0220, "type": "체험/액티비티"}
        ], 
        "food": [
            {"name": "가보정 (Gabojeong BBQ)", "lat": 37.2764, "lng": 127.0298, "rating": 4.6, "type": "바베큐/고기"},
            {"name": "보영만두 (Boyoung Mandu)", "lat": 37.2862, "lng": 127.0152, "rating": 4.1, "type": "국수/면"},
            {"name": "정지영커피로스터즈", "lat": 37.2844, "lng": 127.0163, "rating": 4.3, "type": "카페/디저트"},
            {"name": "연포갈비 (Yeonpo Galbi)", "lat": 37.2885, "lng": 127.0180, "rating": 4.2, "type": "바베큐/고기"},
            {"name": "진미통닭 (Jinmi Chicken)", "lat": 37.2755, "lng": 127.0175, "rating": 4.0, "type": "바베큐/고기"}
        ]
    },
    "강릉 (Gangneung)": {"lat": 37.7519, "lng": 128.8760, 
        "spots": [
            {"name": "경포대 (Gyeongpodae Pavilion)", "lat": 37.7951, "lng": 128.9080, "type": "힐링/자연"},
            {"name": "안목해변 카페거리 (Coffee Street)", "lat": 37.7719, "lng": 128.9482, "type": "쇼핑/핫플"},
            {"name": "오죽헌 (Ojukheon)", "lat": 37.7792, "lng": 128.8794, "type": "역사/문화"},
            {"name": "정동진역 (Jeongdongjin Station)", "lat": 37.6914, "lng": 129.0326, "type": "힐링/자연"},
            {"name": "아르떼뮤지엄 강릉 (Arte Museum)", "lat": 37.7905, "lng": 128.8970, "type": "체험/액티비티"}
        ], 
        "food": [
            {"name": "동화가든 (Donghwa Garden)", "lat": 37.7915, "lng": 128.9146, "rating": 4.3, "type": "전통한식"},
            {"name": "툇마루 커피 (Toenmaru Coffee)", "lat": 37.7923, "lng": 128.9161, "rating": 4.5, "type": "카페/디저트"},
            {"name": "강릉중앙시장 (Central Market)", "lat": 37.7538, "lng": 128.8986, "rating": 4.2, "type": "길거리음식"},
            {"name": "엄지네 포장마차 (Eomji's Cockle)", "lat": 37.7655, "lng": 128.9015, "rating": 4.4, "type": "전통한식"},
            {"name": "강릉당 커피콩빵", "lat": 37.7540, "lng": 128.8975, "rating": 4.0, "type": "카페/디저트"}
        ]
    },
    "속초 (Sokcho)": {"lat": 38.2070, "lng": 128.5918, 
        "spots": [
            {"name": "속초아이 (Sokcho Eye)", "lat": 38.1906, "lng": 128.6033, "type": "체험/액티비티"},
            {"name": "설악산 케이블카 (Seoraksan Cable Car)", "lat": 38.1728, "lng": 128.4877, "type": "힐링/자연"},
            {"name": "영금정 (Yeonggeumjeong)", "lat": 38.2118, "lng": 128.6015, "type": "야경/뷰"},
            {"name": "속초해수욕장 (Sokcho Beach)", "lat": 38.1903, "lng": 128.6030, "type": "힐링/자연"},
            {"name": "아바이마을 (Abai Village)", "lat": 38.2025, "lng": 128.5920, "type": "역사/문화"}
        ], 
        "food": [
            {"name": "만석닭강정 (Manseok Chicken)", "lat": 38.2036, "lng": 128.5866, "rating": 4.1, "type": "길거리음식"},
            {"name": "봉포머구리집 (Seafood)", "lat": 38.2215, "lng": 128.5962, "rating": 4.2, "type": "전통한식"},
            {"name": "88생선구이 (88 Grilled Fish)", "lat": 38.2045, "lng": 128.5905, "rating": 4.0, "type": "전통한식"},
            {"name": "단천식당 (Abai Sundae)", "lat": 38.2028, "lng": 128.5925, "rating": 4.3, "type": "전통한식"},
            {"name": "칠성조선소 (Chilsung Boatyard Cafe)", "lat": 38.1970, "lng": 128.5860, "rating": 4.5, "type": "카페/디저트"}
        ]
    },
    "대구 (Daegu)": {"lat": 35.8714, "lng": 128.6014, 
        "spots": [
            {"name": "김광석 거리 (Kim Kwang-seok St)", "lat": 35.8606, "lng": 128.6079, "type": "체험/액티비티"},
            {"name": "수성못 (Suseongmot Lake)", "lat": 35.8285, "lng": 128.6166, "type": "힐링/자연"},
            {"name": "이월드 & 83타워", "lat": 35.8532, "lng": 128.5636, "type": "야경/뷰"},
            {"name": "서문시장 (Seomun Market)", "lat": 35.8690, "lng": 128.5815, "type": "쇼핑/핫플"},
            {"name": "앞산 전망대 (Apsan Observatory)", "lat": 35.8275, "lng": 128.5775, "type": "야경/뷰"}
        ], 
        "food": [
            {"name": "미성당 납작만두 (Flat Dumplings)", "lat": 35.8633, "lng": 128.5843, "rating": 3.9, "type": "길거리음식"},
            {"name": "걸리버 막창 (Gulliver Makchang)", "lat": 35.8856, "lng": 128.5830, "rating": 4.4, "type": "바베큐/고기"},
            {"name": "삼송빵집 (Samsong Bakery)", "lat": 35.8698, "lng": 128.5954, "rating": 4.1, "type": "카페/디저트"},
            {"name": "중앙떡볶이 (Jungang Tteokbokki)", "lat": 35.8705, "lng": 128.5950, "rating": 4.2, "type": "길거리음식"},
            {"name": "안지랑 곱창골목 (Anjirang Alley)", "lat": 35.8365, "lng": 128.5750, "rating": 4.3, "type": "바베큐/고기"}
        ]
    },
    "여수 (Yeosu)": {"lat": 34.7604, "lng": 127.6622, 
        "spots": [
            {"name": "여수 해상케이블카 (Cable Car)", "lat": 34.7439, "lng": 127.7456, "type": "체험/액티비티"},
            {"name": "오동도 (Odongdo Island)", "lat": 34.7460, "lng": 127.7667, "type": "힐링/자연"},
            {"name": "돌산공원 (Dolsan Park)", "lat": 34.7303, "lng": 127.7461, "type": "야경/뷰"},
            {"name": "이순신 광장 (Yi Sun-sin Square)", "lat": 34.7395, "lng": 127.7355, "type": "역사/문화"},
            {"name": "아쿠아플라넷 여수 (Aqua Planet)", "lat": 34.7450, "lng": 127.7405, "type": "체험/액티비티"}
        ], 
        "food": [
            {"name": "여수낭만포차 (Romantic Pocha)", "lat": 34.7391, "lng": 127.7389, "rating": 3.8, "type": "길거리음식"},
            {"name": "돌산게장명가 (Crab Marinated)", "lat": 34.7225, "lng": 127.7661, "rating": 4.3, "type": "전통한식"},
            {"name": "여수당 (Yeosudang Baguette)", "lat": 34.7420, "lng": 127.7335, "rating": 4.0, "type": "길거리음식"},
            {"name": "백천선어 (Sashimi)", "lat": 34.7550, "lng": 127.7250, "rating": 4.5, "type": "전통한식"},
            {"name": "로타리식당 (Rotary Sikdang)", "lat": 34.7415, "lng": 127.7315, "rating": 4.2, "type": "전통한식"}
        ]
    }
}

st.title("🌏 Welcome to Korea! Travel Guide")
st.caption("Designed for international travelers - Find the best spots & routes.")

# 사이드바
with st.sidebar:
    st.header("1. Travel Information")
    
    # 환율
    rate = get_exchange_rate()
    if rate:
        st.success(f"💰 **Exchange Rate:** 1 USD ≈ {rate:,.0f} KRW")
    else:
        st.warning("💰 Exchange rate unavailable")

    st.divider()

    st.subheader("Select City")
    selected_city_name = st.selectbox("Choose a city:", list(city_data.keys()))
    city_info = city_data[selected_city_name]
    
    # 날씨
    weather_data = get_weather(city_info['lat'], city_info['lng'])
    if weather_data:
        temp = weather_data['main']['temp']
        desc = weather_data['weather'][0]['description']
        icon = weather_data['weather'][0]['icon']
        icon_url = f"https://openweathermap.org/img/wn/{icon}@2x.png"
        col_w1, col_w2 = st.columns([1, 2])
        with col_w1: st.image(icon_url, width=50)
        with col_w2: 
            st.write(f"**{temp}°C**")
            st.caption(f"{desc.capitalize()}")
    else:
        st.info("☁️ Weather info unavailable")

    st.divider()
    
    # 관광지
    st.header("2. Recommend Spots")
    spot_options = {f"{s['name']} [{s['type']}]": s for s in city_info['spots']}
    all_spots = st.checkbox("Select All Spots", value=True)
    selected_spots = st.multiselect("Tourist Attractions:", options=list(spot_options.keys()), default=list(spot_options.keys()) if all_spots else [])
    
    st.divider()

    # 맛집
    st.header("3. Recommend Restaurants")
    food_options = {f"{f['name']} [{f['type']}]": f for f in city_info['food']}
    all_foods = st.checkbox("Select All Restaurants", value=True)
    selected_foods = st.multiselect("Restaurants (⭐3.5+):", options=list(food_options.keys()), default=list(food_options.keys()) if all_foods else [])
    
    st.divider()

    # 순서 정하기
    st.header("4. Plan Your Route (Drag & Drop)")
    combined_items = selected_spots + selected_foods
    sorted_items = sort_items(combined_items, direction='vertical') if combined_items else []

# 지도 데이터 정리
markers = []
path_coords = []
for key in sorted_items:
    if key in spot_options:
        d = spot_options[key]
        markers.append({"name": d['name'], "lat": d['lat'], "lng": d['lng'], "type": "Spot"})
        path_coords.append({"lat": d['lat'], "lng": d['lng']})
    elif key in food_options:
        d = food_options[key]
        markers.append({"name": d['name'], "lat": d['lat'], "lng": d['lng'], "type": "Food"})
        path_coords.append({"lat": d['lat'], "lng": d['lng']})

markers_json = json.dumps(markers)
center_lat, center_lng = city_info['lat'], city_info['lng']

# 카카오맵 HTML/JS 코드 (CSP 적용으로 HTTP 차단 방지)
html_code = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta http-equiv="Content-Security-Policy" content="upgrade-insecure-requests">
    <title>Kakao Map</title>
    <script type="text/javascript" src="https://dapi.kakao.com/v2/maps/sdk.js?appkey={kakao_api_key}"></script>
    <style>
        html, body {{ margin: 0; padding: 0; height: 100%; }}
        #map {{ width: 100%; height: 500px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
    </style>
</head>
<body>
    <div id="map"></div>
    <script>
        var container = document.getElementById('map');
        var options = {{ center: new kakao.maps.LatLng({center_lat}, {center_lng}), level: 7 }};
        var map = new kakao.maps.Map(container, options);
        var markers = {markers_json};
        var linePath = [];

        markers.forEach(function(m) {{
            var position = new kakao.maps.LatLng(m.lat, m.lng);
            linePath.push(position);
            
            // 이미지 교체: 튼튼한 GitHub 호스팅 이미지
            var imageSrc = m.type === 'Food' ? 
                "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-blue.png" : 
                "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-gold.png";
            
            var markerImage = new kakao.maps.MarkerImage(imageSrc, new kakao.maps.Size(25, 41)); 
            var marker = new kakao.maps.Marker({{ map: map, position: position, title: m.name, image: markerImage }});
            var infowindow = new kakao.maps.InfoWindow({{ content: '<div style="padding:5px;font-size:12px;">' + m.name + '</div>' }});
            kakao.maps.event.addListener(marker, 'mouseover', function() {{ infowindow.open(map, marker); }});
            kakao.maps.event.addListener(marker, 'mouseout', function() {{ infowindow.close(); }});
        }});

        if (linePath.length > 1) {{
            new kakao.maps.Polyline({{
                path: linePath, strokeWeight: 5, strokeColor: '#FF0000', strokeOpacity: 0.8, strokeStyle: 'solid'
            }}).setMap(map);
            var bounds = new kakao.maps.LatLngBounds();
            linePath.forEach(function(coords) {{ bounds.extend(coords); }});
            map.setBounds(bounds);
        }}
    </script>
</body>
</html>
"""

components.html(html_code, height=520)

st.divider()
if sorted_items:
    st.subheader(f"📋 Your Itinerary in {selected_city_name}")
    for i, item in enumerate(sorted_items, 1):
        st.write(f"**{i}.** {item}")
else:
    st.write("👈 Select spots and restaurants to create your route.")