import streamlit as st
import pandas as pd
import os
import subprocess
import sys, time
from tkinter import Tk, filedialog

# 페이지 설정 및 기본 UI 숨기기
st.set_page_config(
    page_title="자격증 불법 대여 검색 자동화",
    page_icon="📑",
    layout="centered",
    initial_sidebar_state="collapsed"
)
st.markdown(
    """
    <style>
        /* 기본 메뉴, 헤더, 푸터 숨기기 */
        #MainMenu, header, footer {visibility: hidden;}
        /* ===== 배경색 추가 (여기부터) ===== */
        .stApp {
            background:
                radial-gradient(circle at 10% 5%, #e6fffb 0%, transparent 35%),
                radial-gradient(circle at 90% 10%, #eaf2ff 0%, transparent 30%),
                #f4f7fb;
        }
        /* 앱 컨테이너 테두리 및 그림자 제거 */
        section[data-testid="stAppViewContainer"] .css-1d391kg {
            border: none !important;
            box-shadow: none !important;
        }
        /* Expander 컨텐트 박스 스타일 */
        [data-testid="stExpanderContent"] {
            border:1px solid #ccc;
            border-radius:5px;
            padding:10px;
            margin-bottom:20px;
        }
        /* Expander 토글 화살표 숨기기 */
        [data-testid="stExpanderHeader"] button > svg {display: none;}
    </style>
    """,
    unsafe_allow_html=True
)

# 폴더 선택 대화
def select_folder():
    root = Tk(); root.withdraw()
    root.attributes("-topmost", True)  # 창을 항상 최상단으로 설정
    path = filedialog.askdirectory(title="결과 저장 폴더 선택")
    root.destroy(); return path

# 즉시 UI 갱신용 콜백
def on_select_folder():
    path = select_folder()
    if path:
        st.session_state.result_path = path
        #st.experimental_rerun()

# 메인 앱

def main():
    # 세션 초기화
    if 'result_path' not in st.session_state: st.session_state.result_path = ''
    if 'stop_flag' not in st.session_state: st.session_state.stop_flag = False

    # 제목 및 종료 버튼
    col_title, col_exit = st.columns([9,1])
    with col_title:
        st.markdown(
            "<div style='text-align:center; margin-top:-40px; margin-bottom:100px;'><h1>자격증 불법 대여 검색 자동화</h1></div>",
            unsafe_allow_html=True
        )
    with col_exit:
        if st.button("실행 종료"):
            proc = st.session_state.get('process', None)  # 안전하게 접근
            if proc:
                proc.terminate()
                st.session_state.stop_flag = True
                del st.session_state['process']
                st.success("자동화를 중단했습니다.")
                print('자동화 종료 버튼 선택')
            else:
                st.warning("실행 중인 프로세스가 없습니다.")

    # 사이트 선택 Expander
    with st.expander("검색할 웹사이트", expanded=True):
        cb1, cb2, cb3 = st.columns(3)
        with cb1:
            naverblog = st.checkbox("네이버 블로그")
        with cb2:
            navercafe = st.checkbox("네이버 카페")
        with cb3:
            daumtotal = st.checkbox("다음 통합 검색")

    # 선택된 사이트
    selected = []
    if naverblog: selected.append("네이버 블로그")
    if navercafe: selected.append("네이버 카페")
    if daumtotal: selected.append("다음 통합 검색")

    # 검색할 키워드 입력
    with st.expander("검색할 키워드", expanded=True):
        search_keyword = st.text_input(
            "아래 키워드를 입력하세요. 키워드가 다수일 경우 세미콜론(;)을 구분자로 입력하세요(ex: 자격증 대여;비상주 근무)",
        )

    # 날짜검색 기한 선택
    with st.expander("날짜검색 기한", expanded=True):

        col_left, col_right = st.columns([3, 2])
        with col_left:
            date_range = st.radio(
                "오늘날짜 기준으로, 검색할 기간을 선택하세요",
                options=["1주일", "1개월", "직접입력"],
                index=0,
                horizontal=True
            )

        with col_right:
            # 직접입력 선택 시
            if date_range == "직접입력":
                custom_days = st.text_input(
                    "검색할 기간을 일(day) 단위로 입력 (예: 10)",
                    placeholder="숫자만 입력"
                )
            else:
                custom_days = None

    # 결과 저장 폴더 선택
    r3, r4 = st.columns([4,1])
    with r3:
        st.text_input("결과 저장 폴더", value=st.session_state.result_path, disabled=True)
    with r4:
        # 버튼을 텍스트박스 중앙 줄에 맞추기 위한 여백
        st.markdown("<div style='margin-top:24px;'></div>", unsafe_allow_html=True)
        st.button("폴더 선택", on_click=on_select_folder, key="sel_folder")
    # 참고사항
    st.info(
        "※ 참고사항\n"
        "1. 선택한 웹사이트만 조회합니다.\n"
        "2. 입력한 키워드만 조회합니다.\n"
        "3. 선택한 날짜기한 내 작성게시물만 다운로드 합니다.\n"
        "4. 결과 저장 폴더에는 화면 캡쳐파일 및 결과파일이 저장됩니다."
    )

    # 실행 버튼
    st.markdown("<div style='text-align:center; margin-top:30px;'>", unsafe_allow_html=True)
    if st.button("실행"):
        #실행 중인지 먼저 체크
        if 'process' in st.session_state:
            proc = st.session_state.process
            if proc and proc.poll() is None:
                st.warning("이미 자동화가 실행 중입니다.")
                return

        #stop_flag 초기화 (중단후 재실행 대비)
        st.session_state.stop_flag = False

        # 체크박스 확인
        if not selected:
            st.error("최소 하나 이상의 웹사이트를 선택해주세요.")
            return
        # 텍스트박스 확인
        if not search_keyword:
            st.error("최소 하나 이상의 키워드를 입력해 주세요.")
            return
        # 중단 플래그 확인
        if st.session_state.stop_flag:
            st.error("자동화가 중단되었습니다.")
            return
        # 경로 확인
        if not st.session_state.result_path:
            st.error("결과 저장 폴더를 선택해주세요.")
            return
        try:

            sites_param = ";".join(selected)
            # 月,年 값을 日로 재조정
            if date_range == "직접입력":
                if not custom_days:
                    st.error("직접입력 선택 시 검색 기간(일)을 입력해주세요.")
                    return
                if not custom_days.isdigit():
                    st.error("검색 기간은 숫자만 입력할 수 있습니다.")
                    return
                date_limit = custom_days
            else:
                if "1주일" in date_range:
                    date_limit = date_range.replace("주일", "")  # "1주일" → "1" → 7 * 1 = 7
                    date_limit = int(date_limit) * 7
                else:
                    date_limit = date_range.replace("개월", "")  # "1개월" → "1" → 30 * 1 = 30
                    date_limit = int(date_limit) * 30
                date_limit = str(date_limit)

            # TODO: 자동화 로직 구현 (sites_param 사용)
            #st.success(f"{sites_param}, {search_keyword}, {date_limit}, {st.session_state.result_path}")
            BASE_DIR = os.path.dirname(os.path.abspath(__file__))
            SCRIPT = os.path.join(BASE_DIR, "NaverDaumScrapping.py")
            cmd = [sys.executable, SCRIPT, sites_param, search_keyword, date_limit, st.session_state.result_path]
            proc = subprocess.Popen(cmd)
            st.session_state.process = proc
            #subprocess.Popen(cmd)
            st.success("NaverDaumScrapping.py 스크립트를 실행했습니다.")
        except Exception as err:
            st.error(f"실행 중 오류: {err}")
    st.markdown("</div>", unsafe_allow_html=True)

if __name__ == '__main__':
    main()
