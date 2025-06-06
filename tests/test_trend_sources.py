import pytest
from unittest.mock import Mock, patch
from src.trend_fetching.sources import (
    TrendSource, 
    CoinMarketCapTrendSource, 
    TrendAggregator, 
    TrendItem
)

class MockTrendSource(TrendSource):
    """Mock implementation of TrendSource for testing."""
    
    def __init__(self, trends):
        self._trends = trends
    
    def fetch_trends(self):
        return self._trends

def test_trend_item_validation():
    """Test TrendItem model validation."""
    trend_data = {
        'name': 'Bitcoin',
        'relevance_score': 0.9,
        'source': 'Test',
        'category': 'cryptocurrency'
    }
    
    trend_item = TrendItem(**trend_data)
    
    assert trend_item.name == 'Bitcoin'
    assert trend_item.relevance_score == 0.9

def test_trend_aggregator_basic():
    """Test trend aggregation functionality."""
    mock_trends1 = [
        TrendItem(name='Bitcoin', relevance_score=0.9, source='Source1'),
        TrendItem(name='Ethereum', relevance_score=0.7, source='Source1')
    ]
    
    mock_trends2 = [
        TrendItem(name='Dogecoin', relevance_score=0.5, source='Source2')
    ]
    
    mock_source1 = MockTrendSource(mock_trends1)
    mock_source2 = MockTrendSource(mock_trends2)
    
    aggregator = TrendAggregator([mock_source1, mock_source2])
    
    aggregated_trends = aggregator.get_trends()
    
    assert len(aggregated_trends) == 3
    assert aggregated_trends[0].name == 'Bitcoin'
    assert aggregated_trends[0].relevance_score == 0.9

@patch('requests.get')
def test_coinmarketcap_trend_source(mock_get):
    """Test CoinMarketCap trend source integration."""
    mock_response = Mock()
    mock_response.json.return_value = {
        'data': [
            {
                'name': 'Bitcoin', 
                'score': 0.9,
                'market_cap': 500000000000
            }
        ]
    }
    mock_response.raise_for_status = Mock()
    mock_get.return_value = mock_response
    
    trend_source = CoinMarketCapTrendSource('mock_api_key')
    
    trends = trend_source.fetch_trends()
    
    assert len(trends) == 1
    assert trends[0].name == 'Bitcoin'
    assert trends[0].relevance_score == 0.9
    assert trends[0].source == 'CoinMarketCap'

def test_trend_aggregator_error_handling():
    """Test trend aggregator's resilience to source failures."""
    mock_good_source = MockTrendSource([
        TrendItem(name='Bitcoin', relevance_score=0.9, source='GoodSource')
    ])
    
    class FailingSource(TrendSource):
        def fetch_trends(self):
            raise ValueError("Simulated source failure")
    
    failing_source = FailingSource()
    
    aggregator = TrendAggregator([mock_good_source, failing_source])
    
    aggregated_trends = aggregator.get_trends()
    
    assert len(aggregated_trends) == 1
    assert aggregated_trends[0].name == 'Bitcoin'