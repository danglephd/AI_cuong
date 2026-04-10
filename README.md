# YouTube Links Manager - AI Query System

Ứng dụng Flask tích hợp AI (Ollama/Phi3) để truy vấn dữ liệu YouTube links thông qua ngôn ngữ tự nhiên.

## Yêu cầu
- Python 3.8+
- Ollama chạy trên localhost:11434
- Model phi3:latest

## Cấu trúc Database

### Bảng: youtube_links
| Cột | Kiểu | Mô tả |
|-----|------|-------|
| id | TEXT | UUID, khóa chính |
| videoId | TEXT | ID video YouTube |
| youtubeLink | TEXT | URL đầy đủ của video |
| createdAt | INTEGER | Timestamp tạo (ms) |
| deleted | INTEGER | Cờ soft delete (0/1) |

## Cài đặt

1. **Cài đặt dependencies:**
```bash
pip install -r requirements.txt
```

2. **Kiểm tra Ollama:**
```bash
# Ollama phải chạy trên http://localhost:11434
curl http://localhost:11434/v1
```

3. **Chạy ứng dụng:**
```bash
python movieManage.py
```

4. **Truy cập:**
```
http://localhost:5000
```

## Cách sử dụng

1. Nhập câu hỏi tiếng Việt hoặc tiếng Anh
2. Hệ thống sẽ:
   - Lấy schema database
   - Gửi câu hỏi + schema đến AI
   - AI tạo SQL query
   - Thực thi query và hiển thị kết quả

## Ví dụ truy vấn

- "Tìm tất cả video chưa bị xóa"
- "Đếm số lượng video trong database"
- "Tìm video được tạo gần đây nhất"
- "Show tất cả YouTube links"
- "Tìm video có ID là 5I22fIBCw2o"

## Ghi chú

- Chỉ hỗ trợ SELECT query (không DELETE, UPDATE, INSERT)
- Yêu cầu Ollama có model phi3:latest
- Database SQLite đọc được không yêu cầu kết nối remote
