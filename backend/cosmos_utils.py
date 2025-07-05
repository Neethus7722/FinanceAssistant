# Cosmos DB utilities for chat history
from azure.cosmos.aio import CosmosClient
from azure.cosmos import PartitionKey
import os
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / '.env'
load_dotenv(dotenv_path=ENV_PATH)

COSMOS_ENDPOINT = os.getenv("COSMOS_ENDPOINT", "https://your-cosmos-account.documents.azure.com:443/")
COSMOS_KEY = os.getenv("COSMOS_KEY", "your-cosmos-key")
COSMOS_DB = os.getenv("COSMOS_DB", "chatdb")
COSMOS_CONTAINER = os.getenv("COSMOS_CONTAINER", "chathistory")

async def get_cosmos_container():
    client = CosmosClient(COSMOS_ENDPOINT, COSMOS_KEY)
    database = await client.create_database_if_not_exists(COSMOS_DB)
    container = await database.create_container_if_not_exists(
        id=COSMOS_CONTAINER, partition_key=PartitionKey(path="/session_id")
    )
    return client, container

async def save_chat_message(item: dict):
    client, container = await get_cosmos_container()
    await container.upsert_item(item)
    await client.close()

async def get_chat_history(session_id: str, user_id: str):
    client, container = await get_cosmos_container()
    query = f"SELECT * FROM c WHERE c.session_id=@session_id AND c.user_id=@user_id ORDER BY c._ts ASC"
    params = [
        {"name": "@session_id", "value": session_id},
        {"name": "@user_id", "value": user_id}
    ]
    items = container.query_items(query=query, parameters=params, enable_cross_partition_query=True)
    history = []
    async for item in items:
        history.append({"user": item["user"], "assistant": item["assistant"], "timestamp": item.get("timestamp")})
    await client.close()
    return history

async def get_all_sessions(user_id: str):
    client, container = await get_cosmos_container()
    query = "SELECT DISTINCT c.session_id FROM c WHERE c.user_id=@user_id"
    params = [{"name": "@user_id", "value": user_id}]
    items = container.query_items(query=query, parameters=params, enable_cross_partition_query=True)
    sessions = set()
    async for item in items:
        sessions.add(item["session_id"])
    await client.close()
    return list(sessions)
