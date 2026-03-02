"""
UI helper components for the Streamlit application.
Ensures separation of concerns; no business logic or cryptography here.
"""

import os


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


def render_tasks(lab_id: int, lab_name: str, lang: str) -> None:
    """
    Reads and renders the task description for the specific lab.
    """
    task_file_path = f"labs/lab{lab_id}/task{lab_id}.txt"

    if not os.path.exists(task_file_path):
        st.info(f"Task file not found: {task_file_path}")
        return

    try:
        with open(task_file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Beautiful formatting for the task
        st.markdown(
            f"""
        <div style="border-left: 5px solid #00a0d2; padding-left: 15px; background-color: rgba(0, 160, 210, 0.1); padding-top: 10px; padding-bottom: 10px; border-radius: 0 10px 10px 0; margin-bottom: 20px;">
            <h2 style="color: #00a0d2; margin-top: 0; font-size: 1.5rem;">{t(T.TASKS, lang)}: {lab_name}</h2>
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Manual parsing for better look
        lines = content.split("\n")
        formatted_md = ""
        for line in lines:
            line = line.strip()
            if not line:
                formatted_md += "\n"
                continue

            # Heading detection
            headers = [
                "Тема:",
                "Завдання:",
                "Контрольні запитання:",
                "Теоретичні відомості:",
                "Оформлення звіту:",
                "Структура звіту:",
            ]
            if any(line.startswith(h) for h in headers):
                formatted_md += f"### {line}\n"
            elif line.startswith("Лабораторна робота"):
                formatted_md += f"## {line}\n"
            else:
                # Check for lists
                if line.startswith("-") or (
                    len(line) > 2 and line[0].isdigit() and line[1] == "."
                ):
                    formatted_md += f"{line}\n"
                else:
                    formatted_md += f"{line}  \n"  # Double space for line break

        st.markdown(formatted_md)
    except Exception as e:
        st.error(f"Error loading task: {str(e)}")
