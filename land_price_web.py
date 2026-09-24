import streamlit as st

import pandas as pd
import requests
import time

API_KEY = "52E81169-9BCC-4214-9C27-3C38093F4356"


# =========================================================
# 기본 설정
# =========================================================

st.set_page_config(
    page_title="개별공시지가 조회 시스템",
    page_icon="🏠",
    layout="centered"
)

st.markdown("""
<style>

/* 화면 여백 */
.block-container {
    padding-top: 2.5rem !important;
    padding-bottom: 1rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
}

/* 메인 제목 */
h1 {
    display: block !important;
    visibility: visible !important;
    height: auto !important;
    min-height: 38px !important;
    overflow: visible !important;

    font-size: 24px !important;
    line-height: 1.5 !important;

    margin-top: 0 !important;
    margin-bottom: 0.5rem !important;
    padding-top: 0.6rem !important;
    padding-bottom: 0.2rem !important;
}

/* 섹션 제목 */
h2 {
    font-size: 20px !important;
    line-height: 1.35 !important;
    margin-top: 0.4rem !important;
    margin-bottom: 0.4rem !important;
}

h3 {
    font-size: 17px !important;
    line-height: 1.35 !important;
    margin-top: 0.3rem !important;
    margin-bottom: 0.3rem !important;
}

/* 일반 글자 */
p {
    font-size: 14px !important;
    line-height: 2 !important;
    margin-top: 0.2rem !important;
    margin-bottom: 0.3rem !important;
}

/* 입력창 */
input {
    font-size: 14px !important;
}

/* 버튼 */
button {
    font-size: 14px !important;
}

/* 안내문 */
.stCaption {
    font-size: 12px !important;
}

/* 전체 세로 간격 축소 */
div[data-testid="stVerticalBlock"] {
    gap: 0.4rem !important;
}

/* 가로 컬럼 간격 축소 */
div[data-testid="stHorizontalBlock"] {
    gap: 0.5rem !important;
}

/* 입력창 주변 여백 축소 */
#div[data-testid="stTextInput"] {
#    margin-bottom: 0.2rem !important;
#}

/* 파일 업로더 주변 여백 축소 */
div[data-testid="stFileUploader"] {
    margin-bottom: 0.2rem !important;
}

/* 버튼 주변 여백 축소 */
#div[data-testid="stButton"] {
#    margin-top: 0.1rem !important;
#    margin-bottom: 0.1rem !important;
#}

/* 구분선 여백 축소 */
hr {
    margin-top: 0.5rem !important;
    margin-bottom: 0.5rem !important;
}

/* Expander 내부 여백 축소 */


#div[data-testid="stExpander"] details {
#    padding-top: 0.2rem !important;
#    padding-bottom: 0.2rem !important;
#}


</style>
""", unsafe_allow_html=True)

# =========================================================
# 주소 → PNU 조회
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

        response = requests.get(
            url,
            params=params,
            timeout=10
        )

        data = response.json()

        if data["response"]["status"] != "OK":
            return ""

        structure = data["response"]["refined"]["structure"]

        return structure["level4LC"]

    except Exception:

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

        response = requests.get(
            url,
            params=params,
            timeout=10
        )

        data = response.json()

        fields = data.get(
            "indvdLandPrices", {}
        ).get(
            "field", []
        )

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
# 제목
# =========================================================

st.title("🏠 개별공시지가 조회 시스템(API 활용)")

#st.caption(
#    "API를 이용한 개별공시지가 조회"
#)


# =========================================================
# 기본 설정
# =========================================================

st.subheader("⚙️ 기본 설정")

with st.form("stand_form"):
    col1, col2 = st.columns([1, 2], vertical_alignment="bottom")
    
    with col1:
        year = st.text_input(
        "**기준연도**",
        value="2026"
        )



# =========================================================
# ① 개별 주소 조회 #http://gov.wrks.ai/ko?redirect_url=%2Fchat&login=1
# =========================================================

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
            st.warning(
            "조회할 주소를 입력하세요."
            )
        else:
            with st.spinner("주소를 조회하고 있습니다..."):

                pnu = get_pnu(
                    address.strip(),
                    API_KEY
                )

                if pnu == "":

                    st.error(
                        "주소를 찾을 수 없습니다."
                    )

                else:

                    result = get_land_price(
                        pnu,
                        API_KEY,
                        year.strip()
                    )

                    if result is None:

                        st.warning(
                            f"{year}년 개별공시지가 데이터를 찾을 수 없습니다."
                        )

                    else:

                        st.success(
                            "✓ 개별공시지가 데이터 정상 확인"
                        )

                        st.markdown("### 조회 결과")

                        col1, col2, col3, col4, col5 = st.columns([0.2,1.5,3.3,2,5])

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


# =========================================================
# ② 주소목록 일괄 조회
# =========================================================

st.divider()

st.subheader("② 주소목록 일괄 조회")

with st.container(border=True):
    uploaded_file = st.file_uploader(
        "주소목록 엑셀 파일을 선택하세요. (※ 엑셀 파일에는 반드시 '주소'라는 이름의 열이 있어야 합니다)",
        type=["xlsx"]
    )


if uploaded_file is not None:

    try:

        df = pd.read_excel(
            uploaded_file
        )

        st.write(
            f"총 {len(df):,}건의 주소를 확인했습니다."
        )

        if "주소" not in df.columns:

            st.error(
                "엑셀에 '주소' 열이 없습니다."
            )

        else:

            st.dataframe(
                df.head(10),
                use_container_width=True
            )

            if st.button(
                "🚀 주소목록 일괄 조회 시작",
                type="primary"
            ):

                total = len(df)

                df["PNU"] = ""
                df["법정동"] = ""
                df["지번"] = ""
                df["기준연도"] = ""
                df["개별공시지가"] = None
                df["공시일"] = ""
                df["조회결과"] = ""

                success = 0
                fail = 0

                progress_bar = st.progress(
                    0
                )

                status_text = st.empty()

                count_text = st.empty()

                for index, row in df.iterrows():

                    address = str(
                        row["주소"]
                    ).strip()

                    current = index + 1

                    status_text.write(
                        f"현재 조회: {address}"
                    )

                    if address == "" or address == "nan":

                        df.loc[
                            index,
                            "조회결과"
                        ] = "주소 없음"

                        fail += 1

                    else:

                        pnu = get_pnu(
                            address,
                            API_KEY
                        )

                        if pnu == "":

                            df.loc[
                                index,
                                "조회결과"
                            ] = "PNU 조회 실패"

                            fail += 1

                        else:

                            df.loc[
                                index,
                                "PNU"
                            ] = pnu

                            result = get_land_price(
                                pnu,
                                API_KEY,
                                year.strip()
                            )

                            if result is None:

                                df.loc[
                                    index,
                                    "조회결과"
                                ] = "공시지가 조회 실패"

                                fail += 1

                            else:

                                df.loc[
                                    index,
                                    "법정동"
                                ] = result["legal_dong"]

                                df.loc[
                                    index,
                                    "지번"
                                ] = result["parcel"]

                                df.loc[
                                    index,
                                    "기준연도"
                                ] = result["year"]

                                df.loc[
                                    index,
                                    "개별공시지가"
                                ] = result["price"]

                                df.loc[
                                    index,
                                    "공시일"
                                ] = result["date"]

                                if result["price"] != "":

                                    df.loc[
                                        index,
                                        "조회결과"
                                    ] = "정상 확인"

                                    success += 1

                                else:

                                    df.loc[
                                        index,
                                        "조회결과"
                                    ] = "공시지가 없음"

                                    fail += 1

                    progress_bar.progress(
                        current / total
                    )

                    count_text.write(
                        f"진행: {current:,} / {total:,}    "
                        f"성공: {success:,}건    "
                        f"실패: {fail:,}건"
                    )

                    time.sleep(
                        0.3
                    )

                status_text.success(
                    "✓ 조회가 완료되었습니다."
                )

                st.write(
                    f"정상 확인: **{success:,}건**"
                )

                st.write(
                    f"확인 필요: **{fail:,}건**"
                )

                # -----------------------------------------
                # 엑셀 다운로드
                # -----------------------------------------

                output = df.to_excel(
                    "temp.xlsx",
                    index=False
                )

                import io

                output = io.BytesIO()

                with pd.ExcelWriter(
                    output,
                    engine="openpyxl"
                ) as writer:

                    df.to_excel(
                        writer,
                        index=False,
                        sheet_name="개별공시지가"
                    )

                output.seek(0)

                st.download_button(
                    label="📥 조회 결과 엑셀 다운로드",
                    data=output,
                    file_name="개별공시지가_조회결과.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

    except Exception as e:

        st.error(
            f"파일을 읽는 중 오류가 발생했습니다.\n\n{e}"
        )