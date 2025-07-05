import streamlit as st
from datetime import datetime
import time
import subprocess
import concurrent.futures
import requests

# Initialize session state
if 'logs' not in st.session_state:
    st.session_state.logs = []

st.title("Checkpoint Logger")

# Initialize ThreadPoolExecutor in session state for git commands and file reading
if 'executor' not in st.session_state:
    st.session_state.executor = concurrent.futures.ThreadPoolExecutor(max_workers=3) # Increased max_workers for 2 file reads + git

# Function to run git command
def run_git_command(command):
    return subprocess.check_output(command, cwd=".").decode("utf-8")

# Function to read file content
def read_file_content(filepath):
    try:
        with open(filepath, "r") as f:
            return f.read()
    except Exception as e:
        return f"# Error reading file {filepath}: {e}"

# --- MCP Server Integration ---
MCP_SERVER_URL = "http://localhost:8000/mcp/" # Default FastMCP RPC endpoint

def send_log_to_mcp_server(message: str, level: str, source: str):
    payload = {
        "jsonrpc": "2.0",
        "method": "log_message",
        "params": {"message": f"From Streamlit ({source}): {message}", "level": level},
        "id": 1 # A simple ID for the request
    }
    headers = {'Accept': 'application/json'}
    try:
        response = requests.post(MCP_SERVER_URL, json=payload, headers=headers)
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        result = response.json()
        if "result" in result:
            st.success(f"MCP Server response: {result['result']['message']}")
        elif "error" in result:
            st.error(f"MCP Server error: {result['error']['message']}")
        return result
    except requests.exceptions.ConnectionError as e:
        st.error(f"Could not connect to MCP server at {MCP_SERVER_URL}. Is it running? Error: {e}")
        return {"error": {"message": f"Connection error: {e}"}}
    except requests.exceptions.RequestException as e:
        st.error(f"Error sending log to MCP server: {e}")
        return {"error": {"message": f"Request error: {e}"}}


# --- Other Application Content ---


st.header("Add Log Entry")
message = st.text_input("Message")
level = st.selectbox("Level", ["info", "warning", "error"])
source = st.text_input("Source", value="agent")

if st.button("Add Log"):
    # Send log to MCP server
    send_log_to_mcp_server(message, level, source)
    
    # Add to Streamlit's local logs for display
    entry = {
        "message": message,
        "level": level,
        "source": source,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    }
    st.session_state.logs.append(entry)
    st.success("Log added to Streamlit display!")

st.header("Results (Markdown)")

if st.session_state.logs:
    markdown_content = "# System Logs\n\n"
    for log in st.session_state.logs:
        emoji = {"info": "ℹ️", "warning": "⚠️", "error": "❌"}
        markdown_content += f"{emoji.get(log['level'], '📝')} **[{log['timestamp']}]** `{log['source']}`: {log['message']}\n\n"
    
    st.markdown(markdown_content)
else:
    st.info("No logs yet - add some entries!")

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

# Git Status
if 'git_status_future' not in st.session_state:
    st.session_state.git_status_future = st.session_state.executor.submit(run_git_command, ["git", "status"])

if st.session_state.git_status_future.running():
    st.info("Fetching git status...")
    st.spinner("Loading...")
    st.rerun()
else:
    try:
        git_status_output = st.session_state.git_status_future.result()
        st.code(git_status_output, language="bash")
    except Exception as e:
        st.error(f"Error getting git status: {e}")

# Git Diff
if 'git_diff_future' not in st.session_state:
    st.session_state.git_diff_future = st.session_state.executor.submit(run_git_command, ["git", "diff"])

if st.session_state.git_diff_future.running():
    st.info("Fetching git diff...")
    st.spinner("Loading...")
    st.rerun()
else:
    try:
        git_diff_output = st.session_state.git_diff_future.result()
        st.code(git_diff_output, language="diff")
    except Exception as e:
        st.error(f"Error getting git diff: {e}")