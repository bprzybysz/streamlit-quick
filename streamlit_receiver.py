import streamlit as st
import asyncio
import json
from fastmcp.client import Client

async def call_mcp_tool(server_url: str, tool_name: str, tool_arguments: dict) -> dict:
    """
    Connects to the MCP server, calls a specified tool, and returns the result.
    """
    try:
        async with Client(server_url) as client:
            raw_result = await client.call_tool(tool_name, tool_arguments)

            
            # 1. Prioritize structured_content if it exists and is not empty
            if hasattr(raw_result, 'structured_content') and raw_result.structured_content:

                return raw_result.structured_content
            
            # 2. Handle raw_result.content if it exists
            elif hasattr(raw_result, 'content') and raw_result.content:

                if isinstance(raw_result.content, str):
                    try:
                        parsed_json = json.loads(raw_result.content)

                        return parsed_json
                    except json.JSONDecodeError as e:

                        return {"status": "error", "message": f"JSON decode error: {e}"}
                elif isinstance(raw_result.content, list) and len(raw_result.content) > 0:
                    # This is the case where content is a list of TextContent objects
                    first_item = raw_result.content[0]

                    if hasattr(first_item, 'text'):
                        try:
                            parsed_json = json.loads(first_item.text)

                            return parsed_json
                        except json.JSONDecodeError as e:

                            return {"status": "error", "message": f"JSON decode error: {e}"}
                    else:

                        return {"status": "error", "message": "No text content in result from raw_result.content list"}
                else:

                    return {"status": "error", "message": "Unexpected content format"}
            
            # 3. Handle the case where raw_result itself is a list (less common now, but keep for robustness)
            elif isinstance(raw_result, list) and len(raw_result) > 0:

                first_item = raw_result[0]

                if hasattr(first_item, 'text'):
                    try:
                        parsed_json = json.loads(first_item.text)

                        return parsed_json
                    except json.JSONDecodeError as e:

                        return {"status": "error", "message": f"JSON decode error: {e}"}
                else:

                    return {"status": "error", "message": "No text content in result from raw_result list"}
            
            # 4. If none of the above, return unexpected format
            else:

                return {"status": "error", "message": "Unexpected result format"}
                
    except Exception as e:

        return {"status": "error", "message": f"Error calling MCP tool: {e}"}

def main():
    st.title("Streamlit MCP Client")
    st.write("Interact with an MCP server by calling a tool.")

    server_url = st.text_input("MCP Server URL", "http://localhost:8000/mcp/")
    tool_name = st.text_input("Tool Name", "log_message")
    message_value = st.text_input("Message", "Hello from Streamlit!")
    level_value = st.text_input("Level (info, warning, error, debug)", "info")

    tool_arguments = {"message": message_value, "level": level_value}

    if st.button("Call MCP Tool"):
        if not server_url or not tool_name:
            st.error("Please fill in all required fields.")
            return

        st.info(f"Calling tool '{tool_name}' on {server_url} with arguments: {tool_arguments}...")
        try:
            result = asyncio.run(call_mcp_tool(server_url, tool_name, tool_arguments))
    
            st.subheader("Tool Result")

        except Exception as e:
            st.error(f"An error occurred: {e}")

    if st.button("Get Log Table"):
        st.info("Fetching log table from MCP server...")
        try:
            result = asyncio.run(call_mcp_tool(server_url, "get_logs_table", {}))

            # Debug: Show the raw result

            
            if isinstance(result, dict) and result.get("status") == "success" and "data" in result:
                st.subheader("Log Table")
                import pandas as pd
                df = pd.DataFrame(result["data"])
                st.dataframe(df, use_container_width=True)
            else:
                st.error(f"Failed to get log table: {result}")
        except Exception as e:
            st.error(f"An error occurred: {e}")

    st.subheader("Generate Pie Chart")
    chart_labels = st.text_input("Chart Labels (comma-separated)", "A,B,C")
    chart_values = st.text_input("Chart Values (comma-separated numbers)", "10,20,30")
    chart_title = st.text_input("Chart Title", "My Pie Chart")

    if st.button("Generate Pie Chart"):
        try:
            labels_list = [label.strip() for label in chart_labels.split(',')]
            values_list = [float(value.strip()) for value in chart_values.split(',')]

            if len(labels_list) != len(values_list):
                st.error("Labels and Values must have the same number of elements.")
                return

            st.info("Generating pie chart on MCP server...")
            tool_arguments = {"labels": labels_list, "values": values_list, "title": chart_title}
            result = asyncio.run(call_mcp_tool(server_url, "generate_pie_chart", tool_arguments))

            # Debug: Show the raw result

            
            if isinstance(result, dict) and result.get("status") == "success" and "chart_json" in result:
                import plotly.io as pio
                
                st.subheader("Generated Pie Chart")
                # Use plotly.io.from_json to properly parse the JSON
                fig = pio.from_json(result["chart_json"])
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.error(f"Failed to generate pie chart: {result.get('message', 'Unknown error')}")
        except ValueError:
            st.error("Please enter valid numbers for chart values.")
        except Exception as e:
            st.error(f"An error occurred: {e}")

    st.subheader("Generate Sunburst Chart")
    data_type = st.selectbox(
        "Select Data Type",
        ["company_structure", "tech_stack", "sales_regions", "project_breakdown"],
        help="Choose the type of hierarchical data to visualize"
    )

    data_descriptions = {
        "company_structure": "Organizational hierarchy with departments and teams",
        "tech_stack": "Technology stack breakdown by categories",
        "sales_regions": "Sales performance across global regions", 
        "project_breakdown": "Software project time allocation by activities"
    }

    st.info(f"📊 {data_descriptions[data_type]}")

    if st.button("Generate Sunburst Chart"):
        st.info("Generating sunburst chart on MCP server...")
        try:
            tool_arguments = {"data_type": data_type}
            result = asyncio.run(call_mcp_tool(server_url, "generate_sunburst_chart", tool_arguments))
            
            if isinstance(result, dict) and result.get("status") == "success" and "chart_json" in result:
                import plotly.io as pio
                
                st.subheader(f"Generated Sunburst Chart: {result.get('data_type', 'Unknown')}")
                
                # Use plotly.io.from_json to properly parse the JSON
                fig = pio.from_json(result["chart_json"])
                st.plotly_chart(fig, use_container_width=True)
                
                # Add some helpful information
                st.markdown("""
                **💡 How to interact with the sunburst chart:**
                - Click on any segment to zoom into that hierarchy level
                - Click the center to zoom back out
                - Hover over segments to see detailed values
                - The color intensity represents the relative values
                """)
            else:
                st.error(f"Failed to generate sunburst chart: {result.get('message', 'Unknown error')}")
                
        except Exception as e:
            st.error(f"An error occurred: {e}")

    # Mermaid Diagram Section
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
                
                # Enhanced Mermaid rendering
                mermaid_html = render_mermaid_diagram(result["mermaid_code"])
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

def render_mermaid_diagram(mermaid_code: str, diagram_id: str = "mermaid-diagram"):
    """Enhanced Mermaid diagram rendering with proper JavaScript integration."""
    
    # Create unique ID for this diagram
    import hashlib
    unique_id = f"{diagram_id}-{hashlib.md5(mermaid_code.encode()).hexdigest()[:8]}"
    
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

if __name__ == "__main__":
    main()
