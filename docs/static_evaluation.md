# Static evaluation function
## Định nghĩa 
 - Hàm đánh giá tĩnh (Static Evaluation Function) là một hàm được sử dụng trong các thuật toán tìm kiếm( Minimax, alpha-beta pruning,..), đặc biệt là trong các trò chơi hoặc trí tuệ nhân tạo để đánh giá "giá trị" của một trạng thái nhật định mà không cần phải mở rộng tìm kiếm đến trạng thái tiếp theo. 

 - Nó nhận vào 1 trạng thái của trò chơi/bài toán
 - Trả về một giá trị số để đánh giá mức độ tốt/xấu của trạng thái đó

## Static eval func trong cờ vua
 ### Nguyên lý 
 - Hàm đánh giá tĩnh trong cờ vua phân tích trạng thái bàn cờ hiện tại và trả về một giá trị sô biểu thị mức thuận lợi của vị thế. 
    + giá trị dương: có lợi cho quân trắng
    + giá trị âm: có lợi cho quân đen
    + giá trị 0: vị thế cân bằng 
- công thức tổng quát:
 Eval(position) = t1 * evaluate_material + t2 *evaluate_king_safety + t3 * W_pawn_structure + t4 *  + W_mobility + t5 * W_center_control + t6 * W_piece_square + t7 * W_evaluation_pieces + t8 * W_tempo  
  ti (i = 1,8): hệ số tối ưu của từng hàm/yếu tố -> xác định mức độ ảnh hưởng của yếu tố đó tới trạng thái bàn cờ.

 ### evaluate_material - đánh giá giá trị quân cờ 
 - Dựa trên nguyên tắc rằng mỗi quân cờ có một giá trị vật chất cụ thể thể hiện sức mạnh của nó tương đối trên toàn bàn cờ.
 - Cung cấp nền tảng đánh giá cơ bản dựa trên sự cân bằng về vật chất giữa hai bên -> xác định liệu một bên có lợi thế về vật chất không.
   Cách xây dựng
 - sử dụng 1 hàm ánh xạ từng loại quân cờ đến giá trị số của nó
 - duyệt qua toàn bộ bàn cờ -> xác định quân cờ
 - cộng giá trị quân cờ nếu là quân trắng và ngược lại
 

 ### evaluate_king_safety
 - Mục tiêu cuối cùng trong cờ vua là **tấn công và chiếu hết vua đối phương**. Vì vậy, an toàn của vua là yếu tố quan trọng hàng đầu, đặc biệt trong giai đoạn trung và tàn cuộc. Vua được bảo vệ tốt sẽ ít bị tấn công hơn.

  Cách xây dựng
- Xác định vị trí của vua trắng và vua đen
- kiểm tra các ô phía trước vua (dựa theo màu)
- Cộng điểm nếu có tốt bảo vệ trước vua trắng và ngược lại

 ### evaluate_pawn_structure
- Cấu trúc quân tốt là xương sống của vị thế, ảnh hưởng đến tính linh hoạt và tiềm năng tấn công/phòng thủ lâu dài.
- **Tốt đôi (doubled penalty)** thường bị coi là bất lợi vì chúng không thể bảo vệ lẫn nhau 
-**tốt cô lập (isolated penalty)** dễ bị tấn công và khó được bảo vệ

  Cách xây dựng
- xác định vị trí của tất cả các quân tốt (trắng và đen)
- xác định cột có nhiều hơn 1 tốt và duyệt từng cột một 
- áp dụng hình phạt trừ điểm khi phát hiện tốt đôi và tốt cô lập với quân trắng và ngược lại

 ### evaluate_ mobility

 ### evaluate_center_control
 - Kiểm soát trung tâm bàn cờ là một chiến lược phổ biến trong cờ vua. Việc kiểm soát khu vực này giúp người chơi vừa phòng thủ lãnh thổ của mình, vừa tấn công lãnh thổ đối thủ dễ dàng hơn.
  Cách xây dựng
- xác định các ô trung tâm (D4, D5,E4,E5)
- cộng điểm cho mỗi ô trung tâm có quân trắng và ngược lại với quân đen.

 ### evaluate_piece_square
- Mỗi loại quân cờ có những vị trí tốt và kém trên bàn cờ, ảnh hưởng đến hiệu quả hoạt động của chúng. Ví dụ, đẩy tốt và trung tâm trong khai cuộc là một chiến lược tốt. 
- thúc đẩy AI đặt quân vào vị trí chiến lược và khuyến khích phát triển quân cờ theo nguyên tắc cờ vua tốt.
  Cách xây dựng
- Xác định bảng giá trị vị trí cho từng loại quân cờ
- mỗi ô trên bàn cờ có một giá trị cụ thể cho từng loại quân 
- cộng/trừ giá trị tương ứng tuỳ thuộc vào màu quân và vị trí

 ### evaluate_tactical_positions
- đánh giá các vị trí chiến thuật đặc biệt giúp AI phát hiện và tận dụng các cơ hội chiến thuật tinh tế hơn:
  + Xe ở trên cột mở có hiệu quả cao hơn rất nhiều so với xe bị chặn
  + Mã bị vị trí outpost(được bảo vệ bởi tốt, không bị đe doạ ) khá mạnh
  + Tượng trên đường chéo dài có thể ảnh hưởng nhiều tới bàn cờ
  + hậu di chuyển quá sớm thường là bất lợi về mặt phát triển.
   
  Cách xây dựng
- Xác định và đánh giá các tình huống chiến thuật cụ thể 

 ### evaluate_tempo
- Tempo trong cờ vua là số nước đi cần để đạt được một mục tiêu. Nếu một người chơi mất nhiều nước đi hơn cần thiết để thực hiện một ý tưởng, họ bị mất tempo. 
. Mất tempo nghĩa là mất lợi thế về thời gian.
- Khuyến khích AI hoàn thành mục tiêu với ít nước đi nhất có thể.
  Cách xây dựng
- đếm số nước đi đã thực hiện(board.move_stack)
- áp dụng 1 hệ số tempo_weight
- thêm điểm âm khi số nước tăng để khuyến khích giải quyết nhanh.

## Vấn đề
 1. Bộ hệ số tối ưu ti chưa được tối ưu
 2. Chưa có phương pháo kiểm tra nước đi mạnh yếu <-> Hàm đánh giá chỉ đánh giá trạng thái bàn cờ mà không kiểm tra nước đi nào là mạnh hay yếu. Mặt khác, một thế cờ có điểm số cao nhưng không có nước đi mạnh thì vẫn có thể bị thua đồng thời thiếu đi cơ chế dự báo nếu đối thủ có nước đi phản công mạnh.
 3. Các hệ số đánh giá giá trị hiện tại trong hầu hết các hàm thành phần đang khá chung mà chưa đủ cụ thể và chính xác trong từng giai đoạn của bàn cờ(opening, midllegame,endgame). 
 4. Một số hàm như evaluate_mobility() và evaluate_piece_square() có thể tính toán lặp lại nhiều lần một số trường hợp. Từ đó làm giảm tốc độ tìm kiếm của engine, đồng thời lãng phí tài nguyên tính toán.
 5. hàm evaluation đang chỉ đánh giá vị trí hiện tại mà không dự đoán được các đòn chiến thuật như: gim, chồng đè, tấn công đôi, chiếu hết.Ví dụ: minimax có thể chọn một bước đi có giá trị tối ưu nhất hiện tại nhưng mà nước đi này có thể dẫn đến chiếu hết trong ngay mấy bước sau.
 6. hàm evaluation có thể tính điểm số cao nhưng lại không thể nhận ra thế cờ này dẫn đến kết quả hoà. Ví dụ: một số tình huống hoà khá phổ biến như
     - 50-move rule
     - threefold repetition
     - vua bị khoá không có nước đi hợp lệ
     -> nếu AI đánh giá thấy vẫn có lợi thế -> chọn nước đi sai lầm.
 
## Giải pháp 
 1. Huấn luyện bộ hệ số tối ưu và các giá trị đánh giá trong hàm thành phần bằng thuật toán di truyền, đồng thời căn chỉnh hệ số trong các giai đoạn của bàn cờ(opening, middlegame, endgame) dựa vào kết quả các ván đấu thực nghiệm.
 2. Lưu trữ các trạng thái bàn cờ đã tính toán vào bảng transposition table để tránh tính toán lặp lại.
 3. Có thể xây dựng thêm modul nhận diện chiến thuật(ví dụ nếu một nước đi dẫn đến bị ghim -> trừ điểm, dẫn đến chiếu hết-> trả về giá trị cao nhất,..), thêm kiểm tra các quy tắc hoà trước đi đánh giá nước đi 

 


## tài liệu tham khảo
https://arxiv.org/pdf/2007.02130
https://byvn.net/nNvJ
https://byvn.net/AtEV
https://www.graham-kendall.com/papers/kw2001a.pdf
https://byvn.net/4CgQ
https://www.chessprogramming.org/Evaluation
https://chessify.me/blog/chess-engine-evaluation
