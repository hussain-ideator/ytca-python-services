import sqlite3
import json
import os
import asyncio
from typing import Optional, Dict, Any
from pathlib import Path
import aiosqlite
from sqlalchemy import create_engine, Column, String, Text, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import settings

# Import sqlitecloud for cloud database support
try:
    import sqlitecloud
    SQLITECLOUD_AVAILABLE = True
except ImportError:
    SQLITECLOUD_AVAILABLE = False
    print("⚠️  SQLite Cloud not available. Install with: pip install sqlitecloud")

# Ensure database directory exists (only for local databases)
settings.ensure_database_directory()

# SQLAlchemy setup using configuration
if settings.is_cloud_database:
    # For cloud databases, we'll handle connections differently
    # SQLAlchemy may not work directly with SQLite Cloud
    print("🌩️  Using SQLite Cloud database")
    engine = None
    SessionLocal = None
    Base = declarative_base()
else:
    # Traditional local SQLite setup
    print("🗂️  Using local SQLite database")
    engine = create_engine(settings.database_url, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()

class ChannelEngagement(Base):
    __tablename__ = "channel_engagement"
    
    channel_id = Column(String, primary_key=True)
    engagement_type = Column(String, primary_key=True)
    json_response = Column(Text)
    
    __table_args__ = (
        UniqueConstraint('channel_id', 'engagement_type', name='_channel_engagement_uc'),
    )

# Create tables (only for local databases)
if engine is not None:
    Base.metadata.create_all(bind=engine)

class DatabaseManager:
    """Database manager for channel engagement operations"""
    
    def __init__(self):
        self.is_cloud = settings.is_cloud_database
        if self.is_cloud:
            self.connection_string = settings.cloud_connection_string
            print(f"🌩️  DatabaseManager: Using SQLite Cloud")
            if not SQLITECLOUD_AVAILABLE:
                raise ImportError("sqlitecloud package is required for cloud database. Install with: pip install sqlitecloud")
        else:
            self.db_path = str(settings.database_full_path)
            print(f"🗂️  DatabaseManager: Using local SQLite at {self.db_path}")
    
    def _get_sync_connection(self):
        """Get a synchronous connection (for cloud database)"""
        if self.is_cloud:
            return sqlitecloud.connect(self.connection_string)
        else:
            return sqlite3.connect(self.db_path)
    
    async def _execute_query_cloud(self, query: str, params: tuple = ()) -> Optional[Any]:
        """Execute a query on cloud database asynchronously"""
        loop = asyncio.get_event_loop()
        
        def run_query():
            try:
                conn = self._get_sync_connection()
                cursor = conn.execute(query, params)
                result = cursor.fetchone()
                conn.close()
                return result
            except Exception as e:
                print(f"Cloud database query error: {e}")
                return None
        
        return await loop.run_in_executor(None, run_query)
    
    async def _execute_command_cloud(self, command: str, params: tuple = ()) -> bool:
        """Execute a command (INSERT/UPDATE/DELETE) on cloud database asynchronously"""
        loop = asyncio.get_event_loop()
        
        def run_command():
            try:
                conn = self._get_sync_connection()
                conn.execute(command, params)
                conn.commit()
                conn.close()
                return True
            except Exception as e:
                print(f"Cloud database command error: {e}")
                return False
        
        return await loop.run_in_executor(None, run_command)
    
    async def _execute_fetchall_cloud(self, query: str, params: tuple = ()) -> list:
        """Execute a query and fetch all results from cloud database"""
        loop = asyncio.get_event_loop()
        
        def run_query():
            try:
                conn = self._get_sync_connection()
                cursor = conn.execute(query, params)
                results = cursor.fetchall()
                conn.close()
                return results
            except Exception as e:
                print(f"Cloud database fetchall error: {e}")
                return []
        
        return await loop.run_in_executor(None, run_query)
    
    async def get_channel_engagement(self, channel_id: str, engagement_type: str) -> Optional[Dict[str, Any]]:
        """Retrieve channel engagement data by channel_id and engagement_type"""
        try:
            query = "SELECT json_response FROM channel_engagement WHERE channel_id = ? AND engagement_type = ?"
            params = (channel_id, engagement_type)
            
            if self.is_cloud:
                row = await self._execute_query_cloud(query, params)
            else:
                async with aiosqlite.connect(self.db_path) as db:
                    cursor = await db.execute(query, params)
                    row = await cursor.fetchone()
            
            if row:
                return json.loads(row[0]) if row[0] else None
            return None
        except Exception as e:
            print(f"Database error: {e}")
            return None
    
    async def save_channel_engagement(self, channel_id: str, engagement_type: str, data: Dict[str, Any]) -> bool:
        """Save or update channel engagement data"""
        try:
            print(f"🔧 Database: Attempting to save data for channel {channel_id}")
            print(f"📊 Database: Engagement type: {engagement_type}")
            print(f"📝 Database: Data keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
            
            command = """INSERT OR REPLACE INTO channel_engagement 
                        (channel_id, engagement_type, json_response) 
                        VALUES (?, ?, ?)"""
            params = (channel_id, engagement_type, json.dumps(data))
            
            if self.is_cloud:
                print(f"🌩️  Database: Using SQLite Cloud")
                result = await self._execute_command_cloud(command, params)
            else:
                print(f"🗂️  Database: Using local SQLite at {self.db_path}")
                async with aiosqlite.connect(self.db_path) as db:
                    print("✅ Database: Connection established")
                    await db.execute(command, params)
                    print("✅ Database: Execute completed")
                    await db.commit()
                    print("✅ Database: Commit completed")
                    result = True
            
            if result:
                print("✅ Database: Save operation completed successfully")
            else:
                print("❌ Database: Save operation failed")
            
            return result
        except Exception as e:
            print(f"💥 Database save error: {e}")
            print(f"📋 Database error type: {type(e).__name__}")
            import traceback
            print(f"🔍 Database full traceback: {traceback.format_exc()}")
            return False
    
    async def get_all_engagement_types(self, channel_id: str) -> Dict[str, Any]:
        """Get all engagement types for a specific channel"""
        try:
            query = "SELECT engagement_type, json_response FROM channel_engagement WHERE channel_id = ?"
            params = (channel_id,)
            
            if self.is_cloud:
                rows = await self._execute_fetchall_cloud(query, params)
            else:
                async with aiosqlite.connect(self.db_path) as db:
                    cursor = await db.execute(query, params)
                    rows = await cursor.fetchall()
            
            result = {}
            for row in rows:
                engagement_type, json_data = row
                result[engagement_type] = json.loads(json_data) if json_data else None
            
            return result
        except Exception as e:
            print(f"Database error: {e}")
            return {}
    
    async def create_table_if_not_exists(self):
        """Create the channel_engagement table if it doesn't exist"""
        try:
            print(f"🔧 Database: Creating table if not exists")
            
            command = """
                CREATE TABLE IF NOT EXISTS channel_engagement (
                    channel_id TEXT NOT NULL,
                    engagement_type TEXT NOT NULL,
                    json_response TEXT,
                    PRIMARY KEY (channel_id, engagement_type)
                )
            """
            
            if self.is_cloud:
                print(f"🌩️  Database: Creating table in SQLite Cloud")
                result = await self._execute_command_cloud(command, ())
            else:
                print(f"🗂️  Database: Creating table in local SQLite at {self.db_path}")
                async with aiosqlite.connect(self.db_path) as db:
                    print("✅ Database: Table creation connection established")
                    await db.execute(command)
                    print("✅ Database: Table creation execute completed")
                    await db.commit()
                    print("✅ Database: Table creation commit completed")
                    result = True
            
            if result:
                print("✅ Database: Table creation completed successfully")
            else:
                print("❌ Database: Table creation failed")
                
            return result
        except Exception as e:
            print(f"💥 Table creation error: {e}")
            print(f"📋 Table creation error type: {type(e).__name__}")
            import traceback
            print(f"🔍 Table creation full traceback: {traceback.format_exc()}")
            return False

# Global database manager instance
db_manager = DatabaseManager() 