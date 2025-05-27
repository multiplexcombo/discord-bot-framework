import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env

# Bot configuration
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN or TOKEN == "your_bot_token_here":
    raise RuntimeError("DISCORD_TOKEN environment variable is not set or is invalid. Please set it in your .env file or environment.")

COMMAND_PREFIX = os.getenv("COMMAND_PREFIX", "/")

# Default currency settings
DEFAULT_CURRENCY_NAME = "coins"
DEFAULT_CRYPTO_NAME = "gems"
DEFAULT_CURRENCY_EMOJI = "🪙"
DEFAULT_CRYPTO_EMOJI = "💎"

# Starting balances
STARTING_BALANCE = 1000
STARTING_CRYPTO = 0

# Daily rewards
DAILY_REWARD = 100000
WEEKLY_REWARD = 700000
MONTHLY_REWARD = 3000000
YEARLY_REWARD = 36000000

# Vote multipliers (from Payouts.txt)
VOTE_MULTIPLIERS = {
    range(1, 21): {"multiplier": 1, "base_reward": 100000},
    21: {"multiplier": 3, "base_reward": 100000},
    range(22, 42): {"multiplier": 2, "base_reward": 100000},
    42: {"multiplier": 6, "base_reward": 100000},
    range(43, 63): {"multiplier": 3, "base_reward": 100000},
    63: {"multiplier": 9, "base_reward": 100000},
    range(64, 84): {"multiplier": 4, "base_reward": 100000},
    84: {"multiplier": 12, "base_reward": 100000}
}

# Slot machine symbols and payouts (from Payouts.txt)
SLOT_SYMBOLS = {
    "seven": {"emoji": "7️⃣", "payouts": {3: 500, 2: 25}},
    "diamond": {"emoji": "💎", "payouts": {3: 25, 2: 10}},
    "bar": {"emoji": "📊", "payouts": {3: 5, 2: 3}},
    "bell": {"emoji": "🔔", "payouts": {3: 3, 2: 2}},
    "shoe": {"emoji": "👠", "payouts": {3: 2, 2: 1}},
    "lemon": {"emoji": "🍋", "payouts": {3: 1, 2: 1}},
    "melon": {"emoji": "🍉", "payouts": {3: 0.75, 2: 1}},  # 3:4 = 0.75
    "heart": {"emoji": "❤️", "payouts": {3: 0.5, 2: 0.75}},  # 1:2 = 0.5, 3:4 = 0.75
    "cherry": {"emoji": "🍒", "payouts": {3: 0.5, 2: 0.25}}  # 1:2 = 0.5, 1:4 = 0.25
}

# Slot machine weights (higher = more common)
SLOT_WEIGHTS = {
    "cherry": 30,
    "heart": 25,
    "melon": 20,
    "lemon": 15,
    "shoe": 10,
    "bell": 8,
    "bar": 5,
    "diamond": 3,
    "seven": 1
}

# Game settings
MIN_BET = 1
MAX_BET = 1000000000  # 1 billion
HOUSE_EDGE = 0.02  # 2% house edge for most games

# Cooldowns (in seconds)
COOLDOWNS = {
    "daily": 86400,    # 24 hours
    "weekly": 604800,  # 7 days
    "monthly": 2592000, # 30 days
    "yearly": 31536000, # 365 days
    "work": 3600,      # 1 hour
    "overtime": 7200,  # 2 hours
    "spin": 300,       # 5 minutes
    "vote": 43200      # 12 hours
}
