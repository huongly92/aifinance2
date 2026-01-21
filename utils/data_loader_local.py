"""
Data Loader Module
Load và cache dữ liệu từ các file parquet
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import config


@st.cache_data(ttl=3600)  # Cache 1 giờ
def load_all_data():
    """
    Load tất cả dữ liệu từ các file parquet
    
    Returns:
        tuple: (market_df, industry_df, ticker_df)
    """
    market_df = pd.read_parquet(config.MARKET_DATA_FILE)
    industry_df = pd.read_parquet(config.INDUSTRY_DATA_FILE)
    ticker_df = pd.read_parquet(config.TICKER_DATA_FILE)
    
    # Sắp xếp theo thời gian
    market_df = market_df.sort_values(['YEAR', 'QUARTER'])
    industry_df = industry_df.sort_values(['SYMBOL', 'YEAR', 'QUARTER'])
    ticker_df = ticker_df.sort_values(['SYMBOL', 'YEAR', 'QUARTER'])
    
    return market_df, industry_df, ticker_df


@st.cache_data(ttl=3600)
def get_market_data():
    """Load dữ liệu thị trường"""
    return pd.read_parquet(config.MARKET_DATA_FILE).sort_values(['YEAR', 'QUARTER'])


@st.cache_data(ttl=3600)
def get_industry_data():
    """Load dữ liệu ngành"""
    return pd.read_parquet(config.INDUSTRY_DATA_FILE).sort_values(['SYMBOL', 'YEAR', 'QUARTER'])


@st.cache_data(ttl=3600)
def get_ticker_data():
    """Load dữ liệu ticker"""
    return pd.read_parquet(config.TICKER_DATA_FILE).sort_values(['SYMBOL', 'YEAR', 'QUARTER'])


def get_available_quarters(df):
    """
    Lấy danh sách các quarter có sẵn
    
    Args:
        df: DataFrame chứa cột QUARTER và YEAR
        
    Returns:
        list: Danh sách các quarter theo format 'YYYYQX'
    """
    quarters = df[['YEAR', 'QUARTER']].drop_duplicates()
    quarters['KEY'] = quarters['YEAR'].astype(str) + quarters['QUARTER']
    return sorted(quarters['KEY'].unique())


def get_available_industries(industry_df):
    """
    Lấy danh sách các ngành có sẵn
    
    Args:
        industry_df: DataFrame ngành
        
    Returns:
        list: Danh sách tên ngành
    """
    return sorted(industry_df['SYMBOL'].unique())


def get_available_tickers(ticker_df):
    """
    Lấy danh sách các ticker có sẵn
    
    Args:
        ticker_df: DataFrame ticker
        
    Returns:
        list: Danh sách ticker symbols
    """
    return sorted(ticker_df['SYMBOL'].unique())


def get_ticker_info(ticker_df, symbol):
    """
    Lấy thông tin chi tiết của một ticker
    
    Args:
        ticker_df: DataFrame ticker
        symbol: Mã cổ phiếu
        
    Returns:
        dict: Thông tin ticker hoặc None nếu không tìm thấy
    """
    ticker_data = ticker_df[ticker_df['SYMBOL'] == symbol]
    if ticker_data.empty:
        return None
    
    # Lấy dữ liệu quý gần nhất
    latest = ticker_data.iloc[-1]
    
    return {
        'symbol': symbol,
        'industry': latest.get('LEVEL2_NAME_EN', 'N/A'),
        'cal_group': latest.get('CAL_GROUP', 'N/A'),
        'latest_quarter': latest.get('QUARTER', 'N/A'),
        'latest_year': latest.get('YEAR', 'N/A')
    }


def filter_data_by_date_range(df, start_quarter, end_quarter):
    """
    Lọc dữ liệu theo khoảng thời gian
    
    Args:
        df: DataFrame
        start_quarter: Quarter bắt đầu (format: 'YYYYQX')
        end_quarter: Quarter kết thúc (format: 'YYYYQX')
        
    Returns:
        DataFrame: Dữ liệu đã được lọc
    """
    start_year = int(start_quarter[:4])
    start_q = int(start_quarter[-1])
    end_year = int(end_quarter[:4])
    end_q = int(end_quarter[-1])
    
    mask = (
        ((df['YEAR'] > start_year) | ((df['YEAR'] == start_year) & (df['QUARTER'].str[-1].astype(int) >= start_q))) &
        ((df['YEAR'] < end_year) | ((df['YEAR'] == end_year) & (df['QUARTER'].str[-1].astype(int) <= end_q)))
    )
    
    return df[mask]


def get_latest_data(df, symbol=None):
    """
    Lấy dữ liệu quý gần nhất
    
    Args:
        df: DataFrame
        symbol: Mã ticker hoặc ngành (optional)
        
    Returns:
        Series hoặc DataFrame: Dữ liệu quý gần nhất
    """
    if symbol:
        df = df[df['SYMBOL'] == symbol]
    
    if df.empty:
        return None
    
    # Lấy quý gần nhất
    latest_idx = df[['YEAR', 'QUARTER']].apply(lambda x: (x['YEAR'], x['QUARTER']), axis=1).idxmax()
    return df.loc[latest_idx]


def get_metrics_for_tickers(ticker_df, symbols, metrics):
    """
    Lấy các chỉ số tài chính cho nhiều ticker
    
    Args:
        ticker_df: DataFrame ticker
        symbols: List các mã cổ phiếu
        metrics: List các chỉ số cần lấy
        
    Returns:
        DataFrame: Bảng so sánh các chỉ số
    """
    result = []
    
    for symbol in symbols:
        latest = get_latest_data(ticker_df, symbol)
        if latest is not None:
            row = {'Mã CK': symbol}
            for metric in metrics:
                row[metric] = latest.get(metric, None)
            result.append(row)
    
    return pd.DataFrame(result)


def search_tickers(ticker_df, keyword):
    """
    Tìm kiếm ticker theo từ khóa
    
    Args:
        ticker_df: DataFrame ticker
        keyword: Từ khóa tìm kiếm
        
    Returns:
        list: Danh sách ticker phù hợp
    """
    keyword = keyword.upper()
    matching = ticker_df[ticker_df['SYMBOL'].str.contains(keyword, na=False)]['SYMBOL'].unique()
    return sorted(matching)
