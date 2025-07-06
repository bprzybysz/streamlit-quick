Looking at your current Streamlit MCP client code, I'll help you add a Mermaid diagram tool while preserving all existing functionality. Here's a comprehensive approach:

## **Add Mermaid Tool to MCP Server**

First, add this new tool to your `logging_mcp_server.py`:

```python
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
```

## **Update Streamlit Receiver**

Add this new section to your `streamlit_receiver.py` after the sunburst chart section:

```python
# Add this after the existing chart sections
st.subheader("Generate Mermaid Diagram")

# Diagram type selection with descriptions
diagram_types = {
    "flowchart": "📊 Flowchart - Process flows and decision trees",
    "sequence": "🔄 Sequence - Interaction between entities over time", 
    "gantt": "📅 Gantt - Project timeline and scheduling",
    "pie": "🥧 Pie Chart - Data distribution visualization",
    "gitgraph": "🌳 Git Graph - Version control branching",
    "mindmap": "🧠 Mind Map - Hierarchical concept mapping"
}

selected_diagram_type = st.selectbox(
    "Select Diagram Type",
    list(diagram_types.keys()),
    format_func=lambda x: diagram_types[x],
    help="Choose the type of Mermaid diagram to generate"
)

# Custom content option
use_custom_content = st.checkbox("Use Custom Mermaid Code", help="Check to provide your own Mermaid syntax")

custom_content = ""
if use_custom_content:
    custom_content = st.text_area(
        "Custom Mermaid Code",
        placeholder="Enter your Mermaid diagram syntax here...",
        height=150,
        help="Write your own Mermaid diagram code. Leave empty to use predefined template."
    )

# Show example for selected type
if not use_custom_content:
    with st.expander(f"Preview {selected_diagram_type} template"):
        st.info(f"This will generate a sample {selected_diagram_type} diagram using predefined content.")

if st.button("Generate Mermaid Diagram"):
    st.info("Generating Mermaid diagram on MCP server...")
    try:
        tool_arguments = {
            "diagram_type": selected_diagram_type,
            "content": custom_content if use_custom_content else ""
        }
        result = asyncio.run(call_mcp_tool(server_url, "generate_mermaid_diagram", tool_arguments))
        
        # Debug: Show the raw result
        with st.expander("Debug: Raw Result"):
            st.json(result)
        
        if isinstance(result, dict) and result.get("status") == "success" and "mermaid_code" in result:
            st.subheader(f"Generated {result.get('diagram_type', 'Unknown')} Diagram")
            
            # Display the Mermaid code
            st.code(result["mermaid_code"], language="mermaid")
            
            # Render the Mermaid diagram using st.markdown
            mermaid_html = f"""
            <div class="mermaid">
            {result["mermaid_code"]}
            </div>
            
            <script type="module">
                import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
                mermaid.initialize({{ startOnLoad: true }});
            </script>
            """
            
            st.markdown(mermaid_html, unsafe_allow_html=True)
            
            # Add helpful information
            st.markdown("""
            **💡 About Mermaid Diagrams:**
            - Copy the code above to use in GitHub, GitLab, or Notion
            - Mermaid diagrams are text-based and version-control friendly
            - You can edit the code and regenerate for customization
            """)
            
            # Download option
            st.download_button(
                label="📥 Download Mermaid Code",
                data=result["mermaid_code"],
                file_name=f"mermaid_{result.get('diagram_type', 'diagram')}.md",
                mime="text/markdown"
            )
            
        else:
            st.error(f"Failed to generate Mermaid diagram: {result.get('message', 'Unknown error')}")
            
    except Exception as e:
        st.error(f"An error occurred: {e}")
```

## **Enhanced Mermaid Rendering (Optional)**

For better Mermaid rendering, you can also add this enhanced version that includes proper Mermaid.js integration:

```python
def render_mermaid_diagram(mermaid_code: str, diagram_id: str = "mermaid-diagram"):
    """Enhanced Mermaid diagram rendering with proper JavaScript integration."""
    
    # Create unique ID for this diagram
    unique_id = f"{diagram_id}-{hash(mermaid_code) % 10000}"
    
    mermaid_html = f"""
    <div id="{unique_id}" style="text-align: center; margin: 20px 0;">
        <div class="mermaid">
{mermaid_code}
        </div>
    </div>
    
    <script type="module">
        import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
        
        mermaid.initialize({{
            startOnLoad: true,
            theme: 'default',
            securityLevel: 'loose',
            fontFamily: 'Arial, sans-serif'
        }});
        
        // Re-render if already initialized
        if (window.mermaidInitialized) {{
            mermaid.init(undefined, document.querySelectorAll('#{unique_id} .mermaid'));
        }} else {{
            window.mermaidInitialized = true;
        }}
    </script>
    
    <style>
        #{unique_id} .mermaid {{
            background-color: white;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 20px;
            margin: 10px 0;
        }}
    </style>
    """
    
    return mermaid_html

# Then use it in your Streamlit code:
if isinstance(result, dict) and result.get("status") == "success" and "mermaid_code" in result:
    st.subheader(f"Generated {result.get('diagram_type', 'Unknown')} Diagram")
    
    # Display the Mermaid code
    st.code(result["mermaid_code"], language="mermaid")
    
    # Render the diagram
    mermaid_html = render_mermaid_diagram(result["mermaid_code"])
    st.markdown(mermaid_html, unsafe_allow_html=True)
```

## **Key Design Considerations**

**Preserving Existing Functionality:**
- All existing tools (log_message, get_logs_table, generate_pie_chart, generate_sunburst_chart) remain unchanged
- The `call_mcp_tool` function is reused without modification
- UI layout maintains the same structure with the new section added at the end

**Error Handling:**
- Comprehensive try-catch blocks prevent crashes
- Debug information available via expandable section
- Graceful fallbacks for rendering issues

**User Experience:**
- Clear descriptions for each diagram type
- Option for both predefined templates and custom code
- Preview functionality and download capability
- Helpful tooltips and information sections

**Technical Robustness:**
- Unique IDs for multiple diagrams on the same page
- Proper JavaScript module loading
- CSS styling for better visual presentation
- Mermaid.js CDN integration for reliable rendering

This implementation adds powerful diagram capabilities while maintaining all existing functionality and following the same patterns established in your current codebase.

Citations:
[1] [repomix-output.xml](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/8768170/7e23488b-dc72-41b9-a089-912819da4e2c/repomix-output.xml)  
[2] [How to Build an MCP Client GUI with Streamlit and FastAPI - YouTube](https://www.youtube.com/watch?v=C2Pg0nWMWew)  
[3] [Add support for mermaid charts · Issue #10721 · streamlit ... - GitHub](https://github.com/streamlit/streamlit/issues/10721)  
[4] [Discover and share useful bits of code with the 🪢 streamlit-extras library](https://blog.streamlit.io/discover-and-share-useful-bits-of-code-with-the-streamlit-extras-library/)  
[5] [FAQ: How to customize the style or appearance of your Streamlit app](https://discuss.streamlit.io/t/faq-how-to-customize-the-style-or-appearance-of-your-streamlit-app/63878)  
[6] [How To Create a Custom MCP Client Using Streamlit and FastAPI ...](https://www.youtube.com/watch?v=0KJ2oBRtUbs)  
[7] [Best Practices for Building GenAI Apps with Streamlit](https://blog.streamlit.io/best-practices-for-building-genai-apps-with-streamlit/)  
[8] [guinacio/langchain-mcp-client: This Streamlit application ... - GitHub](https://github.com/guinacio/langchain-mcp-client)  
[9] [Your Own MCP Playground: Build It with Streamlit, LangGraph, and ...](https://discuss.streamlit.io/t/your-own-mcp-playground-build-it-with-streamlit-langgraph-and-docker/113080)  
[10] [A Streamlit-powered Jira assistant with MCP integration ... - GitHub](https://github.com/pawankumar94/Jira_mcp_streamlit)  
[11] [Unlocking the Full Potential of Streamlit: Must-Know Tips and Tricks](https://www.toolify.ai/ai-news/unlocking-the-full-potential-of-streamlit-mustknow-tips-and-tricks-1852759)  
[12] [MCP Client Streamlit Interface](https://mcp.so/client/mcp-client/Zeeshanunique)  
[13] [Creating Mermaid Diagrams with AI Using Streamlit! | Satyajit Singh](https://www.linkedin.com/posts/satyajit-singh-58889131_creating-mermaid-diagrams-with-ai-using-activity-7210467800044253185-WLcd)  
[14] [Streamlit: A Faster Way to Build and Share Apps - Simplilearn.com](https://www.simplilearn.com/streamlit-article)  
[15] [3 Tips to Customize your Streamlit App](https://python.plainenglish.io/three-tips-to-improve-your-streamlit-app-a4c94b4d2b30?gi=3e0931705230)  
[16] [Host MCP Client or Server Using Streamlit](https://www.comparepriceacross.com/post/host_mcp_client_or_server_using_streamlit/)  
[17] [Chainlit <> Mermaid Rendering Issue - Stack Overflow](https://stackoverflow.com/questions/79680987/chainlit-mermaid-rendering-issue)  
[18] [4 ways of STYLING Streamlit widgets](https://www.youtube.com/watch?v=OVgPJEMDkak)  
[19] [Building Streamlit UI MCP Client with LangChain, Python ... - YouTube](https://www.youtube.com/watch?v=Ln-Tgz8Pmek)  
[20] [Generate mermaid diagrams using Langhchain & OpenAI|Tutorail:61](https://www.youtube.com/watch?v=x8mXEu8hS1g)  
[21] [Additional Streamlit features - Streamlit Docs](https://docs.streamlit.io/get-started/fundamentals/additional-features)