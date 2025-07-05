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

if __name__ == "__main__":
    main()
