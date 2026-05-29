import streamlit as st
import random

# 고백 멘트 리스트
messages = [
    "너랑 있으면 하루가 너무 빨리 지나가.",
    "사실 너 계속 신경 쓰였어.",
    "우리 그냥 썸 말고 제대로 만나볼래?",
    "네 웃는 모습 보면 기분이 좋아져.",
    "내 하루에서 네가 제일 많이 생각나.",
    "너 좋아해. 진심이야.",
    "앞으로도 계속 네 옆에 있고 싶어.",
    "나랑 연애해볼래?",
    "너한테만은 자꾸 특별하게 행동하게 돼.",
    "솔직히 많이 좋아해."
]

# 페이지 설정
st.set_page_config(
    page_title="고백 멘트 추천기",
    page_icon="💌"
)

# 제목
st.title("💌 고백 멘트 추천 앱")

st.write("버튼을 누르면 랜덤 고백 멘트를 추천해드립니다!")

# 버튼
if st.button("고백 멘트 추천받기"):
    result = random.choice(messages)

    st.success(result)

    st.balloons()

# 하단 문구
st.caption("오늘의 용기를 응원합니다 🍀")
