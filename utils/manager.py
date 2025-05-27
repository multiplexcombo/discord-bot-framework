import json
import asyncio
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from config import STARTING_BALANCE, STARTING_CRYPTO

class Database:
    """Simple JSON-based database for player and guild data"""
    
    def __init__(self):
        self.players_file = "data/players.json"
        self.guilds_file = "data/guilds.json"
        self._players_cache = {}
        self._guilds_cache = {}
        self._lock = asyncio.Lock()
    
    async def load_data(self):
        """Load data from JSON files into cache"""
        async with self._lock:
            try:
                if os.path.exists(self.players_file):
                    with open(self.players_file, 'r') as f:
                        self._players_cache = json.load(f)
                
                if os.path.exists(self.guilds_file):
                    with open(self.guilds_file, 'r') as f:
                        self._guilds_cache = json.load(f)
            except Exception as e:
                print(f"Error loading data: {e}")
                self._players_cache = {}
                self._guilds_cache = {}
    
    async def save_data(self):
        """Save cache data to JSON files"""
        async with self._lock:
            try:
                with open(self.players_file, 'w') as f:
                    json.dump(self._players_cache, f, indent=2)
                
                with open(self.guilds_file, 'w') as f:
                    json.dump(self._guilds_cache, f, indent=2)
            except Exception as e:
                print(f"Error saving data: {e}")
    
    async def get_player(self, user_id: int) -> Dict[str, Any]:
        """Get player data, create if doesn't exist"""
        await self.load_data()
        
        user_id_str = str(user_id)
        if user_id_str not in self._players_cache:
            self._players_cache[user_id_str] = {
                "balance": STARTING_BALANCE,
                "crypto": STARTING_CRYPTO,
                "total_won": 0,
                "total_lost": 0,
                "games_played": 0,
                "last_daily": None,
                "last_weekly": None,
                "last_monthly": None,
                "last_yearly": None,
                "last_work": None,
                "last_overtime": None,
                "last_spin": None,
                "last_vote": None,
                "vote_count": 0,
                "created_at": datetime.now().isoformat(),
                "boosts": {},
                "achievements": []
            }
            await self.save_data()
        
        return self._players_cache[user_id_str]
    
    async def update_player(self, user_id: int, data: Dict[str, Any]):
        """Update player data"""
        await self.load_data()
        user_id_str = str(user_id)
        
        if user_id_str in self._players_cache:
            self._players_cache[user_id_str].update(data)
        else:
            player_data = await self.get_player(user_id)
            player_data.update(data)
        
        await self.save_data()
    
    async def add_balance(self, user_id: int, amount: int) -> int:
        """Add to player balance, return new balance"""
        player = await self.get_player(user_id)
        new_balance = player["balance"] + amount
        await self.update_player(user_id, {"balance": new_balance})
        return new_balance
    
    async def subtract_balance(self, user_id: int, amount: int) -> bool:
        """Subtract from player balance, return success"""
        player = await self.get_player(user_id)
        if player["balance"] >= amount:
            new_balance = player["balance"] - amount
            await self.update_player(user_id, {"balance": new_balance})
            return True
        return False
    
    async def get_guild(self, guild_id: int) -> Dict[str, Any]:
        """Get guild configuration"""
        await self.load_data()
        
        guild_id_str = str(guild_id)
        if guild_id_str not in self._guilds_cache:
            await self.initialize_guild(guild_id)
        
        return self._guilds_cache[guild_id_str]
    
    async def initialize_guild(self, guild_id: int):
        """Initialize guild with default settings"""
        await self.load_data()
        
        guild_id_str = str(guild_id)
        self._guilds_cache[guild_id_str] = {
            "channels": {
                "general": None,
                "games": None,
                "leaderboard": None,
                "announcements": None,
                "logs": None
            },
            "admin_ids": [],
            "currency_emoji": "🪙",
            "currency_name": "coins",
            "crypto_emoji": "💎",
            "crypto_name": "gems",
            "disable_update_messages": False,
            "created_at": datetime.now().isoformat()
        }
        await self.save_data()
    
    async def update_guild(self, guild_id: int, data: Dict[str, Any]):
        """Update guild configuration"""
        await self.load_data()
        guild_id_str = str(guild_id)
        
        if guild_id_str not in self._guilds_cache:
            await self.initialize_guild(guild_id)
        
        self._guilds_cache[guild_id_str].update(data)
        await self.save_data()
    
    async def get_leaderboard(self, metric: str = "balance", limit: int = 10) -> list:
        """Get leaderboard data"""
        await self.load_data()
        
        # Convert to list and sort
        players_list = []
        for user_id, data in self._players_cache.items():
            if metric in data:
                players_list.append({
                    "user_id": int(user_id),
                    "value": data[metric],
                    "balance": data.get("balance", 0),
                    "games_played": data.get("games_played", 0)
                })
        
        # Sort by metric value (descending)
        players_list.sort(key=lambda x: x["value"], reverse=True)
        return players_list[:limit]

def create_tables():
    """Stub for database table creation (for future PostgreSQL support)."""
    pass
