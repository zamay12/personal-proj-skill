import streamlit as st

from novel_continuation_agent.agent import list_pipeline_stage_names


def main() -> None:
    st.set_page_config(page_title="Novel Continuation Agent", layout="wide")
    st.title("novel-continuation-agent")
    st.caption("Minimal runnable skeleton")

    st.subheader("Pipeline")
    for stage in list_pipeline_stage_names():
        st.write(f"- {stage}")


if __name__ == "__main__":
    main()
