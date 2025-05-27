import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timedelta
import random
from utils.manager import Database
from utils.currency import CurrencyUtils
from utils.cooldowns import CooldownManager
from config import DAILY_REWARD

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()
        
        # Shop items configuration
        self.shop_items = {
            "multiplier_2x": {
                "name": "2x Multiplier",
                "description": "Double your winnings for 1 hour",
                "price": 500000,
                "emoji": "⚡",
                "duration": 3600,  # 1 hour in seconds
                "type": "boost"
            },
            "multiplier_3x": {
                "name": "3x Multiplier", 
                "description": "Triple your winnings for 30 minutes",
                "price": 1000000,
                "emoji": "🔥",
                "duration": 1800,  # 30 minutes
                "type": "boost"
            },
            "lucky_charm": {
                "name": "Lucky Charm",
                "description": "Increase win chance by 10% for 2 hours",
                "price": 750000,
                "emoji": "🍀",
                "duration": 7200,  # 2 hours
                "type": "boost"
            },
            "work_boost": {
                "name": "Work Boost",
                "description": "Increase work rewards by 50% for 4 hours",
                "price": 300000,
                "emoji": "💼",
                "duration": 14400,  # 4 hours
                "type": "boost"
            },
            "loot_box": {
                "name": "Mystery Loot Box",
                "description": "Contains random rewards (10k-1M coins)",
                "price": 250000,
                "emoji": "📦",
                "type": "consumable"
            }
        }
        
        # Work job types
        self.work_jobs = [
            {"name": "Delivery Driver", "min_pay": 50000, "max_pay": 150000, "emoji": "🚚"},
            {"name": "Casino Dealer", "min_pay": 75000, "max_pay": 200000, "emoji": "🎰"},
            {"name": "Security Guard", "min_pay": 60000, "max_pay": 180000, "emoji": "🛡️"},
            {"name": "Bartender", "min_pay": 40000, "max_pay": 120000, "emoji": "🍺"},
            {"name": "Chef", "min_pay": 70000, "max_pay": 220000, "emoji": "👨‍🍳"},
            {"name": "Mechanic", "min_pay": 80000, "max_pay": 250000, "emoji": "🔧"},
            {"name": "Programmer", "min_pay": 100000, "max_pay": 300000, "emoji": "💻"},
            {"name": "Doctor", "min_pay": 200000, "max_pay": 500000, "emoji": "⚕️"}
        ]

    @app_commands.command(name="shop", description="Browse the item shop")
    @app_commands.describe(category="Category to browse")
    @app_commands.choices(category=[
        app_commands.Choice(name="Boosts", value="boost"),
        app_commands.Choice(name="Consumables", value="consumable"),
        app_commands.Choice(name="All Items", value="all")
    ])
    async def shop(self, interaction: discord.Interaction, category: str = "all"):
        """Display the shop with available items"""
        embed = discord.Embed(
            title="🏪 Casino Shop",
            description="Spend your coins on powerful boosts and items!",
            color=discord.Color.blue()
        )
        
        items_shown = 0
        for item_id, item_data in self.shop_items.items():
            if category == "all" or item_data["type"] == category:
                price_formatted = CurrencyUtils.format_amount(item_data["price"])
                
                field_value = f"{item_data['description']}\n💰 **Price:** {price_formatted}"
                if item_data["type"] == "boost":
                    duration_hours = item_data["duration"] // 3600
                    duration_minutes = (item_data["duration"] % 3600) // 60
                    if duration_hours > 0:
                        field_value += f"\n⏰ **Duration:** {duration_hours}h"
                        if duration_minutes > 0:
                            field_value += f" {duration_minutes}m"
                    else:
                        field_value += f"\n⏰ **Duration:** {duration_minutes}m"
                
                embed.add_field(
                    name=f"{item_data['emoji']} {item_data['name']} (`{item_id}`)",
                    value=field_value,
                    inline=False
                )
                items_shown += 1
        
        if items_shown == 0:
            embed.add_field(name="No Items", value="No items found in this category.", inline=False)
        
        embed.add_field(
            name="How to Buy",
            value="Use `/buy <item_id>` to purchase items\nExample: `/buy multiplier_2x`",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="buy", description="Buy an item from the shop")
    @app_commands.describe(item_id="The ID of the item to buy")
    async def buy(self, interaction: discord.Interaction, item_id: str):
        """Purchase an item from the shop"""
        user_id = interaction.user.id
        
        # Check if item exists
        if item_id not in self.shop_items:
            await interaction.response.send_message("❌ Item not found! Use `/shop` to see available items.", ephemeral=True)
            return
        
        item = self.shop_items[item_id]
        player = await self.db.get_player(user_id)
        
        # Check if user can afford item
        if player["balance"] < item["price"]:
            needed = item["price"] - player["balance"]
            await interaction.response.send_message(
                f"❌ Insufficient funds! You need {CurrencyUtils.format_amount(needed)} more coins.",
                ephemeral=True
            )
            return
        
        # Process purchase
        await self.db.subtract_balance(user_id, item["price"])
        
        if item["type"] == "boost":
            # Add boost to player's active boosts
            current_boosts = player.get("boosts", {})
            expiry_time = (datetime.now() + timedelta(seconds=item["duration"])).isoformat()
            current_boosts[item_id] = {
                "name": item["name"],
                "expiry": expiry_time,
                "emoji": item["emoji"]
            }
            await self.db.update_player(user_id, {"boosts": current_boosts})
            
        elif item["type"] == "consumable":
            if item_id == "loot_box":
                # Open loot box immediately
                reward = random.randint(10000, 1000000)
                await self.db.add_balance(user_id, reward)
                
                embed = discord.Embed(
                    title="📦 Loot Box Opened!",
                    description=f"You found **{CurrencyUtils.format_amount(reward)}** coins!",
                    color=discord.Color.gold()
                )
                embed.add_field(name="Item Purchased", value=f"{item['emoji']} {item['name']}", inline=True)
                embed.add_field(name="Cost", value=CurrencyUtils.format_amount(item["price"]), inline=True)
                embed.add_field(name="Reward", value=CurrencyUtils.format_amount(reward), inline=True)
                
                updated_player = await self.db.get_player(user_id)
                embed.add_field(name="New Balance", value=CurrencyUtils.format_amount(updated_player["balance"]), inline=False)
                
                await interaction.response.send_message(embed=embed)
                return
        
        # Standard purchase confirmation
        embed = discord.Embed(
            title="✅ Purchase Successful!",
            description=f"You bought **{item['name']}**!",
            color=discord.Color.green()
        )
        
        embed.add_field(name="Item", value=f"{item['emoji']} {item['name']}", inline=True)
        embed.add_field(name="Cost", value=CurrencyUtils.format_amount(item["price"]), inline=True)
        
        if item["type"] == "boost":
            embed.add_field(name="Duration", value=f"{item['duration'] // 60} minutes", inline=True)
            embed.add_field(name="Tip", value="Use `/boosts` to see your active boosts!", inline=False)
        
        updated_player = await self.db.get_player(user_id)
        embed.add_field(name="New Balance", value=CurrencyUtils.format_amount(updated_player["balance"]), inline=False)
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="boosts", description="View your active boosts")
    async def boosts(self, interaction: discord.Interaction):
        """Display user's active boosts"""
        user_id = interaction.user.id
        player = await self.db.get_player(user_id)
        
        current_boosts = player.get("boosts", {})
        active_boosts = {}
        
        # Filter out expired boosts
        current_time = datetime.now()
        for boost_id, boost_data in current_boosts.items():
            expiry_time = datetime.fromisoformat(boost_data["expiry"])
            if expiry_time > current_time:
                active_boosts[boost_id] = boost_data
        
        # Update player data if boosts were removed
        if len(active_boosts) != len(current_boosts):
            await self.db.update_player(user_id, {"boosts": active_boosts})
        
        embed = discord.Embed(
            title="⚡ Your Active Boosts",
            color=discord.Color.purple()
        )
        
        if not active_boosts:
            embed.description = "You don't have any active boosts.\nVisit the `/shop` to buy some!"
        else:
            for boost_id, boost_data in active_boosts.items():
                expiry_time = datetime.fromisoformat(boost_data["expiry"])
                time_left = expiry_time - current_time
                
                hours = int(time_left.total_seconds() // 3600)
                minutes = int((time_left.total_seconds() % 3600) // 60)
                
                time_str = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"
                
                embed.add_field(
                    name=f"{boost_data['emoji']} {boost_data['name']}",
                    value=f"⏰ **Time left:** {time_str}",
                    inline=True
                )
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="work", description="Work a job to earn money")
    async def work(self, interaction: discord.Interaction):
        """Work for money with cooldown"""
        user_id = interaction.user.id
        player = await self.db.get_player(user_id)
        
        # Check cooldown
        can_work, error_msg = CooldownManager.check_cooldown(player.get("last_work"), "work")
        if not can_work:
            await interaction.response.send_message(f"❌ {error_msg}", ephemeral=True)
            return
        
        # Select random job
        job = random.choice(self.work_jobs)
        base_pay = random.randint(job["min_pay"], job["max_pay"])
        
        # Check for work boost
        current_boosts = player.get("boosts", {})
        work_boost_active = False
        current_time = datetime.now()
        
        for boost_id, boost_data in current_boosts.items():
            if boost_id == "work_boost":
                expiry_time = datetime.fromisoformat(boost_data["expiry"])
                if expiry_time > current_time:
                    work_boost_active = True
                    break
        
        # Apply work boost if active
        if work_boost_active:
            final_pay = int(base_pay * 1.5)
            boost_text = "💼 **Work Boost Active!** (+50%)"
        else:
            final_pay = base_pay
            boost_text = ""
        
        # Add money and update cooldown
        await self.db.add_balance(user_id, final_pay)
        await self.db.update_player(user_id, {
            "last_work": CooldownManager.set_cooldown_used("work")
        })
        
        embed = discord.Embed(
            title="💼 Work Complete!",
            description=f"You worked as a **{job['name']}** {job['emoji']}",
            color=discord.Color.green()
        )
        
        embed.add_field(name="Base Pay", value=CurrencyUtils.format_amount(base_pay), inline=True)
        if work_boost_active:
            embed.add_field(name="Final Pay", value=CurrencyUtils.format_amount(final_pay), inline=True)
            embed.add_field(name="Boost", value=boost_text, inline=True)
        else:
            embed.add_field(name="Earned", value=CurrencyUtils.format_amount(final_pay), inline=True)
        
        # Show new balance
        updated_player = await self.db.get_player(user_id)
        embed.add_field(name="New Balance", value=CurrencyUtils.format_amount(updated_player["balance"]), inline=False)
        embed.add_field(name="Next Work", value="<t:{}:R>".format(int((datetime.now().timestamp() + 3600))), inline=True)
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="overtime", description="Work overtime for extra money (longer cooldown)")
    async def overtime(self, interaction: discord.Interaction):
        """Work overtime for higher pay but longer cooldown"""
        user_id = interaction.user.id
        player = await self.db.get_player(user_id)
        
        # Check cooldown
        can_work, error_msg = CooldownManager.check_cooldown(player.get("last_overtime"), "overtime")
        if not can_work:
            await interaction.response.send_message(f"❌ {error_msg}", ephemeral=True)
            return
        
        # Higher paying jobs for overtime
        overtime_jobs = [
            {"name": "Casino Manager", "min_pay": 200000, "max_pay": 500000, "emoji": "🎩"},
            {"name": "Investment Banker", "min_pay": 300000, "max_pay": 700000, "emoji": "💰"},
            {"name": "Cryptocurrency Trader", "min_pay": 250000, "max_pay": 800000, "emoji": "₿"},
            {"name": "High Stakes Dealer", "min_pay": 400000, "max_pay": 900000, "emoji": "🃏"},
            {"name": "CEO", "min_pay": 500000, "max_pay": 1000000, "emoji": "👔"}
        ]
        
        job = random.choice(overtime_jobs)
        base_pay = random.randint(job["min_pay"], job["max_pay"])
        
        # Check for work boost
        current_boosts = player.get("boosts", {})
        work_boost_active = False
        current_time = datetime.now()
        
        for boost_id, boost_data in current_boosts.items():
            if boost_id == "work_boost":
                expiry_time = datetime.fromisoformat(boost_data["expiry"])
                if expiry_time > current_time:
                    work_boost_active = True
                    break
        
        # Apply work boost if active
        if work_boost_active:
            final_pay = int(base_pay * 1.5)
            boost_text = "💼 **Work Boost Active!** (+50%)"
        else:
            final_pay = base_pay
            boost_text = ""
        
        # Add money and update cooldown
        await self.db.add_balance(user_id, final_pay)
        await self.db.update_player(user_id, {
            "last_overtime": CooldownManager.set_cooldown_used("overtime")
        })
        
        embed = discord.Embed(
            title="⏰ Overtime Complete!",
            description=f"You worked overtime as a **{job['name']}** {job['emoji']}\n*Higher risk, higher reward!*",
            color=discord.Color.gold()
        )
        
        embed.add_field(name="Base Pay", value=CurrencyUtils.format_amount(base_pay), inline=True)
        if work_boost_active:
            embed.add_field(name="Final Pay", value=CurrencyUtils.format_amount(final_pay), inline=True)
            embed.add_field(name="Boost", value=boost_text, inline=True)
        else:
            embed.add_field(name="Earned", value=CurrencyUtils.format_amount(final_pay), inline=True)
        
        # Show new balance
        updated_player = await self.db.get_player(user_id)
        embed.add_field(name="New Balance", value=CurrencyUtils.format_amount(updated_player["balance"]), inline=False)
        embed.add_field(name="Next Overtime", value="<t:{}:R>".format(int((datetime.now().timestamp() + 7200))), inline=True)
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Economy(bot))