import sqlite3
import json
import os
from typing import Optional, Dict, Any
from pathlib import Path
import aiosqlite
from sqlalchemy import create_engine, Column, String, Text, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import settings

# Ensure database directory exists
settings.ensure_database_directory()

# SQLAlchemy setup using configuration
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

# Create tables
Base.metadata.create_all(bind=engine)

class DatabaseManager:
    """Database manager for channel engagement operations"""
    
    def __init__(self):
        self.db_path = str(settings.database_full_path)
    
    async def get_channel_engagement(self, channel_id: str, engagement_type: str) -> Optional[Dict[str, Any]]:
        """Retrieve channel engagement data by channel_id and engagement_type"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute(
                    "SELECT json_response FROM channel_engagement WHERE channel_id = ? AND engagement_type = ?",
                    (channel_id, engagement_type)
                )
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
            print(f"🗂️  Database: Using path: {self.db_path}")
            
            async with aiosqlite.connect(self.db_path) as db:
                print("✅ Database: Connection established")
                
                await db.execute(
                    """INSERT OR REPLACE INTO channel_engagement 
                       (channel_id, engagement_type, json_response) 
                       VALUES (?, ?, ?)""",
                    (channel_id, engagement_type, json.dumps(data))
                )
                print("✅ Database: Execute completed")
                
                await db.commit()
                print("✅ Database: Commit completed")
                return True
        except Exception as e:
            print(f"💥 Database save error: {e}")
            print(f"📋 Database error type: {type(e).__name__}")
            import traceback
            print(f"🔍 Database full traceback: {traceback.format_exc()}")
            return False
    
    async def get_all_engagement_types(self, channel_id: str) -> Dict[str, Any]:
        """Get all engagement types for a specific channel"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute(
                    "SELECT engagement_type, json_response FROM channel_engagement WHERE channel_id = ?",
                    (channel_id,)
                )
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
            print(f"🗂️  Database: Using path: {self.db_path}")
            
            async with aiosqlite.connect(self.db_path) as db:
                print("✅ Database: Table creation connection established")
                
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS channel_engagement (
                        channel_id TEXT NOT NULL,
                        engagement_type TEXT NOT NULL,
                        json_response TEXT,
                        PRIMARY KEY (channel_id, engagement_type)
                    )
                """)
                print("✅ Database: Table creation execute completed")
                
                await db.commit()
                print("✅ Database: Table creation commit completed")
                return True
        except Exception as e:
            print(f"💥 Table creation error: {e}")
            print(f"📋 Table creation error type: {type(e).__name__}")
            import traceback
            print(f"🔍 Table creation full traceback: {traceback.format_exc()}")
            return False

# Global database manager instance
db_manager = DatabaseManager() 