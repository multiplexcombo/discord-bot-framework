import discord
from discord.ext import commands
from discord import app_commands
from utils.manager import Database
from utils.currency import CurrencyUtils
from typing import Optional

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()
    
    async def is_admin(self, interaction: discord.Interaction) -> bool:
        """Check if user is bot admin or has manage server permission"""
        if interaction.user.guild_permissions.manage_guild:
            return True
        
        guild_data = await self.db.get_guild(interaction.guild.id)
        admin_ids = guild_data.get("admin_ids", [])
        return interaction.user.id in admin_ids
    
    @app_commands.command(name="config", description="Configure bot settings for this server")
    async def config(self, interaction: discord.Interaction):
        """Display current server configuration"""
        if not await self.is_admin(interaction):
            await interaction.response.send_message("❌ You need Manage Server permissions or be a bot admin!", ephemeral=True)
            return
        
        guild_data = await self.db.get_guild(interaction.guild.id)
        
        embed = discord.Embed(
            title="⚙️ Server Configuration",
            color=discord.Color.blue()
        )
        
        # Currency settings
        currency_info = f"**Name:** {guild_data.get('currency_name', 'coins')}\n"
        currency_info += f"**Emoji:** {guild_data.get('currency_emoji', '🪙')}"
        embed.add_field(name="Currency Settings", value=currency_info, inline=True)
        
        crypto_info = f"**Name:** {guild_data.get('crypto_name', 'gems')}\n"
        crypto_info += f"**Emoji:** {guild_data.get('crypto_emoji', '💎')}"
        embed.add_field(name="Crypto Settings", value=crypto_info, inline=True)
        
        # Channels
        channels = guild_data.get("channels", {})
        channel_info = ""
        for channel_type, channel_id in channels.items():
            if channel_id:
                channel = interaction.guild.get_channel(channel_id)
                channel_name = channel.mention if channel else f"Unknown ({channel_id})"
                channel_info += f"**{channel_type.title()}:** {channel_name}\n"
        
        if not channel_info:
            channel_info = "No channels configured"
        embed.add_field(name="Configured Channels", value=channel_info, inline=False)
        
        # Admin settings
        admin_ids = guild_data.get("admin_ids", [])
        admin_info = ""
        for admin_id in admin_ids:
            member = interaction.guild.get_member(admin_id)
            if member:
                admin_info += f"• {member.display_name}\n"
        
        if not admin_info:
            admin_info = "No additional admins configured"
        embed.add_field(name="Bot Admins", value=admin_info, inline=True)
        
        # Other settings
        other_info = f"**Disable Update Messages:** {guild_data.get('disable_update_messages', False)}"
        embed.add_field(name="Other Settings", value=other_info, inline=True)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="config-currency", description="Configure currency settings")
    @app_commands.describe(
        name="Name for the main currency",
        emoji="Emoji for the main currency"
    )
    async def config_currency(self, interaction: discord.Interaction, name: str = None, emoji: str = None):
        """Configure main currency settings"""
        if not await self.is_admin(interaction):
            await interaction.response.send_message("❌ You need Manage Server permissions or be a bot admin!", ephemeral=True)
            return
        
        updates = {}
        if name:
            updates["currency_name"] = name
        if emoji:
            updates["currency_emoji"] = emoji
        
        if not updates:
            await interaction.response.send_message("❌ Please provide at least one setting to update!", ephemeral=True)
            return
        
        await self.db.update_guild(interaction.guild.id, updates)
        
        embed = discord.Embed(
            title="✅ Currency Settings Updated",
            color=discord.Color.green()
        )
        
        if name:
            embed.add_field(name="Currency Name", value=name, inline=True)
        if emoji:
            embed.add_field(name="Currency Emoji", value=emoji, inline=True)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="config-crypto", description="Configure crypto currency settings")
    @app_commands.describe(
        name="Name for the crypto currency",
        emoji="Emoji for the crypto currency"
    )
    async def config_crypto(self, interaction: discord.Interaction, name: str = None, emoji: str = None):
        """Configure crypto currency settings"""
        if not await self.is_admin(interaction):
            await interaction.response.send_message("❌ You need Manage Server permissions or be a bot admin!", ephemeral=True)
            return
        
        updates = {}
        if name:
            updates["crypto_name"] = name
        if emoji:
            updates["crypto_emoji"] = emoji
        
        if not updates:
            await interaction.response.send_message("❌ Please provide at least one setting to update!", ephemeral=True)
            return
        
        await self.db.update_guild(interaction.guild.id, updates)
        
        embed = discord.Embed(
            title="✅ Crypto Settings Updated",
            color=discord.Color.green()
        )
        
        if name:
            embed.add_field(name="Crypto Name", value=name, inline=True)
        if emoji:
            embed.add_field(name="Crypto Emoji", value=emoji, inline=True)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="admin-add", description="Add a user as bot admin")
    @app_commands.describe(user="User to add as admin")
    async def admin_add(self, interaction: discord.Interaction, user: discord.Member):
        """Add a user as bot admin"""
        if not await self.is_admin(interaction):
            await interaction.response.send_message("❌ You need Manage Server permissions or be a bot admin!", ephemeral=True)
            return
        
        guild_data = await self.db.get_guild(interaction.guild.id)
        admin_ids = guild_data.get("admin_ids", [])
        
        if user.id in admin_ids:
            await interaction.response.send_message(f"❌ {user.display_name} is already a bot admin!", ephemeral=True)
            return
        
        admin_ids.append(user.id)
        await self.db.update_guild(interaction.guild.id, {"admin_ids": admin_ids})
        
        embed = discord.Embed(
            title="✅ Admin Added",
            description=f"**{user.display_name}** has been added as a bot admin!",
            color=discord.Color.green()
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="admin-remove", description="Remove a user from bot admins")
    @app_commands.describe(user="User to remove from admins")
    async def admin_remove(self, interaction: discord.Interaction, user: discord.Member):
        """Remove a user from bot admins"""
        if not await self.is_admin(interaction):
            await interaction.response.send_message("❌ You need Manage Server permissions or be a bot admin!", ephemeral=True)
            return
        
        guild_data = await self.db.get_guild(interaction.guild.id)
        admin_ids = guild_data.get("admin_ids", [])
        
        if user.id not in admin_ids:
            await interaction.response.send_message(f"❌ {user.display_name} is not a bot admin!", ephemeral=True)
            return
        
        admin_ids.remove(user.id)
        await self.db.update_guild(interaction.guild.id, {"admin_ids": admin_ids})
        
        embed = discord.Embed(
            title="✅ Admin Removed",
            description=f"**{user.display_name}** has been removed from bot admins!",
            color=discord.Color.orange()
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="give-money", description="Give money to a user (Admin only)")
    @app_commands.describe(
        user="User to give money to",
        amount="Amount to give"
    )
    async def give_money(self, interaction: discord.Interaction, user: discord.Member, amount: str):
        """Give money to a user (admin command)"""
        if not await self.is_admin(interaction):
            await interaction.response.send_message("❌ You need Manage Server permissions or be a bot admin!", ephemeral=True)
            return
        
        # Parse amount
        give_amount = CurrencyUtils.parse_amount(amount)
        if give_amount is None or give_amount <= 0:
            await interaction.response.send_message("❌ Invalid amount!", ephemeral=True)
            return
        
        # Give money
        new_balance = await self.db.add_balance(user.id, give_amount)
        
        embed = discord.Embed(
            title="💰 Money Given",
            description=f"Gave **{CurrencyUtils.format_amount(give_amount)}** to **{user.display_name}**!",
            color=discord.Color.green()
        )
        
        embed.add_field(name="New Balance", value=CurrencyUtils.format_amount(new_balance), inline=True)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="take-money", description="Take money from a user (Admin only)")
    @app_commands.describe(
        user="User to take money from",
        amount="Amount to take"
    )
    async def take_money(self, interaction: discord.Interaction, user: discord.Member, amount: str):
        """Take money from a user (admin command)"""
        if not await self.is_admin(interaction):
            await interaction.response.send_message("❌ You need Manage Server permissions or be a bot admin!", ephemeral=True)
            return
        
        # Parse amount
        take_amount = CurrencyUtils.parse_amount(amount)
        if take_amount is None or take_amount <= 0:
            await interaction.response.send_message("❌ Invalid amount!", ephemeral=True)
            return
        
        # Take money
        player = await self.db.get_player(user.id)
        actual_taken = min(take_amount, player["balance"])
        new_balance = await self.db.add_balance(user.id, -actual_taken)
        
        embed = discord.Embed(
            title="💸 Money Taken",
            description=f"Took **{CurrencyUtils.format_amount(actual_taken)}** from **{user.display_name}**!",
            color=discord.Color.orange()
        )
        
        embed.add_field(name="New Balance", value=CurrencyUtils.format_amount(new_balance), inline=True)
        
        if actual_taken < take_amount:
            embed.set_footer(text=f"User only had {CurrencyUtils.format_amount(player['balance'])} available")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="reset-user", description="Reset a user's data (Admin only)")
    @app_commands.describe(user="User to reset")
    async def reset_user(self, interaction: discord.Interaction, user: discord.Member):
        """Reset a user's data (admin command)"""
        if not await self.is_admin(interaction):
            await interaction.response.send_message("❌ You need Manage Server permissions or be a bot admin!", ephemeral=True)
            return
        
        # Reset user data
        await self.db.update_player(user.id, {
            "balance": 1000,  # Starting balance
            "crypto": 0,
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
            "boosts": {},
            "achievements": []
        })
        
        embed = discord.Embed(
            title="🔄 User Data Reset",
            description=f"**{user.display_name}**'s data has been reset to default values!",
            color=discord.Color.blue()
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="help", description="Show available commands")
    async def help(self, interaction: discord.Interaction):
        """Display help information"""
        embed = discord.Embed(
            title="🎰 Casino Bot Commands",
            description="Welcome to the casino! Here are all available commands:",
            color=discord.Color.blue()
        )
        
        # Games section
        games_commands = [
            "`/slots <bet>` - Play the slot machine",
            "`/coinflip <heads/tails> <bet>` - Flip a coin",
            "`/roll <dice_type> <prediction> <bet>` - Roll dice",
            "`/roulette <color/number> <bet>` - Play roulette"
        ]
        embed.add_field(name="🎮 Games", value="\n".join(games_commands), inline=False)
        
        # Player commands
        player_commands = [
            "`/balance [user]` - Check balance",
            "`/daily` - Claim daily reward",
            "`/weekly` - Claim weekly reward", 
            "`/monthly` - Claim monthly reward",
            "`/vote` - Claim vote reward",
            "`/send <user> <amount>` - Send money",
            "`/leaderboard [metric]` - View leaderboards"
        ]
        embed.add_field(name="👤 Player", value="\n".join(player_commands), inline=False)
        
        # Admin commands (if user is admin)
        if await self.is_admin(interaction):
            admin_commands = [
                "`/config` - View server configuration",
                "`/config-currency <name> <emoji>` - Set currency",
                "`/config-crypto <name> <emoji>` - Set crypto",
                "`/admin-add <user>` - Add bot admin",
                "`/admin-remove <user>` - Remove bot admin",
                "`/give-money <user> <amount>` - Give money",
                "`/take-money <user> <amount>` - Take money",
                "`/reset-user <user>` - Reset user data"
            ]
            embed.add_field(name="⚙️ Admin", value="\n".join(admin_commands), inline=False)
        
        # Information
        embed.add_field(
            name="💡 Tips", 
            value="• Use shorthand notation: `1k`, `5m`, `10g`, `all`\n• Use `/slots-help` for payout info\n• Vote daily for bonus rewards!", 
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Admin(bot))
