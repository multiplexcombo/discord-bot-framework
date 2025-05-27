import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
from utils.manager import Database
from utils.currency import CurrencyUtils
from utils.cooldowns import CooldownManager
from config import DAILY_REWARD, WEEKLY_REWARD, MONTHLY_REWARD, YEARLY_REWARD, VOTE_MULTIPLIERS

class Player(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()
    
    @app_commands.command(name="balance", description="Check your current balance")
    async def balance(self, interaction: discord.Interaction, user: discord.Member = None):
        """Display user balance and stats"""
        target_user = user or interaction.user
        player = await self.db.get_player(target_user.id)
        
        embed = discord.Embed(
            title=f"💰 {target_user.display_name}'s Balance",
            color=discord.Color.green()
        )
        
        # Get guild settings for currency names
        guild = await self.db.get_guild(interaction.guild.id)
        currency_name = guild.get("currency_name", "coins")
        currency_emoji = guild.get("currency_emoji", "🪙")
        crypto_name = guild.get("crypto_name", "gems")
        crypto_emoji = guild.get("crypto_emoji", "💎")
        
        embed.add_field(
            name=f"{currency_emoji} {currency_name.title()}", 
            value=CurrencyUtils.format_amount(player["balance"]), 
            inline=True
        )
        embed.add_field(
            name=f"{crypto_emoji} {crypto_name.title()}", 
            value=CurrencyUtils.format_amount(player["crypto"]), 
            inline=True
        )
        embed.add_field(name="Games Played", value=f"{player['games_played']:,}", inline=True)
        
        # Calculate net profit/loss
        net_profit = player["total_won"] - player["total_lost"]
        embed.add_field(name="Total Won", value=CurrencyUtils.format_amount(player["total_won"]), inline=True)
        embed.add_field(name="Total Lost", value=CurrencyUtils.format_amount(player["total_lost"]), inline=True)
        embed.add_field(
            name="Net Profit/Loss", 
            value=f"{'🟢 +' if net_profit >= 0 else '🔴 '}{CurrencyUtils.format_amount(abs(net_profit))}", 
            inline=True
        )
        
        embed.set_thumbnail(url=target_user.display_avatar.url)
        embed.timestamp = datetime.now()
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="daily", description="Claim your daily reward")
    async def daily(self, interaction: discord.Interaction):
        """Claim daily reward"""
        user_id = interaction.user.id
        player = await self.db.get_player(user_id)
        
        # Check cooldown
        can_use, error_msg = CooldownManager.check_cooldown(player.get("last_daily"), "daily")
        if not can_use:
            await interaction.response.send_message(f"❌ {error_msg}", ephemeral=True)
            return
        
        # Give reward
        await self.db.add_balance(user_id, DAILY_REWARD)
        await self.db.update_player(user_id, {
            "last_daily": CooldownManager.set_cooldown_used("daily")
        })
        
        embed = discord.Embed(
            title="🎁 Daily Reward Claimed!",
            description=f"You received **{CurrencyUtils.format_amount(DAILY_REWARD)}** coins!",
            color=discord.Color.green()
        )
        
        # Show new balance
        updated_player = await self.db.get_player(user_id)
        embed.add_field(name="New Balance", value=CurrencyUtils.format_amount(updated_player["balance"]), inline=True)
        embed.add_field(name="Next Daily", value="<t:{}:R>".format(int((datetime.now().timestamp() + 86400))), inline=True)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="weekly", description="Claim your weekly reward")
    async def weekly(self, interaction: discord.Interaction):
        """Claim weekly reward"""
        user_id = interaction.user.id
        player = await self.db.get_player(user_id)
        
        # Check cooldown
        can_use, error_msg = CooldownManager.check_cooldown(player.get("last_weekly"), "weekly")
        if not can_use:
            await interaction.response.send_message(f"❌ {error_msg}", ephemeral=True)
            return
        
        # Give reward
        await self.db.add_balance(user_id, WEEKLY_REWARD)
        await self.db.update_player(user_id, {
            "last_weekly": CooldownManager.set_cooldown_used("weekly")
        })
        
        embed = discord.Embed(
            title="🎁 Weekly Reward Claimed!",
            description=f"You received **{CurrencyUtils.format_amount(WEEKLY_REWARD)}** coins!",
            color=discord.Color.blue()
        )
        
        # Show new balance
        updated_player = await self.db.get_player(user_id)
        embed.add_field(name="New Balance", value=CurrencyUtils.format_amount(updated_player["balance"]), inline=True)
        embed.add_field(name="Next Weekly", value="<t:{}:R>".format(int((datetime.now().timestamp() + 604800))), inline=True)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="monthly", description="Claim your monthly reward")
    async def monthly(self, interaction: discord.Interaction):
        """Claim monthly reward"""
        user_id = interaction.user.id
        player = await self.db.get_player(user_id)
        
        # Check cooldown
        can_use, error_msg = CooldownManager.check_cooldown(player.get("last_monthly"), "monthly")
        if not can_use:
            await interaction.response.send_message(f"❌ {error_msg}", ephemeral=True)
            return
        
        # Give reward
        await self.db.add_balance(user_id, MONTHLY_REWARD)
        await self.db.update_player(user_id, {
            "last_monthly": CooldownManager.set_cooldown_used("monthly")
        })
        
        embed = discord.Embed(
            title="🎁 Monthly Reward Claimed!",
            description=f"You received **{CurrencyUtils.format_amount(MONTHLY_REWARD)}** coins!",
            color=discord.Color.purple()
        )
        
        # Show new balance
        updated_player = await self.db.get_player(user_id)
        embed.add_field(name="New Balance", value=CurrencyUtils.format_amount(updated_player["balance"]), inline=True)
        embed.add_field(name="Next Monthly", value="<t:{}:R>".format(int((datetime.now().timestamp() + 2592000))), inline=True)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="vote", description="Claim your vote reward with multiplier")
    async def vote(self, interaction: discord.Interaction):
        """Claim vote reward with multiplier system"""
        user_id = interaction.user.id
        player = await self.db.get_player(user_id)
        
        # Check cooldown
        can_use, error_msg = CooldownManager.check_cooldown(player.get("last_vote"), "vote")
        if not can_use:
            await interaction.response.send_message(f"❌ {error_msg}", ephemeral=True)
            return
        
        # Increment vote count
        vote_count = player.get("vote_count", 0) + 1
        
        # Find appropriate multiplier
        multiplier_data = None
        for vote_range, data in VOTE_MULTIPLIERS.items():
            if isinstance(vote_range, range):
                if vote_count in vote_range:
                    multiplier_data = data
                    break
            elif vote_count == vote_range:
                multiplier_data = data
                break
        
        # Default if not found
        if not multiplier_data:
            multiplier_data = {"multiplier": 1, "base_reward": 100000}
        
        # Calculate reward
        base_reward = multiplier_data["base_reward"]
        multiplier = multiplier_data["multiplier"]
        total_reward = base_reward * multiplier
        
        # Give reward
        await self.db.add_balance(user_id, total_reward)
        await self.db.update_player(user_id, {
            "last_vote": CooldownManager.set_cooldown_used("vote"),
            "vote_count": vote_count
        })
        
        embed = discord.Embed(
            title="🗳️ Vote Reward Claimed!",
            color=discord.Color.gold()
        )
        
        embed.add_field(name="Vote Count", value=f"#{vote_count}", inline=True)
        embed.add_field(name="Multiplier", value=f"{multiplier}x", inline=True)
        embed.add_field(name="Reward", value=CurrencyUtils.format_amount(total_reward), inline=True)
        
        # Show new balance
        updated_player = await self.db.get_player(user_id)
        embed.add_field(name="New Balance", value=CurrencyUtils.format_amount(updated_player["balance"]), inline=False)
        embed.add_field(name="Next Vote", value="<t:{}:R>".format(int((datetime.now().timestamp() + 43200))), inline=True)
        
        if multiplier > 1:
            embed.description = f"🎉 **BONUS MULTIPLIER!** You got {multiplier}x rewards!"
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="send", description="Send money to another user")
    @app_commands.describe(
        recipient="User to send money to",
        amount="Amount to send"
    )
    async def send(self, interaction: discord.Interaction, recipient: discord.Member, amount: str):
        """Send money to another user"""
        sender_id = interaction.user.id
        recipient_id = recipient.id
        
        # Can't send to yourself
        if sender_id == recipient_id:
            await interaction.response.send_message("❌ You can't send money to yourself!", ephemeral=True)
            return
        
        # Can't send to bots
        if recipient.bot:
            await interaction.response.send_message("❌ You can't send money to bots!", ephemeral=True)
            return
        
        # Parse amount
        send_amount = CurrencyUtils.parse_amount(amount)
        if send_amount is None:
            await interaction.response.send_message("❌ Invalid amount!", ephemeral=True)
            return
        
        # Get sender data
        sender = await self.db.get_player(sender_id)
        
        # Handle "all" amount
        if send_amount == -1:
            send_amount = sender["balance"]
        
        # Validate amount
        if send_amount <= 0:
            await interaction.response.send_message("❌ Amount must be positive!", ephemeral=True)
            return
        
        if send_amount > sender["balance"]:
            await interaction.response.send_message("❌ Insufficient funds!", ephemeral=True)
            return
        
        # Transfer money
        await self.db.subtract_balance(sender_id, send_amount)
        await self.db.add_balance(recipient_id, send_amount)
        
        embed = discord.Embed(
            title="💸 Money Transfer",
            description=f"**{interaction.user.display_name}** sent **{CurrencyUtils.format_amount(send_amount)}** to **{recipient.display_name}**!",
            color=discord.Color.green()
        )
        
        # Show updated balances
        updated_sender = await self.db.get_player(sender_id)
        embed.add_field(name="Your New Balance", value=CurrencyUtils.format_amount(updated_sender["balance"]), inline=True)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="leaderboard", description="View leaderboards")
    @app_commands.describe(
        metric="What to rank by",
        global_board="Show global leaderboard (default: this server only)"
    )
    @app_commands.choices(metric=[
        app_commands.Choice(name="Balance", value="balance"),
        app_commands.Choice(name="Total Won", value="total_won"),
        app_commands.Choice(name="Games Played", value="games_played"),
        app_commands.Choice(name="Vote Count", value="vote_count")
    ])
    async def leaderboard(self, interaction: discord.Interaction, metric: str = "balance", global_board: bool = False):
        """Display leaderboard"""
        leaderboard_data = await self.db.get_leaderboard(metric, limit=10)
        
        if not leaderboard_data:
            await interaction.response.send_message("❌ No leaderboard data available!", ephemeral=True)
            return
        
        embed = discord.Embed(
            title=f"🏆 {'Global ' if global_board else ''}Leaderboard - {metric.replace('_', ' ').title()}",
            color=discord.Color.gold()
        )
        
        leaderboard_text = ""
        for i, entry in enumerate(leaderboard_data):
            try:
                if global_board:
                    user = self.bot.get_user(entry["user_id"])
                    display_name = user.display_name if user else f"User #{entry['user_id']}"
                else:
                    member = interaction.guild.get_member(entry["user_id"])
                    if not member:
                        continue
                    display_name = member.display_name
                
                rank_emoji = ["🥇", "🥈", "🥉"][i] if i < 3 else f"{i+1}."
                value = CurrencyUtils.format_amount(entry["value"]) if metric in ["balance", "total_won"] else f"{entry['value']:,}"
                leaderboard_text += f"{rank_emoji} **{display_name}** - {value}\n"
                
            except Exception:
                continue
        
        if not leaderboard_text:
            embed.description = "No eligible users found for this leaderboard."
        else:
            embed.description = leaderboard_text
        
        embed.set_footer(text=f"Showing top {len(leaderboard_data)} players")
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Player(bot))
