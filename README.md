# Chess Bot API

Một API đơn giản để tìm nước đi tốt nhất trong cờ vua sử dụng FastAPI và chess engine.

## Giới thiệu

Chess Bot API là một dịch vụ web cho phép người dùng gửi trạng thái bàn cờ dưới dạng ký hiệu FEN (Forsyth-Edwards Notation) và nhận về nước đi tốt nhất được đề xuất bởi chess engine. API này được xây dựng với FastAPI và sử dụng một chess engine tùy chỉnh để tính toán các nước đi.

## Yêu cầu hệ thống

- Python 3.8 trở lên
- pip (Python package installer)

## Hướng dẫn cài đặt

### 1. Clone repository

```bash
git clone https://github.com/pathust/chess-bot
cd chess-bot
```

### 2. Tạo môi trường ảo (venv)

#### Trên Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

#### Trên macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Cài đặt các gói phụ thuộc

```bash
pip install -r requirements.txt
```

## Chạy ứng dụng

Để khởi chạy ứng dụng với chế độ tự động tải lại khi có thay đổi, sử dụng lệnh:

```bash
uvicorn api::app.py --reload
```

Ứng dụng sẽ chạy mặc định tại địa chỉ: http://127.0.0.1:8000

## API Endpoints

### Trang chủ
- `GET /`: Kiểm tra xem API có đang hoạt động không

### Tìm nước đi tốt nhất
- `POST /move/`: Nhận một trạng thái bàn cờ dưới dạng FEN và trả về nước đi tốt nhất

## Sử dụng API

Bạn cũng có thể sử dụng giao diện Swagger bằng cách thêm ```/docs``` vào cuối địa chỉ hoặc một công cụ như Postman .

## Tham số API

| Tham số | Loại | Mô tả |
|---------|------|-------|
| fen | string (query) | Trạng thái bàn cờ ở dạng FEN (Forsyth-Edwards Notation) |
| depth | integer (query, optional) | Độ sâu tìm kiếm, mặc định là 3 |

## Cấu trúc dự án

```
chess-bot/
│
├── api/
│   └── app.py        # Ứng dụng FastAPI (mã được cung cấp)
│
├── chess_engine.py   # Chess engine để tính toán nước đi tốt nhất
│
├── requirements.txt  # File yêu cầu các gói phụ thuộc
└── README.md         # File này
```

## File requirements.txt

```
fastapi>=0.68.0
uvicorn>=0.15.0
```

## Đóng góp

Mọi đóng góp đều được chào đón! Hãy tạo issue hoặc pull request để đóng góp vào dự án.

## Giấy phép

Dự án này được phân phối dưới giấy phép MIT. Xem file `LICENSE` để biết thêm chi tiết.
