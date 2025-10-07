from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Annotated, Optional
import traceback
import time
import pandas as pd

from llm_service import get_llm_chain, generate_code_with_llm
from database_service import DatabaseService

app = FastAPI()

class LLMRequest(BaseModel):
    columns: List[str]
    question: str
    dataset_name: Optional[str] = None

class DatasetRequest(BaseModel):
    name: str
    filename: str
    columns: List[str]
    row_count: int

# Initialize LLM chain globally
try:
    print("🚀 Initializing LLM chain...")
    llm_chain = get_llm_chain()
    print("✅ LLM chain is ready.")
except Exception as e:
    print("❌ Failed to initialize LLM chain:")
    traceback.print_exc()
    raise RuntimeError("LLM initialization failed") from e

@app.post("/generate_code/")
async def generate_code(request: LLMRequest):
    start_time = time.time()
    
    try:
        print("📨 Received request:", request.dict())
        
        # Generate code from LLM
        code = generate_code_with_llm(
            chain=llm_chain,
            columns=request.columns,
            question=request.question
        )
        print("✅ Generated code:\n", code)

        # Log query to database
        with DatabaseService() as db_service:
            query_id = db_service.log_query(
                question=request.question,
                generated_code=code,
                dataset_name=request.dataset_name,
                dataset_columns=request.columns
            )

        execution_time = time.time() - start_time
        
        return {
            "generated_code": code,
            "query_id": query_id,
            "execution_time": execution_time
        }

    except Exception as e:
        print("❌ Error in /generate_code:")
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"error": f"LLM failed: {str(e)}"}
        )

@app.get("/health/")
def health_check():
    return {"status": "ok"}

@app.post("/store_dataset/")
async def store_dataset(request: DatasetRequest):
    """Store dataset information in the database"""
    try:
        with DatabaseService() as db_service:
            dataset_id = db_service.store_dataset(
                name=request.name,
                filename=request.filename,
                columns=request.columns,
                row_count=request.row_count
            )
        return {"dataset_id": dataset_id, "message": "Dataset stored successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/recent_queries/")
async def get_recent_queries(limit: int = 10):
    """Get recent queries from the database"""
    try:
        with DatabaseService() as db_service:
            queries = db_service.get_recent_queries(limit=limit)
        return {"queries": queries}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/query/{query_id}")
async def get_query_details(query_id: int):
    """Get detailed information about a specific query"""
    try:
        with DatabaseService() as db_service:
            query_details = db_service.get_query_details(query_id)
        if not query_details:
            raise HTTPException(status_code=404, detail="Query not found")
        return query_details
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/datasets/")
async def get_datasets():
    """Get all datasets from the database"""
    try:
        with DatabaseService() as db_service:
            datasets = db_service.get_datasets()
        return {"datasets": datasets}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/statistics/")
async def get_statistics():
    """Get database statistics"""
    try:
        with DatabaseService() as db_service:
            stats = db_service.get_statistics()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/update_execution/{query_id}")
async def update_execution(
    query_id: int,
    execution_output: Optional[str] = None,
    success: bool = True,
    execution_time: Optional[float] = None
):
    """Update query execution results"""
    try:
        with DatabaseService() as db_service:
            db_service.update_query_execution(
                query_id=query_id,
                execution_output=execution_output,
                success=success,
                execution_time=execution_time
            )
        return {"message": "Execution updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/dataset_history/")
async def get_dataset_history():
    """Get recent dataset history"""
    try:
        with DatabaseService() as db_service:
            history = db_service.get_dataset_history(limit=10)
        return {"datasets": history}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to get dataset history: {str(e)}"}
        )

@app.get("/favorites/")
async def get_favorites():
    """Get favorite datasets"""
    try:
        with DatabaseService() as db_service:
            favorites = db_service.get_favorites()
        return {"favorites": favorites}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to get favorites: {str(e)}"}
        )

@app.post("/toggle_favorite/{dataset_id}")
async def toggle_favorite(dataset_id: int):
    """Toggle favorite status of a dataset"""
    try:
        with DatabaseService() as db_service:
            is_favorite = db_service.toggle_favorite(dataset_id)
        return {"is_favorite": is_favorite}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to toggle favorite: {str(e)}"}
        )

@app.post("/cleanup_datasets/")
async def cleanup_datasets():
    """Clean up old datasets (except favorites)"""
    try:
        with DatabaseService() as db_service:
            removed_count = db_service.cleanup_old_datasets(days=30)
        return {"removed_count": removed_count, "message": f"Removed {removed_count} old datasets"}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to cleanup datasets: {str(e)}"}
        )

@app.delete("/delete_dataset/{dataset_id}")
async def delete_dataset(dataset_id: int):
    """Delete a dataset from history and remove its file. If not found, return 200 OK (idempotent)."""
    import os
    try:
        with DatabaseService() as db_service:
            file_path = db_service.delete_dataset_from_history(dataset_id)
        if file_path:
            print(f"DEBUG: Deleted dataset id={dataset_id}, file_path={file_path}")
            if os.path.exists(file_path):
                os.remove(file_path)
            return {"message": "Dataset deleted successfully"}
        else:
            print(f"DEBUG: Dataset id={dataset_id} not found in DB (already deleted)")
            return {"message": "Dataset not found (already deleted)"}
    except Exception as e:
        print(f"DEBUG: Exception in delete_dataset: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to delete dataset: {str(e)}"}
        )

# Print all routes at startup for debugging
def print_routes():
    print("DEBUG: FastAPI registered routes:")
    for route in app.routes:
        print(f"DEBUG: {route.path} [{','.join(route.methods)}]")

print_routes()
