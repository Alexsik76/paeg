"""
UI helper components for the Streamlit application.
Ensures separation of concerns; no business logic or cryptography here.
"""

import streamlit as st
from typing import List, Dict


def render_terminal(logs: List[str]) -> None:
    """
    Renders a terminal-like window displaying the provided logs.
    """
    st.markdown("### Process Terminal Log")

    if not logs:
        st.info("No actions logged yet.")
        return

    terminal_content = "\n".join(logs)
    st.code(terminal_content, language="bash")


def render_results(tallies: Dict[str, int]) -> None:
    """
    Renders the election results as metrics and a bar chart.
    """
    st.markdown("### Election Results")

    if not tallies:
        st.warning("No votes have been cast yet or no candidates available.")
        return

    cols = st.columns(len(tallies))
    for i, (candidate, count) in enumerate(tallies.items()):
        with cols[i]:
            st.metric(label=candidate, value=count)

    # Optional bar chart
    st.bar_chart(tallies)
