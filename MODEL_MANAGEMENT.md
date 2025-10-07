# 🤖 Gemini Model Management Guide

## 🎯 Problem Solved: Future-Proof Model Selection

Your application now has **automatic model selection** with fallback strategies to prevent future model deprecation issues.

---

## ✨ What Changed?

### **Before (Old System)**
```python
def get_llm_chain(model_name="gemini-pro"):  # ❌ Hardcoded, can become outdated
    # No fallback mechanism
    # Would fail if model is deprecated
```

### **After (New System)**
```python
def get_llm_chain(model_name=None):  # ✅ Auto-selects best available model
    # ✅ Checks available models dynamically
    # ✅ Has fallback strategy
    # ✅ Can be overridden via environment variable
```

---

## 🔧 How It Works

### **1. Automatic Model Discovery**
The system queries Google's API to get a list of all available models:
```python
def get_available_models():
    # Fetches current list of models from Google
    # Returns only models that support content generation
```

### **2. Smart Model Selection**
Priority order (from fastest to most capable):
1. **User preference** (from `GEMINI_MODEL` env variable)
2. `gemini-2.0-flash` (current stable)
3. `gemini-2.5-flash` (newer)
4. `gemini-flash-latest` (always latest flash)
5. `gemini-2.5-pro` (most capable)
6. `gemini-pro-latest` (always latest pro)
7. **First available model** (if none of above exist)

### **3. Automatic Retry with Fallback**
If a model fails (404 error):
- ✅ Automatically tries another model
- ✅ Logs the issue for debugging
- ✅ Retries up to 2 times
- ✅ Only fails if all models are unavailable

---

## 🎮 How to Use

### **Option 1: Let It Auto-Select (Recommended)**
Do nothing! The system will automatically choose the best available model.

```bash
# No configuration needed
docker-compose up -d
```

### **Option 2: Specify Your Preferred Model**
Add to your `.env` file:

```env
# Use a specific model
GEMINI_MODEL=gemini-2.5-pro
```

Available models (as of now):
- `gemini-2.0-flash` - Fast, stable (default)
- `gemini-2.5-flash` - Newer, faster
- `gemini-2.5-pro` - Most powerful
- `gemini-flash-latest` - Always uses latest flash model
- `gemini-pro-latest` - Always uses latest pro model

### **Option 3: Check Available Models**
Run this command to see all available models:

```bash
docker exec fastapi python -c "
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

print('Available models:')
for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f'  - {model.name.replace(\"models/\", \"\")}')"
```

---

## 🛡️ Protection Against Future Deprecation

### **What Happens When a Model is Deprecated?**

**Scenario**: Google deprecates `gemini-2.0-flash` in 3 months

**Old System**: ❌ Your app breaks completely
```
Error: 404 models/gemini-2.0-flash is not found
```

**New System**: ✅ Your app continues working
```
⚠️ Model 'gemini-2.0-flash' failed (attempt 1/2)
🔄 Attempting to auto-select a working model...
✅ Selected model: gemini-2.5-flash
🔄 Retrying with model: gemini-2.5-flash
✅ Success!
```

---

## 📊 Model Comparison

| Model | Speed | Capability | Cost | Best For |
|-------|-------|------------|------|----------|
| `gemini-2.0-flash` | ⚡⚡⚡ | ⭐⭐⭐ | 💰 | General use (default) |
| `gemini-2.5-flash` | ⚡⚡⚡ | ⭐⭐⭐⭐ | 💰 | Newer, better quality |
| `gemini-2.5-pro` | ⚡⚡ | ⭐⭐⭐⭐⭐ | 💰💰 | Complex analysis |
| `gemini-flash-latest` | ⚡⚡⚡ | ⭐⭐⭐⭐ | 💰 | Always latest (auto-updates) |
| `gemini-pro-latest` | ⚡⚡ | ⭐⭐⭐⭐⭐ | 💰💰 | Always latest pro (auto-updates) |

---

## 🔍 Monitoring & Debugging

### **Check Which Model is Being Used**
Look at the FastAPI logs:
```bash
docker logs fastapi | grep "Selected model"
```

Output:
```
✅ Selected model: gemini-2.0-flash
```

### **Check for Model Fallbacks**
```bash
docker logs fastapi | grep -E "(⚠️|🔄)"
```

### **Test Model Selection**
```bash
docker exec fastapi python -c "
from llm_service import select_best_model
print('Best available model:', select_best_model())"
```

---

## 🚨 Troubleshooting

### **Issue: "No models found"**
**Cause**: API key invalid or network issue

**Solution**:
1. Check your API key in `.env`
2. Verify internet connection
3. Check Google API status

### **Issue: "All retry attempts failed"**
**Cause**: All models are unavailable (rare)

**Solution**:
1. Check Google Gemini API status
2. Verify your API key has access
3. Try specifying a different model in `.env`

### **Issue: Slow response times**
**Cause**: Using a powerful but slow model

**Solution**:
```env
# Switch to faster model
GEMINI_MODEL=gemini-2.0-flash
```

---

## 📝 Best Practices

### **1. Use Aliases for Future-Proofing**
```env
# ✅ Good - Always uses latest
GEMINI_MODEL=gemini-flash-latest

# ❌ Avoid - Specific version may be deprecated
GEMINI_MODEL=gemini-2.0-flash-001
```

### **2. Monitor Logs Regularly**
Check for deprecation warnings:
```bash
docker logs fastapi | grep -i "deprecat"
```

### **3. Test After Google Updates**
When Google announces new models:
```bash
# 1. Check available models
docker exec fastapi python -c "from llm_service import get_available_models; print(get_available_models())"

# 2. Restart services
docker-compose restart

# 3. Test with a query
```

### **4. Keep Dependencies Updated**
Update `google-generativeai` package periodically:
```bash
# Update requirements.txt
google-generativeai>=0.8.3  # Change to latest version

# Rebuild containers
docker-compose build --no-cache
docker-compose up -d
```

---

## 🎓 Understanding the Code

### **Key Functions**

#### `get_available_models()`
- Queries Google API for current models
- Filters for models that support content generation
- Returns list of model names

#### `select_best_model(preferred_model=None)`
- Takes optional preferred model
- Checks against available models
- Returns best available model from priority list

#### `get_llm_chain(model_name=None)`
- Initializes LLM with selected model
- Checks environment variable override
- Validates model availability

#### `generate_code_with_llm(chain, columns, question)`
- Generates code using selected model
- Automatically retries with different model if 404 error
- Returns cleaned Python code

---

## 📚 Additional Resources

- [Google Gemini API Documentation](https://ai.google.dev/docs)
- [Model Versions & Updates](https://ai.google.dev/models/gemini)
- [API Pricing](https://ai.google.dev/pricing)

---

## ✅ Summary

**Your application is now future-proof!**

- ✅ Automatically selects best available model
- ✅ Falls back if primary model fails
- ✅ Can be overridden via environment variable
- ✅ Logs all model selection decisions
- ✅ Retries with different models on failure
- ✅ No more manual updates needed when models change

**You won't face the same issue again!** 🎉
