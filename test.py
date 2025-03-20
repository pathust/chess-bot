from chess_engine import find_best_move

fen = "rnbqkb1r/pppppppp/5n2/8/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq - 1 2"
fen2= "8/7p/4k1p1/8/8/p3KNP1/1b5P/8 w - - 0 50"
fen3 = "r1bq1rk1/pp2bppp/2n2n2/2p1p3/4P3/2NP1N2/PPP2PPP/R1BQ1RK1 w - - 6 8"
print(find_best_move(fen2,6,3,False,False,True))