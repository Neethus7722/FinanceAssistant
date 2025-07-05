import os
from fastapi import FastAPI, Depends, HTTPException, status, Query, UploadFile, File
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from pathlib import Path
import openai
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Set
from azure.cosmos.aio import CosmosClient
from azure.cosmos import PartitionKey
import uuid
import pandas as pd
from sqlalchemy import Table, Column, Integer, String, Float, MetaData, text
from azure.identity.aio import DefaultAzureCredential
from azure.storage.blob.aio import BlobServiceClient
from langchain.prompts import PromptTemplate
from langchain.chains import create_sql_query_chain
from backend.schemas import ChatMessage, ChatHistoryRequest, RAGQueryRequest, ExcelIngestRequest, AdvancedRAGRequest
from backend.db import engine
from backend.storage_utils import fetch_excel_from_blob, read_excel_to_df
from backend.rag_utils import run_rag_pipeline
from backend.cosmos_utils import save_chat_message, get_chat_history, get_all_sessions
from fastapi.responses import JSONResponse

# Load environment variables from .env file in project root
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / '.env'
load_dotenv(dotenv_path=ENV_PATH)

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@localhost/finance_db")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-azure-openai-key")
COSMOS_ENDPOINT = os.getenv("COSMOS_ENDPOINT", "https://your-cosmos-account.documents.azure.com:443/")
COSMOS_KEY = os.getenv("COSMOS_KEY", "your-cosmos-key")
COSMOS_DB = os.getenv("COSMOS_DB", "chatdb")
COSMOS_CONTAINER = os.getenv("COSMOS_CONTAINER", "chathistory")
AZURE_AD_CLIENT_ID = os.getenv("AZURE_AD_CLIENT_ID", "your-azure-ad-client-id")
AZURE_AD_TENANT_ID = os.getenv("AZURE_AD_TENANT_ID", "your-azure-ad-tenant-id")
AZURE_STORAGE_ACCOUNT_URL = os.getenv("AZURE_STORAGE_ACCOUNT_URL", "https://yourstorageaccount.blob.core.windows.net/")

# Database setup
engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# FastAPI app
app = FastAPI(title="NextGen Revenue Insights Assistant")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.get("/")
def read_root():
    return {"message": "Welcome to the NextGen Revenue Insights Assistant API"}

# CORS for frontend-backend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cosmos DB config
@app.on_event("startup")
async def startup_event():
    app.state.cosmos_client = CosmosClient(COSMOS_ENDPOINT, COSMOS_KEY)
    app.state.database = await app.state.cosmos_client.create_database_if_not_exists(COSMOS_DB)
    app.state.container = await app.state.database.create_container_if_not_exists(
        id=COSMOS_CONTAINER, partition_key=PartitionKey(path="/session_id")
    )

@app.on_event("shutdown")
async def shutdown_event():
    await app.state.cosmos_client.close()

# Save chat message with user_id
@app.post("/chat/save/")
async def save_chat_message_api(msg: ChatMessage):
    await save_chat_message(msg.dict())
    return {"status": "saved"}

# Get chat history for a user/session
@app.post("/chat/history/")
async def get_chat_history_api(req: ChatHistoryRequest):
    history = await get_chat_history(req.session_id, req.user_id)
    return {"history": history}

# Get all sessions for a user
@app.get("/chat/sessions/")
async def get_all_sessions_api(user_id: str = Query(...)):
    sessions = await get_all_sessions(user_id)
    return {"sessions": sessions}

# Placeholder for secure, role-based endpoint
@app.get("/secure-data/")
def get_secure_data(token: str = Depends(oauth2_scheme)):
    # TODO: Implement Azure AD validation and RBAC
    return {"data": "Secure financial data (role-based access)"}

# --- Excel Ingestion Endpoint (from Azure Storage) ---
@app.post("/ingest-excel-blob/")
async def ingest_excel_blob(req: ExcelIngestRequest):
    excel_bytes = await fetch_excel_from_blob(req.container_name, req.blob_name)
    df_blob = read_excel_to_df(excel_bytes)
    from sqlalchemy import MetaData, Table, Column, Integer, String
    metadata = MetaData()
    columns = [Column(col, String(255)) for col in df_blob.columns]
    table = Table('financials', metadata, Column('id', Integer, primary_key=True, autoincrement=True), *columns, extend_existing=True)
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)
        for _, row in df_blob.iterrows():
            await conn.execute(table.insert().values(**row.to_dict()))
    return {"status": "success", "rows": len(df_blob)}

# --- Advanced RAG Endpoint with SQL + GPT-4o ---
# Utility: Generate SQL from user query using GPT-4o
async def generate_sql_from_nl(query: str, table_schema: str) -> str:
    openai.api_key = OPENAI_API_KEY
    system_prompt = f"""
You are a financial analytics SQL expert. Given a user question and the table schema, generate a safe, optimized SQL query to answer the question. Only use columns and tables present in the schema. Do not hallucinate. Return only the SQL query.

Schema:
{table_schema}
"""
    response = openai.ChatCompletion.create(
        engine="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ],
        max_tokens=256,
        temperature=0.0
    )
    sql = response.choices[0].message["content"].strip()
    return sql

# Utility: Get table schema as string
async def get_table_schema(table_name: str = 'financials') -> str:
    async with engine.begin() as conn:
        result = await conn.execute(text(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table_name}'"))
        schema = "\n".join([f"{row[0]}: {row[1]}" for row in result.fetchall()])
    return schema

# Utility: Data masking for role-based access (demo: mask 'cost' for non-admins)
def mask_data(rows, user_role):
    if user_role != 'admin':
        for row in rows:
            if 'cost' in row:
                row['cost'] = '***'
    return rows

@app.post("/rag-advanced/")
async def rag_advanced(request: AdvancedRAGRequest):
    try:
        result = await run_rag_pipeline(request.query, request.user_role)
        return JSONResponse(content=result)
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"error": e.detail})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Unexpected error: {str(e)}"})
