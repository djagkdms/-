import streamlit as st
import random

# 메뉴 리스트
menus = [
    "김치찌개",
    "된장찌개",
    "제육볶음",
    "비빔밥",
    "돈까스",
    "햄버거",
    "치킨",
    "피자",
    "초밥",
    "라면"
]

# 제목
st.title("🍚 식사 메뉴 추천 앱")

st.write("버튼을 누르면 오늘 먹을 메뉴를 추천해드립니다!")

# 버튼
if st.button("메뉴 추천받기"):
    menu = random.choice(menus)
    st.success(f"오늘의 추천 메뉴는 👉 {menu}")
