import discord
from discord.ext import commands
import asyncio
import os
import json
from config import TOKEN, COMMAND_PREFIX
from utils.manager import create_tables 
from flask import Flask
import threading

# Bot setup with intents
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

class CasinoBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=COMMAND_PREFIX,
            intents=intents,
            help_command=None
        )
        
    async def setup_hook(self):
        """Load all cogs when bot starts"""
        cogs = [
            'cogs.games',
            'cogs.player',
            'cogs.admin',
            'cogs.economy'
        ]
        
        for cog in cogs:
            try:
                await self.load_extension(cog)
                print(f"Loaded {cog}")
            except Exception as e:
                print(f"Failed to load {cog}: {e}")
                
        # Sync slash commands
        try:
            synced = await self.tree.sync()
            print(f"Synced {len(synced)} command(s)")
        except Exception as e:
            print(f"Failed to sync commands: {e}")
    
    async def on_ready(self):
        """Bot ready event"""
        print(f'{self.user} has connected to Discord!')
        print(f'Bot is in {len(self.guilds)} guilds')
        
        # Initialize PostgreSQL database
        try:
            create_tables()
            print("✅ PostgreSQL database initialized successfully")
        except Exception as e:
            print(f"⚠️ Database initialization warning: {e}")
        
        # Set bot status
        await self.change_presence(
            activity=discord.Game(name="🎰 Casino Games | /help")
        )
    
    async def on_guild_join(self, guild):
        """Initialize guild data when joining"""
        from utils.manager import Database
        db = Database()
        await db.initialize_guild(guild.id)
        print(f"Joined guild: {guild.name}")

# Create bot instance
bot = CasinoBot()

app = Flask(__name__)

@app.route("/")
def index():
    return "Casino Bot Flask server is running."

def run_bot():
    # Create data directories if they don't exist
    os.makedirs("data", exist_ok=True)
    # Initialize data files
    if not os.path.exists("data/players.json"):
        with open("data/players.json", "w") as f:
            json.dump({}, f)
    if not os.path.exists("data/guilds.json"):
        with open("data/guilds.json", "w") as f:
            json.dump({}, f)
    bot.run(TOKEN)

if __name__ != "__main__":
    # If running via 'flask run', start the bot in a background thread
    threading.Thread(target=run_bot, daemon=True).start()

if __name__ == "__main__":
    run_bot()
