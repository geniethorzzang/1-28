import streamlit as st # 웹사이트 화면을 만드는 도구 상자
from dotenv import load_dotenv # API 키 로드
import os # 시스템 설정
import requests # 네이버 API 요청
import folium # 지도 생성
import math # 거리 계산
import streamlit.components.v1 as components # iframe 렌더링을 위한 컴포넌트

# 1. 환경 변수 로드
load_dotenv()
NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")

# 2. 페이지 설정
st.set_page_config(
    page_title="네이버 검색 + iframe 지도",
    page_icon="🗺️",
    layout="wide"
)

st.title("🗺️ 네이버 검색 + 지도 (iframe 방식)")

# 3. API 키 유효성 검사
if not NAVER_CLIENT_ID or NAVER_CLIENT_ID == "your_naver_client_id_here":
    st.error("⚠️ .env 파일에 네이버 API 키를 설정해주세요!")
    st.stop()

# 4. Session State 초기화
if "search_results" not in st.session_state:
    st.session_state.search_results = []
if "last_query" not in st.session_state:
    st.session_state.last_query = ""
if "user_location" not in st.session_state:
    st.session_state.user_location = None

# 5. 현재 위치 가져오기 (기존 라이브러리 유지)
from streamlit_geolocation import streamlit_geolocation
st.subheader("📍 내 위치")
location = streamlit_geolocation()

if location and location.get("latitude") and location.get("longitude"):
    st.session_state.user_location = {
        "lat": location["latitude"],
        "lng": location["longitude"]
    }
    st.success(f"현재 위치: {location['latitude']:.6f}, {location['longitude']:.6f}")
else:
    st.info("위치 버튼을 클릭하여 현재 위치를 가져오세요.")

# 6. 거리 계산 함수
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

# 7. 네이버 검색 API 호출 함수
def search_places(query, user_lat=None, user_lng=None):
    if not query:
        return []

    url = "https://openapi.naver.com/v1/search/local.json"
    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
    }
    params = {"query": query, "display": 10, "sort": "random"}

    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            items = data.get("items", [])
            results = []
            for item in items:
                lng = int(item.get("mapx", 0)) / 10000000.0
                lat = int(item.get("mapy", 0)) / 10000000.0
                if lat > 0 and lng > 0:
                    distance = calculate_distance(user_lat, user_lng, lat, lng) if user_lat else None
                    results.append({
                        "title": item.get("title", "").replace("<b>", "").replace("</b>", ""),
                        "address": item.get("roadAddress", "") or item.get("address", ""),
                        "category": item.get("category", ""),
                        "lat": lat,
                        "lng": lng,
                        "distance": distance
                    })
            if user_lat and user_lng:
                results.sort(key=lambda x: x["distance"] if x["distance"] else float('inf'))
            return results
        return []
    except:
        return []

# 8. 검색 UI
st.subheader("🔍 장소 검색")
with st.form(key="search_form"):
    search_query = st.text_input("검색할 장소를 입력하세요")
    search_clicked = st.form_submit_button("검색", type="primary")

if search_clicked and search_query:
    lat = st.session_state.user_location["lat"] if st.session_state.user_location else None
    lng = st.session_state.user_location["lng"] if st.session_state.user_location else None
    results = search_places(search_query, lat, lng)
    st.session_state.search_results = results
    st.session_state.last_query = search_query

# 10. 지도 생성 및 iframe 렌더링 함수
def render_map_iframe():
    if st.session_state.user_location:
        center = [st.session_state.user_location["lat"], st.session_state.user_location["lng"]]
        zoom = 14
    elif st.session_state.search_results:
        center = [st.session_state.search_results[0]["lat"], st.session_state.search_results[0]["lng"]]
        zoom = 14
    else:
        center = [37.5665, 126.9780]
        zoom = 12

    m = folium.Map(location=center, zoom_start=zoom)

    # 내 위치 마커
    if st.session_state.user_location:
        folium.Marker(
            [st.session_state.user_location["lat"], st.session_state.user_location["lng"]],
            popup="📍 내 위치",
            icon=folium.Icon(color="blue", icon="info-sign")
        ).add_to(m)

    # 검색 결과 마커
    for idx, place in enumerate(st.session_state.search_results, 1):
        popup_text = f"<b>{idx}. {place['title']}</b><br>{place['address']}"
        folium.Marker(
            [place["lat"], place["lng"]],
            popup=folium.Popup(popup_text, max_width=200),
            icon=folium.Icon(color="red")
        ).add_to(m)

    # Folium 지도를 HTML 문자열로 변환
    map_html = m._repr_html_()
    
    # iframe으로 화면에 띄우기
    components.html(map_html, height=500)

# 11. 지도 출력
st.subheader("🗺️ 지도 보기")
render_map_iframe()

# 12. 검색 결과 목록
if st.session_state.search_results:
    st.subheader(f"📋 '{st.session_state.last_query}' 결과 리스트")
    for idx, place in enumerate(st.session_state.search_results, 1):
        col1, col2 = st.columns([7, 2])
        with col1:
            st.markdown(f"**{idx}. {place['title']}**")
            st.caption(f"{place['address']} ({place['category']})")
        with col2:
            if place['distance']:
                st.write(f"📏 {place['distance']:.2f}km")
        st.divider()

st.caption("© 2026 - Naver Search API + Folium iframe")