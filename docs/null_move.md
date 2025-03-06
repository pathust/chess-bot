# 1.1 standard null move heuristic heuristic

### -Definition
+) Null move: thực hiện 1 bước đi rỗng, để đối thủ di chuyển 2 lần với giả định việc đó sẽ cho đối thủ 1 nước đi tốt.   
--> Tạo một trạng thái có vẻ tồi để thực hiện pruning.  
+) Zugzwang: các nước đi mà mọi hành động đều làm trạng thái người chơi tồi đi--> khác giả thuyết của Null movemove  


There are a class of chess positions where employing the null-move heuristic can result in severe tactical blunders. In these zugzwang (German for "forced to move") positions, the player whose turn it is to move has only bad moves as their legal choices, and so would actually be better off if allowed to forfeit the right to move. In these positions, the null-move heuristic may produce a cutoff where a full search would not have found one, causing the program to assume the position is very good for a side when it may in fact be very bad for them.

To avoid using the null-move heuristic in zugzwang positions, most chess-playing programs that use the null-move heuristic put restrictions on its use. Such restrictions often include not using the null-move heuristic if

The side to move is in check  
The side to move has only its king and pawns remaining  
The side to move has a small number of pieces remaining  
TThe previous move in the search was also a null move  

### -Problem:
Các trạng thái Zugzwang có thể gây nhầm lẫn trong tính toán tạo thành nước đi tốt nhất lỗi   
-> tính toán thất bại   

### -References:
https://en.wikipedia.org/wiki/Null-move_heuristic  
https://en.wikipedia.org/wiki/Zugzwang


# 1.2 Verified Null-Move Pruning (on coding)
+) Reduce depth 3 after null-move;   
+) Verified the cutoff if the branch used Null-move   
+) ...   
### -References:
https://ui.adsabs.harvard.edu/abs/2008arXiv0808.1125D/abstract