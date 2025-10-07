# database_service.py

import time
import json
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from db import SessionLocal
from models import QueryLog, Dataset, AnalysisResult, DatasetHistory

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class DatabaseService:
    def __init__(self):
        self.db = SessionLocal()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db.close()
    
    def log_query(self, question: str, generated_code: str, dataset_name: str = None, 
                  dataset_columns: List[str] = None) -> int:
        """Log a query to the database"""
        query_log = QueryLog(
            question=question,
            generated_code=generated_code,
            dataset_name=dataset_name,
            dataset_columns=json.dumps(dataset_columns) if dataset_columns else None
        )
        self.db.add(query_log)
        self.db.commit()
        self.db.refresh(query_log)
        return query_log.id
    
    def update_query_execution(self, query_id: int, execution_output: str = None, 
                              success: bool = True, execution_time: float = None):
        """Update query execution results"""
        query_log = self.db.query(QueryLog).filter(QueryLog.id == query_id).first()
        if query_log:
            query_log.execution_output = execution_output
            query_log.execution_success = 1 if success else 0
            query_log.execution_time = execution_time
            self.db.commit()
    
    def log_analysis_result(self, query_id: int, result_type: str, result_data: str = None, 
                           plot_filename: str = None):
        """Log analysis results"""
        result = AnalysisResult(
            query_log_id=query_id,
            result_type=result_type,
            result_data=result_data,
            plot_filename=plot_filename
        )
        self.db.add(result)
        self.db.commit()
    
    def store_dataset(self, name: str, filename: str, columns: List[str], row_count: int):
        """Store dataset information"""
        dataset = Dataset(
            name=name,
            filename=filename,
            columns=json.dumps(columns),
            row_count=row_count
        )
        self.db.add(dataset)
        self.db.commit()
        return dataset.id
    
    def get_recent_queries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent queries"""
        queries = self.db.query(QueryLog).order_by(QueryLog.timestamp.desc()).limit(limit).all()
        return [
            {
                "id": q.id,
                "question": q.question,
                "timestamp": q.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "success": bool(q.execution_success),
                "dataset_name": q.dataset_name
            }
            for q in queries
        ]
    
    def get_query_details(self, query_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific query"""
        query = self.db.query(QueryLog).filter(QueryLog.id == query_id).first()
        if not query:
            return None
        
        results = self.db.query(AnalysisResult).filter(AnalysisResult.query_log_id == query_id).all()
        
        return {
            "id": query.id,
            "question": query.question,
            "generated_code": query.generated_code,
            "execution_output": query.execution_output,
            "success": bool(query.execution_success),
            "execution_time": query.execution_time,
            "timestamp": query.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "dataset_name": query.dataset_name,
            "results": [
                {
                    "type": r.result_type,
                    "data": r.result_data,
                    "plot_filename": r.plot_filename
                }
                for r in results
            ]
        }
    
    def get_datasets(self) -> List[Dict[str, Any]]:
        """Get all datasets"""
        datasets = self.db.query(Dataset).order_by(Dataset.upload_timestamp.desc()).all()
        return [
            {
                "id": d.id,
                "name": d.name,
                "filename": d.filename,
                "columns": json.loads(d.columns) if d.columns else [],
                "row_count": d.row_count,
                "upload_timestamp": d.upload_timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "last_used": d.last_used.strftime("%Y-%m-%d %H:%M:%S") if d.last_used else None
            }
            for d in datasets
        ]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        total_queries = self.db.query(QueryLog).count()
        successful_queries = self.db.query(QueryLog).filter(QueryLog.execution_success == 1).count()
        total_datasets = self.db.query(Dataset).count()
        
        return {
            "total_queries": total_queries,
            "successful_queries": successful_queries,
            "success_rate": (successful_queries / total_queries * 100) if total_queries > 0 else 0,
            "total_datasets": total_datasets
        } 

    def add_dataset_to_history(self, name: str, filename: str, columns: List[str] = None, 
                              row_count: int = None) -> int:
        """Add or update dataset in history. Never add a new row for the same filename."""
        try:
            # Check if dataset already exists (by filename)
            existing = self.db.query(DatasetHistory).filter(
                DatasetHistory.filename == filename
            ).first()
            
            if existing:
                # Only update last_used and usage_count
                existing.last_used = datetime.utcnow()
                existing.usage_count += 1
                self.db.commit()
                return existing.id
            else:
                # Add new entry
                dataset = DatasetHistory(
                    name=name,
                    filename=filename,
                    columns=columns,
                    row_count=row_count
                )
                self.db.add(dataset)
                self.db.commit()
                self.db.refresh(dataset)
                return dataset.id
        except Exception as e:
            self.db.rollback()
            raise e

    def get_dataset_history(self, limit: int = 10) -> List[Dict]:
        """Get recent dataset history"""
        try:
            datasets = self.db.query(DatasetHistory).order_by(
                DatasetHistory.last_used.desc()
            ).limit(limit).all()
            
            return [
                {
                    "id": ds.id,
                    "name": ds.name,
                    "filename": ds.filename,
                    "columns": ds.columns,
                    "row_count": ds.row_count,
                    "upload_date": ds.upload_date,
                    "last_used": ds.last_used,
                    "is_favorite": ds.is_favorite,
                    "usage_count": ds.usage_count
                }
                for ds in datasets
            ]
        except Exception as e:
            raise e

    def get_favorites(self) -> List[Dict]:
        """Get favorite datasets"""
        try:
            favorites = self.db.query(DatasetHistory).filter(
                DatasetHistory.is_favorite == True
            ).order_by(DatasetHistory.last_used.desc()).all()
            
            return [
                {
                    "id": ds.id,
                    "name": ds.name,
                    "filename": ds.filename,
                    "columns": ds.columns,
                    "row_count": ds.row_count,
                    "upload_date": ds.upload_date,
                    "last_used": ds.last_used,
                    "usage_count": ds.usage_count
                }
                for ds in favorites
            ]
        except Exception as e:
            raise e

    def toggle_favorite(self, dataset_id: int) -> bool:
        """Toggle favorite status of a dataset"""
        try:
            dataset = self.db.query(DatasetHistory).filter(
                DatasetHistory.id == dataset_id
            ).first()
            
            if dataset:
                dataset.is_favorite = not dataset.is_favorite
                self.db.commit()
                return dataset.is_favorite
            return False
        except Exception as e:
            self.db.rollback()
            raise e

    def update_dataset_usage(self, dataset_id: int):
        """Update last used time and usage count"""
        try:
            dataset = self.db.query(DatasetHistory).filter(
                DatasetHistory.id == dataset_id
            ).first()
            
            if dataset:
                dataset.last_used = datetime.utcnow()
                dataset.usage_count += 1
                self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise e

    def cleanup_old_datasets(self, days: int = 30):
        """Remove datasets older than specified days (except favorites)"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            old_datasets = self.db.query(DatasetHistory).filter(
                DatasetHistory.last_used < cutoff_date,
                DatasetHistory.is_favorite == False
            ).all()
            
            for dataset in old_datasets:
                self.db.delete(dataset)
            
            self.db.commit()
            return len(old_datasets)
        except Exception as e:
            self.db.rollback()
            raise e 

    def delete_dataset_from_history(self, dataset_id: int) -> str:
        """Delete a dataset from history and return its file path for deletion"""
        try:
            dataset = self.db.query(DatasetHistory).filter(
                DatasetHistory.id == dataset_id
            ).first()
            if dataset:
                print(f"DEBUG: Found dataset in DB for delete: id={dataset_id}, filename={dataset.filename}")
                file_path = dataset.filename
                self.db.delete(dataset)
                self.db.commit()
                print(f"DEBUG: Deleted dataset from DB: id={dataset_id}")
                return file_path
            print(f"DEBUG: Dataset id={dataset_id} not found in DB for delete")
            return None
        except Exception as e:
            print(f"DEBUG: Exception in delete_dataset_from_history: {e}")
            self.db.rollback()
            raise e 