
import streamlit as st
import os

def display_results():
    # Check if there's any output from the execution
    if os.path.exists("output.png"):
        st.subheader("Generated Plot:")
        st.image("output.png")
    
    # Read the execution output and display it
    with open("execution_output.txt", "r") as file:
        result = file.read()
        st.subheader("Execution Output:")
        st.text(result)
