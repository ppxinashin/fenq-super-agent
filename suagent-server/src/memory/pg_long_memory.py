"""
PostgreSQL 长期记忆
"""
import os
from dataclasses import dataclass
from langgraph.store.postgres import PostgresStore, AsyncPostgresStore
from src.config import settings

class PGLongMemory:
    @classmethod
    def _store(cls) -> PostgresStore:
        with PostgresStore.from_conn_string(settings.postgres_connection_string) as store:
            store.setup()
        return store
    
    @classmethod
    def get_store(cls) -> PostgresStore:
        return cls._store()
    
    @classmethod
    async def _astore(cls) -> AsyncPostgresStore:
        async with AsyncPostgresStore.from_conn_string(settings.postgres_connection_string) as store:
            await store.setup()
        return store
    
    @classmethod
    async def get_astore(cls) -> AsyncPostgresStore:
        return await cls._astore()