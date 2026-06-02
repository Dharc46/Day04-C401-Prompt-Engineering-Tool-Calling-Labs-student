from __future__ import annotations

from pathlib import Path
from typing import Any

import streamlit as st

from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from chat import run_model_tool_loop, trim_history

ROOT = Path(__file__).parent
ARTIFACTS_DIR = ROOT / "artifacts"

load_lab_env(ROOT)


def init_state() -> None:
    if "history" not in st.session_state:
        st.session_state.history = []
    if "rounds" not in st.session_state:
        st.session_state.rounds = []
    if "tool_events" not in st.session_state:
        st.session_state.tool_events = []
    if "assistant_text" not in st.session_state:
        st.session_state.assistant_text = ""


def reset_conversation() -> None:
    st.session_state.history = []
    st.session_state.rounds = []
    st.session_state.tool_events = []
    st.session_state.assistant_text = ""
    st.session_state.user_input = ""


def load_system_prompt(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def main() -> None:
    st.set_page_config(page_title="Research Agent UI", layout="wide")
    st.title("Research Agent Test UI")

    with st.sidebar:
        st.header("Agent settings")
        provider_name = st.selectbox("Provider", ["openrouter", "openai", "anthropic", "gemini"], index=0)
        version = st.text_input("Version label", value="v5")
        model = st.text_input("Model override (optional)", value="")
        history_window = st.slider("History window", min_value=1, max_value=20, value=5, help="Number of past user/assistant turns to keep in context.")
        max_tool_rounds = st.slider("Max tool rounds", min_value=1, max_value=10, value=4)
        st.button("Reset conversation", on_click=reset_conversation)

    init_state()

    system_prompt_path = ARTIFACTS_DIR / "system_prompt.md"
    tools_path = ARTIFACTS_DIR / "tools.yaml"
    system_prompt = load_system_prompt(system_prompt_path)
    tool_declarations = load_tool_declarations(tools_path)
    openai_tools = to_openai_tools(tool_declarations)
    provider = make_provider(provider_name)

    st.markdown("## System prompt preview")
    st.code(system_prompt[:2000] + ("..." if len(system_prompt) > 2000 else ""), language="markdown")

    st.markdown("## Conversation")
    with st.form("user_input_form"):
        user_input = st.text_area("User request", value=st.session_state.get("user_input", ""), height=160)
        submit = st.form_submit_button("Send")

    if submit and user_input.strip():
        messages = [
            {"role": "system", "content": system_prompt},
            *trim_history(st.session_state.history, history_window),
            {"role": "user", "content": user_input.strip()},
        ]
        result = run_model_tool_loop(
            provider=provider,
            messages=messages,
            tools=openai_tools,
            model=model or None,
            max_tool_rounds=max_tool_rounds,
        )

        st.session_state.history.append({"role": "user", "content": user_input.strip()})
        st.session_state.history.append({"role": "assistant", "content": result["assistant_text"]})
        st.session_state.rounds = result.get("rounds", [])
        st.session_state.tool_events = result.get("tool_events", [])
        st.session_state.assistant_text = result["assistant_text"]
        st.session_state.user_input = ""

    for turn in st.session_state.history:
        if turn["role"] == "user":
            st.markdown(f"**You:** {turn['content']}")
        else:
            st.markdown(f"**Agent:** {turn['content']}")

    if st.session_state.rounds:
        with st.expander("Round details", expanded=True):
            for round_record in st.session_state.rounds:
                st.markdown(f"### Round {round_record['round']}")
                st.markdown(f"**Assistant text:** {round_record['assistant_text']}" if round_record['assistant_text'] else "**Assistant text:** _None_")
                st.write("**Tool calls:**")
                st.json([{"name": call['name'], "args": call['args']} for call in round_record.get("tool_calls", [])])
                st.write("**Tool results:**")
                st.json(round_record.get("tool_results", []))

    if st.session_state.tool_events:
        with st.expander("All tool events", expanded=False):
            st.json(st.session_state.tool_events)

    st.markdown("---")
    st.markdown(
        "**How to use:** Set provider and model, then type a request. The UI preserves the latest conversation turns and shows tool call details for each round."
    )

    st.markdown("## Hướng dẫn sử dụng công cụ (Tiếng Việt)")
    st.markdown("Dưới đây là mô tả ngắn về những tool chính có sẵn và ví dụ prompt mẫu bằng tiếng Việt để người dùng thử.")

    st.markdown("**Tool cốt lõi (tóm tắt):**")
    st.markdown(
        "- `clarify`: Hỏi câu hỏi làm rõ khi thiếu thông tin (ví dụ: xác nhận yes/no hoặc thông tin bổ sung).\n"
        "- `fetch`: Lấy nội dung thô của một URL.\n"
        "- `format`: Làm sạch/chuẩn hoá văn bản hoặc chuyển định dạng.\n"
        "- `lookup`: Tìm kiếm trong kho tài liệu/cơ sở tri thức.\n"
        "- `paper_text`/`papers`: Lấy hoặc tìm thông tin bài báo khoa học.\n"
        "- `policy`: Tra cứu chính sách công ty theo chủ đề.\n"
        "- `send`: Gửi nội dung ra kênh bên ngoài (yêu cầu xác nhận trước khi gửi).\n"
        "- `social_search`: Tìm bài đăng mạng xã hội theo truy vấn.\n"
        "- `timeline`: Xây timeline từ các sự kiện hoặc văn bản."
    )

    # Show new tool docs if available
    ent_md = ROOT / "tools" / "entity_extract" / "TOOL.md"

    with st.expander("entity_extract — Trích thực thể (ví dụ)", expanded=False):
        if ent_md.exists():
            st.markdown(ent_md.read_text(encoding="utf-8"))
        else:
            st.markdown("Tool `entity_extract` không có tài liệu tại đường dẫn mong đợi.")

        st.markdown("**Ví dụ prompt (tiếng Việt):**")
        st.markdown(
            "- `Tách thực thể chính từ đoạn sau: \"OpenAI released GPT-4 and Sam Altman spoke at the event. Elon Musk attended.\" Trả về các thực thể hàng đầu và tần suất, tối đa 5.`\n"
            "- `Hãy liệt kê 5 thực thể quan trọng nhất (tên người, tổ chức, sản phẩm) trong văn bản sau: \"...\"`\n"
            "- `Extract top 3 entities from this paragraph: <paste text here>` (cũng chấp nhận tiếng Anh)."
        )

    st.markdown("---")
    st.markdown("**Chạy test nhanh:** Sử dụng `pytest` trong thư mục `starter_v0` để chạy unit tests đã thêm (ví dụ cho `entity_extract`).")


if __name__ == "__main__":
    main()
