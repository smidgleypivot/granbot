import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

"""
# A simple Chtbot App
"""



st.caption("A simple streamlit app that generates a spiral -updated to check deployment mechanism")


st.header("Chatbot")
user_input = st.text_input("Say something")
if st.button("Send"):
    st.write(f"Bot: You said '{user_input}'")