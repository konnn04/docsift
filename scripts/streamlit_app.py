from __future__ import annotations
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st

from src.config import settings
from src.providers.base import ProviderError
from src.providers.factory import build_providers

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

st.set_page_config(page_title="OptiBot test UI", page_icon="🤖")
st.title("OptiBot test UI")
st.caption(f"Store: {settings.gemini_store_name} · Model: {settings.gemini_model}")

if "messages" not in st.session_state:
    st.session_state.messages = [] 


def render_citations(citations: list[str]) -> None:
    if not citations:
        st.caption("(No citation metadata returned by the SDK for this call.)")
        return
    with st.expander(f"📎 {len(citations)} citation(s)", expanded=False):
        for c in citations:
            st.caption(c)


for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if msg["role"] == "assistant":
            st.caption(f"Provider used: {msg['provider']}")
            render_citations(msg["citations"])

question = st.chat_input("Ask a question about OptiSigns docs...")

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.write(question)

    with st.chat_message("assistant"):
        try:
            providers = build_providers()
        except ProviderError as exc:
            st.error(str(exc))
            st.stop()

        provider = providers[0]
        citations_box: list[list[str]] = [[]]
        stream = provider.ask_stream(
            question,
            settings.system_prompt,
            on_citations=lambda c: citations_box.__setitem__(0, c),
        )

        try:
            answer = st.write_stream(stream)
        except ProviderError as exc:
            st.error(f"Query failed: {exc}")
            st.stop()

        st.caption(f"Provider used: {provider.name}")
        citations = citations_box[0]
        render_citations(citations)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
            "provider": provider.name,
            "citations": citations,
        }
    )
