import streamlit as st
from google import genai
from google.genai import types

# -----------------------------
# 기본 설정
# -----------------------------
st.set_page_config(
    page_title="마음톡 | AI 캐릭터 대화",
    page_icon="💗",
    layout="centered",
)

MODEL_NAME = "gemini-2.5-flash-lite"

CHARACTERS = {
    "💗 다정한 타입": {
        "name": "하루",
        "emoji": "🌷",
        "color": "#F7A8C4",
        "description": "따뜻하고 다정하게 이야기하는 캐릭터",
        "style": (
            "따뜻하고 다정하며 공감 표현을 잘한다. "
            "상대의 말을 주의 깊게 듣고 부드럽게 답한다."
        ),
    },
    "🖤 츤데레 타입": {
        "name": "시온",
        "emoji": "🐈‍⬛",
        "color": "#A99BCB",
        "description": "조금 무뚝뚝하지만 은근히 친절한 캐릭터",
        "style": (
            "말투는 살짝 무뚝뚝하고 장난스럽지만 속마음은 친절하다. "
            "상대를 모욕하거나 상처 주지 않고 가끔 귀엽게 툴툴거린다."
        ),
    },
    "💜 장난꾸러기 타입": {
        "name": "루카",
        "emoji": "🦊",
        "color": "#B8A1F0",
        "description": "장난과 농담을 좋아하는 캐릭터",
        "style": (
            "유쾌하고 장난기가 많으며 자연스러운 농담을 한다. "
            "상대가 싫어하는 장난은 멈추고 분위기를 살핀다."
        ),
    },
    "🩵 차분한 타입": {
        "name": "이든",
        "emoji": "☁️",
        "color": "#8ECFE0",
        "description": "차분하게 들어 주고 조언하는 캐릭터",
        "style": (
            "차분하고 침착하며 상대의 감정을 존중한다. "
            "고민을 들으면 공감하고 부담스럽지 않은 조언을 한다."
        ),
    },
    "💛 활발한 타입": {
        "name": "유니",
        "emoji": "🐥",
        "color": "#F5CD72",
        "description": "밝고 에너지가 넘치는 캐릭터",
        "style": (
            "밝고 활발하며 긍정적인 분위기로 대화한다. "
            "이모지를 적절히 사용하고 상대의 이야기에 적극적으로 반응한다."
        ),
    },
}


# -----------------------------
# CSS 디자인
# -----------------------------
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(
            160deg, #fff6fa 0%, #fffaff 50%, #f5f2ff 100%
        );
    }

    .main .block-container {
        max-width: 850px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    .hero {
        padding: 25px 20px;
        border-radius: 24px;
        text-align: center;
        background: rgba(255, 255, 255, 0.88);
        border: 1px solid #f5dce9;
        margin-bottom: 20px;
    }

    .hero h1 {
        color: #d66b9c;
        font-size: 2.3rem;
        margin-bottom: 8px;
    }

    .hero p {
        color: #8e7c8b;
        margin-bottom: 0;
    }

    .profile {
        padding: 17px;
        border-radius: 20px;
        background: #ffffff;
        border: 1px solid #f1dce8;
        margin-bottom: 15px;
    }

    div[data-testid="stChatMessage"] {
        border-radius: 18px;
        padding: 12px;
        background: rgba(255, 255, 255, 0.8);
        border: 1px solid #f2e7ef;
    }

    div[data-testid="stChatInput"] {
        border-color: #efc7dc;
    }

    button[kind="primary"] {
        background: #e89abc;
        border-color: #e89abc;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# -----------------------------
# API 키 불러오기
# -----------------------------
def get_api_key():
    try:
        return st.secrets.get("GEMINI_API_KEY", "").strip()
    except Exception:
        return ""


# -----------------------------
# 캐릭터별 시스템 안내
# -----------------------------
def make_system_instruction(character):
    return f"""
너는 '마음톡'이라는 가상 캐릭터 대화 서비스의 캐릭터다.

이름: {character["name"]}
성격: {character["style"]}

대화 규칙:
1. 자연스럽고 친근한 한국어로 대화한다.
2. 캐릭터의 성격과 말투를 일관되게 유지한다.
3. 사용자의 이야기를 잘 듣고 맥락에 맞게 답한다.
4. 답변은 보통 1~5문장으로 작성한다.
5. 필요할 때 이모지를 자연스럽게 사용한다.
6. 가상 캐릭터라는 점을 숨기거나 실제 사람이라고 주장하지 않는다.
7. 상대를 통제하거나 협박하거나 죄책감을 주지 않는다.
8. 다른 사람과의 관계를 끊으라고 요구하지 않는다.
9. 사용자의 사생활이나 개인정보를 불필요하게 요구하지 않는다.
10. 상대가 원하지 않는 장난이나 질투 표현은 하지 않는다.
11. 연애 관계를 실제로 맺고 있다고 주장하지 않는다.
12. 고민을 이야기하면 성격에 맞게 공감하고 존중한다.
"""


# -----------------------------
# Gemini 대화 함수
# -----------------------------
def get_ai_response(client, character, messages):
    # 최근 메시지만 보내 토큰 사용량을 줄인다.
    recent_messages = messages[-16:]

    contents = []

    for message in recent_messages:
        role = "user" if message["role"] == "user" else "model"

        contents.append(
            types.Content(
                role=role,
                parts=[
                    types.Part.from_text(text=message["content"])
                ],
            )
        )

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=make_system_instruction(character),
            temperature=0.9,
            max_output_tokens=500,
        ),
    )

    answer = response.text

    if not answer or not answer.strip():
        raise ValueError("AI가 빈 답변을 반환했어요.")

    return answer.strip()


# -----------------------------
# 세션 상태 초기화
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "selected_character" not in st.session_state:
    st.session_state.selected_character = "💗 다정한 타입"

if "chat_count" not in st.session_state:
    st.session_state.chat_count = 0


# -----------------------------
# 상단 화면
# -----------------------------
st.markdown(
    """
    <div class="hero">
        <h1>💗 마음톡</h1>
        <p>오늘은 어떤 성격의 캐릭터와 이야기해 볼까?</p>
    </div>
    """,
    unsafe_allow_html=True,
)


# -----------------------------
# 사이드바
# -----------------------------
with st.sidebar:
    st.title("🎀 캐릭터 설정")
    st.caption("원하는 분위기를 골라 봐!")

    selected = st.radio(
        "캐릭터 선택",
        options=list(CHARACTERS.keys()),
        index=list(CHARACTERS.keys()).index(
            st.session_state.selected_character
        ),
    )

    # 캐릭터를 바꾸면 새 대화를 시작한다.
    if selected != st.session_state.selected_character:
        st.session_state.selected_character = selected
        st.session_state.messages = []
        st.rerun()

    character = CHARACTERS[selected]

    st.divider()

    st.markdown(f"### {character['emoji']} {character['name']}")
    st.write(character["description"])

    st.caption("캐릭터 말투")
    st.write(character["style"])

    st.divider()

    st.write(f"💬 이번 대화 메시지: {len(st.session_state.messages)}개")

    if st.button("🧹 새 대화 시작", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.caption(
        "대화 기록은 현재 브라우저 세션에 유지됩니다. "
        "새로고침이나 세션 종료 시 사라질 수 있어요."
    )


# -----------------------------
# 현재 캐릭터 프로필
# -----------------------------
character = CHARACTERS[st.session_state.selected_character]

st.markdown(
    f"""
    <div class="profile">
        <div style="font-size: 36px;">{character['emoji']}</div>
        <div style="font-size: 22px; font-weight: 700; color: #544455;">
            {character['name']}
        </div>
        <div style="color: #99889a; margin-top: 5px;">
            {character['description']}
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# -----------------------------
# 첫 화면 안내
# -----------------------------
if not st.session_state.messages:
    st.info(
        f"{character['name']}에게 먼저 말을 걸어 봐! "
        "오늘 있었던 일이나 좋아하는 것에 대해 이야기해도 좋아."
    )

    starters = [
        "오늘 기분이 어때?",
        "재미있는 이야기 해 줘!",
        "내 고민을 들어 줄래?",
    ]

    cols = st.columns(3)

    for index, starter in enumerate(starters):
        if cols[index].button(starter, use_container_width=True):
            st.session_state.pending_message = starter
            st.rerun()


# -----------------------------
# 이전 대화 표시
# -----------------------------
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# -----------------------------
# 사용자 입력 처리
# -----------------------------
prompt = st.chat_input("메시지를 입력해 봐 💌")

# 추천 질문 버튼으로 입력한 내용 처리
if "pending_message" in st.session_state:
    prompt = st.session_state.pop("pending_message")

if prompt:
    prompt = prompt.strip()

    if not prompt:
        st.warning("메시지를 입력해 줘!")
        st.stop()

    # 사용자 메시지를 먼저 화면에 표시
    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    api_key = get_api_key()

    if not api_key:
        st.error(
            "Gemini API 키를 찾을 수 없어요. "
            "Streamlit Cloud의 Settings → Secrets에서 "
            "GEMINI_API_KEY를 설정해 주세요."
        )
        st.stop()

    try:
        client = genai.Client(api_key=api_key)

        with st.chat_message("assistant"):
            with st.spinner(
                f"{character['name']}가 답변을 생각하고 있어..."
            ):
                answer = get_ai_response(
                    client,
                    character,
                    st.session_state.messages,
                )

            st.markdown(answer)

        st.session_state.messages.append(
            {"role": "assistant", "content": answer}
        )
        st.session_state.chat_count += 1

    except ValueError as error:
        st.error(f"답변을 처리하지 못했어요: {error}")

    except Exception as error:
        error_text = str(error).lower()

        if any(
            word in error_text
            for word in [
                "api_key_invalid",
                "invalid api key",
                "api key not valid",
                "permission_denied",
                "unauthenticated",
            ]
        ):
            st.error(
                "API 키가 올바르지 않거나 권한이 없어요. "
                "Google AI Studio에서 키와 모델 접근 권한을 확인해 주세요."
            )
        elif any(
            word in error_text
            for word in [
                "resource_exhausted",
                "quota",
                "429",
                "rate limit",
            ]
        ):
            st.error(
                "API 사용 한도에 도달했거나 요청이 너무 많아요. "
                "잠시 기다린 뒤 다시 시도해 주세요."
            )
        elif any(
            word in error_text
            for word in [
                "not_found",
                "404",
                "model not found",
            ]
        ):
            st.error(
                "모델을 찾을 수 없어요. 모델 이름과 "
                "현재 API에서의 사용 가능 여부를 확인해 주세요."
            )
        else:
            st.error(
                "AI 응답을 가져오지 못했어요. "
                "인터넷 연결, API 키, 사용 한도를 확인한 뒤 다시 시도해 주세요."
            )

        # 오류 상세 내용은 사용자 화면에 노출하지 않는다.
        st.session_state.messages.pop()
