import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json

class StockDataGenerator:
    def __init__(self, symbol: str, initial_price: float = 100.0, volatility: float = 2.0):
        self.symbol = symbol
        self.current_price = initial_price
        self.volatility = volatility
        self.last_update = datetime.now()
    
    def generate_daily_data(self, days: int = 30) -> Dict:
        """Generate mock stock data for the specified number of days"""
        result = {
            "symbol": self.symbol,
            "time_series": {},
            "meta": {
                "generated_at": datetime.now().isoformat(),
                "data_points": days
            }
        }
        
        current_date = datetime.now()
        current_price = self.current_price
        
        for i in range(days):
            date_str = current_date.strftime("%Y-%m-%d")
            
            # Generate random price movements
            open_price = current_price
            high = open_price * (1 + random.uniform(0, self.volatility/100))
            low = open_price * (1 - random.uniform(0, self.volatility/100))
            close = random.uniform(low, high)
            volume = random.randint(100000, 1000000)
            
            result["time_series"][date_str] = {
                "1. open": round(open_price, 2),
                "2. high": round(max(open_price, high, low, close), 2),
                "3. low": round(min(open_price, high, low, close), 2),
                "4. close": round(close, 2),
                "5. volume": volume
            }
            
            # Update for next day
            current_price = close * (1 + random.uniform(-self.volatility/100, self.volatility/100))
            current_date -= timedelta(days=1)
        
        return result

    def get_formatted_data(self, days: int = 30) -> List[Dict]:
        """Get data in the requested format"""
        data = self.generate_daily_data(days)
        formatted_data = []
        
        for date, values in data["time_series"].items():
            formatted_data.append({
                "date": date,
                "open": float(values["1. open"]),
                "high": float(values["2. high"]),
                "low": float(values["3. low"]),
                "close": float(values["4. close"]),
                "volume": int(values["5. volume"]),
                "value": float(values["4. close"])  # Same as close price
            })
        
        return formatted_data

# Example usage
if __name__ == "__main__":
    # Create a stock data generator for AAPL
    aapl = StockDataGenerator("AAPL", initial_price=150.0, volatility=2.5)
    
    # Get 5 days of formatted data
    data = aapl.get_formatted_data(5)
    print(json.dumps(data, indent=2))