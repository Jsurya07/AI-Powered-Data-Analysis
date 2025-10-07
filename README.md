# 🤖 AI-Powered Data Analysis

A comprehensive, containerized data analysis platform that combines the power of AI with professional data science tools. Upload datasets, ask questions in natural language, and get instant insights with beautiful visualizations.

## ✨ Features

### 🚀 Core Capabilities
- **📁 Dataset Upload** - Support for CSV and Excel files
- **🔍 Advanced Data Profiling** - Comprehensive dataset analysis
- **🧹 Missing Values Handling** - Smart data cleaning with multiple strategies
- **🤔 Natural Language Queries** - Ask questions in plain English
- **📊 Interactive Visualizations** - Professional plots and charts
- **📋 Analytics Templates** - Pre-built analysis workflows
- **💾 Dataset Management** - Save, load, and manage datasets
- **📥 Export Results** - Download cleaned data, plots, and code

### 🎨 User Experience
- **🌙 Dark Theme** - Modern, professional interface
- **📱 Responsive Design** - Works on all devices
- **⚡ Real-time Processing** - Instant results and feedback
- **🔄 Interactive Workflow** - Iterative analysis process

### 🔧 Technical Features
- **🐳 Docker Containerized** - Easy deployment and scaling
- **🔌 Microservices Architecture** - FastAPI backend + Streamlit frontend
- **🗄️ PostgreSQL Database** - Persistent data storage
- **🤖 Google Gemini AI** - Advanced code generation
- **📈 Professional Plotting** - Matplotlib, Seaborn, Plotly

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamlit     │    │    FastAPI      │    │   PostgreSQL    │
│   Frontend      │◄──►│    Backend      │◄──►│   Database      │
│   (Port 8501)   │    │   (Port 8000)   │    │   (Port 5432)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │
         │                       │
         ▼                       ▼
┌─────────────────┐    ┌─────────────────┐
│   Google        │    │   Docker        │
│   Gemini AI     │    │   Compose       │
└─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Google API Key for Gemini AI

### 1. Clone the Repository
```bash
git clone <repository-url>
cd AI-Powered-Data-Analysis
```

### 2. Set Environment Variables
Create a `.env` file in the root directory:
```env
GOOGLE_API_KEY=your_google_api_key_here
DATABASE_URL=postgresql://user:password@postgres:5432/data_analysis
```

### 3. Start the Application
```bash
docker-compose up -d
```

### 4. Access the Application
Open your browser and navigate to:
- **Main Application**: http://localhost:8501
- **API Documentation**: http://localhost:8000/docs

## 📖 Usage Guide

### 1. Upload Your Dataset
- Click "Browse files" to upload CSV or Excel files
- View dataset preview and basic statistics
- Check data quality indicators

### 2. Explore Data Profiling
- **Data Overview**: Rows, columns, memory usage, missing values
- **Data Types Analysis**: Column types and distributions
- **Missing Values Analysis**: Heatmap and detailed breakdown
- **Statistical Analysis**: Descriptive statistics for numeric columns
- **Correlation Analysis**: Relationship matrix with high correlations
- **Distribution Analysis**: Histograms, box plots, and statistics
- **Outlier Detection**: Identify and analyze outliers
- **Data Quality Assessment**: Overall data health score

### 3. Handle Missing Values
- **Automatic Detection**: Identifies missing values in your dataset
- **Smart Strategies**:
  - **Numeric**: Fill with Mean, Median, or 0
  - **Categorical**: Fill with Mode, 'Unknown', or 'Missing'
  - **Drop Rows**: Remove rows with missing values
- **Before/After Comparison**: See the impact of cleaning
- **Revert Changes**: Go back to original data anytime

### 4. Ask Questions in Natural Language
Examples:
- "What is the average value?"
- "Which category has the highest sales?"
- "Show me the distribution of ages"
- "Find correlations between variables"
- "What are the top 10 countries by GDP?"

### 5. Use Analytics Templates
- **📈 Trend Analysis**: Time-based patterns and trends
- **🔍 Pattern Detection**: Identify recurring patterns
- **📊 Comparative Analysis**: Compare different groups
- **🎯 Target Analysis**: Focus on specific variables
- **📋 Data Summary Report**: Comprehensive overview
- **🔗 Relationship Analysis**: Correlation and association studies

### 6. Export Results
- **Download Cleaned Dataset**: Get processed CSV files
- **Download Plots**: High-resolution PNG images
- **Download Generated Code**: Python scripts for reproducibility

## 🛠️ Technical Details

### Data Processing Capabilities
- **Missing Value Handling**: Multiple strategies for different data types
- **Outlier Detection**: IQR and Z-score methods
- **Data Type Conversion**: Automatic and manual type handling
- **Statistical Analysis**: Comprehensive descriptive statistics
- **Correlation Analysis**: Pearson, Spearman correlations
- **Distribution Analysis**: Histograms, box plots, density plots

### Visualization Features
- **Professional Styling**: Seaborn themes and custom styling
- **Smart Plot Selection**: Automatic choice of best visualization
- **Large Dataset Handling**: Horizontal charts for many categories
- **Interactive Elements**: Hover effects and zoom capabilities
- **Export Options**: High-resolution downloads

### AI-Powered Analysis
- **Natural Language Processing**: Understands complex queries
- **Code Generation**: Produces executable Python code
- **Smart Visualization**: Chooses appropriate plot types
- **Error Handling**: Graceful handling of edge cases
- **Context Awareness**: Understands dataset structure

## 🔧 Configuration

### Environment Variables
```env
GOOGLE_API_KEY=your_google_api_key_here
DATABASE_URL=postgresql://user:password@postgres:5432/data_analysis
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=data_analysis
```

### Docker Services
- **streamlit**: Frontend application (Port 8501)
- **fastapi**: Backend API service (Port 8000)
- **postgres**: Database service (Port 5432)

## 📊 Supported Data Formats

### Input Formats
- **CSV Files**: Comma-separated values
- **Excel Files**: .xlsx and .xls formats
- **Large Datasets**: Handles datasets with thousands of rows

### Output Formats
- **CSV**: Cleaned and processed datasets
- **PNG**: High-resolution plot images
- **Python Code**: Reproducible analysis scripts

## 🎯 Use Cases

### Business Intelligence
- **Sales Analysis**: Revenue trends and customer insights
- **Market Research**: Competitive analysis and market trends
- **Performance Metrics**: KPI tracking and optimization
- **Customer Analytics**: Behavior patterns and segmentation

### Academic Research
- **Statistical Analysis**: Hypothesis testing and validation
- **Data Exploration**: Pattern discovery and relationship analysis
- **Report Generation**: Automated insights and visualizations
- **Reproducible Research**: Code generation for methodology

### Data Science
- **Exploratory Data Analysis**: Comprehensive dataset understanding
- **Data Cleaning**: Automated quality improvement
- **Feature Engineering**: Variable analysis and transformation
- **Model Preparation**: Data preprocessing for machine learning

## 🔒 Security & Privacy

- **Local Processing**: All data processed locally in containers
- **No External Storage**: Data never leaves your infrastructure
- **Secure API Keys**: Environment variable protection
- **Database Security**: PostgreSQL with user authentication

## 🚀 Performance

- **Fast Processing**: Optimized for large datasets
- **Parallel Processing**: Multi-service architecture
- **Caching**: Session state management for efficiency
- **Resource Optimization**: Docker container resource limits

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Streamlit** for the amazing web framework
- **FastAPI** for the high-performance API
- **Google Gemini** for AI-powered code generation
- **Pandas** for data manipulation
- **Matplotlib/Seaborn** for visualizations
- **Docker** for containerization

## 📞 Support

For issues, questions, or contributions:
- Create an issue in the repository
- Check the documentation
- Review the API documentation at http://localhost:8000/docs

---

**Built with ❤️ for data scientists, analysts, and researchers who want to focus on insights, not code.**



