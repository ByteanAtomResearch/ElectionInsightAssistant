import openai
import time
import streamlit as st
import pandas as pd
import plotly.express as px

def initialize_client():
    """Initialize the OpenAI client with an API key."""
    if 'client' not in st.session_state:
        st.session_state.client = openai.OpenAI(api_key=st.secrets["openai_secret_key"])

def create_assistant():
    pass

def create_thread():
    """Create a thread for the OpenAI Assistant if not already present."""
    if 'thread' not in st.session_state:
        st.session_state.thread = st.session_state.client.beta.threads.create()

def data_upload():
    """Allow users to upload CSV or Excel files and load the data."""
    uploaded_file = st.file_uploader("Choose your CSV or Excel file")
    if uploaded_file is not None:
        # Determine the file format from the uploaded file
        file_type = uploaded_file.type
        
        # Process CSV files
        if 'csv' in file_type:
            data = pd.read_csv(uploaded_file)
        
        # Process Excel files
        elif 'excel' in file_type or 'spreadsheetml' in file_type:
            data = pd.read_excel(uploaded_file)
        
        # Return the loaded data
        return data
    
    # If no file is uploaded, return None
    return None


def interactive_visualizations(data):
    """Provide interactive visualizations for the uploaded data."""
    if data is not None:
        st.subheader("Interactive Visualizations")
        chart_type = st.selectbox("Select the type of chart:", ["Bar Chart", "Line Chart", "Histogram", "Pie Chart"])
        columns = data.columns.tolist()
        if chart_type in ["Bar Chart", "Line Chart", "Histogram"]:
            x_axis = st.selectbox("Select the X-axis:", columns)
            if chart_type != "Histogram":
                y_axis = st.selectbox("Select the Y-axis:", columns, index=1)
            if chart_type == "Bar Chart":
                fig = px.bar(data, x=x_axis, y=y_axis)
            elif chart_type == "Line Chart":
                fig = px.line(data, x=x_axis, y=y_axis)
            elif chart_type == "Histogram":
                fig = px.histogram(data, x=x_axis)
            st.plotly_chart(fig)
        elif chart_type == "Pie Chart":
            name_column = st.selectbox("Select the column for names:", columns)
            fig = px.pie(data, names=name_column)
            st.plotly_chart(fig)

def analyze_query(user_query, assistant_id):
    """Analyze the user's query using the OpenAI Assistant."""
    if user_query:  # Ensure there's a query to analyze
        with st.spinner("Processing your query..."):
            st.session_state.client.beta.threads.messages.create(
                thread_id=st.session_state.thread.id,
                assistant_id=assistant_id,
                role="user",
                content=user_query
            )
            time.sleep(3)  # Simulate processing time
            display_response()

def display_response():
    """Display the response from the OpenAI Assistant."""
    messages = st.session_state.client.beta.threads.messages.list(
        thread_id=st.session_state.thread.id
    )
    for msg in messages.data:
        if msg.role == "assistant":
            st.write(f"Assistant: {msg.content[0].text.value}")

def main():
    st.title("Election Data Analysis Assistant")
    initialize_client()
    assistant_id = "asst_xxxxxxxxxxxxxxxxxxxx"
    create_thread()
    #interactive_visualizations()

    data = data_upload()
    if data is not None:
        st.write("Uploaded Data:", data)
        interactive_visualizations(data)

    user_query = st.text_input("Enter your query about the election data:")
    if st.button('Analyze'):
        analyze_query(user_query, assistant_id)

    st.sidebar.header("Help and Guidelines")
    st.sidebar.info(
        "For your election analysis, enter your election data such as:\n"
        "- Total number of registered voters\n"
        "- Total votes cast\n"
        "- Total valid votes cast\n"
        "- Total rejected ballots\n"
        "- % turnout\n"
        "- % of total votes due to rejected ballots"
    )

if __name__ == "__main__":
    main()
