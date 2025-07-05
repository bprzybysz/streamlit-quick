Looking at your Streamlit MCP client code, I've identified several issues preventing the Plotly chart and log table from displaying properly. Here are the problems and their fixes:

## **Issue 1: Chart JSON Parsing Error**

The main problem is in the pie chart generation section. The code expects `chart_html` in the result but the MCP server returns `chart_json`[1]. Additionally, there's a mismatch in the JSON parsing logic.

**Fix the chart display logic:**

```python
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
        
        if isinstance(result, str):
            st.error(result)
        else:
            # Fix: Check for chart_json instead of chart_html
            if result.get("status") == "success" and "chart_json" in result:
                import plotly.graph_objects as go
                import json
                
                st.subheader("Generated Pie Chart")
                # Fix: Parse the JSON string properly
                chart_data = json.loads(result["chart_json"])
                fig = go.Figure(chart_data)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.error(f"Failed to generate pie chart: {result.get('message', 'Unknown error')}")
    except ValueError:
        st.error("Please enter valid numbers for chart values.")
    except Exception as e:
        st.error(f"An error occurred: {e}")
```

## **Issue 2: Log Table Data Structure**

The log table display logic has a potential issue with the data structure handling[1].

**Fix the log table display:**

```python
if st.button("Get Log Table"):
    st.info("Fetching log table from MCP server...")
    try:
        result = asyncio.run(call_mcp_tool(server_url, "get_logs_table", {}))
        
        if isinstance(result, str):
            st.error(result)
        else:
            st.json(result)  # Show raw result for debugging
            
            # Fix: Better handling of the result structure
            if isinstance(result, dict) and result.get("status") == "success" and "data" in result:
                st.subheader("Log Table")
                # Convert to DataFrame for better display
                import pandas as pd
                df = pd.DataFrame(result["data"])
                st.dataframe(df, use_container_width=True)
            else:
                st.error(f"Failed to get log table: {result}")
    except Exception as e:
        st.error(f"An error occurred: {e}")
```

## **Issue 3: MCP Server Response Handling**

The `call_mcp_tool` function might not be returning the expected data structure[1].

**Improve the MCP tool calling function:**

```python
async def call_mcp_tool(server_url: str, tool_name: str, tool_arguments: dict) -> dict:
    """
    Connects to the MCP server, calls a specified tool, and returns the result.
    """
    try:
        async with Client(server_url) as client:
            result = await client.call_tool(tool_name, tool_arguments)
            # Return the actual result content, not just structured_content
            if hasattr(result, 'content') and result.content:
                # Try to parse JSON if it's a string
                if isinstance(result.content, str):
                    try:
                        return json.loads(result.content)
                    except json.JSONDecodeError:
                        return {"status": "error", "message": result.content}
                return result.content
            elif hasattr(result, 'structured_content'):
                return result.structured_content
            else:
                return {"status": "error", "message": "No content in result"}
    except Exception as e:
        return {"status": "error", "message": f"Error calling MCP tool: {e}"}
```

## **Issue 4: Missing Import**

Add the missing JSON import at the top of your file:

```python
import streamlit as st
import asyncio
import json  # Add this import
from fastmcp.client import Client
```

## **Complete Fixed Version**

Here's the corrected section of your `streamlit_receiver.py`:

```python
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
            result = await client.call_tool(tool_name, tool_arguments)
            if hasattr(result, 'content') and result.content:
                if isinstance(result.content, str):
                    try:
                        return json.loads(result.content)
                    except json.JSONDecodeError:
                        return {"status": "error", "message": result.content}
                return result.content
            elif hasattr(result, 'structured_content'):
                return result.structured_content
            else:
                return {"status": "error", "message": "No content in result"}
    except Exception as e:
        return {"status": "error", "message": f"Error calling MCP tool: {e}"}

def main():
    st.title("Streamlit MCP Client")
    st.write("Interact with an MCP server by calling a tool.")

    server_url = st.text_input("MCP Server URL", "http://localhost:8000/mcp/")
    
    # ... (rest of your existing code until the log table section)
    
    if st.button("Get Log Table"):
        st.info("Fetching log table from MCP server...")
        try:
            result = asyncio.run(call_mcp_tool(server_url, "get_logs_table", {}))
            
            if isinstance(result, dict) and result.get("status") == "success" and "data" in result:
                st.subheader("Log Table")
                import pandas as pd
                df = pd.DataFrame(result["data"])
                st.dataframe(df, use_container_width=True)
            else:
                st.error(f"Failed to get log table: {result}")
        except Exception as e:
            st.error(f"An error occurred: {e}")

    # ... (chart generation section with fixes as shown above)
```

These fixes should resolve the display issues with both the Plotly chart and log table in your Streamlit application[2][3].

Citations:
[1] [repomix-output.xml](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/8768170/5bb866a4-1cdb-498b-8a6e-c2f2f4d18b72/repomix-output.xml)  
[2] [st.plotly_chart - Streamlit Docs](https://docs.streamlit.io/develop/api-reference/charts/st.plotly_chart)  
[3] [st.dataframe - Streamlit Docs](https://docs.streamlit.io/develop/api-reference/data/st.dataframe)  
[4] [Streamlit and Plotly: Interactive Data Visualization Made Easy](https://docs.kanaries.net/topics/Streamlit/streamlit-plotly)  
[5] [How to display tabular data using streamlit -](https://www.projectpro.io/recipes/display-tabular-data-streamlit)  
[6] [Displaying Tables in Streamlit | Evidence Learn](https://evidence.dev/learn/streamlit-table)  
[7] [Generating Plotly Charts in Streamlit](https://www.youtube.com/watch?v=KmcoofohV64)  
[8] [Develop a dashboard app with streamlit using plotly](https://discuss.streamlit.io/t/develop-a-dashboard-app-with-streamlit-using-plotly/37148)  
[9] [Adding Interactive Plotly Charts to a Streamlit App](https://www.youtube.com/watch?v=3f-j-PZ5N8A)  
[10] [Plotly barplot not rendering fine in streamlit app](https://stackoverflow.com/questions/70883942/plotly-barplot-not-rendering-fine-in-streamlit-app)  
[11] [Streamlit DataFrame: Displaying, Styling, and Optimizing Pandas ...](https://docs.kanaries.net/topics/Streamlit/streamlit-dataframe)  
[12] [How to put a Plotly graph inside a box shape?](https://discuss.streamlit.io/t/how-to-put-a-plotly-graph-inside-a-box-shape/40093)  
[13] [Plotly chart render fail - Using Streamlit](https://discuss.streamlit.io/t/plotly-chart-render-fail/22405)  
[14] [Dataframe display - Using Streamlit](https://discuss.streamlit.io/t/dataframe-display/36686)  
[15] [How to display charts using plotly library in Streamlit](https://www.projectpro.io/recipes/display-charts-plotly-library-streamlit)  
[16] [Why is streamlit messing up my Plotly chart?](https://stackoverflow.com/questions/76546838/why-is-streamlit-messing-up-my-plotly-chart)  
[17] [Displaying local images inside a streamlit dataframe](https://discuss.streamlit.io/t/displaying-local-images-inside-a-streamlit-dataframe/80077)  
[18] [Streamlit theme for Plotly charts!](https://plotly.streamlit.app)  
[19] [Streamlit dataframe Function: Display Data Effortlessly (Session 3)](https://www.youtube.com/watch?v=SWxq4j9qJZs)  
[20] [Plotly image not showing on Streamlit](https://discuss.streamlit.io/t/plotly-image-not-showing-on-streamlit/27950)  
[21] [Maintaining the display of a dataframe in Streamlit - Stack Overflow](https://stackoverflow.com/questions/72507487/maintaining-the-display-of-a-dataframe-in-streamlit)