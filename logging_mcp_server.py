import logging
from fastmcp import FastMCP

# Configure basic logging for the server
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize the FastMCP server
mcp = FastMCP(name="logging-server")

@mcp.tool(name="log_message", description="Logs a message with a specified level.")
def log_message(message: str, level: str = "info"):
    """
    Logs a message using the server's logger.
    """
    if level.lower() == "info":
        logging.info(message)
    elif level.lower() == "warning":
        logging.warning(message)
    elif level.lower() == "error":
        logging.error(message)
    else:
        logging.debug(message) # Default to debug for unknown levels
    return {"status": "success", "message": f"Logged: {message} with level {level}"}

@mcp.tool(name="get_logs_table", description="Returns a table of simulated log data.")
def get_logs_table():
    """
    Returns a list of dictionaries representing log entries.
    """
    logs = [
        {"timestamp": "2025-07-06 01:00:00", "level": "INFO", "message": "User logged in"},
        {"timestamp": "2025-07-06 01:01:00", "level": "WARNING", "message": "High CPU usage detected"},
        {"timestamp": "2025-07-06 01:02:00", "level": "ERROR", "message": "Database connection failed"},
        {"timestamp": "2025-07-06 01:03:00", "level": "INFO", "message": "Report generated"},
        {"timestamp": "2025-07-06 01:04:00", "level": "DEBUG", "message": "Function X completed"},
    ]
    return {"status": "success", "data": logs}

@mcp.tool(name="generate_pie_chart", description="Generates a Plotly pie chart.")
def generate_pie_chart(labels: list[str], values: list[float], title: str = "Pie Chart"):
    """
    Generates a Plotly pie chart and returns it as an HTML string.
    """
    import plotly.graph_objects as go

    fig = go.Figure(data=[go.Pie(labels=labels, values=values)])
    fig.update_layout(title_text=title)
    return {"status": "success", "chart_json": fig.to_json()}


