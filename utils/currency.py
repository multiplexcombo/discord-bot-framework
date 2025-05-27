import re
from typing import Union

class CurrencyUtils:
    """Utilities for handling currency conversion and formatting"""
    
    # Multipliers for shorthand notation
    MULTIPLIERS = {
        'y': 1_000_000_000_000_000_000_000_000,  # yotta
        'z': 1_000_000_000_000_000_000_000,      # zetta
        'e': 1_000_000_000_000_000_000,          # exa
        'p': 1_000_000_000_000_000,              # peta
        't': 1_000_000_000_000,                  # tera
        'g': 1_000_000_000,                      # giga
        'm': 1_000_000,                          # mega
        'k': 1_000,                              # kilo
    }
    
    @classmethod
    def parse_amount(cls, amount_str: str) -> Union[int, None]:
        """
        Parse amount string with shorthand notation
        Examples: 1k = 1000, 5m = 5000000, 10.5g = 10500000000
        """
        if not amount_str:
            return None
            
        amount_str = str(amount_str).lower().strip()
        
        # Handle "all" or "max"
        if amount_str in ['all', 'max']:
            return -1  # Special value for all money
            
        # Regular expression to match number with optional suffix
        pattern = r'^(\d+(?:\.\d+)?)\s*([yzeptgmk]?)$'
        match = re.match(pattern, amount_str)
        
        if not match:
            # Try parsing as plain number
            try:
                return int(float(amount_str))
            except ValueError:
                return None
        
        number_part = float(match.group(1))
        suffix = match.group(2)
        
        if suffix and suffix in cls.MULTIPLIERS:
            return int(number_part * cls.MULTIPLIERS[suffix])
        else:
            return int(number_part)
    
    @classmethod
    def format_amount(cls, amount: int) -> str:
        """
        Format large numbers with appropriate suffixes
        """
        if amount == 0:
            return "0"
            
        # Find the largest suffix that applies
        for suffix, multiplier in sorted(cls.MULTIPLIERS.items(), 
                                       key=lambda x: x[1], reverse=True):
            if amount >= multiplier:
                value = amount / multiplier
                if value == int(value):
                    return f"{int(value)}{suffix}"
                else:
                    return f"{value:.1f}{suffix}"
        
        # Format with commas for readability
        return f"{amount:,}"
    
    @classmethod
    def validate_bet(cls, bet_amount: int, user_balance: int, 
                    min_bet: int = 1, max_bet: int = None) -> tuple[bool, str]:
        """
        Validate if a bet is valid
        Returns (is_valid, error_message)
        """
        if bet_amount < min_bet:
            return False, f"Minimum bet is {cls.format_amount(min_bet)}"
            
        if max_bet and bet_amount > max_bet:
            return False, f"Maximum bet is {cls.format_amount(max_bet)}"
            
        if bet_amount > user_balance:
            return False, "Insufficient funds!"
            
        return True, ""
    
    @classmethod
    def calculate_payout(cls, bet_amount: int, multiplier: float) -> int:
        """Calculate payout from bet amount and multiplier"""
        return int(bet_amount * multiplier)
