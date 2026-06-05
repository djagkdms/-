import streamlit as st
from google import genai

# 페이지 설정
st.set_page_config(
    page_title="고백멘트 추천 챗봇",
    page_icon="💌",
)

st.title("💌 고백멘트 추천 챗봇")
st.caption("상황을 입력하면 어울리는 고백 멘트를 추천해드립니다.")

# API 키 불러오기
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.error("GEMINI_API_KEY가 Secrets에 설정되어 있지 않습니다.")
    st.stop()

# Gemini 클라이언트 생성
try:
    client = genai.Client(api_key=api_key)
except Exception as e:
    st.error(f"Gemini 초기화 오류: {e}")
    st.stop()

# 채팅 기록 유지
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "안녕하세요! 💌\n\n"
                "고백하려는 상황을 알려주세요.\n"
                "예시:\n"
                "- 같은 과 친구에게 고백\n"
                "- 직장 동료에게 고백\n"
                "- 오래 알고 지낸 친구에게 고백\n"
                "- 귀엽게 / 진지하게 / 유머 있게"
            ),
        }
    ]

# 이전 대화 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 사용자 입력
user_input = st.chat_input("고백 상황을 입력하세요")

if user_input:
    # 사용자 메시지 저장
    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )

    with st.chat_message("user"):
        st.markdown(user_input)

    # 대화 이력 구성
    conversation = ""

    for msg in st.session_state.messages:
        role = "사용자" if msg["role"] == "user" else "챗봇"
        conversation += f"{role}: {msg['content']}\n"

    prompt = f"""
당신은 연애 상담 및 고백 멘트 추천 전문가입니다.

규칙:
1. 상황에 맞는 고백 멘트 5개를 추천한다.
2. 분위기(진지함, 달달함, 귀여움)를 적절히 섞는다.
3. 멘트는 실제로 사용할 수 있게 자연스럽게 작성한다.
4. 마지막에 간단한 전달 팁도 제공한다.
5. 한국어로 답변한다.

대화 기록:
{conversation}
"""

    try:
        with st.chat_message("assistant"):
            with st.spinner("고백 멘트 생성 중..."):
                response = client.models.generate_content(
                    model="gemini-2.5-flash-lite",
                    contents=prompt,
                )

                answer = response.text

                st.markdown(answer)

        # 응답 저장
        st.session_state.messages.append(
            {"role": "assistant", "content": answer}
        )

    except Exception as e:
        error_msg = f"오류가 발생했습니다: {e}"

        with st.chat_message("assistant"):
            st.error(error_msg)

        st.session_state.messages.append(
            {"role": "assistant", "content": error_msg}
        )
