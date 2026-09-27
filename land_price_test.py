import streamlit as st
import requests

st.title("VWorld API 연결 테스트")

# VWorld 인증키
api_key = st.text_input(
    "VWorld API Key",
    type="password"
)

if st.button("VWorld 연결 테스트"):

    if not api_key:
        st.error("API Key를 입력하세요.")
        st.stop()

    url = "https://api.vworld.kr/req/address"

    params = {
        "service": "address",
        "request": "getcoord",
        "version": "2.0",
        "crs": "epsg:4326",
        "address": "서울특별시 성동구 마장동 336-7",
        "refine": "true",
        "simple": "false",
        "format": "json",
        "type": "PARCEL",
        "key": api_key
    }

    st.write("① VWorld 서버 접속 테스트 중...")

    try:
        response = requests.get(
            url,
            params=params,
            timeout=20
        )

        st.write("HTTP 상태 코드:", response.status_code)

        st.write("응답 주소:")
        st.code(response.url)

        st.write("응답 내용:")

        try:
            data = response.json()
            st.json(data)

        except Exception:
            st.code(response.text)

    except requests.exceptions.Timeout:
        st.error("❌ 20초 동안 VWorld 서버에서 응답이 없습니다.")

    except requests.exceptions.ConnectionError as e:
        st.error("❌ VWorld 서버에 연결하지 못했습니다.")
        st.code(str(e))

    except Exception as e:
        st.error("❌ 예상하지 못한 오류")
        st.code(str(e))
