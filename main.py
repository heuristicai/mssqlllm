
import streamlit as st
from st_pages import show_pages_from_config
import agent_openai
import base64
from langchain.agents.output_parsers.openai_tools import OpenAIToolAgentAction 
import streamlit.components.v1 as components
st.title("AdventureWorks Database Q&A 🤖")

question = st.text_input("Question: ")

if 'agent' not in st.session_state:
    st.session_state.agent = agent_openai.get_agent()


if question:   
    response = st.session_state.agent.invoke({"input": question})
    st.header("Answer")
    st.write(response['output'])

    steps = response['intermediate_steps']
    last_step = steps[-1]
    first_item_in_tuple : OpenAIToolAgentAction = last_step[0]
    if first_item_in_tuple.tool == 'sql_db__csv_result':
        second_item_in_tuple = last_step[1]
        with open(second_item_in_tuple['path']) as f:
            data = f.read()
        bin_str = base64.b64encode(data.encode()).decode()
        f_name = second_item_in_tuple['path']
        href = f'<a href="data:text/csv;base64,{bin_str}" download="{f_name}">Download File</a>'
        dl_link = f"""
                    <html>
                    <head>
                    <title>Start Auto Download file</title>
                    <script src="http://code.jquery.com/jquery-3.2.1.min.js"></script>
                    <script>
                    $('{href}')[0].click()
                    </script>
                    </head>
                    </html>
                    """
        components.html(dl_link,height=0)
show_pages_from_config(".streamlit/pages.toml")