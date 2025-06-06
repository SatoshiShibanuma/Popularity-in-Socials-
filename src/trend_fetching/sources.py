from abc import ABC, abstractmethod
from typing import List, Dict, Any
import requests
from pydantic import BaseModel, Field, ValidationError

class TrendSource(ABC):
    """Abstract base class for trend data sources."""

    @abstractmethod
    def fetch_trends(self) -> List[Dict[str, Any]]:
        """
        Fetch trends from a specific source.
        
        Returns:
            List of trend dictionaries containing trend metadata.
        
        Raises:
            ValueError: If trend fetching fails.
        """
        pass

class TrendItem(BaseModel):
    """
    Structured model representing a single trend item.
    
    Validates and standardizes trend data across different sources.
    """
    name: str = Field(..., description="Name or title of the trend")
    relevance_score: float = Field(default=0.0, ge=0.0, le=1.0, 
                                   description="Normalized relevance score between 0 and 1")
    source: str = Field(..., description="Source of the trend")
    category: str = Field(default="general", description="Trend category")
    additional_metadata: Dict[str, Any] = Field(default_factory=dict)

class CoinMarketCapTrendSource(TrendSource):
    """
    Trend source implementation for CoinMarketCap trending cryptocurrencies.
    
    Note: Requires valid API key and respects rate limits.
    """
    
    def __init__(self, api_key: str):
        """
        Initialize CoinMarketCap trend source.
        
        Args:
            api_key (str): CoinMarketCap API authentication key
        """
        self._api_key = api_key
        self._base_url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/trending"
    
    def fetch_trends(self) -> List[TrendItem]:
        """
        Fetch trending cryptocurrencies from CoinMarketCap.
        
        Returns:
            List of validated TrendItem instances.
        
        Raises:
            ValueError: If API request fails or returns invalid data.
        """
        try:
            headers = {
                'X-CMC_PRO_API_KEY': self._api_key,
                'Accept': 'application/json'
            }
            
            response = requests.get(self._base_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json().get('data', [])
            
            trends = [
                TrendItem(
                    name=item['name'],
                    relevance_score=item.get('score', 0.5),
                    source='CoinMarketCap',
                    category='cryptocurrency',
                    additional_metadata=item
                ) for item in data
            ]
            
            return trends
        
        except requests.RequestException as e:
            raise ValueError(f"Failed to fetch trends: {e}") from e
        except (KeyError, ValidationError) as e:
            raise ValueError(f"Invalid trend data: {e}") from e

class TrendAggregator:
    """
    Aggregates trends from multiple sources and provides unified trend data.
    """
    
    def __init__(self, sources: List[TrendSource]):
        """
        Initialize trend aggregator with multiple sources.
        
        Args:
            sources (List[TrendSource]): List of trend sources to aggregate
        """
        self._sources = sources
    
    def get_trends(self) -> List[TrendItem]:
        """
        Retrieve and aggregate trends from all configured sources.
        
        Returns:
            List of aggregated and validated trend items.
        """
        all_trends = []
        
        for source in self._sources:
            try:
                source_trends = source.fetch_trends()
                all_trends.extend(source_trends)
            except ValueError as e:
                # Log the error and continue with other sources
                print(f"Error fetching trends from {source.__class__.__name__}: {e}")
        
        # Sort trends by relevance score in descending order
        return sorted(all_trends, key=lambda x: x.relevance_score, reverse=True)