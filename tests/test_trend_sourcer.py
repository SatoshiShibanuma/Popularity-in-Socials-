import pytest
from src.trend_sourcer import TrendSourcer, TrendData

def test_trend_sourcer_initialization():
    """Test that TrendSourcer can be initialized without errors."""
    sourcer = TrendSourcer()
    assert sourcer is not None

def test_trend_data_creation():
    """Test creating a TrendData object."""
    trend = TrendData(
        name="Bitcoin",
        symbol="BTC",
        price=50000.0,
        trend_score=1.0,
        volume=1000000.0,
        market_cap=1000000000.0
    )
    assert trend.name == "Bitcoin"
    assert trend.symbol == "BTC"

def test_get_top_trends():
    """Test retrieving top trends."""
    sourcer = TrendSourcer()
    top_trends = sourcer.get_top_trends(limit=5)
    
    assert len(top_trends) <= 5
    assert all(isinstance(trend, TrendData) for trend in top_trends)
    
    # Verify trends are sorted by market cap
    for i in range(len(top_trends) - 1):
        assert top_trends[i].market_cap >= top_trends[i+1].market_cap

def test_trend_data_attributes():
    """Validate TrendData has all required attributes."""
    trend = TrendData(
        name="Ethereum",
        symbol="ETH",
        price=3000.0,
        trend_score=2.0,
        volume=500000.0,
        market_cap=500000000.0
    )
    
    assert hasattr(trend, 'name')
    assert hasattr(trend, 'symbol')
    assert hasattr(trend, 'price')
    assert hasattr(trend, 'trend_score')
    assert hasattr(trend, 'volume')
    assert hasattr(trend, 'market_cap')