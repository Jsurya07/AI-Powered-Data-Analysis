import streamlit as st
import pandas as pd
import os
import requests
from ui_components import (
    load_css, set_theme, apply_color_scheme, display_data_profiling,
    display_download_section, display_analytics_templates, display_automl_section,
    display_dataset_switcher, load_dataset_from_history, toggle_favorite, delete_dataset
)
from data_processing import (
    load_dataset, generate_code_with_llm, execute_generated_code,
    clean_generated_code, validate_dataset, get_dataset_statistics
)

# Page configuration
st.set_page_config(
    page_title="AI-Powered Data Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load CSS and set theme
load_css()
set_theme()

# Constants
UPLOAD_DIR = "uploaded_datasets"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Initialize session state
if 'df' not in st.session_state:
    st.session_state.df = None
if 'current_dataset' not in st.session_state:
    st.session_state.current_dataset = None

def main():
    """Main application function"""
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🤖 AI-Powered Data Analysis</h1>
        <p>Upload your dataset and ask questions in natural language!</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Theme Settings
        with st.expander("🎨 Theme Settings", expanded=False):
            st.session_state.theme = st.selectbox(
                "Theme:",
                ["light", "dark"],
                index=0 if st.session_state.theme == "light" else 1
            )
            
            st.session_state.color_scheme = st.selectbox(
                "Color Scheme:",
                ["default", "ocean", "sunset", "forest"],
                index=["default", "ocean", "sunset", "forest"].index(st.session_state.color_scheme)
            )
        
        # Plot Settings
        with st.expander("📊 Plot Settings", expanded=False):
            st.session_state.max_data_points = st.slider(
                "Max Data Points:",
                min_value=10,
                max_value=1000,
                value=100,
                step=10
            )
            
            st.session_state.auto_rotate_labels = st.checkbox(
                "Auto-rotate Labels",
                value=True
            )
        
        # Dataset Switcher
        display_dataset_switcher()
        
        # Analytics Templates
        display_analytics_templates(st.session_state.df if st.session_state.df is not None else pd.DataFrame())
        
        # AutoML Section
        display_automl_section(st.session_state.df if st.session_state.df is not None else pd.DataFrame())
        
        # Current Dataset Display
        if st.session_state.current_dataset:
            st.markdown("---")
            st.markdown("🎯 **Current Dataset:**")
            st.write(f"📄 {os.path.basename(st.session_state.current_dataset)}")
            if st.session_state.df is not None:
                st.write(f"📊 {len(st.session_state.df)} rows, {len(st.session_state.df.columns)} columns")
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # File upload
        uploaded_file = st.file_uploader(
            "📁 Upload your dataset (CSV, Excel)",
            type=['csv', 'xlsx', 'xls']
        )
        
        if uploaded_file is not None:
            # Save uploaded file
            file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Load dataset
            df = load_dataset(file_path)
            if df is not None:
                st.session_state.df = df
                st.session_state.current_dataset = file_path
                
                # Log to database
                try:
                    response = requests.post(
                        "http://fastapi:8000/log_dataset/",
                        json={
                            "filename": uploaded_file.name,
                            "file_path": file_path,
                            "rows": len(df),
                            "columns": len(df.columns)
                        }
                    )
                except Exception as e:
                    st.warning(f"Could not log dataset: {str(e)}")
                
                st.success(f"✅ Dataset loaded successfully! {len(df)} rows, {len(df.columns)} columns")
            else:
                st.error("❌ Error loading dataset")
    
    with col2:
        # Dataset info
        if st.session_state.df is not None:
            st.markdown("### 📊 Dataset Info")
            info = validate_dataset(st.session_state.df)
            
            st.metric("Rows", info["rows"])
            st.metric("Columns", info["columns"])
            
            # Show first few rows
            st.markdown("### 📋 Preview")
            st.dataframe(st.session_state.df.head(), use_container_width=True)
    
    # Main analysis section
    if st.session_state.df is not None:
        st.markdown("---")
        
        # Data Profiling
        display_data_profiling(st.session_state.df)
        
        # Ask questions section
        st.markdown("### 🤔 Ask a Question About Your Data")
        user_question = st.text_input(
            "Enter your question:",
            placeholder="e.g., What is the average age? Which category has the highest sales?"
        )
        
        cleaned_code = None
        
        if user_question:
            # Get API key from environment
            api_key = os.getenv('GOOGLE_API_KEY')
            if not api_key:
                st.error("❌ Google API key not found. Please set GOOGLE_API_KEY environment variable.")
                return
            
            # Generate code
            columns = ", ".join(st.session_state.df.columns)
            result = generate_code_with_llm(user_question, columns, api_key)
            
            if "error" in result:
                st.error(f"❌ {result['error']}")
            else:
                cleaned_code = clean_generated_code(result.get("code", ""))
                
                # Display generated code
                with st.expander("🔍 Generated Code", expanded=False):
                    st.code(cleaned_code, language="python")
                
                # Execute code
                if st.button("🚀 Execute Code"):
                    with st.spinner("Executing code..."):
                        execution_result = execute_generated_code(cleaned_code, st.session_state.df)
                        
                        if execution_result["success"]:
                            st.success("✅ Code executed successfully!")
                            
                            # Display plot if generated
                            if os.path.exists('output.png'):
                                st.image('output.png', caption="Generated Plot", use_column_width=True)
                        else:
                            st.error(f"❌ Execution failed: {execution_result['error']}")
        
        # Download section
        display_download_section(st.session_state.df, cleaned_code)
    
    else:
        # Welcome message
        st.markdown("""
        <div class="info-box">
            <h3>👋 Welcome to AI-Powered Data Analysis!</h3>
            <p>To get started:</p>
            <ol>
                <li>📁 Upload your dataset (CSV or Excel file)</li>
                <li>🤔 Ask questions about your data in natural language</li>
                <li>📊 Explore insights with interactive visualizations</li>
                <li>🤖 Try AutoML for predictive analytics</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 