import streamlit as st
import few_shots_helper
import vectorstore_helper
# Set page width
st.set_page_config(layout='wide')
st.title("Few Shot Prompt Instant Training")

def get_data():
    df = few_shots_helper.get_few_shots_df()
    return df

with st.form("my_form"):

    edited_df = st.data_editor(get_data(), column_order=("Question","SQLQuery"), num_rows="dynamic")
    submitted = st.form_submit_button("Update Training Set")

if submitted:
    st.write("Edited dataframe:", edited_df)
    few_shots_helper.update_few_shots(edited_df)
    vectorstore_helper.add_new_items(edited_df)
    if 'agent' in st.session_state: 
        del st.session_state['agent']
