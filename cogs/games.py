import discord
from discord.ext import commands
from discord import app_commands
import random
import asyncio
from utils.manager import Database
from utils.currency import CurrencyUtils
from utils.cooldowns import CooldownManager
from config import MIN_BET, MAX_BET, HOUSE_EDGE, SLOT_SYMBOLS, SLOT_WEIGHTS

class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()
    
    @app_commands.command(name="coinflip", description="Flip a coin and bet on the outcome")
    @app_commands.describe(
        prediction="Choose heads or tails",
        bet="Amount to bet (supports k, m, g, t notation)"
    )
    @app_commands.choices(prediction=[
        app_commands.Choice(name="Heads", value="heads"),
        app_commands.Choice(name="Tails", value="tails")
    ])
    async def coinflip(self, interaction: discord.Interaction, prediction: str, bet: str):
        """Coinflip gambling game"""
        user_id = interaction.user.id
        
        # Parse bet amount
        bet_amount = CurrencyUtils.parse_amount(bet)
        if bet_amount is None:
            await interaction.response.send_message("❌ Invalid bet amount!", ephemeral=True)
            return
        
        # Get player data
        player = await self.db.get_player(user_id)
        
        # Handle "all" bet
        if bet_amount == -1:
            bet_amount = player["balance"]
        
        # Validate bet
        is_valid, error_msg = CurrencyUtils.validate_bet(bet_amount, player["balance"], MIN_BET, MAX_BET)
        if not is_valid:
            await interaction.response.send_message(f"❌ {error_msg}", ephemeral=True)
            return
        
        # Subtract bet from balance
        success = await self.db.subtract_balance(user_id, bet_amount)
        if not success:
            await interaction.response.send_message("❌ Insufficient funds!", ephemeral=True)
            return
        
        # Flip the coin
        result = random.choice(["heads", "tails"])
        won = prediction.lower() == result
        
        # Calculate winnings (2x payout minus house edge)
        if won:
            payout = int(bet_amount * (2 - HOUSE_EDGE))
            await self.db.add_balance(user_id, payout)
            profit = payout - bet_amount
        else:
            payout = 0
            profit = -bet_amount
        
        # Update stats
        await self.db.update_player(user_id, {
            "games_played": player["games_played"] + 1,
            "total_won": player["total_won"] + (profit if profit > 0 else 0),
            "total_lost": player["total_lost"] + (abs(profit) if profit < 0 else 0)
        })
        
        # Create response embed
        embed = discord.Embed(
            title="🪙 Coinflip Result",
            color=discord.Color.green() if won else discord.Color.red()
        )
        
        coin_emoji = "🔴" if result == "heads" else "⚪"
        embed.add_field(name="Result", value=f"{coin_emoji} {result.title()}", inline=True)
        embed.add_field(name="Your Prediction", value=f"{prediction.title()}", inline=True)
        embed.add_field(name="Outcome", value="🎉 **YOU WON!**" if won else "💀 **YOU LOST!**", inline=True)
        
        embed.add_field(name="Bet Amount", value=CurrencyUtils.format_amount(bet_amount), inline=True)
        if won:
            embed.add_field(name="Payout", value=CurrencyUtils.format_amount(payout), inline=True)
            embed.add_field(name="Profit", value=f"+{CurrencyUtils.format_amount(profit)}", inline=True)
        else:
            embed.add_field(name="Lost", value=f"-{CurrencyUtils.format_amount(bet_amount)}", inline=True)
        
        # Get updated balance
        updated_player = await self.db.get_player(user_id)
        embed.add_field(name="New Balance", value=CurrencyUtils.format_amount(updated_player["balance"]), inline=False)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="roll", description="Roll dice and bet on the outcome")
    @app_commands.describe(
        dice_type="Type of dice to roll",
        prediction="Number to predict",
        bet="Amount to bet"
    )
    @app_commands.choices(dice_type=[
        app_commands.Choice(name="6-sided dice", value=6),
        app_commands.Choice(name="20-sided dice", value=20),
        app_commands.Choice(name="100-sided dice", value=100)
    ])
    async def roll(self, interaction: discord.Interaction, dice_type: int, prediction: int, bet: str):
        """Dice roll gambling game"""
        user_id = interaction.user.id
        
        # Validate prediction
        if prediction < 1 or prediction > dice_type:
            await interaction.response.send_message(f"❌ Prediction must be between 1 and {dice_type}!", ephemeral=True)
            return
        
        # Parse bet amount
        bet_amount = CurrencyUtils.parse_amount(bet)
        if bet_amount is None:
            await interaction.response.send_message("❌ Invalid bet amount!", ephemeral=True)
            return
        
        # Get player data
        player = await self.db.get_player(user_id)
        
        # Handle "all" bet
        if bet_amount == -1:
            bet_amount = player["balance"]
        
        # Validate bet
        is_valid, error_msg = CurrencyUtils.validate_bet(bet_amount, player["balance"], MIN_BET, MAX_BET)
        if not is_valid:
            await interaction.response.send_message(f"❌ {error_msg}", ephemeral=True)
            return
        
        # Subtract bet from balance
        success = await self.db.subtract_balance(user_id, bet_amount)
        if not success:
            await interaction.response.send_message("❌ Insufficient funds!", ephemeral=True)
            return
        
        # Roll the dice
        result = random.randint(1, dice_type)
        won = prediction == result
        
        # Calculate winnings (dice_type multiplier minus house edge)
        if won:
            multiplier = dice_type * (1 - HOUSE_EDGE)
            payout = int(bet_amount * multiplier)
            await self.db.add_balance(user_id, payout)
            profit = payout - bet_amount
        else:
            payout = 0
            profit = -bet_amount
        
        # Update stats
        await self.db.update_player(user_id, {
            "games_played": player["games_played"] + 1,
            "total_won": player["total_won"] + (profit if profit > 0 else 0),
            "total_lost": player["total_lost"] + (abs(profit) if profit < 0 else 0)
        })
        
        # Create response embed
        embed = discord.Embed(
            title=f"🎲 D{dice_type} Roll Result",
            color=discord.Color.green() if won else discord.Color.red()
        )
        
        embed.add_field(name="Roll Result", value=f"🎲 **{result}**", inline=True)
        embed.add_field(name="Your Prediction", value=f"**{prediction}**", inline=True)
        embed.add_field(name="Outcome", value="🎉 **JACKPOT!**" if won else "💀 **MISS!**", inline=True)
        
        embed.add_field(name="Bet Amount", value=CurrencyUtils.format_amount(bet_amount), inline=True)
        if won:
            embed.add_field(name="Payout", value=CurrencyUtils.format_amount(payout), inline=True)
            embed.add_field(name="Profit", value=f"+{CurrencyUtils.format_amount(profit)}", inline=True)
        else:
            embed.add_field(name="Lost", value=f"-{CurrencyUtils.format_amount(bet_amount)}", inline=True)
        
        # Get updated balance
        updated_player = await self.db.get_player(user_id)
        embed.add_field(name="New Balance", value=CurrencyUtils.format_amount(updated_player["balance"]), inline=False)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="roulette", description="Play roulette and bet on colors or numbers")
    @app_commands.describe(
        prediction="What to bet on (red, black, green, or number 0-36)",
        bet="Amount to bet"
    )
    async def roulette(self, interaction: discord.Interaction, prediction: str, bet: str):
        """Roulette gambling game"""
        user_id = interaction.user.id
        
        # Parse prediction
        prediction = prediction.lower()
        red_numbers = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
        black_numbers = [2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35]
        
        bet_type = None
        bet_number = None
        
        if prediction in ["red", "black", "green"]:
            bet_type = prediction
        else:
            try:
                bet_number = int(prediction)
                if bet_number < 0 or bet_number > 36:
                    raise ValueError()
                bet_type = "number"
            except ValueError:
                await interaction.response.send_message("❌ Invalid prediction! Use 'red', 'black', 'green', or a number 0-36.", ephemeral=True)
                return
        
        # Parse bet amount
        bet_amount = CurrencyUtils.parse_amount(bet)
        if bet_amount is None:
            await interaction.response.send_message("❌ Invalid bet amount!", ephemeral=True)
            return
        
        # Get player data
        player = await self.db.get_player(user_id)
        
        # Handle "all" bet
        if bet_amount == -1:
            bet_amount = player["balance"]
        
        # Validate bet
        is_valid, error_msg = CurrencyUtils.validate_bet(bet_amount, player["balance"], MIN_BET, MAX_BET)
        if not is_valid:
            await interaction.response.send_message(f"❌ {error_msg}", ephemeral=True)
            return
        
        # Subtract bet from balance
        success = await self.db.subtract_balance(user_id, bet_amount)
        if not success:
            await interaction.response.send_message("❌ Insufficient funds!", ephemeral=True)
            return
        
        # Spin the wheel
        result_number = random.randint(0, 36)
        
        # Determine result color
        if result_number == 0:
            result_color = "green"
            color_emoji = "🟢"
        elif result_number in red_numbers:
            result_color = "red"
            color_emoji = "🔴"
        else:
            result_color = "black"
            color_emoji = "⚫"
        
        # Check if won
        won = False
        multiplier = 0
        
        if bet_type == "number" and bet_number == result_number:
            won = True
            multiplier = 35  # 35:1 payout for single number
        elif bet_type == result_color:
            won = True
            if bet_type == "green":
                multiplier = 35  # 35:1 for green
            else:
                multiplier = 1.8  # ~2:1 for red/black minus house edge
        
        # Calculate winnings
        if won:
            payout = int(bet_amount * multiplier)
            await self.db.add_balance(user_id, payout)
            profit = payout - bet_amount
        else:
            payout = 0
            profit = -bet_amount
        
        # Update stats
        await self.db.update_player(user_id, {
            "games_played": player["games_played"] + 1,
            "total_won": player["total_won"] + (profit if profit > 0 else 0),
            "total_lost": player["total_lost"] + (abs(profit) if profit < 0 else 0)
        })
        
        # Create response embed
        embed = discord.Embed(
            title="🎰 Roulette Result",
            color=discord.Color.green() if won else discord.Color.red()
        )
        
        embed.add_field(name="Result", value=f"{color_emoji} **{result_number} {result_color.title()}**", inline=True)
        embed.add_field(name="Your Bet", value=f"**{prediction.title()}**", inline=True)
        embed.add_field(name="Outcome", value="🎉 **YOU WON!**" if won else "💀 **YOU LOST!**", inline=True)
        
        embed.add_field(name="Bet Amount", value=CurrencyUtils.format_amount(bet_amount), inline=True)
        if won:
            embed.add_field(name="Payout", value=CurrencyUtils.format_amount(payout), inline=True)
            embed.add_field(name="Profit", value=f"+{CurrencyUtils.format_amount(profit)}", inline=True)
        else:
            embed.add_field(name="Lost", value=f"-{CurrencyUtils.format_amount(bet_amount)}", inline=True)
        
        # Get updated balance
        updated_player = await self.db.get_player(user_id)
        embed.add_field(name="New Balance", value=CurrencyUtils.format_amount(updated_player["balance"]), inline=False)
        
        await interaction.response.send_message(embed=embed)
    
    def get_random_symbol(self):
        """Get a random slot symbol based on weights"""
        symbols = list(SLOT_SYMBOLS.keys())
        weights = [SLOT_WEIGHTS[symbol] for symbol in symbols]
        return random.choices(symbols, weights=weights)[0]
    
    def calculate_payout(self, symbols, bet_amount):
        """Calculate payout based on slot result"""
        # Count occurrences of each symbol
        symbol_counts = {}
        for symbol in symbols:
            symbol_counts[symbol] = symbol_counts.get(symbol, 0) + 1
        
        total_payout = 0
        winning_lines = []
        
        # Check for winning combinations
        for symbol, count in symbol_counts.items():
            if count >= 2 and symbol in SLOT_SYMBOLS:
                payouts = SLOT_SYMBOLS[symbol]["payouts"]
                if count in payouts:
                    multiplier = payouts[count]
                    payout = int(bet_amount * multiplier)
                    total_payout += payout
                    winning_lines.append({
                        "symbol": symbol,
                        "count": count,
                        "multiplier": multiplier,
                        "payout": payout
                    })
        
        return total_payout, winning_lines
    
    @app_commands.command(name="slots", description="Play the slot machine!")
    @app_commands.describe(bet="Amount to bet (supports k, m, g, t notation)")
    async def slots(self, interaction: discord.Interaction, bet: str):
        """Slot machine game with authentic payouts"""
        user_id = interaction.user.id
        
        # Parse bet amount
        bet_amount = CurrencyUtils.parse_amount(bet)
        if bet_amount is None:
            await interaction.response.send_message("❌ Invalid bet amount!", ephemeral=True)
            return
        
        # Get player data
        player = await self.db.get_player(user_id)
        
        # Handle "all" bet
        if bet_amount == -1:
            bet_amount = player["balance"]
        
        # Validate bet
        is_valid, error_msg = CurrencyUtils.validate_bet(bet_amount, player["balance"], MIN_BET, MAX_BET)
        if not is_valid:
            await interaction.response.send_message(f"❌ {error_msg}", ephemeral=True)
            return
        
        # Subtract bet from balance
        success = await self.db.subtract_balance(user_id, bet_amount)
        if not success:
            await interaction.response.send_message("❌ Insufficient funds!", ephemeral=True)
            return
        
        # Spin the reels
        reel1 = self.get_random_symbol()
        reel2 = self.get_random_symbol()
        reel3 = self.get_random_symbol()
        symbols = [reel1, reel2, reel3]
        
        # Calculate payout
        total_payout, winning_lines = self.calculate_payout(symbols, bet_amount)
        
        # Add winnings to balance
        if total_payout > 0:
            await self.db.add_balance(user_id, total_payout)
            profit = total_payout - bet_amount
        else:
            profit = -bet_amount
        
        # Update stats
        await self.db.update_player(user_id, {
            "games_played": player["games_played"] + 1,
            "total_won": player["total_won"] + (profit if profit > 0 else 0),
            "total_lost": player["total_lost"] + (abs(profit) if profit < 0 else 0)
        })
        
        # Create response embed
        embed = discord.Embed(
            title="🎰 Slot Machine",
            color=discord.Color.gold() if total_payout > 0 else discord.Color.red()
        )
        
        # Show the slot result
        slot_display = ""
        for symbol in symbols:
            slot_display += SLOT_SYMBOLS[symbol]["emoji"]
        
        embed.add_field(name="Result", value=f"**{slot_display}**", inline=False)
        
        # Show winning combinations
        if winning_lines:
            win_text = ""
            for line in winning_lines:
                symbol_data = SLOT_SYMBOLS[line["symbol"]]
                emoji = symbol_data["emoji"]
                win_text += f"{emoji} x{line['count']} = {line['multiplier']}:1 (+{CurrencyUtils.format_amount(line['payout'])})\n"
            
            embed.add_field(name="🎉 Winning Lines", value=win_text, inline=False)
            embed.add_field(name="Total Payout", value=CurrencyUtils.format_amount(total_payout), inline=True)
            embed.add_field(name="Profit", value=f"+{CurrencyUtils.format_amount(profit)}", inline=True)
        else:
            embed.add_field(name="Result", value="💀 **NO MATCH**", inline=True)
            embed.add_field(name="Lost", value=f"-{CurrencyUtils.format_amount(bet_amount)}", inline=True)
        
        embed.add_field(name="Bet Amount", value=CurrencyUtils.format_amount(bet_amount), inline=True)
        
        # Get updated balance
        updated_player = await self.db.get_player(user_id)
        embed.add_field(name="New Balance", value=CurrencyUtils.format_amount(updated_player["balance"]), inline=False)
        
        # Add payout table as footer for reference
        embed.set_footer(text="💡 Use /slots-help for payout information")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="slots-help", description="Show slot machine payout table")
    async def slots_help(self, interaction: discord.Interaction):
        """Display slot machine payout information"""
        embed = discord.Embed(
            title="🎰 Slot Machine Payouts",
            description="Match symbols to win! Payouts are multiplied by your bet amount.",
            color=discord.Color.blue()
        )
        
        # Create payout table
        payout_text = ""
        for symbol, data in SLOT_SYMBOLS.items():
            emoji = data["emoji"]
            payouts = data["payouts"]
            
            line = f"{emoji} "
            payout_parts = []
            for count, multiplier in sorted(payouts.items(), reverse=True):
                if multiplier >= 1:
                    payout_parts.append(f"x{count} = {int(multiplier)}:1")
                else:
                    # Handle fractional payouts
                    if multiplier == 0.75:
                        payout_parts.append(f"x{count} = 3:4")
                    elif multiplier == 0.5:
                        payout_parts.append(f"x{count} = 1:2")
                    elif multiplier == 0.25:
                        payout_parts.append(f"x{count} = 1:4")
                    else:
                        payout_parts.append(f"x{count} = {multiplier}:1")
            
            line += " | ".join(payout_parts)
            payout_text += line + "\n"
        
        embed.add_field(name="Payout Table", value=f"```{payout_text}```", inline=False)
        embed.add_field(name="How to Play", value="• Use `/slots <bet>` to spin\n• Match 2 or 3 symbols to win\n• Higher value symbols = bigger payouts", inline=False)
        embed.add_field(name="Bet Formats", value="• Numbers: `100`, `1000`\n• Shorthand: `1k`, `5m`, `10g`\n• All-in: `all` or `max`", inline=False)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="blackjack", description="Play Blackjack against the dealer")
    @app_commands.describe(bet="Amount to bet (supports k, m, g, t notation)")
    async def blackjack(self, interaction: discord.Interaction, bet: str):
        """Blackjack game with authentic casino rules"""
        user_id = interaction.user.id
        
        # Parse bet amount
        bet_amount = CurrencyUtils.parse_amount(bet)
        if bet_amount is None:
            await interaction.response.send_message("❌ Invalid bet amount!", ephemeral=True)
            return
        
        # Get player data
        player = await self.db.get_player(user_id)
        
        # Handle "all" bet
        if bet_amount == -1:
            bet_amount = player["balance"]
        
        # Validate bet
        is_valid, error_msg = CurrencyUtils.validate_bet(bet_amount, player["balance"], MIN_BET, MAX_BET)
        if not is_valid:
            await interaction.response.send_message(f"❌ {error_msg}", ephemeral=True)
            return
        
        # Subtract bet from balance
        success = await self.db.subtract_balance(user_id, bet_amount)
        if not success:
            await interaction.response.send_message("❌ Insufficient funds!", ephemeral=True)
            return
        
        # Create deck and deal cards
        suits = ['♠', '♥', '♦', '♣']
        ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
        deck = [(rank, suit) for suit in suits for rank in ranks]
        random.shuffle(deck)
        
        # Deal initial hands
        player_hand = [deck.pop(), deck.pop()]
        dealer_hand = [deck.pop(), deck.pop()]
        
        def card_value(hand):
            value = 0
            aces = 0
            for rank, _ in hand:
                if rank in ['J', 'Q', 'K']:
                    value += 10
                elif rank == 'A':
                    aces += 1
                    value += 11
                else:
                    value += int(rank)
            
            # Handle aces
            while value > 21 and aces > 0:
                value -= 10
                aces -= 1
            return value
        
        def format_hand(hand, hide_dealer=False):
            if hide_dealer:
                return f"{hand[0][0]}{hand[0][1]} ??"
            return " ".join([f"{rank}{suit}" for rank, suit in hand])
        
        player_value = card_value(player_hand)
        dealer_value = card_value(dealer_hand)
        
        # Check for natural blackjack
        player_blackjack = player_value == 21
        dealer_blackjack = dealer_value == 21
        
        embed = discord.Embed(title="🃏 Blackjack", color=discord.Color.blue())
        embed.add_field(name="Your Hand", value=f"{format_hand(player_hand)} = {player_value}", inline=True)
        embed.add_field(name="Dealer Hand", value=f"{format_hand(dealer_hand, True)}", inline=True)
        embed.add_field(name="Bet", value=CurrencyUtils.format_amount(bet_amount), inline=True)
        
        # Determine outcome
        if player_blackjack and dealer_blackjack:
            # Push (tie)
            await self.db.add_balance(user_id, bet_amount)
            embed.color = discord.Color.orange()
            embed.add_field(name="Result", value="🤝 **PUSH!** Both have blackjack", inline=False)
            payout = bet_amount
            profit = 0
        elif player_blackjack:
            # Player blackjack wins 3:2
            payout = int(bet_amount * 2.5)
            await self.db.add_balance(user_id, payout)
            profit = payout - bet_amount
            embed.color = discord.Color.gold()
            embed.add_field(name="Result", value="🎉 **BLACKJACK!** You win!", inline=False)
        elif dealer_blackjack:
            # Dealer blackjack, player loses
            embed.color = discord.Color.red()
            embed.add_field(name="Result", value="💀 **DEALER BLACKJACK!** You lose!", inline=False)
            payout = 0
            profit = -bet_amount
        elif player_value > 21:
            # Player bust
            embed.color = discord.Color.red()
            embed.add_field(name="Result", value="💥 **BUST!** You lose!", inline=False)
            payout = 0
            profit = -bet_amount
        else:
            # Dealer plays
            while dealer_value < 17:
                dealer_hand.append(deck.pop())
                dealer_value = card_value(dealer_hand)
            
            embed.set_field_at(1, name="Dealer Hand", value=f"{format_hand(dealer_hand)} = {dealer_value}", inline=True)
            
            if dealer_value > 21:
                # Dealer bust, player wins
                payout = bet_amount * 2
                await self.db.add_balance(user_id, payout)
                profit = payout - bet_amount
                embed.color = discord.Color.green()
                embed.add_field(name="Result", value="🎉 **DEALER BUST!** You win!", inline=False)
            elif dealer_value > player_value:
                # Dealer wins
                embed.color = discord.Color.red()
                embed.add_field(name="Result", value="💀 **DEALER WINS!** You lose!", inline=False)
                payout = 0
                profit = -bet_amount
            elif player_value > dealer_value:
                # Player wins
                payout = bet_amount * 2
                await self.db.add_balance(user_id, payout)
                profit = payout - bet_amount
                embed.color = discord.Color.green()
                embed.add_field(name="Result", value="🎉 **YOU WIN!**", inline=False)
            else:
                # Push (tie)
                await self.db.add_balance(user_id, bet_amount)
                embed.color = discord.Color.orange()
                embed.add_field(name="Result", value="🤝 **PUSH!** It's a tie", inline=False)
                payout = bet_amount
                profit = 0
        
        # Update stats
        await self.db.update_player(user_id, {
            "games_played": player["games_played"] + 1,
            "total_won": player["total_won"] + (profit if profit > 0 else 0),
            "total_lost": player["total_lost"] + (abs(profit) if profit < 0 else 0)
        })
        
        # Show payout info
        if profit > 0:
            embed.add_field(name="Payout", value=CurrencyUtils.format_amount(payout), inline=True)
            embed.add_field(name="Profit", value=f"+{CurrencyUtils.format_amount(profit)}", inline=True)
        elif profit < 0:
            embed.add_field(name="Lost", value=f"-{CurrencyUtils.format_amount(bet_amount)}", inline=True)
        
        # Show new balance
        updated_player = await self.db.get_player(user_id)
        embed.add_field(name="New Balance", value=CurrencyUtils.format_amount(updated_player["balance"]), inline=False)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="higherorlower", description="Guess if the next card will be higher or lower")
    @app_commands.describe(
        prediction="Higher or Lower prediction",
        bet="Amount to bet"
    )
    @app_commands.choices(prediction=[
        app_commands.Choice(name="Higher", value="higher"),
        app_commands.Choice(name="Lower", value="lower")
    ])
    async def higherorlower(self, interaction: discord.Interaction, prediction: str, bet: str):
        """Higher or Lower card guessing game"""
        user_id = interaction.user.id
        
        # Parse bet amount
        bet_amount = CurrencyUtils.parse_amount(bet)
        if bet_amount is None:
            await interaction.response.send_message("❌ Invalid bet amount!", ephemeral=True)
            return
        
        # Get player data
        player = await self.db.get_player(user_id)
        
        # Handle "all" bet
        if bet_amount == -1:
            bet_amount = player["balance"]
        
        # Validate bet
        is_valid, error_msg = CurrencyUtils.validate_bet(bet_amount, player["balance"], MIN_BET, MAX_BET)
        if not is_valid:
            await interaction.response.send_message(f"❌ {error_msg}", ephemeral=True)
            return
        
        # Subtract bet from balance
        success = await self.db.subtract_balance(user_id, bet_amount)
        if not success:
            await interaction.response.send_message("❌ Insufficient funds!", ephemeral=True)
            return
        
        # Generate cards
        card_values = list(range(1, 14))  # A=1, 2-10, J=11, Q=12, K=13
        card_names = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
        suits = ['♠', '♥', '♦', '♣']
        
        first_card_value = random.choice(card_values)
        second_card_value = random.choice(card_values)
        
        first_card_name = card_names[first_card_value - 1]
        second_card_name = card_names[second_card_value - 1]
        
        first_suit = random.choice(suits)
        second_suit = random.choice(suits)
        
        # Determine if prediction was correct
        if prediction == "higher":
            won = second_card_value > first_card_value
        else:
            won = second_card_value < first_card_value
        
        # Handle ties (house wins)
        if second_card_value == first_card_value:
            won = False
        
        # Calculate payout
        if won:
            # 1.9:1 payout (with house edge)
            payout = int(bet_amount * 1.9)
            await self.db.add_balance(user_id, payout)
            profit = payout - bet_amount
        else:
            payout = 0
            profit = -bet_amount
        
        # Update stats
        await self.db.update_player(user_id, {
            "games_played": player["games_played"] + 1,
            "total_won": player["total_won"] + (profit if profit > 0 else 0),
            "total_lost": player["total_lost"] + (abs(profit) if profit < 0 else 0)
        })
        
        # Create response embed
        embed = discord.Embed(
            title="📈 Higher or Lower",
            color=discord.Color.green() if won else discord.Color.red()
        )
        
        embed.add_field(name="First Card", value=f"🃏 **{first_card_name}{first_suit}**", inline=True)
        embed.add_field(name="Second Card", value=f"🃏 **{second_card_name}{second_suit}**", inline=True)
        embed.add_field(name="Your Prediction", value=f"**{prediction.title()}**", inline=True)
        
        if second_card_value == first_card_value:
            embed.add_field(name="Result", value="🤝 **TIE - HOUSE WINS!**", inline=False)
        elif won:
            embed.add_field(name="Result", value="🎉 **CORRECT!** You win!", inline=False)
        else:
            embed.add_field(name="Result", value="💀 **WRONG!** You lose!", inline=False)
        
        embed.add_field(name="Bet Amount", value=CurrencyUtils.format_amount(bet_amount), inline=True)
        
        if won:
            embed.add_field(name="Payout", value=CurrencyUtils.format_amount(payout), inline=True)
            embed.add_field(name="Profit", value=f"+{CurrencyUtils.format_amount(profit)}", inline=True)
        else:
            embed.add_field(name="Lost", value=f"-{CurrencyUtils.format_amount(bet_amount)}", inline=True)
        
        # Get updated balance
        updated_player = await self.db.get_player(user_id)
        embed.add_field(name="New Balance", value=CurrencyUtils.format_amount(updated_player["balance"]), inline=False)
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Games(bot))
