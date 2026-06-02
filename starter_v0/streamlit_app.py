from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

from chat import (
    ARTIFACTS_DIR,
    ROOT,
    now_iso,
    run_model_tool_loop,
    safe_slug,
    trim_history,
    write_transcript,
)
from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version


PROVIDERS = ["openrouter", "openai", "anthropic", "gemini"]
PROVIDER_KEY_ENV = {
    "openrouter": "OPENROUTER_API_KEY",
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "gemini": "GEMINI_API_KEY",
}


st.set_page_config(page_title="Research Agent", page_icon=":", layout="wide")
load_lab_env(ROOT)


def default_session() -> dict[str, Any]:
    return {
        "provider": "openrouter",
        "model": "",
        "version": "v0",
        "history_window": 5,
        "max_tool_rounds": 4,
        "messages": [],
        "turns": [],
        "transcript_path": None,
        "transcript": None,
        "turn_index": 0,
    }


def reset_chat() -> None:
    config = {
        "provider": st.session_state.get("provider", "openrouter"),
        "model": st.session_state.get("model", ""),
        "version": st.session_state.get("version", "v0"),
        "history_window": st.session_state.get("history_window", 5),
        "max_tool_rounds": st.session_state.get("max_tool_rounds", 4),
    }
    st.session_state.agent_chat = default_session()
    st.session_state.agent_chat.update(config)


def json_pretty(value: Any, *, max_chars: int = 20000) -> str:
    text = json.dumps(value, ensure_ascii=False, indent=2, default=str)
    if len(text) > max_chars:
        return text[:max_chars] + "\n...<truncated>"
    return text


def env_status(provider: str) -> tuple[str, bool]:
    key_name = PROVIDER_KEY_ENV[provider]
    return key_name, bool(os.getenv(key_name))


@st.cache_resource(show_spinner=False)
def load_runtime(system_prompt_path: str, tools_path: str) -> tuple[str, list[dict[str, Any]]]:
    system_prompt = Path(system_prompt_path).read_text(encoding="utf-8")
    tool_declarations = load_tool_declarations(Path(tools_path))
    return system_prompt, to_openai_tools(tool_declarations)


def new_transcript(
    *,
    provider_name: str,
    selected_model: str | None,
    version: str,
    system_prompt_path: Path,
    tools_path: Path,
    history_window: int,
    max_tool_rounds: int,
) -> tuple[Path, dict[str, Any]]:
    artifact_version = build_artifact_version(version, system_prompt_path, tools_path)
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    transcript_id = "_".join([safe_slug(version), safe_slug(provider_name), "streamlit", timestamp])
    transcript_path = ROOT / "transcripts" / f"{transcript_id}.transcript.json"
    transcript: dict[str, Any] = {
        "transcript_id": transcript_id,
        **artifact_version_dict(artifact_version),
        "provider": provider_name,
        "model": selected_model,
        "system_prompt": str(system_prompt_path),
        "tools": str(tools_path),
        "history_window": history_window,
        "max_tool_rounds": max_tool_rounds,
        "interface": "streamlit",
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "turns": [],
    }
    write_transcript(transcript_path, transcript)
    return transcript_path, transcript


def ensure_transcript(
    *,
    chat: dict[str, Any],
    provider_name: str,
    selected_model: str | None,
    version: str,
    system_prompt_path: Path,
    tools_path: Path,
    history_window: int,
    max_tool_rounds: int,
) -> None:
    if chat["transcript"] is not None and chat["transcript_path"] is not None:
        return
    transcript_path, transcript = new_transcript(
        provider_name=provider_name,
        selected_model=selected_model,
        version=version,
        system_prompt_path=system_prompt_path,
        tools_path=tools_path,
        history_window=history_window,
        max_tool_rounds=max_tool_rounds,
    )
    chat["transcript_path"] = str(transcript_path)
    chat["transcript"] = transcript


def render_tool_rounds(turn: dict[str, Any]) -> None:
    rounds = turn.get("rounds") or []
    if not rounds:
        return
    with st.expander("Tool calls and results", expanded=False):
        for round_record in rounds:
            st.caption(f"Round {round_record.get('round')}")
            tool_calls = round_record.get("tool_calls") or []
            tool_results = round_record.get("tool_results") or []
            if tool_calls:
                st.markdown("**Calls**")
                st.code(json_pretty(tool_calls), language="json")
            if tool_results:
                st.markdown("**Results**")
                st.code(json_pretty(tool_results), language="json")


def provider_error_message(error: str) -> str:
    if "Missing API key env var:" in error:
        key_name = error.rsplit(":", 1)[-1].strip()
        return f"Missing `{key_name}`. Add it to `.env`, then reset the chat or rerun the app."
    if "Missing " in error and " env var" in error:
        return f"{error}. Add the required tool key to `.env` and try again."
    return error


def missing_tool_keys(turn: dict[str, Any]) -> list[str]:
    keys: list[str] = []
    for event in turn.get("tool_events") or []:
        result = event.get("result")
        if not isinstance(result, dict):
            continue
        message = str(result.get("message", ""))
        if message.startswith("Missing ") and " env var" in message:
            key_name = message.removeprefix("Missing ").removesuffix(" env var").strip()
            if key_name and key_name not in keys:
                keys.append(key_name)
    return keys


if "agent_chat" not in st.session_state:
    st.session_state.agent_chat = default_session()

chat = st.session_state.agent_chat

with st.sidebar:
    st.title("Research Agent")
    provider_name = st.selectbox(
        "Provider",
        PROVIDERS,
        index=PROVIDERS.index(chat["provider"]) if chat["provider"] in PROVIDERS else 0,
        key="provider",
    )
    model_text = st.text_input("Model override", value=chat["model"], key="model")
    version = st.text_input("Version", value=chat["version"], key="version")
    history_window = st.number_input(
        "History window",
        min_value=0,
        max_value=20,
        value=int(chat["history_window"]),
        step=1,
        key="history_window",
    )
    max_tool_rounds = st.number_input(
        "Max tool rounds",
        min_value=1,
        max_value=10,
        value=int(chat["max_tool_rounds"]),
        step=1,
        key="max_tool_rounds",
    )

    key_name, has_provider_key = env_status(provider_name)
    if has_provider_key:
        st.success(f"{key_name} loaded")
    else:
        st.warning(f"{key_name} is not set")

    if st.button("Reset chat", use_container_width=True):
        reset_chat()
        st.rerun()

    if chat["transcript_path"]:
        st.caption("Transcript")
        st.code(chat["transcript_path"], language=None)

system_prompt_path = ARTIFACTS_DIR / "system_prompt.md"
tools_path = ARTIFACTS_DIR / "tools.yaml"
selected_model = model_text.strip() or None

st.title("Research Agent Chat")
st.caption("Multi-turn chat with local tool execution and JSON transcript logging.")

for message in chat["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant" and message.get("turn"):
            render_tool_rounds(message["turn"])

user_text = st.chat_input("Ask for research, summaries, source lookups, or tool-based actions")

if user_text:
    chat["messages"].append({"role": "user", "content": user_text})
    with st.chat_message("user"):
        st.markdown(user_text)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        try:
            system_prompt, openai_tools = load_runtime(str(system_prompt_path), str(tools_path))
            provider = make_provider(provider_name)
            actual_model = selected_model or getattr(provider, "default_model", None)
            ensure_transcript(
                chat=chat,
                provider_name=provider_name,
                selected_model=actual_model,
                version=version,
                system_prompt_path=system_prompt_path,
                tools_path=tools_path,
                history_window=int(history_window),
                max_tool_rounds=int(max_tool_rounds),
            )
            chat["turn_index"] += 1

            history = [
                {"role": item["role"], "content": item["content"]}
                for item in chat["messages"][:-1]
                if item["role"] in {"user", "assistant"}
            ]
            messages = [
                {"role": "system", "content": system_prompt},
                *trim_history(history, int(history_window)),
                {"role": "user", "content": user_text},
            ]
            turn_record: dict[str, Any] = {
                "turn_index": chat["turn_index"],
                "started_at": now_iso(),
                "user": user_text,
                "status": "started",
                "assistant_text": None,
                "rounds": [],
                "tool_events": [],
            }

            with st.spinner("Running model and tools..."):
                result = run_model_tool_loop(
                    provider=provider,
                    messages=messages,
                    tools=openai_tools,
                    model=selected_model,
                    max_tool_rounds=int(max_tool_rounds),
                )

            turn_record.update(result)
            assistant_text = result["assistant_text"] or ""
            turn_record["assistant_text"] = assistant_text
            placeholder.markdown(assistant_text)
            missing_keys = missing_tool_keys(turn_record)
            if missing_keys:
                st.warning(
                    "Missing tool API key(s): "
                    + ", ".join(f"`{key}`" for key in missing_keys)
                    + ". Add them to `.env` for those tools to work."
                )
            render_tool_rounds(turn_record)

        except Exception as exc:
            error = f"{type(exc).__name__}: {str(exc)}"
            assistant_text = provider_error_message(str(exc))
            if "turn_index" not in locals() and "turn_record" not in locals():
                chat["turn_index"] += 1
            turn_record = {
                "turn_index": chat.get("turn_index", 0),
                "started_at": now_iso(),
                "ended_at": now_iso(),
                "user": user_text,
                "status": "provider_error",
                "assistant_text": assistant_text,
                "rounds": [],
                "tool_events": [],
                "error": error,
            }
            placeholder.error(assistant_text)

        turn_record["ended_at"] = now_iso()
        chat["turns"].append(turn_record)
        chat["messages"].append({"role": "assistant", "content": assistant_text, "turn": turn_record})

        if chat.get("transcript") is not None and chat.get("transcript_path") is not None:
            chat["transcript"]["turns"].append(turn_record)
            write_transcript(Path(chat["transcript_path"]), chat["transcript"])
