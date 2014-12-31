import copy
import sys
import cProfile
import time

boardsize=6
_kmoves = ((2,1), (1,2), (-1,2), (-2,1), (-2,-1), (-1,-2), (1,-2), (2,-1)) 
 
 
def chess2index(chess, boardsize=boardsize):
    chess = chess.strip().lower()
    x = ord(chess[0]) - ord('a')
    y = boardsize - int(chess[1:])
    return (x, y)
 
def boardstring(board, boardsize=boardsize):
    r = range(boardsize)
    lines = ''
    for y in r:
        lines += '\n' + ','.join('%2i' % board[(x,y)] if board[(x,y)] else '  '
                                 for x in r)
    return lines
 
def knightmoves(board, P, boardsize=boardsize):
    Px, Py = P
    kmoves = set((Px+x, Py+y) for x,y in _kmoves)
    kmoves = set( (x,y)
                  for x,y in kmoves
                  if 0 <= x < boardsize
                     and 0 <= y < boardsize
                     and not board[(x,y)] )
    return kmoves
 
def _accessibility(board, P, boardsize=boardsize):
    access = []
    brd = copy.deepcopy(board)
    for pos in knightmoves(board, P, boardsize=boardsize):
        brd[pos] = -1
        access.append( (len(knightmoves(brd, pos, boardsize=boardsize)), pos) )
        brd[pos] = 0
    return access

def accessibility(board, P, boardsize=boardsize):
    access = []
    #brd = copy.deepcopy(board)
    for pos in knightmoves(board, P, boardsize=boardsize):
        tmp = board[pos]
        board[pos] = -1
        access.append( (len(knightmoves(board, pos, boardsize=boardsize)), pos) )
        board[pos] = tmp
    return access

def rollback(board, move, boardsize):
    print ("Rollback called on move %s" % move)
    new_board = {(x,y):0 for x in range(boardsize) for y in range(boardsize)}
    new_pos = (0, 0)
    for pos,val in iter(board.items()):
            if val < move:
                new_board[pos] = val
            elif val == move:
                new_pos = pos
    return new_board, new_pos
 
def knights_tour(start, boardsize=boardsize):
    board = {(x,y):0 for x in range(boardsize) for y in range(boardsize)}
    move = 1
    P = chess2index(start, boardsize)
    board[P] = move
    move += 1
    nxt = 0
    min_rollback_move = -1
    step = 1
    rb = 0
    while move <= len(board):
        a = accessibility(board, P, boardsize)
        if len(a) - 1 < nxt:
                nxt = 100
        else:    
            a.sort()
            P = a[nxt][1]
            board[P] = move
            move += 1   
            if nxt > 0:
                print ("Fine on move %s, next %s" % (move - 1, nxt))
            nxt = 0
            continue
        if nxt < len(a) - 1:
            board, P = rollback(board, move, boardsize)
            nxt += 1
        else:
            if min_rollback_move < 0:
                min_rollback_move = move - 1
            rb += 1
            delta = move - min_rollback_move
            board, P = rollback(board, move - delta, boardsize)
            move = move - delta
            step = int(move/20)
            if boardsize < 100:
                step = 1
            elif move > 200 and move < 5000:
                step = 2
            elif move < 30000:
                step = 5 + int(rb / 10)
            elif move < 100000:
                step = int(rb/10 + 1500)
            else:
                step = int(move/20)
            #step = size < 200 ? 2 : size < 500 ? 3 : int(move/10)
            #min_rollback_move = min_rollback_move - int(move/10)
            min_rollback_move = min_rollback_move - step
            nxt = 1
    return board
 

def main():
    boardsize = int(sys.argv[1])
    start = sys.argv[2]
    board = knights_tour(start, boardsize)
    print(boardstring(board, boardsize=boardsize))


if __name__ == '__main__':
    if len(sys.argv) > 3 and sys.argv[3] == "profile":
        cProfile.run('main()')
    else:
        a = time.time()
        main()
        b = time.time()
        diff = b - a
        sys.stderr.write("%s\n" % str(diff))
