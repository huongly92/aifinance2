# 🏗️ KIẾN TRÚC & HƯỚNG DẪN MAINTAIN

## 📐 Kiến Trúc Tổng Quan

Dashboard được thiết kế theo **mô hình modular** với các thành phần độc lập, dễ maintain và mở rộng.

### Nguyên tắc thiết kế:

1. **Separation of Concerns**: Tách biệt logic, data, và UI
2. **DRY (Don't Repeat Yourself)**: Tái sử dụng code tối đa
3. **Single Responsibility**: Mỗi module có 1 trách nhiệm rõ ràng
4. **Easy to Extend**: Dễ dàng thêm features mới

## 📂 Cấu Trúc Chi Tiết

### 1. `config.py` - Cấu hình trung tâm

**Mục đích**: Quản lý tất cả constants và settings

**Chứa**:
- Đường dẫn files
- Cấu hình dashboard (colors, layout)
- Định nghĩa metric groups
- Preset screening strategies
- Format functions

**Cách sử dụng**:
```python
import config

# Lấy màu
color = config.COLORS['success']

# Lấy metrics theo nhóm
metrics = config.ALL_METRIC_GROUPS['Sinh lời']

# Preset screening
criteria = config.SCREENING_PRESETS['Value Investing']
```

**Khi nào chỉnh sửa**:
- Thêm metrics mới
- Thay đổi theme/colors
- Thêm screening presets
- Thay đổi đường dẫn data

---

### 2. `utils/` - Utility Functions

#### 2.1 `data_loader.py` - Quản lý dữ liệu

**Chức năng**:
- Load & cache data từ parquet
- Filter data theo điều kiện
- Lấy thông tin ticker/industry
- Search functions

**Functions chính**:
```python
load_all_data()              # Load 3 files parquet
get_market_data()            # Load market only
filter_data_by_date_range()  # Lọc theo thời gian
get_latest_data()            # Lấy quý mới nhất
search_tickers()             # Tìm kiếm ticker
```

**Caching**:
- Sử dụng `@st.cache_data(ttl=3600)` - cache 1h
- Auto refresh sau 1h

**Khi nào chỉnh sửa**:
- Thêm nguồn data mới
- Thay đổi logic filter
- Thêm search criteria

#### 2.2 `formatters.py` - Format dữ liệu

**Chức năng**:
- Format số theo loại (billion, percent, ratio)
- Tạo màu cho values
- Style dataframes

**Functions chính**:
```python
format_number(value)         # Format số thông thường
format_percent(value)        # Format %
format_billion(value)        # Format tỷ
format_change(value)         # Format thay đổi
get_color_for_value()        # Lấy màu cho value
```

**Khi nào chỉnh sửa**:
- Thay đổi format hiển thị
- Thêm format types mới
- Custom color logic

#### 2.3 `metrics.py` - Tính toán

**Chức năng**:
- Tính toán metrics phái sinh
- Statistics functions
- Screening logic
- Scoring functions

**Functions chính**:
```python
calculate_summary_stats()    # Mean, median, std
calculate_growth_rate()      # Tốc độ tăng trưởng
calculate_cagr()            # CAGR
interpret_z_score()         # Giải thích Z-Score
screen_stocks()             # Lọc cổ phiếu
```

**Khi nào chỉnh sửa**:
- Thêm công thức tính mới
- Thay đổi logic screening
- Custom scoring

---

### 3. `components/` - UI Components

#### 3.1 `charts.py` - Biểu đồ

**Chức năng**: Tạo tất cả loại charts với Plotly

**Charts có sẵn**:
```python
create_line_chart()          # Biểu đồ đường
create_bar_chart()           # Biểu đồ cột
create_grouped_bar_chart()   # Cột nhóm
create_scatter_chart()       # Phân tán
create_pie_chart()           # Tròn
create_heatmap()            # Heatmap
create_waterfall_chart()     # Waterfall
create_radar_chart()         # Radar
create_histogram()          # Histogram
create_gauge_chart()        # Gauge
```

**Thêm chart mới**:
```python
def create_new_chart(df, x_col, y_col, title="", height=400):
    fig = go.Figure()
    # ... your logic
    fig.update_layout(
        title=title,
        template=config.CHART_TEMPLATE,
        height=height
    )
    return fig
```

#### 3.2 `tables.py` - Bảng dữ liệu

**Functions**:
- `create_styled_table()` - Bảng có format
- `create_comparison_table()` - Bảng so sánh
- `create_ranking_table()` - Bảng xếp hạng

#### 3.3 `filters.py` - Bộ lọc

**Widgets có sẵn**:
- `date_range_filter()` - Lọc thời gian
- `multi_select_filter()` - Multi-select
- `metric_selector()` - Chọn metrics theo nhóm
- `number_range_filter()` - Slider range

**Thêm filter mới**:
```python
def custom_filter(label, options, key=None):
    return st.selectbox(label, options, key=key)
```

#### 3.4 `kpi_cards.py` - KPI Cards

**Functions**:
- `display_kpi_card()` - 1 KPI card
- `display_kpi_row()` - 1 hàng KPIs
- `display_metric_card()` - Card nhiều metrics

---

### 4. `pages/` - Các trang

Mỗi page là một module độc lập với cấu trúc:

```python
"""
Docstring mô tả page
"""

# Imports
import streamlit as st
import sys
from pathlib import Path

# Add root to path
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

# Page config
st.set_page_config(...)

# Get data from session state
if 'xxx_df' not in st.session_state:
    st.error("...")
    st.stop()

# Main logic
st.title("...")

# Sidebar filters
st.sidebar.header("...")

# Content sections
st.header("...")
# ... charts, tables, etc.
```

**Naming convention**: `XX_🔰_Tên_Page.py`
- `XX`: Số thứ tự (01, 02, ...)
- `🔰`: Emoji icon
- `Tên_Page`: Tên page (viết hoa chữ cái đầu, dấu gạch dưới)

---

### 5. `app.py` - Main Application

**Chức năng**:
- Page configuration
- Load & cache data globally
- Sidebar navigation
- Home page content

**Flow**:
1. Set page config
2. Load data with caching
3. Store in session_state
4. Display sidebar
5. Show home page

---

## 🔧 HƯỚNG DẪN MAINTAIN

### ✅ Thêm biểu đồ mới

1. **Tạo function trong `components/charts.py`**:
```python
def create_my_chart(df, x, y, title="", height=400):
    fig = px.line(df, x=x, y=y, title=title)
    fig.update_layout(
        template=config.CHART_TEMPLATE,
        height=height
    )
    return fig
```

2. **Export trong `components/__init__.py`**:
```python
from .charts import create_my_chart

__all__ = [..., 'create_my_chart']
```

3. **Sử dụng trong pages**:
```python
from components.charts import create_my_chart

fig = create_my_chart(df, 'x', 'y', 'Title')
st.plotly_chart(fig, use_container_width=True)
```

---

### ✅ Thêm metric mới

1. **Define trong `config.py`**:
```python
METRIC_LABELS = {
    ...
    'NEW_METRIC': 'Tên hiển thị',
}

# Thêm vào nhóm phù hợp
PROFITABILITY_METRICS = [..., 'NEW_METRIC']
```

2. **Thêm format (nếu cần) trong `config.py`**:
```python
def get_number_format(column_name):
    if 'NEW_METRIC' in column_name:
        return 'percent'
    ...
```

3. **Sử dụng trong pages**:
```python
if 'NEW_METRIC' in df.columns:
    st.metric(config.METRIC_LABELS['NEW_METRIC'], df['NEW_METRIC'])
```

---

### ✅ Thêm page mới

1. **Tạo file `pages/07_🎯_Tên_Mới.py`**:
```python
import streamlit as st
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

st.set_page_config(page_title="Tên Mới", page_icon="🎯", layout="wide")
st.title("🎯 Tên Mới")

# Your logic here
```

2. **Streamlit tự động nhận diện** - không cần config thêm!

---

### ✅ Thêm bộ lọc mới

1. **Tạo function trong `components/filters.py`**:
```python
def my_filter(label, options, key=None):
    return st.multiselect(label, options, key=key)
```

2. **Sử dụng**:
```python
from components.filters import my_filter

selected = my_filter("Label", options, "my_key")
```

---

### ✅ Fix bugs

1. **Check logs**: Xem terminal để thấy error stack trace
2. **Debug**: Dùng `st.write()` để print variables
3. **Cache issues**: Clear cache với `C` key
4. **Data issues**: Kiểm tra data với `st.dataframe(df.head())`

---

### ✅ Performance optimization

1. **Caching**:
```python
@st.cache_data(ttl=3600)  # Cache 1h
def expensive_function(data):
    # Heavy computation
    return result
```

2. **Lazy loading**:
```python
# Chỉ load khi cần
if st.button("Show details"):
    data = load_detailed_data()
```

3. **Filter early**:
```python
# Filter trước khi compute
filtered = df[df['YEAR'] == selected_year]
result = compute_metrics(filtered)
```

---

## 🐛 DEBUG CHECKLIST

Khi có lỗi, check theo thứ tự:

1. ✅ **Terminal logs** - Error message?
2. ✅ **Data availability** - Column exists?
3. ✅ **Data types** - Correct dtype?
4. ✅ **Null values** - Handle NaN?
5. ✅ **Session state** - Data in session_state?
6. ✅ **Cache** - Try clear cache
7. ✅ **Imports** - All modules imported?

---

## 📊 TESTING WORKFLOW

1. **Test locally**: `streamlit run app.py`
2. **Test each page**: Click through all pages
3. **Test filters**: Try different filter combinations
4. **Test edge cases**: Empty data, null values
5. **Test exports**: Download CSV works?

---

## 🚀 DEPLOYMENT

### Local deployment:
```bash
streamlit run app.py
```

### Docker deployment:
```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["streamlit", "run", "app.py"]
```

### Streamlit Cloud:
1. Push to GitHub
2. Connect to Streamlit Cloud
3. Deploy!

---

## 📚 BEST PRACTICES

### Code Style:
- ✅ Use type hints khi có thể
- ✅ Docstrings cho functions
- ✅ Descriptive variable names
- ✅ Constants in UPPER_CASE

### Performance:
- ✅ Cache data loading
- ✅ Filter before compute
- ✅ Use session_state for persistence

### UX:
- ✅ Loading states
- ✅ Error messages rõ ràng
- ✅ Help text với tooltips
- ✅ Consistent layout

---

🎉 **Happy coding!**
