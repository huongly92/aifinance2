"""
Data Loader Module
Load và cache dữ liệu từ Google Cloud Storage
"""
import os
import certifi
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
os.environ['SSL_CERT_FILE'] = certifi.where()

import streamlit as st
import pandas as pd
from pathlib import Path
from io import BytesIO
from google.cloud import storage
from google.oauth2 import service_account
import config

# ========== GCS CONFIGURATION ==========
# Thay đổi các giá trị này theo GCS bucket của bạn
GCS_BUCKET_NAME = "aifinance-data-storage"  # Tên bucket GCS của bạn
GCS_DATA_FOLDER = "data/"  # Thư mục chứa data trong bucket (có thể để trống nếu files ở root)

# Tên các file trong GCS
GCS_MARKET_FILE = f"{GCS_DATA_FOLDER}market_analysis.parquet"
GCS_INDUSTRY_FILE = f"{GCS_DATA_FOLDER}industry_analysis.parquet"
GCS_TICKER_FILE = f"{GCS_DATA_FOLDER}ticker_analysis.parquet"


def get_gcs_client():
    """
    Khởi tạo GCS client với credentials từ Streamlit secrets
    
    Returns:
        storage.Client: GCS client đã được authenticate
    """
    try:
        credentials = service_account.Credentials.from_service_account_info(
            st.secrets["gcp_service_account"]
        )
        client = storage.Client(credentials=credentials)
        return client
    except Exception as e:
        st.error(f"❌ Lỗi khi khởi tạo GCS client: {str(e)}")
        raise


@st.cache_data(ttl=3600)  # Cache 1 giờ
def load_parquet_from_gcs(bucket_name, blob_name):
    """
    Load file parquet trực tiếp từ GCS
    
    Args:
        bucket_name (str): Tên GCS bucket
        blob_name (str): Tên file trong bucket
        
    Returns:
        pd.DataFrame: DataFrame đã load
    """
    try:
        # Khởi tạo GCS client
        client = get_gcs_client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        
        # Download file content vào memory
        content = blob.download_as_bytes()
        
        # Load parquet từ bytes
        df = pd.read_parquet(BytesIO(content))
        
        return df
        
    except Exception as e:
        st.error(f"❌ Lỗi khi load file {blob_name} từ GCS: {str(e)}")
        raise


@st.cache_data(ttl=3600)  # Cache 1 giờ
def load_all_data():
    """
    Load tất cả dữ liệu từ GCS
    
    Returns:
        tuple: (market_df, industry_df, ticker_df)
    """
    try:
        with st.spinner("⏳ Đang tải dữ liệu từ Google Cloud Storage..."):
            # Load từng file từ GCS
            market_df = load_parquet_from_gcs(GCS_BUCKET_NAME, GCS_MARKET_FILE)
            industry_df = load_parquet_from_gcs(GCS_BUCKET_NAME, GCS_INDUSTRY_FILE)
            ticker_df = load_parquet_from_gcs(GCS_BUCKET_NAME, GCS_TICKER_FILE)
            
            # Sắp xếp theo thời gian
            market_df = market_df.sort_values(['YEAR', 'QUARTER'])
            industry_df = industry_df.sort_values(['SYMBOL', 'YEAR', 'QUARTER'])
            ticker_df = ticker_df.sort_values(['SYMBOL', 'YEAR', 'QUARTER'])
            
            st.success("✅ Đã tải xong dữ liệu từ GCS!")
            
            return market_df, industry_df, ticker_df
            
    except Exception as e:
        st.error(f"""
        ❌ **Lỗi khi load dữ liệu từ GCS!**
        
        Vui lòng kiểm tra:
        - GCS credentials đã được cấu hình trong secrets.toml
        - Bucket name: `{GCS_BUCKET_NAME}`
        - Files tồn tại trong bucket:
          - {GCS_MARKET_FILE}
          - {GCS_INDUSTRY_FILE}
          - {GCS_TICKER_FILE}
        
        Chi tiết lỗi: {str(e)}
        """)
        raise


@st.cache_data(ttl=3600)
def get_market_data():
    """Load dữ liệu thị trường từ GCS"""
    df = load_parquet_from_gcs(GCS_BUCKET_NAME, GCS_MARKET_FILE)
    return df.sort_values(['YEAR', 'QUARTER'])


@st.cache_data(ttl=3600)
def get_industry_data():
    """Load dữ liệu ngành từ GCS"""
    df = load_parquet_from_gcs(GCS_BUCKET_NAME, GCS_INDUSTRY_FILE)
    return df.sort_values(['SYMBOL', 'YEAR', 'QUARTER'])


@st.cache_data(ttl=3600)
def get_ticker_data():
    """Load dữ liệu ticker từ GCS"""
    df = load_parquet_from_gcs(GCS_BUCKET_NAME, GCS_TICKER_FILE)
    return df.sort_values(['SYMBOL', 'YEAR', 'QUARTER'])


def list_available_files_in_gcs():
    """
    Liệt kê các files có sẵn trong GCS bucket
    
    Returns:
        list: Danh sách tên files
    """
    try:
        client = get_gcs_client()
        bucket = client.bucket(GCS_BUCKET_NAME)
        blobs = bucket.list_blobs(prefix=GCS_DATA_FOLDER)
        return [blob.name for blob in blobs]
    except Exception as e:
        st.warning(f"⚠️ Không thể list files trong GCS: {str(e)}")
        return []


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


# ========== UTILITY FUNCTIONS FOR GCS ==========

def upload_parquet_to_gcs(df, bucket_name, blob_name):
    """
    Upload DataFrame dưới dạng parquet lên GCS
    
    Args:
        df: DataFrame cần upload
        bucket_name: Tên bucket
        blob_name: Tên file trong bucket
        
    Returns:
        bool: True nếu thành công
    """
    try:
        client = get_gcs_client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        
        # Convert DataFrame to parquet bytes
        buffer = BytesIO()
        df.to_parquet(buffer, index=False)
        buffer.seek(0)
        
        # Upload
        blob.upload_from_file(buffer, content_type='application/octet-stream')
        
        st.success(f"✅ Đã upload {blob_name} lên GCS!")
        return True
        
    except Exception as e:
        st.error(f"❌ Lỗi khi upload {blob_name}: {str(e)}")
        return False


def check_gcs_connection():
    """
    Kiểm tra kết nối với GCS
    
    Returns:
        bool: True nếu kết nối thành công
    """
    try:
        client = get_gcs_client()
        bucket = client.bucket(GCS_BUCKET_NAME)
        exists = bucket.exists()
        
        if exists:
            st.success(f"✅ Kết nối GCS thành công! Bucket: `{GCS_BUCKET_NAME}`")
            return True
        else:
            st.error(f"❌ Bucket `{GCS_BUCKET_NAME}` không tồn tại!")
            return False
            
    except Exception as e:
        st.error(f"❌ Không thể kết nối với GCS: {str(e)}")
        return False
