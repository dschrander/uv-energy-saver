import streamlit as st

def apply_custom_styles():
    st.markdown("""
        <style>
        .stButton > button {
            width: 100%;
            border-radius: 5px;
            height: 3em;
            background-color: #0066cc;
        }
        .stTextInput > div > div > input {
            background-color: #f8f9fa;
        }
        .industrial-header {
            background-color: #2c3e50;
            padding: 1rem;
            border-radius: 5px;
            color: white;
            margin-bottom: 2rem;
        }
        .info-box {
            background-color: #e9ecef;
            padding: 1rem;
            border-radius: 5px;
            margin: 1rem 0;
        }
        </style>
    """, unsafe_allow_html=True)

