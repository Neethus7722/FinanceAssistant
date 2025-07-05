# OpenAI GPT-4o and RAG utilities
import openai
import os
from sqlalchemy import text
from db import engine
from fastapi import HTTPException

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-azure-openai-key")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "https://your-azure-openai-resource.openai.azure.com/")
OPENAI_API_DEPLOYMENT = os.getenv("OPENAI_API_DEPLOYMENT", "gpt-4o")
OPENAI_API_VERSION = os.getenv("OPENAI_API_VERSION", "2024-02-15-preview")

async def get_table_schema(table_name: str = 'financials') -> str:
    try:
        async with engine.begin() as conn:
            result = await conn.execute(text(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table_name}'"))
            schema = "\n".join([f"{row[0]}: {row[1]}" for row in result.fetchall()])
        return schema
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching table schema: {str(e)}")

async def generate_sql_from_nl(query: str, table_schema: str) -> str:
    try:
        openai.api_type = "azure"
        openai.api_key = OPENAI_API_KEY
        openai.api_base = OPENAI_API_BASE
        openai.api_version = OPENAI_API_VERSION
        system_prompt = f"""
You are a financial analytics SQL expert. Given a user question and the table schema, generate a safe, optimized SQL query to answer the question. Only use columns and tables present in the schema. Do not hallucinate. Return only the SQL query.

Schema:
{table_schema}
"""
        response = openai.ChatCompletion.create(
            engine=OPENAI_API_DEPLOYMENT,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            max_tokens=256,
            temperature=0.0
        )
        sql = response.choices[0].message["content"].strip()
        return sql
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating SQL from NL: {str(e)}")

def mask_data(rows, user_role):
    if user_role != 'admin':
        for row in rows:
            if 'cost' in row:
                row['cost'] = '***'
    return rows

async def run_rag_pipeline(user_query: str, user_role: str = 'user'):
    try:
        schema = await get_table_schema('financials')
        sql = await generate_sql_from_nl(user_query, schema)
        async with engine.begin() as conn:
            try:
                result = await conn.execute(text(sql))
                rows = [dict(row) for row in result.fetchall()]
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"SQL execution error: {str(e)}\nSQL: {sql}")
        rows = mask_data(rows, user_role)
        context = "\n".join([str(row) for row in rows])
        prompt = f"Context:\n{context}\n\nUser Query: {user_query}\n\nAnswer as a financial analytics expert. Provide a summary and, if relevant, a table or chart-ready data."
        openai.api_type = "azure"
        openai.api_key = OPENAI_API_KEY
        openai.api_base = OPENAI_API_BASE
        openai.api_version = OPENAI_API_VERSION
        try:
            response = openai.ChatCompletion.create(
                engine=OPENAI_API_DEPLOYMENT,
                messages=[{"role": "system", "content": "You are a financial analytics assistant."},
                          {"role": "user", "content": prompt}],
                max_tokens=512,
                temperature=0.2
            )
            answer = response.choices[0].message["content"]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error generating LLM response: {str(e)}")
        return {"result": answer, "sql": sql, "data": rows}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG pipeline error: {str(e)}")
