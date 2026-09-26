import streamlit as st
import pandas as pd
import requests
import time
import io

API_KEY = "52E81169-9BCC-4214-9C27-3C38093F4356"

# =========================================================
# 기본 설정
# =========================================================

st.set_page_config(
    page_title="개별공시지가 조회 시스템",
    page_icon="🏠",
    layout="centered"
)

# =========================================================
# 주소 → PNU 조회 (디버깅 로그 추가)
# =========================================================

def get_pnu(address, api_key):
    url = "https://api.vworld.kr/req/address"
    params = {
        "service": "address",
        "request": "getcoord",
        "version": "2.0",
        "crs": "epsg:4326",
        "address": address,
        "refine": "true",
        "simple": "false",
        "format": "json",
        "type": "PARCEL",
        "key": api_key
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        if data.get("response", {}).get("status") != "OK":
            return ""

        structure = data["response"]["refined"]["structure"]
        return structure.get("level4LC", "")

    except Exception as e:
        return ""


# =========================================================
# PNU → 개별공시지가 조회
# =========================================================

def get_land_price(pnu, api_key, year):
    url = "https://api.vworld.kr/ned/data/getIndvdLandPriceAttr"
    params = {
        "key": api_key,
        "pnu": pnu,
        "stdrYear": year,
        "format": "json",
        "numOfRows": "10",
        "pageNo": "1"
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        fields = data.get("indvdLandPrices", {}).get("field", [])

        if len(fields) == 0:
            return None

        field = fields[0]
        return {
            "price": field.get("pblntfPclnd", ""),
            "date": field.get("pblntfDe", ""),
            "legal_dong": field.get("ldCodeNm", ""),
            "parcel": field.get("mnnmSlno", ""),
            "year": field.get("stdrYear", year)
        }

    except Exception:
        return None


# =========================================================
# 화면 레이아웃 구성
# =========================================================

st.title("🏠 개별공시지가 조회 시스템(API 활용)")

st.subheader("⚙️ 기본 설정")

with st.form("stand_form"):
    col1, col2 = st.columns([1, 2], vertical_alignment="bottom")
    with col1:
        year = st.text_input("**기준연도**", value="2026")

st.subheader("① 개별 주소 조회")

with st.container(border=True):
    with st.form("single_address_form"):
        col_addr, col_btn = st.columns([5, 1.5], vertical_alignment="bottom")

        with col_addr:
            address = st.text_input(
                "※ 정확한 조회를 위해 시·군·구를 포함한 전체 지번주소를 입력하세요",
                placeholder="예: 서울특별시 성동구 행당동 7"
            )

        with col_btn:
            search_clicked = st.form_submit_button(
                "개별공시지가조회",
                type="primary",
                use_container_width=True
            )

    if search_clicked:
        if address.strip() == "":
            st.warning("조회할 주소를 입력하세요.")
        else:
            with st.spinner("주소를 조회하고 있습니다..."):
                pnu = get_pnu(address.strip(), API_KEY)

                if pnu == "":
                    st.error("주소를 찾을 수 없거나 API 인증키 도메인 설정을 확인해주세요.")
                else:
                    result = get_land_price(pnu, API_KEY, year.strip())

                    if result is None:
                        st.warning(f"{year}년 개별공시지가 데이터를 찾을 수 없습니다.")
                    else:
                        st.success("✓ 개별공시지가 데이터 정상 확인")

                        st.markdown("### 조회 결과")
                        col1, col2, col3, col4, col5 = st.columns([0.2, 1.5, 3.3, 2, 5])

                        with col2:
                            st.write("**입력주소**")
                            st.write("**기준연도**")
                            st.write("**공시일**")
                        with col3:
                            st.write(address)
                            st.write(result["year"])
                            st.write(result["date"])
                        with col4:
                            st.write("**확인주소**")
                            st.write("**PNU**")
                            st.write("**개별공시지가**")
                        with col5:
                            st.write(result["legal_dong"] + " " + result["parcel"])
                            st.write(pnu)                  
                            if result["price"] != "":
                                price_text = f'{int(result["price"]):,}원/㎡'
                            else:
                                price_text = "확인되지 않음"                    
                            st.write(price_text)