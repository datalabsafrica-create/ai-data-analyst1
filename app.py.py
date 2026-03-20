import streamlit as st
import pandas as pd
import plotly.express as px
import openai
import streamlit_authenticator as stauth

# --- 1. USER AUTHENTICATION SETUP ---
# In a real app, you would store these in a database or a config file
names = ["Admin User", "Analyst User"]
usernames = ["admin", "analyst"]
# Passwords must be hashed. For this demo, I'm using pre-hashed versions of 'admin123' and 'data2024'
passwords = ["admin123", "data2024"] 

# Hash the passwords (this is required for security)
hashed_passwords = stauth.Hasher(passwords).generate()

credentials = {"usernames":{}}

for un, name, pw in zip(usernames, names, hashed_passwords):
    user_dict = {"name":name,"password":pw}
    credentials["usernames"][un] = user_dict

# Create the authenticator object
authenticator = stauth.Authenticate(
    credentials,
    "data_app_cookie", # Cookie name
    "signature_key",   # Cookie key
    cookie_expiry_days=30
)

# Render the login widget
name, authentication_status, username = authenticator.login("Login", "main")

# --- 2. CHECK AUTHENTICATION ---
if authentication_status == False:
    st.error("Username/password is incorrect")

elif authentication_status == None:
    st.warning("Please enter your username and password")

elif authentication_status:
    # --- START OF YOUR ACTUAL APP ---
    with st.sidebar:
        st.title(f"Welcome, {name}")
        authenticator.logout("Logout", "sidebar")
        st.divider()
        
        st.header("1. Setup")
        api_key = st.text_input("Enter OpenAI API Key", type="password")
        
        st.header("2. Upload Data")
        uploaded_file = st.file_uploader("Choose a CSV or Excel file", type=["csv", "xlsx"])

    # App Title
    st.title("📊 AI Dataset Analysis Dashboard")

    if uploaded_file:
        # Load Data
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        # Tabs logic
        tab1, tab2, tab3, tab4 = st.tabs(["📋 Data Overview", "🛠️ Auto-Clean", "📈 Visualizations", "🤖 AI Assistant"])

        with tab1:
            st.subheader("Raw Data Preview")
            st.dataframe(df.head(10), use_container_width=True)
            col1, col2, col3 = st.columns(3)
            col1.metric("Rows", df.shape[0])
            col2.metric("Columns", df.shape[1])
            col3.metric("Missing", df.isna().sum().sum())

        with tab2:
            st.subheader("Data Cleaning")
            if st.button("Auto-Clean Data"):
                df = df.drop_duplicates()
                st.success("Cleaned!")

        with tab3:
            st.subheader("Visualizations")
            cols = df.columns.tolist()
            x_axis = st.selectbox("X Axis", cols)
            y_axis = st.selectbox("Y Axis", cols)
            fig = px.bar(df, x=x_axis, y=y_axis)
            st.plotly_chart(fig, use_container_width=True)

        with tab4:
            st.subheader("AI Insight")
            user_question = st.text_input("Ask a question about your data")
            if user_question and api_key:
                openai.api_key = api_key
                # (Same AI logic as before...)
                st.info("AI is processing...")
                # Simplified for demo
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": f"Analyze this columns: {df.columns.tolist()}. Question: {user_question}"}]
                )
                st.write(response.choices[0].message.content)

    else:
        st.info("Waiting for file upload...")

# --- END OF APP ---