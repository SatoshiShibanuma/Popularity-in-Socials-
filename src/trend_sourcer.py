import requests
from typing import List, Dict, Optional
import logging
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TrendData:
    """
    Structured data class to represent cryptocurrency trend information.
    """
    name: str
    symbol: str
    price: float
    trend_score: float
    volume: float
    market_cap: float

class TrendSourcer:
    """
    A comprehensive trend sourcing class for cryptocurrency market trends.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the trend sourcer with optional API key.
        
        :param api_key: Optional API key for external services
        """
        self.api_key = api_key
        self.sources = [
            self._fetch_coingecko_trends,
            self._fetch_cryptocompare_trends
        ]
    
    def _fetch_coingecko_trends(self) -> List[TrendData]:
        """
        Fetch trends from CoinGecko API.
        
        :return: List of trend data
        """
        try:
            response = requests.get(
                'https://api.coingecko.com/api/v3/coins/markets',
                params={
                    'vs_currency': 'usd', 
                    'order': 'market_cap_desc', 
                    'per_page': 10
                }
            )
            response.raise_for_status()
            coins = response.json()
            
            return [
                TrendData(
                    name=coin['name'],
                    symbol=coin['symbol'],
                    price=coin['current_price'],
                    trend_score=coin['market_cap_rank'],
                    volume=coin['total_volume'],
                    market_cap=coin['market_cap']
                ) for coin in coins
            ]
        except requests.RequestException as e:
            logger.error(f"CoinGecko API error: {e}")
            return []
    
    def _fetch_cryptocompare_trends(self) -> List[TrendData]:
        """
        Fetch trends from CryptoCompare API.
        
        :return: List of trend data
        """
        try:
            response = requests.get(
                'https://min-api.cryptocompare.com/data/top/totalvolfull',
                params={
                    'limit': 10,
                    'tsym': 'USD'
                }
            )
            response.raise_for_status()
            data = response.json().get('Data', [])
            
            return [
                TrendData(
                    name=entry['CoinInfo']['FullName'],
                    symbol=entry['CoinInfo']['Name'],
                    price=entry['RAW']['USD']['PRICE'],
                    trend_score=entry['RAW']['USD']['VOLUME24HOUR'],
                    volume=entry['RAW']['USD']['VOLUME24HOURTO'],
                    market_cap=entry['RAW']['USD']['MKTCAP']
                ) for entry in data
            ]
        except requests.RequestException as e:
            logger.error(f"CryptoCompare API error: {e}")
            return []
    
    def get_top_trends(self, limit: int = 5) -> List[TrendData]:
        """
        Aggregate and rank trends from multiple sources.
        
        :param limit: Number of top trends to return
        :return: Sorted list of top trends
        """
        all_trends = []
        for source in self.sources:
            all_trends.extend(source())
        
        # Sort by trend score (in this case, market cap)
        sorted_trends = sorted(
            all_trends, 
            key=lambda x: x.market_cap, 
            reverse=True
        )
        
        return sorted_trends[:limit]