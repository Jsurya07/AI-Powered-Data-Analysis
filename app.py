import streamlit as st
import pandas as pd
import subprocess
import os
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory


llm = Ollama(model="llama3")

st.title("📊 LLM-Powered Data Analyst (LangChain + Ollama)")


uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    df.to_csv("dataset.csv", index=False)

    st.success("✅ File uploaded and loaded successfully!")
    st.subheader("Dataset Preview")
    st.dataframe(df.head())
    st.info(f"Available columns: {', '.join(df.columns)}")

  
    for col in df.columns:
        if df[col].dtype in ['float64', 'int64']:
            df[col].fillna(df[col].mean(), inplace=True)
        else:
            df[col].fillna(df[col].mode()[0], inplace=True)

    st.subheader("Processed Dataset Preview")
    st.dataframe(df.head())

  
    if 'memory' not in st.session_state:
        st.session_state.memory = ConversationBufferMemory(
            memory_key="chat_history",
            input_key="question",
            return_messages=True
        )


    user_question = st.text_input("Ask a question about the dataset")

    if user_question:
        # Step 6: Prompt Template
        template = """
IMPORTANT: Return ONLY valid Python code. Do NOT include any explanations, comments, or preamble before or after the code.

You are a Python data analyst.

Given a dataset saved as dataset.csv with the following columns: {columns}, 
your task is to write Python code using pandas, matplotlib, seaborn, and other necessary libraries 
to answer the following question:

Question: {question}

Instructions:
- Return ONLY Python code (no text, markdown, or explanation).
- Strictly NO PREAMBLE give only python code
- Only use columns that exist in the dataset and check for their existence before using them.
- Handle non-numeric values gracefully when doing numeric operations.
- Always load the data using: dataset.csv
- Only give the exact python code for the user question.
- Use `.reset_index()` only after `groupby` operations.
- Do NOT use `.reset_index()` on scalar results like `.mean()` or `.max()` applied directly on a column.
- The output must:
  1. Import all necessary libraries.
  2. Include a visualization (matplotlib/seaborn).
  3. Print the relevant output.
  4. Save plots as output.png
  5. Ensure the plots are clean, with readable labels, appropriate figsize, xticks rotation if needed, and use plt.tight_layout() to avoid clutter.
  6. Be robust and dynamic.
"""

        prompt = PromptTemplate(
            input_variables=["columns", "question"],
            template=template
        )

        
        chain = LLMChain(
            llm=llm,
            prompt=prompt,
            memory=st.session_state.memory,
            verbose=True
        )


        llm_output = chain.run({
            "columns": ", ".join(df.columns),
            "question": user_question
        })

        cleaned_code = llm_output.strip().strip("`").strip("`").strip()
        cleaned_code = cleaned_code.replace("plt.show()", "plt.savefig('output.png')")
        cleaned_code = cleaned_code.replace(".2f} tons", "} tons")

        st.subheader("Generated Python Code")
        st.code(cleaned_code)

        with open("fixed_script.py", "w") as file:
            file.write(cleaned_code)


        if st.button("Run Code"):
            result = subprocess.run(["python3", "fixed_script.py"], capture_output=True, text=True)

            if result.stdout:
                st.subheader("Execution Output:")
                st.text(result.stdout)

            if os.path.exists("output.png"):
                st.subheader("Generated Plot:")
                st.image("output.png")

            if result.stderr:
                st.subheader("Execution Errors:")
                st.text(result.stderr)

 
      
