import json
from datetime import datetime, timedelta
from typing import Optional
from config import COOLDOWNS

class CooldownManager:
    """Manage command cooldowns for players"""
    
    @staticmethod
    def parse_datetime(dt_str: Optional[str]) -> Optional[datetime]:
        """Parse datetime string to datetime object"""
        if not dt_str:
            return None
        try:
            return datetime.fromisoformat(dt_str)
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    def get_cooldown_remaining(last_used: Optional[str], cooldown_seconds: int) -> Optional[timedelta]:
        """
        Get remaining cooldown time
        Returns None if no cooldown, timedelta if cooldown active
        """
        if not last_used:
            return None
            
        last_time = CooldownManager.parse_datetime(last_used)
        if not last_time:
            return None
            
        cooldown_end = last_time + timedelta(seconds=cooldown_seconds)
        now = datetime.now()
        
        if now >= cooldown_end:
            return None  # Cooldown expired
        
        return cooldown_end - now
    
    @staticmethod
    def format_cooldown(remaining: timedelta) -> str:
        """Format cooldown time remaining as human readable string"""
        total_seconds = int(remaining.total_seconds())
        
        days = total_seconds // 86400
        hours = (total_seconds % 86400) // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        parts = []
        if days > 0:
            parts.append(f"{days}d")
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        if seconds > 0 and not days:  # Only show seconds if less than a day
            parts.append(f"{seconds}s")
        
        return " ".join(parts) if parts else "0s"
    
    @staticmethod
    def check_cooldown(last_used: Optional[str], command: str) -> tuple[bool, Optional[str]]:
        """
        Check if command is on cooldown
        Returns (can_use, error_message)
        """
        if command not in COOLDOWNS:
            return True, None
            
        cooldown_seconds = COOLDOWNS[command]
        remaining = CooldownManager.get_cooldown_remaining(last_used, cooldown_seconds)
        
        if remaining is None:
            return True, None
        
        formatted_time = CooldownManager.format_cooldown(remaining)
        return False, f"Command on cooldown! Try again in {formatted_time}"
    
    @staticmethod
    def set_cooldown_used(command: str) -> str:
        """
        Mark command as used now
        Returns current timestamp as ISO string
        """
        return datetime.now().isoformat()
