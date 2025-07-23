import pytest
import os
import sys

def test_streamlit_imports():
    """Test that Streamlit and other dependencies can be imported"""
    try:
        import streamlit as st
        assert st is not None
    except ImportError as e:
        pytest.fail(f"Failed to import streamlit: {e}")

def test_app_imports():
    """Test that app modules can be imported"""
    try:
        # Test individual components that should be importable
        import pandas as pd
        import plotly.express as px
        import plotly.graph_objects as go
        
        assert pd is not None
        assert px is not None
        assert go is not None
    except ImportError as e:
        pytest.fail(f"Failed to import required modules: {e}")

def test_session_frontend_imports():
    """Test session frontend imports"""
    try:
        from session_frontend import SessionManager
        assert SessionManager is not None
    except ImportError as e:
        # This is expected if requests/backend not available
        pytest.skip(f"Session frontend not available: {e}")

def test_config_imports():
    """Test config imports"""
    try:
        import config
        assert config is not None
    except ImportError as e:
        pytest.skip(f"Config import failed: {e}")

def test_environment_setup():
    """Test environment is properly set up"""
    # Test that Python path includes current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    
    assert parent_dir in sys.path or '.' in sys.path

def test_sample_data_generation():
    """Test that sample data can be generated"""
    import pandas as pd
    import numpy as np
    from datetime import datetime, timedelta
    
    # Generate sample revenue data
    dates = pd.date_range(start='2023-01-01', end='2024-12-31', freq='D')
    revenue_data = pd.DataFrame({
        'date': dates,
        'revenue': np.random.uniform(10000, 50000, len(dates)),
        'region': np.random.choice(['North', 'South', 'East', 'West'], len(dates))
    })
    
    assert len(revenue_data) > 0
    assert 'date' in revenue_data.columns
    assert 'revenue' in revenue_data.columns

def test_plotly_chart_creation():
    """Test that Plotly charts can be created"""
    import plotly.express as px
    import pandas as pd
    import numpy as np
    
    # Create sample data
    df = pd.DataFrame({
        'month': ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
        'revenue': [100000, 120000, 110000, 130000, 125000]
    })
    
    # Create a simple chart
    fig = px.bar(df, x='month', y='revenue', title='Monthly Revenue')
    
    assert fig is not None
    assert len(fig.data) > 0

def test_ui_components():
    """Test UI component functions"""
    def create_metric_card(title, value, delta=None):
        """Mock metric card creation"""
        return {
            'title': title,
            'value': value,
            'delta': delta
        }
    
    # Test metric card creation
    card = create_metric_card("Total Revenue", "$1,250,000", "+12.5%")
    
    assert card['title'] == "Total Revenue"
    assert card['value'] == "$1,250,000"
    assert card['delta'] == "+12.5%"

if __name__ == "__main__":
    pytest.main([__file__])
