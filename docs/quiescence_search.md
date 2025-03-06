### -Định nghĩa
+) Horizon problem: Trong trường hợp nếu đi thêm 1 bước nữa sẽ là nước đẹp (Ví dụ: chiếu hết), nhưng ở nước kết thúc tìm kiếm lại là một nước xấu. Nếu tiếp tục tăng độ sâu tìm kiếm vẫn gặp vấn đề tương tự ở mức depth+1.  
--> Thực hiện việc tìm kiếm những nước đi có tỷ lệ cao tạo đột biến khi depth = 0.  
+) Quiescence search: Khi depth = 0, thuật toán tìm kiếm chính sẽ dừng lại và chuyển sang vét các nước đi có tỷ lệ cao tạo đột biến.

### Các nước đi được kiểm tra gồm:  
    -) Các nước đi chiếu  
    -) Các nước ăn quân  
    -) Các nước phong cấp  

### Vấn đề:
-) Tìm kiếm quá sâu gây áp lực lên bộ nhớ và khả năng tính toán.  
-) Chưa tính đến các nước phòng thủ.  

### Tài liệu tham khảo:  
https://en.wikipedia.org/wiki/Quiescence_search  

---

## Advance Quiescence (Zzzzzz#Quiescence)  
Khi một quân cờ thực hiện nước ăn quân, một cờ đánh dấu (capture flag) được đặt trên quân cờ đó. Trong thuật toán quiescence, tôi cho phép **QUIES_MAX** số nước ăn quân miễn phí (tức là bất kỳ quân nào cũng có thể ăn quân khác). Tuy nhiên, sau khi vượt qua giới hạn **QUIES_MAX**, chỉ những nước ăn quân vào các quân có cờ đánh dấu mới được phép tiếp tục. Cách này giúp thuật toán quiescence luôn kết thúc và nhiều chuỗi trao đổi như "tôi ăn hậu của bạn, bạn ăn hậu của tôi, v.v." được đánh giá chính xác.  

Giá trị **QUIES_MAX** càng cao thì kết quả càng tốt, nhưng đồng thời cũng làm chậm chương trình, do đó có một sự đánh đổi giữa độ chính xác và tốc độ. Trong **ZZZZZZ**, thuật toán quiescence hầu như không mất nhiều thời gian: thuật toán thường kết thúc ngay sau lần gọi **eval()** đầu tiên (depth = 0) (đánh giá mà dù sao cũng phải thực hiện), và chỉ khoảng 10% các lần gọi **eval()** đến từ các nút bên trong sâu hơn. Tôi cũng đã thử nghiệm với nước đi null-move trong quiescence search, nhưng không đem lại hiệu quả đáng kể.  

### Tài liệu tham khảo:  
https://www.chessprogramming.org/Zzzzzz#Quiescence  
