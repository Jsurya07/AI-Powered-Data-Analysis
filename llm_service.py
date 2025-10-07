
import os
import google.generativeai as genai

def get_available_models():
    """
    Get list of available Gemini models that support content generation.
    This ensures we always use a valid model.
    """
    try:
        available = []
        for model in genai.list_models():
            if 'generateContent' in model.supported_generation_methods:
                available.append(model.name.replace('models/', ''))
        return available
    except Exception as e:
        print(f"Warning: Could not fetch available models: {e}")
        return []

def select_best_model(preferred_model=None):
    """
    Automatically select the best available model with fallback strategy.
    Priority order: User preference > Latest stable > Flash > Pro > Any available
    """
    available_models = get_available_models()
    
    if not available_models:
        # Fallback to common model names if API call fails
        print("⚠️ Warning: Using fallback model list")
        return "gemini-2.0-flash"
    
    # Priority list of models to try (from fastest to most capable)
    priority_models = [
        preferred_model,  # User's preference from env variable
        "gemini-2.0-flash",  # Current stable fast model
        "gemini-2.5-flash",  # Newer fast model
        "gemini-flash-latest",  # Latest flash alias
        "gemini-2.0-flash-001",  # Specific version
        "gemini-2.5-pro",  # More capable
        "gemini-pro-latest",  # Latest pro alias
    ]
    
    # Try each model in priority order
    for model in priority_models:
        if model and model in available_models:
            print(f"✅ Selected model: {model}")
            return model
    
    # If none of the priority models are available, use the first available one
    if available_models:
        selected = available_models[0]
        print(f"⚠️ Using first available model: {selected}")
        return selected
    
    # Last resort fallback
    print("❌ Warning: No models found, using default")
    return "gemini-2.0-flash"

def get_llm_chain(model_name=None):
    """
    Initialize LLM chain with automatic model selection.
    You can override the model by setting GEMINI_MODEL in .env file.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    genai.configure(api_key=api_key)
    
    # Allow model override from environment variable
    env_model = os.getenv("GEMINI_MODEL")
    if env_model:
        print(f"📌 Using model from environment: {env_model}")
        model_name = env_model
    
    # Auto-select best available model if not specified
    if not model_name:
        model_name = select_best_model()
    else:
        # Verify the specified model is available
        available = get_available_models()
        if available and model_name not in available:
            print(f"⚠️ Warning: Model '{model_name}' not available, auto-selecting...")
            model_name = select_best_model()

    # Enhanced prompt template for better analysis
    template = """
CRITICAL: You MUST generate COMPLETE Python code that includes BOTH a text answer AND a visualization. 

You are a Python data analyst. You are given a dataset already loaded as a pandas DataFrame called `df` with the following columns: {columns}.

IMPORTANT: The DataFrame `df` is ALREADY loaded with the user's actual data. DO NOT create sample data or use pd.DataFrame() to create new data. Use the existing `df` variable directly.

Write Python code that answers: {question}

REQUIREMENTS:
1. Start with import statements (pandas, matplotlib, seaborn)
2. Write the complete Python code that finds the answer
3. ALWAYS print a clear, concise answer using print() - this is MANDATORY
4. ALWAYS create a relevant visualization - this is MANDATORY
5. The print statement should come BEFORE the visualization code
6. Do NOT print DataFrames, lists, or tables unless explicitly asked
7. For bar charts, always plot ALL data points unless the user specifically asks for a subset
8. Use plt.savefig('output.png', dpi=300, bbox_inches='tight') followed by plt.show()
9. Set figure size to (16, 10) for better readability with many categories
10. Use professional styling: plt.style.use('seaborn-v0_8')
11. Set font sizes: plt.rcParams['font.size'] = 10, plt.rcParams['axes.titlesize'] = 14
12. Use better colors: sns.set_palette("husl") or "viridis"
13. Add grid: plt.grid(True, alpha=0.3)
14. For many categories (>10): rotate x-axis labels by 90 degrees and adjust figure size
15. For very many categories (>20): show only top 20 and add note about others
16. Use tight_layout() for better spacing
17. For bar charts with many categories, consider horizontal orientation

EXAMPLE OUTPUT FORMAT:
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Find the maximum value (using the existing df DataFrame)
max_idx = df['SSC Percentage'].idxmax()
max_roll = df.loc[max_idx, 'Roll No']
max_ssc = df.loc[max_idx, 'SSC Percentage']
print(f"Roll No {{max_roll}} has the highest SSC percentage: {{max_ssc}}")

# Set up professional styling
plt.style.use('seaborn-v0_8')
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 14
sns.set_palette("husl")

# For many categories, use horizontal orientation
if len(df) > 10:
    plt.figure(figsize=(16, 10))
    # Sort by value and take top 20 if too many
    if len(df) > 20:
        top_data = df.nlargest(20, 'SSC Percentage')
        print(f"Showing top 20 out of {{len(df)}} entries")
    else:
        top_data = df
    
    # Horizontal bar chart for better readability
    sns.barplot(y='Roll No', x='SSC Percentage', data=top_data.sort_values('SSC Percentage', ascending=True))
    plt.title('SSC Percentage by Roll No (Top Entries)', fontweight='bold')
    plt.xlabel('SSC Percentage', fontweight='bold')
    plt.ylabel('Roll No', fontweight='bold')
else:
    plt.figure(figsize=(12, 8))
    sns.barplot(x='Roll No', y='SSC Percentage', data=df.sort_values('SSC Percentage', ascending=False))
    plt.title('SSC Percentage by Roll No', fontweight='bold')
    plt.xlabel('Roll No', fontweight='bold')
    plt.ylabel('SSC Percentage', fontweight='bold')
    plt.xticks(rotation=90)

plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('output.png', dpi=300, bbox_inches='tight')
plt.show()

REMEMBER: 
- ALWAYS print the answer first
- ALWAYS create a visualization
- Use the existing `df` DataFrame - DO NOT create sample data
- Generate COMPLETE working code
- For categorical data with many unique values (like country codes):
  * Use horizontal bar charts for better readability
  * Show only top 20 entries if there are more than 20 categories
  * Add a note about how many entries are being shown
  * Use larger figure size (16, 10) for many categories
  * Consider grouping small categories into "Others" if appropriate
"""

    # Return both the template and model name for use in generate_code_with_llm
    return template, model_name

def generate_code_with_llm(chain, columns, question):
    import re
    template, model_name = chain
    
    # Try with the specified model, fallback to auto-select if it fails
    max_retries = 2
    last_error = None
    llm_output = None
    
    for attempt in range(max_retries):
        try:
            # Format the prompt
            prompt_str = template.format(columns=", ".join(columns), question=question)
            
            # Call Gemini
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt_str)
            llm_output = response.text
            
            # If we get here, it worked!
            break
            
        except Exception as e:
            last_error = e
            error_msg = str(e)
            
            # Check if it's a model not found error
            if "404" in error_msg or "not found" in error_msg.lower():
                print(f"⚠️ Model '{model_name}' failed (attempt {attempt + 1}/{max_retries})")
                
                if attempt < max_retries - 1:
                    # Try to auto-select a different model
                    print("🔄 Attempting to auto-select a working model...")
                    model_name = select_best_model()
                    print(f"🔄 Retrying with model: {model_name}")
                    continue
                else:
                    print("❌ All retry attempts failed")
                    raise Exception(f"Model selection failed after {max_retries} attempts. Last error: {error_msg}")
            else:
                # For other errors, raise immediately
                print("LLM Error:", e)
                raise e
    
    if not llm_output:
        if last_error:
            raise last_error
        else:
            raise Exception("Failed to generate code - no output received")
    
    # Clean output: remove markdown/code fences, leading/trailing whitespace, and "python" prefix
    cleaned_code = llm_output.strip()
    
    # Remove markdown code blocks
    if cleaned_code.startswith("```python"):
        cleaned_code = cleaned_code[9:]  # Remove "```python"
    elif cleaned_code.startswith("```"):
        cleaned_code = cleaned_code[3:]  # Remove "```"
    
    if cleaned_code.endswith("```"):
        cleaned_code = cleaned_code[:-3]  # Remove trailing "```"
    
    # Remove "python" prefix if it exists
    if cleaned_code.startswith("python"):
        cleaned_code = cleaned_code[6:].strip()
    
    cleaned_code = cleaned_code.strip()

    # Keep plt.show() for Streamlit display, but also save the plot
    if "plt.savefig('output.png')" not in cleaned_code and "plt.show()" in cleaned_code:
        cleaned_code = cleaned_code.replace("plt.show()", "plt.savefig('output.png')\nplt.show()")
    elif "plt.savefig('output.png')" in cleaned_code and "plt.show()" not in cleaned_code:
        cleaned_code = cleaned_code.replace("plt.savefig('output.png')", "plt.savefig('output.png')\nplt.show()")

    # Fix common formatting artifacts (optional, add more as needed)
    cleaned_code = cleaned_code.replace(".2f} tons", "} tons")

    # Fix inplace operations (fillna, replace, dropna)
    inplace_patterns = [
        (r"(df\[[^\]]+\])\.fillna\(([^,]+),\s*inplace=True\)", r"\1 = \1.fillna(\2)"),
        (r"(df\[[^\]]+\])\.replace\(([^,]+),\s*inplace=True\)", r"\1 = \1.replace(\2)"),
        (r"(df\[[^\]]+\])\.dropna\(([^)]*),?\s*inplace=True\)", r"\1 = \1.dropna(\1)")
    ]
    for pattern, replacement in inplace_patterns:
        cleaned_code = re.sub(pattern, replacement, cleaned_code)

    return cleaned_code