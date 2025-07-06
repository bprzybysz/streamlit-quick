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

@mcp.tool(name="generate_sunburst_chart", description="Generates a Plotly sunburst chart for hierarchical data visualization.")
def generate_sunburst_chart(data_type: str = "company_structure"):
    """
    Generates a Plotly sunburst chart with interesting hierarchical data.
    
    Args:
        data_type: Type of data to visualize ("company_structure", "tech_stack", "sales_regions", "project_breakdown")
    """
    import plotly.express as px
    import pandas as pd
    
    # Define different interesting datasets
    datasets = {
        "company_structure": {
            "names": ["TechCorp", "Engineering", "Sales", "Marketing", "HR", 
                     "Frontend", "Backend", "DevOps", "Direct Sales", "Online Sales", 
                     "Channel Partners", "Content Marketing", "Digital Marketing", 
                     "SEO/SEM", "Recruitment", "Training", "Benefits"],
            "parents": ["", "TechCorp", "TechCorp", "TechCorp", "TechCorp",
                       "Engineering", "Engineering", "Engineering", "Sales", "Sales",
                       "Sales", "Marketing", "Marketing", "Marketing", "HR", "HR", "HR"],
            "values": [500, 200, 150, 100, 50,
                      80, 70, 50, 60, 50, 40, 40, 35, 25, 20, 20, 10],
            "title": "Company Organizational Structure"
        },
        
        "tech_stack": {
            "names": ["Tech Stack", "Frontend", "Backend", "Database", "DevOps",
                     "React", "Vue", "Angular", "Python", "Node.js", "Java",
                     "PostgreSQL", "MongoDB", "Redis", "Docker", "Kubernetes", "AWS"],
            "parents": ["", "Tech Stack", "Tech Stack", "Tech Stack", "Tech Stack",
                       "Frontend", "Frontend", "Frontend", "Backend", "Backend", "Backend",
                       "Database", "Database", "Database", "DevOps", "DevOps", "DevOps"],
            "values": [1000, 300, 400, 200, 100,
                      120, 100, 80, 180, 120, 100,
                      80, 70, 50, 40, 35, 25],
            "title": "Technology Stack Distribution"
        },
        
        "sales_regions": {
            "names": ["Global Sales", "North America", "Europe", "Asia Pacific",
                     "USA", "Canada", "Mexico", "UK", "Germany", "France",
                     "Japan", "China", "Australia", "India"],
            "parents": ["", "Global Sales", "Global Sales", "Global Sales",
                       "North America", "North America", "North America", 
                       "Europe", "Europe", "Europe",
                       "Asia Pacific", "Asia Pacific", "Asia Pacific", "Asia Pacific"],
            "values": [10000, 4500, 3000, 2500,
                      3000, 1000, 500, 1200, 800, 1000,
                      800, 700, 500, 500],
            "title": "Sales Performance by Region (in thousands)"
        },
        
        "project_breakdown": {
            "names": ["Software Project", "Development", "Testing", "Documentation", "Management",
                     "Core Features", "UI/UX", "API", "Unit Tests", "Integration Tests", "E2E Tests",
                     "User Manual", "API Docs", "Code Comments", "Planning", "Monitoring", "Reviews"],
            "parents": ["", "Software Project", "Software Project", "Software Project", "Software Project",
                       "Development", "Development", "Development", "Testing", "Testing", "Testing",
                       "Documentation", "Documentation", "Documentation", "Management", "Management", "Management"],
            "values": [800, 400, 200, 120, 80,
                      200, 120, 80, 80, 70, 50,
                      50, 40, 30, 30, 30, 20],
            "title": "Software Project Time Allocation (hours)"
        }
    }
    
    # Get the selected dataset or default to company_structure
    selected_data = datasets.get(data_type, datasets["company_structure"])
    
    # Create DataFrame
    df = pd.DataFrame(selected_data)
    
    # Create sunburst chart
    fig = px.sunburst(
        df,
        names='names',
        parents='parents', 
        values='values',
        title=selected_data['title'],
        color='values',
        color_continuous_scale='Viridis',
        hover_data={'values': ':,'}
    )
    
    # Customize the layout
    fig.update_layout(
        font_size=12,
        title_font_size=16,
        margin=dict(t=50, l=25, r=25, b=25)
    )
    
    return {"status": "success", "chart_json": fig.to_json(), "data_type": data_type}

@mcp.tool(name="generate_mermaid_diagram", description="Generates a Mermaid diagram for various types of visualizations.")
def generate_mermaid_diagram(diagram_type: str = "flowchart", content: str = ""):
    """
    Generates a Mermaid diagram based on type and content.
    
    Args:
        diagram_type: Type of diagram ("flowchart", "sequence", "gantt", "pie", "gitgraph", "mindmap")
        content: Custom content or use predefined examples if empty
    """
    
    # Predefined diagram templates
    templates = {
        "flowchart": """
graph TD
    A[Start] --> B{Decision}
    B -->|Yes| C[Process A]
    B -->|No| D[Process B]
    C --> E[End]
    D --> E
""",
        "sequence": """
sequenceDiagram
    participant A as Client
    participant B as Server
    participant C as Database
    
    A->>B: Request Data
    B->>C: Query Database
    C-->>B: Return Results
    B-->>A: Send Response
""",
        "gantt": """
gantt
    title Project Timeline
    dateFormat  YYYY-MM-DD
    section Phase 1
    Planning    :done, p1, 2025-01-01, 2025-01-15
    Design      :active, d1, 2025-01-10, 2025-01-25
    section Phase 2
    Development :dev1, 2025-01-20, 2025-03-01
    Testing     :test1, after dev1, 30d
""",
        "pie": """
pie title Project Resources
    "Development" : 45
    "Testing" : 25
    "Documentation" : 15
    "Management" : 15
""",
        "gitgraph": """
gitgraph
    commit
    branch feature
    checkout feature
    commit
    commit
    checkout main
    merge feature
    commit
""",
        "mindmap": """
mindmap
  root((MCP Architecture))
    Client
      Streamlit UI
      FastMCP Client
    Server
      Tools
      Resources
    Protocol
      JSON-RPC
      WebSocket
"""
    }
    
    # Use custom content if provided, otherwise use template
    if content.strip():
        mermaid_code = content
    else:
        mermaid_code = templates.get(diagram_type, templates["flowchart"])
    
    return {
        "status": "success", 
        "mermaid_code": mermaid_code,
        "diagram_type": diagram_type,
        "message": f"Generated {diagram_type} diagram successfully"
    }


