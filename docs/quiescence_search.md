### -Định nghĩa
+)Horizon problem: Trong trường hợp nếu đi thêm 1 bước nữa sẽ là nước đẹp(Ex: chiếu tướng hết cờ) nhưng ở nước kết thúc tìm kiếm đang là 1 nước xấu. Nếu cứ tăng depth lên vẫn gặp với mức depth+1  
--> Thực hiện việc search những nước đi có tỉ lệ cao tạo đột biến khi depth = 0  
+)quiescence_search: khi depth = 0, thuật toán search chính sẽ dừng tìm kiếm, chuyển sang vét các nước có tỉ lệ cao tạo đột biến.


### Các nước đi được kiểm tra gồm:  
    -) các nước đi chiếu  
    -) các nước ăn quân  
    -) các nước phong cấp  

### Vấn đề:
-) Tìm kiếm quá sâu gây áp lực nên bộ nhớ, khả năng tính toán.   
-) chưa tính đến các nước phòng thủ    
### References:  
https://en.wikipedia.org/wiki/Quiescence_search

quiescence_search
khi depth = 0, thuật toán sẽ dừng tìm kiếm:

## Advance Quiescence (Zzzzzz#Quiescence)   
When a piece captures, a capture flag is set on that piece. In the quiescence I allow QUIES_MAX free captures (so any piece may capture any other piece), but after these QUIES_MAX free captures only captures to pieces with the capture flag set are allowed. In this way the quiescence search always terminates and many exchanges like 'I capture your queen, you capture my queen etc.' are evaluated correctly. Higher QUIES_MAX values give better results, but also makes the program slower, so there is a trade off here. In ZZZZZZ the quiescence search hardly takes time: the quiescence search usually already terminates after the first eval() call (depth = 0) (an evaluation you would have to do any way) and only about 10% of the eval() calls come from deeper inner nodes. I also experimented with null moves in the quiescence search, but that did not help much.  
### References:
https://www.chessprogramming.org/Zzzzzz#Quiescence