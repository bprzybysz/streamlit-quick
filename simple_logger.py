import streamlit as st
from datetime import datetime
import time
import subprocess

# Initialize session state
if 'logs' not in st.session_state:
    st.session_state.logs = []

st.title("Checkpoint Logger")

col1, col2 = st.columns(2)

with col1:
    st.header("Add Log Entry")
    message = st.text_input("Message")
    level = st.selectbox("Level", ["info", "warning", "error"])
    source = st.text_input("Source", value="agent")
    
    if st.button("Add Log"):
        entry = {
            "message": message,
            "level": level,
            "source": source,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        }
        st.session_state.logs.append(entry)
        st.success("Log added!")

with col2:
    st.header("Results (Markdown)")
    
    if st.session_state.logs:
        markdown_content = "# System Logs\n\n"
        for log in st.session_state.logs:
            emoji = {"info": "ℹ️", "warning": "⚠️", "error": "❌"}
            markdown_content += f"{emoji.get(log['level'], '📝')} **[{log['timestamp']}]** `{log['source']}`: {log['message']}\n\n"
        
        st.markdown(markdown_content)
    else:
        st.info("No logs yet - add some entries!")

st.header("Source Code: simple_logger.py")

code_placeholder = st.empty()

# Read the content of the current file
try:
    with open(__file__, "r") as f:
        full_code = f.read()
except Exception as e:
    st.error(f"Error reading source file: {e}")
    full_code = "# Could not load source code."

if 'code_printed_length' not in st.session_state:
    st.session_state.code_printed_length = 0

# Only run the animation if it hasn't completed yet
if st.session_state.code_printed_length < len(full_code):
    for i in range(st.session_state.code_printed_length, len(full_code)):
        code_placeholder.code(full_code[:i+1], language='python')
        time.sleep(0.005) # Adjust speed here
        st.session_state.code_printed_length = i + 1
    st.session_state.code_printed_length = len(full_code)
else:
    # If already printed, just show the full code
    code_placeholder.code(full_code, language='python')

st.header("Project Files")
project_files = [
    {"file": "simple_logger.py", "description": "The main Streamlit application for logging."},
    {"file": "requirements.txt", "description": "Lists Python dependencies for the project."},
    {"file": ".gitignore", "description": "Specifies intentionally untracked files to ignore."},
    {"file": "venv/", "description": "Python virtual environment for project dependencies."}
]

file_table_markdown = "| File | Description |\n|---|---|\n"
for item in project_files:
    file_table_markdown += f"| {item['file']} | {item['description']} |\n"
st.markdown(file_table_markdown)

st.header("Streamlit Architecture")
mermaid_diagram = """
graph TD
    A[Client Browser] -->|Requests| B(Streamlit Server)
    B -->|Serves App| C{Streamlit App}
    C -->|Renders UI| A
"""
st.markdown(f"```mermaid\n{mermaid_diagram}```", unsafe_allow_html=True)

st.header("Git Status")
try:
    git_status_output = subprocess.check_output(["git", "status"], cwd=".").decode("utf-8")
    st.code(git_status_output, language="bash")
except Exception as e:
    st.error(f"Error getting git status: {e}")

st.header("Git Diff")
try:
    git_diff_output = subprocess.check_output(["git", "diff"], cwd=".").decode("utf-8")
    st.code(git_diff_output, language="diff")
except Exception as e:
    st.error(f"Error getting git diff: {e}")
