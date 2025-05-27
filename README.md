# 🎰 Discord Casino Bot

A comprehensive Discord bot featuring casino games, player currency system, and administrative tools.

## 🎮 Features

### Casino Games
- **Slot Machine** - Authentic payouts with weighted symbol system
- **Coinflip** - Classic heads or tails betting
- **Dice Roll** - Multiple dice types (D6, D20, D100)
- **Roulette** - Color and number betting with realistic odds

### Player System
- **Currency Management** - Balance tracking with shorthand notation (1k, 5m, etc.)
- **Daily Rewards** - Daily, weekly, monthly claim systems
- **Vote Rewards** - Special multiplier system for voting
- **Money Transfer** - Send coins between players
- **Leaderboards** - Multiple ranking systems

### Admin Features
- **Server Configuration** - Custom currency names and emojis
- **Money Management** - Give/take player funds
- **User Administration** - Reset player data
- **Permission System** - Configurable admin roles

## 🚀 Quick Start

### 1. Discord Bot Setup
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Go to "Bot" section and create a bot
4. Copy the bot token
5. Enable "Message Content Intent"

### 2. Bot Permissions
Your bot needs these permissions:
- Send Messages
- Use Slash Commands
- Embed Links
- Read Message History

### 3. Deployment Options

#### Option A: Docker (Recommended)
```bash
# Clone the repository
git clone <your-repo-url>
cd discord-casino-bot

# Set up environment
cp .env.example .env
# Edit .env and add your DISCORD_TOKEN

# Deploy
docker-compose up -d
```

#### Option B: Direct Python
```bash
# Install dependencies
pip install discord.py

# Set environment variable
export DISCORD_TOKEN="your_token_here"

# Run the bot
python main.py
```

## 📋 Commands

### 🎮 Games
- `/slots <bet>` - Play slot machine
- `/coinflip <heads/tails> <bet>` - Flip a coin
- `/roll <dice_type> <prediction> <bet>` - Roll dice
- `/roulette <color/number> <bet>` - Play roulette

### 👤 Player
- `/balance [user]` - Check balance and stats
- `/daily` - Claim daily reward (100k coins)
- `/weekly` - Claim weekly reward (700k coins)
- `/monthly` - Claim monthly reward (3M coins)
- `/vote` - Claim vote reward with multipliers
- `/send <user> <amount>` - Transfer money
- `/leaderboard [metric]` - View rankings

### ⚙️ Admin (Manage Server permission required)
- `/config` - View server settings
- `/config-currency <name> <emoji>` - Set currency
- `/config-crypto <name> <emoji>` - Set crypto currency
- `/admin-add <user>` - Add bot admin
- `/admin-remove <user>` - Remove bot admin
- `/give-money <user> <amount>` - Give money
- `/take-money <user> <amount>` - Take money
- `/reset-user <user>` - Reset player data

### 📚 Help
- `/help` - Show all commands
- `/slots-help` - Slot machine payout table

## 💰 Currency System

### Bet Formats
- Numbers: `100`, `1000`
- Shorthand: `1k` (1,000), `5m` (5,000,000), `10g` (10,000,000,000)
- All-in: `all` or `max`

### Multipliers
- k = 1,000 (kilo)
- m = 1,000,000 (mega)
- g = 1,000,000,000 (giga)
- t = 1,000,000,000,000 (tera)
- p = 1,000,000,000,000,000 (peta)
- e = 1,000,000,000,000,000,000 (exa)
- z = 1,000,000,000,000,000,000,000 (zetta)
- y = 1,000,000,000,000,000,000,000,000 (yotta)

## 🎰 Slot Machine Payouts

| Symbol | 3 Matches | 2 Matches |
|--------|-----------|-----------|
| 7️⃣ Seven | 500:1 | 25:1 |
| 💎 Diamond | 25:1 | 10:1 |
| 📊 Bar | 5:1 | 3:1 |
| 🔔 Bell | 3:1 | 2:1 |
| 👠 Shoe | 2:1 | 1:1 |
| 🍋 Lemon | 1:1 | 1:1 |
| 🍉 Melon | 3:4 | 1:1 |
| ❤️ Heart | 1:2 | 3:4 |
| 🍒 Cherry | 1:2 | 1:4 |

## 🗳️ Vote Multiplier System

| Vote Count | Multiplier | Reward |
|------------|------------|---------|
| 1-20 | 1x | 100,000 |
| 21 | 3x | 300,000 |
| 22-41 | 2x | 200,000 |
| 42 | 6x | 600,000 |
| 43-62 | 3x | 300,000 |
| 63 | 9x | 900,000 |
| 64-83 | 4x | 400,000 |
| 84 | 12x | 1,200,000 |

## 🔧 Configuration

### Default Settings
- Starting balance: 1,000 coins
- Daily reward: 100,000 coins
- Weekly reward: 700,000 coins
- Monthly reward: 3,000,000 coins
- House edge: 2%
- Min bet: 1 coin
- Max bet: 1,000,000,000 coins

### Cooldowns
- Daily: 24 hours
- Weekly: 7 days
- Monthly: 30 days
- Vote: 12 hours

## 📁 File Structure

```
discord-casino-bot/
├── main.py              # Bot entry point
├── config.py            # Configuration settings
├── cogs/                # Command modules
│   ├── games.py         # Casino games
│   ├── slots.py         # Slot machine
│   ├── player.py        # Player commands
│   └── admin.py         # Admin commands
├── utils/               # Utility modules
│   ├── database.py      # JSON database
│   ├── currency.py      # Currency utilities
│   └── cooldowns.py     # Cooldown management
├── data/                # Data storage
│   ├── players.json     # Player data
│   └── guilds.json      # Server settings
├── Dockerfile           # Container setup
├── docker-compose.yml   # Orchestration
└── DEPLOYMENT.md        # Deployment guide
```

## 🔒 Security

- Environment variables for sensitive data
- Non-root Docker user
- Input validation and sanitization
- Permission-based admin system
- Cooldown systems to prevent abuse

## 📊 Data Storage

Currently uses JSON files for simplicity:
- `data/players.json` - Player balances, stats, cooldowns
- `data/guilds.json` - Server configurations

For production, consider migrating to PostgreSQL or MongoDB.

## 🚀 Deployment Options

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions including:
- Docker deployment
- Cloud platforms (Railway, Heroku, etc.)
- VPS setup
- Production considerations

## 📞 Support

1. Check bot permissions in Discord
2. Verify bot token is valid
3. Review logs for errors
4. Ensure proper invite link with required permissions

## 📄 License

This project is open source. Feel free to modify and distribute.