# 📊 Dashboard Phân Tích Chứng Khoán Việt Nam

Dashboard phân tích chứng khoán chuyên nghiệp được xây dựng với Python & Streamlit.

## 🎯 Tính Năng

### 1. 🏛️ Tổng Quan Thị Trường
- Theo dõi xu hướng thị trường theo thời gian
- Phân tích các chỉ số vĩ mô (P/E, P/B, ROE, etc.)
- Biểu đồ phân phối và histogram

### 2. 🏭 Phân Tích Ngành
- So sánh hiệu suất giữa các ngành
- Xếp hạng ngành theo tiêu chí
- Top performers

### 3. 📊 Phân Tích Cổ Phiếu
- Phân tích chi tiết từng mã
- Đánh giá định giá, sinh lời, dòng tiền
- Phân tích rủi ro với Z-Score

### 4. ⚖️ So Sánh & Đối Chiếu
- So sánh nhiều cổ phiếu cùng lúc
- Biểu đồ scatter plot
- Bảng so sánh tổng hợp

### 5. 🔍 Sàng Lọc & Tìm Kiếm
- Bộ lọc đa tiêu chí
- Các chiến lược có sẵn:
  - Value Investing
  - Growth Investing
  - Dividend Stocks
  - Quality Stocks
- Export kết quả CSV

### 6. ⭐ Danh Mục Theo Dõi
- Quản lý watchlist cá nhân
- Theo dõi thay đổi
- Xóa/thêm mã dễ dàng

## 🚀 Cài Đặt & Chạy

### Bước 1: Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### Bước 2: Chuẩn bị dữ liệu

Đảm bảo các file parquet nằm trong thư mục `data/`:
- `market_analysis.parquet`
- `industry_analysis.parquet`
- `ticker_analysis.parquet`

### Bước 3: Chạy dashboard

```bash
streamlit run app.py
```

Dashboard sẽ mở tại: http://localhost:8501

## 📁 Cấu Trúc Project

```
stock_dashboard/
├── app.py                      # Main application
├── config.py                   # Configuration
├── requirements.txt            # Dependencies
├── README.md                   # Hướng dẫn
│
├── data/                       # Data directory
│   ├── market_analysis.parquet
│   ├── industry_analysis.parquet
│   └── ticker_analysis.parquet
│
├── utils/                      # Utility functions
│   ├── __init__.py
│   ├── data_loader.py         # Load & cache data
│   ├── formatters.py          # Format functions
│   └── metrics.py             # Calculations
│
├── components/                 # UI components
│   ├── __init__.py
│   ├── charts.py              # Chart functions
│   ├── tables.py              # Table components
│   ├── filters.py             # Filter widgets
│   └── kpi_cards.py           # KPI displays
│
└── pages/                      # Streamlit pages
    ├── 01_🏛️_Tổng_Quan_Thị_Trường.py
    ├── 02_🏭_Phân_Tích_Ngành.py
    ├── 03_📊_Phân_Tích_Cổ_Phiếu.py
    ├── 04_⚖️_So_Sánh.py
    ├── 05_🔍_Sàng_Lọc.py
    └── 06_⭐_Danh_Mục.py
```

## 🔧 Tùy Chỉnh

### Thêm biểu đồ mới

1. Mở file `components/charts.py`
2. Thêm function vẽ biểu đồ mới
3. Import và sử dụng trong pages

### Thêm metrics mới

1. Mở file `utils/metrics.py`
2. Thêm function tính toán mới
3. Sử dụng trong pages

### Thay đổi màu sắc

Chỉnh sửa `config.py`:

```python
COLORS = {
    'primary': '#1f77b4',
    'success': '#2ecc71',
    'danger': '#e74c3c',
    ...
}
```

### Thêm tab mới

1. Tạo file mới trong `pages/`
2. Đặt tên theo format: `XX_🔰_Tên_Tab.py`
3. Streamlit sẽ tự động nhận diện

## 💡 Best Practices

### Code Organization
- **Modular**: Tách logic vào utils/, components/
- **Reusable**: Các function có thể tái sử dụng
- **Documented**: Có docstrings rõ ràng

### Performance
- **Caching**: Sử dụng `@st.cache_data` cho data loading
- **Lazy loading**: Chỉ load data khi cần
- **Efficient queries**: Filter data trước khi xử lý

### Debugging
- Check logs trong terminal
- Sử dụng `st.write()` để debug
- Xem trạng thái với `st.session_state`

## 🐛 Troubleshooting

### Lỗi import module

```bash
# Cài lại dependencies
pip install -r requirements.txt --force-reinstall
```

### Lỗi không tìm thấy data

Kiểm tra:
1. File parquet có trong thư mục `data/`?
2. Tên file đúng chưa?
3. Đường dẫn trong `config.py` đúng chưa?

### Lỗi hiển thị

- Clear cache: Nhấn `C` trong Streamlit
- Restart server: Ctrl+C và chạy lại

## 📝 Ghi Chú

- Dashboard sử dụng data offline (parquet files)
- Để cập nhật data real-time, cần tích hợp API
- Export chức năng có sẵn cho CSV

## 🤝 Đóng Góp

Để thêm tính năng mới:

1. Tạo branch mới
2. Implement feature
3. Test kỹ
4. Submit pull request

## 📧 Liên Hệ

Phát triển bởi BSC Research Team

---

**Version**: 1.0  
**Last Updated**: 2024  
**License**: MIT
