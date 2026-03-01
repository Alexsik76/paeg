"""
UI helper components for the Streamlit application.
Ensures separation of concerns; no business logic or cryptography here.
"""

import streamlit as st
from typing import List, Dict
from core.i18n import t, T


def render_terminal(logs: List[str], lang: str) -> None:
    """
    Renders a terminal-like window displaying the provided logs.
    """
    st.markdown(t(T.PROCESS_TERMINAL_LOG, lang))

    if not logs:
        st.info(t(T.NO_LOGS, lang))
        return

    terminal_content = "\n".join(logs)
    st.code(terminal_content, language="bash")


def render_results(tallies: Dict[str, int], lang: str) -> None:
    """
    Renders the election results as metrics and a bar chart, and handles tie conditions.
    """
    st.markdown(t(T.ELECTION_RESULTS, lang))

    if not tallies or sum(tallies.values()) == 0:
        st.warning(t(T.NO_VOTES, lang))
        return

    # Check for tie
    values = list(tallies.values())
    if len(values) > 1 and len(set(values)) == 1 and values[0] > 0:
        st.warning(t(T.TIE_WARNING, lang))

    cols = st.columns(len(tallies))
    for i, (candidate, count) in enumerate(tallies.items()):
        with cols[i]:
            st.metric(label=candidate, value=count)

    # Optional bar chart
    st.bar_chart(tallies)
