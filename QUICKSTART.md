# 🚀 HƯỚNG DẪN NHANH

## 1️⃣ Cài Đặt (1 phút)

```bash
# Giải nén project
unzip stock_dashboard.zip
cd stock_dashboard

# Cài dependencies
pip install -r requirements.txt
```

## 2️⃣ Chạy Dashboard (30 giây)

```bash
streamlit run app.py
```

✅ Dashboard sẽ mở tự động tại: **http://localhost:8501**

## 3️⃣ Sử Dụng

### Điều hướng
- Sử dụng sidebar bên trái để chọn trang
- Mỗi trang có bộ lọc riêng

### Các trang chính:
1. **🏛️ Tổng Quan Thị Trường** - Xem xu hướng TT
2. **🏭 Phân Tích Ngành** - So sánh các ngành
3. **📊 Phân Tích Cổ Phiếu** - Chi tiết từng mã
4. **⚖️ So Sánh** - So sánh nhiều mã
5. **🔍 Sàng Lọc** - Tìm kiếm cơ hội
6. **⭐ Danh Mục** - Quản lý watchlist

### Tương tác với biểu đồ:
- **Hover**: Xem chi tiết
- **Zoom**: Cuộn chuột hoặc kéo
- **Pan**: Giữ shift + kéo
- **Download**: Nút camera góc trên phải

### Export dữ liệu:
- Mỗi trang có nút "📥 Tải xuống"
- Format: CSV

## 4️⃣ Tùy Chỉnh

### Thay đổi màu sắc:
Chỉnh `config.py`:
```python
COLORS = {
    'primary': '#1f77b4',  # Màu chính
    ...
}
```

### Thêm chỉ số mới:
1. Thêm vào `config.py` -> `METRIC_LABELS`
2. Sử dụng trong pages

### Thêm bộ lọc mới:
1. Mở `components/filters.py`
2. Tạo function mới
3. Import vào pages

## 5️⃣ Troubleshooting

### ❌ Module not found
```bash
pip install -r requirements.txt --force-reinstall
```

### ❌ Data not found
Kiểm tra thư mục `data/` có 3 file parquet

### ❌ Page không load
- Nhấn `C` để clear cache
- Restart: Ctrl+C và chạy lại

## 📌 Tips

💡 **Shortcuts Streamlit:**
- `C` - Clear cache
- `R` - Rerun
- `Ctrl+K` - Command palette

💡 **Performance:**
- Dashboard cache data 1 giờ
- Để refresh: Clear cache hoặc restart

💡 **Debugging:**
- Xem terminal để thấy errors
- Dùng `st.write()` để debug

## 🎯 Workflow Đề Xuất

1. **Bắt đầu**: Tổng Quan Thị Trường
2. **Phân tích ngành**: Chọn ngành tiềm năng
3. **Phân tích cổ phiếu**: Xem chi tiết từng mã
4. **So sánh**: So sánh các mã trong shortlist
5. **Sàng lọc**: Tìm thêm cơ hội
6. **Watchlist**: Lưu mã quan tâm

---

🎉 **Chúc bạn phân tích hiệu quả!**

📧 Hỗ trợ: BSC Research Team
