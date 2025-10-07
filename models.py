# models.py

from sqlalchemy import Column, Integer, String, Text, DateTime, Float, JSON, Boolean
from datetime import datetime
from db import Base

class QueryLog(Base):
    __tablename__ = "query_logs"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(String, nullable=False)
    generated_code = Column(Text, nullable=False)
    execution_output = Column(Text, nullable=True)
    execution_success = Column(Integer, default=1)  # 1 for success, 0 for failure
    execution_time = Column(Float, nullable=True)  # Time taken to execute
    timestamp = Column(DateTime, default=datetime.utcnow)
    dataset_name = Column(String, nullable=True)
    dataset_columns = Column(JSON, nullable=True)  # Store columns as JSON

class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    filename = Column(String, nullable=False)
    columns = Column(JSON, nullable=True)  # Store columns as JSON
    row_count = Column(Integer, nullable=True)
    upload_timestamp = Column(DateTime, default=datetime.utcnow)
    last_used = Column(DateTime, nullable=True)

class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, index=True)
    query_log_id = Column(Integer, nullable=False)
    result_type = Column(String, nullable=False)  # 'text', 'plot', 'statistics'
    result_data = Column(Text, nullable=True)
    plot_filename = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

class DatasetHistory(Base):
    __tablename__ = "dataset_history"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    filename = Column(String, nullable=False)  # Original filename
    columns = Column(JSON, nullable=True)  # Store columns as JSON
    row_count = Column(Integer, nullable=True)
    upload_date = Column(DateTime, default=datetime.utcnow)
    last_used = Column(DateTime, default=datetime.utcnow)
    is_favorite = Column(Boolean, default=False)
    usage_count = Column(Integer, default=1)  # Track how often it's used
