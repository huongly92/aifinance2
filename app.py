"""
Main Application File
Dashboard Phân Tích Chứng Khoán Việt Nam
Version: GCS Integration
"""

import streamlit as st
import sys
from pathlib import Path

# Add root directory to path
ROOT_DIR = Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR))

import config
from utils.data_loader import load_all_data, check_gcs_connection

# ========== PAGE CONFIGURATION ==========
st.set_page_config(
    page_title=config.APP_TITLE,
    page_icon=config.APP_ICON,
    layout=config.LAYOUT,
    initial_sidebar_state=config.INITIAL_SIDEBAR_STATE
)

# ========== CHECK GCS CONNECTION (Optional) ==========
# Uncomment dòng dưới nếu muốn kiểm tra kết nối GCS khi khởi động app
# with st.sidebar.expander("🔧 GCS Connection Status"):
#     check_gcs_connection()

# ========== LOAD DATA FROM GCS ==========
@st.cache_data(ttl=3600)
def load_data():
    """Load tất cả dữ liệu từ GCS và cache"""
    return load_all_data()

# Load data globally
try:
    with st.spinner("⏳ Đang tải dữ liệu từ Google Cloud Storage..."):
        market_df, industry_df, ticker_df = load_data()
    
    # Store in session state
    if 'market_df' not in st.session_state:
        st.session_state.market_df = market_df
    if 'industry_df' not in st.session_state:
        st.session_state.industry_df = industry_df
    if 'ticker_df' not in st.session_state:
        st.session_state.ticker_df = ticker_df
    
    # Show success message (will disappear after first load due to cache)
    if 'data_loaded' not in st.session_state:
        st.success("✅ Dữ liệu đã được tải từ GCS và cached!")
        st.session_state.data_loaded = True
        
except Exception as e:
    st.error(f"""
    ❌ **Lỗi khi load dữ liệu từ Google Cloud Storage!**
    
    Vui lòng kiểm tra:
    
    1. **GCS Credentials**: 
       - File `.streamlit/secrets.toml` đã được tạo
       - Credentials đúng format
       - Service account có quyền Storage Object Viewer
    
    2. **Bucket Configuration**:
       - Bucket name đúng trong `utils/data_loader.py`
       - Files parquet tồn tại trong bucket:
         - market_analysis.parquet
         - industry_analysis.parquet
         - ticker_analysis.parquet
    
    3. **Network**:
       - Có kết nối internet
       - Firewall không chặn GCS
    
    ---
    
    **Chi tiết lỗi**: 
    ```
    {str(e)}
    ```
    
    ---
    
    **💡 Gợi ý khắc phục**:
    - Chạy `python test_gcs_connection.py` để test kết nối
    - Xem file `TROUBLESHOOTING.md` để biết thêm chi tiết
    - Kiểm tra logs trong terminal
    """)
    st.stop()

# ========== SIDEBAR ==========
with st.sidebar:
    st.title(config.APP_ICON + " Dashboard CK")
    st.markdown("---")
    
    # GCS Status Badge
    st.success("☁️ **Data Source**: Google Cloud Storage")
    
    st.markdown("---")
    
    # Navigation
    st.markdown("### 📌 Điều hướng")
    st.markdown("""
    - 🏛️ Tổng Quan Thị Trường
    - 🏭 Phân Tích Ngành
    - 📊 Phân Tích Cổ Phiếu
    - ⚖️ So Sánh & Đối Chiếu
    - 🔍 Sàng Lọc & Tìm Kiếm
    - ⭐ Danh Mục Theo Dõi             
    """)
    
    st.markdown("---")
    
    # Data info
    st.markdown("### 📈 Thông tin dữ liệu")
    st.info(f"""
    **Thị trường**: {len(market_df)} quý  
    **Ngành**: {industry_df['SYMBOL'].nunique()} ngành  
    **Cổ phiếu**: {ticker_df['SYMBOL'].nunique()} mã
    """)
    
    # Latest quarter
    latest_quarter = market_df.iloc[-1]['QUARTER']
    latest_year = market_df.iloc[-1]['YEAR']
    st.success(f"📅 Quý mới nhất: **{latest_quarter} {latest_year}**")
    
    st.markdown("---")
    
    # Data refresh button
    if st.button("🔄 Refresh Data from GCS"):
        # Clear cache
        st.cache_data.clear()
        st.rerun()
    
    st.markdown("---")
    st.caption("Dashboard v1.0 (GCS) | BSC Research")

# ========== MAIN PAGE ==========
st.title("📊 Dashboard Phân Tích Chứng Khoán Việt Nam")

# Info banner about GCS
st.info("""
☁️ **App này đang load dữ liệu trực tiếp từ Google Cloud Storage**  
Dữ liệu được cache trong 1 giờ để tối ưu performance. Click "🔄 Refresh Data" ở sidebar để load lại.
""")

st.markdown("---")

st.markdown("""
### Chào mừng đến với Dashboard Phân Tích Chứng Khoán! 👋

Dashboard này cung cấp công cụ phân tích toàn diện cho đầu tư chứng khoán với:

#### 🎯 Các tính năng chính:

1. **🏛️ Tổng Quan Thị Trường**
   - Theo dõi xu hướng thị trường theo thời gian
   - Phân tích các chỉ số vĩ mô (P/E, P/B, ROE, etc.)
   - Đánh giá sức khỏe tổng thể thị trường

2. **🏭 Phân Tích Ngành**
   - So sánh hiệu suất giữa các ngành
   - Xếp hạng ngành theo các tiêu chí
   - Phát hiện xu hướng chuyển dịch vốn

3. **📊 Phân Tích Cổ Phiếu**
   - Phân tích sâu từng mã cổ phiếu
   - Đánh giá định giá, sinh lời, dòng tiền
   - Phân tích rủi ro với Z-Score

4. **⚖️ So Sánh & Đối Chiếu**
   - So sánh nhiều cổ phiếu cùng lúc
   - Ma trận tương quan
   - Scoring và xếp hạng tổng hợp

5. **🔍 Sàng Lọc & Tìm Kiếm**
   - Tìm cơ hội đầu tư với bộ lọc đa tiêu chí
   - Các chiến lược lọc có sẵn
   - Export kết quả

6. **⭐ Danh Mục Theo Dõi**
   - Quản lý watchlist cá nhân
   - Theo dõi thay đổi
   - Phân tích danh mục

---

### 🚀 Hướng dẫn sử dụng:

1. **Chọn trang** từ thanh điều hướng bên trái
2. **Tùy chỉnh bộ lọc** theo nhu cầu phân tích
3. **Tương tác với biểu đồ**: zoom, pan, hover để xem chi tiết
4. **Export dữ liệu** khi cần thiết
5. **Refresh data** từ GCS bằng nút ở sidebar

---

### 📊 Thống kê dữ liệu:
""")

# Display data statistics
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Số quý dữ liệu",
        len(market_df),
        help="Tổng số quý có dữ liệu thị trường"
    )

with col2:
    st.metric(
        "Số ngành",
        industry_df['SYMBOL'].nunique(),
        help="Tổng số ngành được phân tích"
    )

with col3:
    st.metric(
        "Số mã CK",
        ticker_df['SYMBOL'].nunique(),
        help="Tổng số mã cổ phiếu có dữ liệu"
    )

st.markdown("---")

# Quick stats
st.markdown("### 📈 Thống kê nhanh (Quý gần nhất)")

latest_market = market_df.iloc[-1]

col1, col2, col3, col4 = st.columns(4)

with col1:
    from utils.formatters import format_billion 
    from utils.formatters import format_change
    st.metric(
        "Vốn hóa TT",
        format_billion(latest_market.get('MARKET_CAP_EOQ', 0)),
        format_change(latest_market.get('MARKET_CAP_EOQ_GYOY', 0)) if 'MARKET_CAP_EOQ_GYOY' in latest_market else None
    )

with col2:
    from utils.formatters import format_ratio
    st.metric(
        "P/E Trung bình",
        format_ratio(latest_market.get('PE_EOQ', 0)),
        help="Price-to-Earnings ratio trung bình thị trường"
    )

with col3:
    from utils.formatters import format_percent
    st.metric(
        "ROE Trung bình",
        format_percent(latest_market.get('ROAE', 0)),
        help="Return on Equity trung bình thị trường"
    )

with col4:
    st.metric(
        "P/B Trung bình",
        format_ratio(latest_market.get('PB_EOQ', 0)),
        help="Price-to-Book ratio trung bình thị trường"
    )

st.markdown("---")

st.info("""
💡 **Mẹo sử dụng:**
- Sử dụng thanh bên trái để điều hướng giữa các trang
- Mỗi trang có bộ lọc riêng để tùy chỉnh phân tích
- Biểu đồ có thể zoom, pan và tải xuống
- Bảng dữ liệu có thể sắp xếp và export
- Dữ liệu từ GCS được cache 1 giờ, click "🔄 Refresh Data" để cập nhật
""")

st.markdown("---")

# Additional info about GCS
with st.expander("ℹ️ Thông tin về Data Source"):
    st.markdown("""
    ### ☁️ Google Cloud Storage Integration
    
    App này sử dụng Google Cloud Storage để lưu trữ và truy xuất dữ liệu:
    
    **Ưu điểm:**
    - ✅ Dữ liệu tập trung, dễ quản lý
    - ✅ Có thể cập nhật dữ liệu mà không cần redeploy app
    - ✅ Chia sẻ data giữa nhiều apps
    - ✅ Backup và version control dễ dàng
    - ✅ Performance tốt với caching
    
    **Cách hoạt động:**
    1. App connect đến GCS bucket khi khởi động
    2. Load các file parquet vào memory
    3. Cache data trong 1 giờ (3600 giây)
    4. Tự động refresh sau khi cache hết hạn
    
    **Để cập nhật dữ liệu:**
    1. Upload files mới lên GCS bucket
    2. Click "🔄 Refresh Data" ở sidebar
    3. Hoặc đợi cache tự động refresh sau 1 giờ
    """)

st.markdown("---")
st.caption("© 2024 BSC Research | Dashboard v1.0 (GCS Integration)")
