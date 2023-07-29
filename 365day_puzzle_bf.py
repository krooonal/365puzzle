from __future__ import annotations
from time import time
import getopt
import sys

board_max_x = 7
board_max_y = 7

class Rectangle:
    def __init__(self, startx: int, starty: int, xlen: int, ylen: int) -> None:
        self.startx = startx
        self.starty = starty
        self.xlen = xlen
        self.ylen = ylen

class Block:
    def __init__(self, name: str) -> None:
        self.name = name
        self.maxx = 10000
        self.maxy = 10000
        self.rects = []
    
    def AddRect(self, rect: Rectangle):
        self.rects.append(rect)

def main(argv):

    month = 'JAN'
    date = ' 26'

    try:
        opts, args = getopt.getopt(argv, "hD:M:",
                                   ["date=",
                                    "month="])
    except getopt.GetoptError:
        print_options()
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print_options()
            sys.exit()
        elif opt in ("-D", "--date"):
            date = arg
        elif opt in ("-M", "--month"):
            month = arg

    all_orientations = DefineAllOrientations()
    grid = [['X' for i in range(board_max_y)] for j in range(board_max_x)]

    grid[0] = ['JAN','FEB','MAR','APR','MAY','JUN',' X ']
    grid[1] = ['JUL','AUG','SEP','OCT','NOV','DEC',' X ']
    grid[2] = [' 01',' 02',' 03',' 04',' 05',' 06',' 07']
    grid[3] = [' 08',' 09',' 10',' 11',' 12',' 13',' 14']
    grid[4] = [' 15',' 16',' 17',' 18',' 19',' 20',' 21']
    grid[5] = [' 22',' 23',' 24',' 25',' 26',' 27',' 28']
    grid[6] = [' 29',' 30',' 31',' X ',' X ',' X ',' X ']

    orig_grid = [['X' for i in range(board_max_y)] for j in range(board_max_x)]

    orig_grid[0] = ['JAN','FEB','MAR','APR','MAY','JUN',' X ']
    orig_grid[1] = ['JUL','AUG','SEP','OCT','NOV','DEC',' X ']
    orig_grid[2] = [' 01',' 02',' 03',' 04',' 05',' 06',' 07']
    orig_grid[3] = [' 08',' 09',' 10',' 11',' 12',' 13',' 14']
    orig_grid[4] = [' 15',' 16',' 17',' 18',' 19',' 20',' 21']
    orig_grid[5] = [' 22',' 23',' 24',' 25',' 26',' 27',' 28']
    orig_grid[6] = [' 29',' 30',' 31',' X ',' X ',' X ',' X ']


    for row in grid:
        print(row)
    for row in orig_grid:
        print(row)
    
    month_x, month_y = GetGridIntervals(grid, month)
    date_x, date_y = GetGridIntervals(grid, date)

    grid[month_x][month_y] = ' X '
    grid[date_x][date_y] = ' X '

    start_t = time()

    block_id = 0
    for ori_id in range(len(all_orientations[block_id])):
        success = Solve(grid, orig_grid, block_id, ori_id, all_orientations)
        if success:
            break
    end_t = time()

    print("Process took", end_t - start_t , "seconds.")

    grid[month_x][month_y] = month
    grid[date_x][date_y] = date
    
    for row in grid:
        print(row)

def print_options():
    print('365day_puzzle_bf.py')
    print(' -D <date>')
    print(' -M <month>')

# Put all blocks starting from block_id, ori_id
def Solve(grid: list[list[str]], orig_grid: list[list[str]], block_id: int, 
          ori_id: int, all_orientations: list[list[Block]]):
    block = all_orientations[block_id][ori_id]
    for startx in range(board_max_x):
        for starty in range(board_max_y):
            if not PutBlockOnGridXY(grid, block, block_id, startx, starty):
                RemoveBlockFromGrid(grid, block_id, orig_grid)
            else:
                # print("Added block " , block_id , " At ", startx, starty, ori_id)
                # for row in grid:
                #     print(row)
                if block_id == len(all_orientations)-1:
                    return True
                for next_ori_id in range(len(all_orientations[block_id+1])):
                    success = Solve(grid, orig_grid, block_id+1, next_ori_id, all_orientations)
                    if success:
                        return True
                # None of the orientation worked.
                RemoveBlockFromGrid(grid, block_id, orig_grid)
                # print("Removed block " , block_id)
                # for row in grid:
                #     print(row)
    return False


def RemoveBlockFromGrid(grid: list[list[str]], block_id: int, orig_grid: list[list[str]]):
    block_str = '*' + str(block_id+1) + '*'
    for x in range(board_max_x):
        for y in range(board_max_y):
            if grid[x][y] == block_str:
                grid[x][y] = orig_grid[x][y]

def PutBlockOnGridXY(grid: list[list[str]], block: Block, block_id: int, startx: int, starty: int):
    for rect in block.rects:
        rect_x_start = startx + rect.startx
        rect_y_start = starty + rect.starty
        for ind in range(rect.xlen):
            if rect_x_start + ind >= board_max_x:
                return False
            for ind2 in range(rect.ylen):
                if rect_y_start+ ind2 >= board_max_y:
                    return False
                if grid[rect_x_start + ind][rect_y_start+ ind2] == ' X ':
                    return False
                if not grid[rect_x_start + ind][rect_y_start+ ind2].startswith('*'):
                    grid[rect_x_start + ind][rect_y_start+ ind2] = '*' + str(block_id+1) + '*'
                else:
                    return False
    return True

def GetGridIntervals(grid: list[list[str]], entry: str):
    for x in range(board_max_x):
        for y in range(board_max_y):
            if grid[x][y] == entry:
                print("Reserving ", grid[x][y], x, y)
                return (x,y)
    return None

def DefineAllOrientations():
    all_orientations = []

    b1_1 = Block("b1_1")
    b1_1.AddRect(Rectangle(0,1,2,1))
    b1_1.AddRect(Rectangle(1,0,3,1))
    b1_2 = Block("b1_2")
    b1_2.AddRect(Rectangle(0,0,1,3))
    b1_2.AddRect(Rectangle(1,2,1,2))
    b1_3 = Block("b1_3")
    b1_3.AddRect(Rectangle(0,1,3,1))
    b1_3.AddRect(Rectangle(2,0,2,1))
    b1_4 = Block("b1_4")
    b1_4.AddRect(Rectangle(0,0,1,2))
    b1_4.AddRect(Rectangle(1,1,1,3))
    b1_5 = Block("b1_5")
    b1_5.AddRect(Rectangle(0,0,2,1))
    b1_5.AddRect(Rectangle(1,1,3,1))
    b1_6 = Block("b1_6")
    b1_6.AddRect(Rectangle(0,1,1,3))
    b1_6.AddRect(Rectangle(1,0,1,2))
    b1_7 = Block("b1_7")
    b1_7.AddRect(Rectangle(0,2,1,2))
    b1_7.AddRect(Rectangle(1,0,1,3))
    b1_8 = Block("b1_8")
    b1_8.AddRect(Rectangle(0,0,3,1))
    b1_8.AddRect(Rectangle(2,1,2,1))
    b1_orientations = [b1_1, b1_2, b1_3, b1_4,b1_5,b1_6,b1_7,b1_8]
    all_orientations.append(b1_orientations)

    b2_1 = Block("b2_1")
    b2_1.AddRect(Rectangle(0,0,3,2))
    b2_2 = Block("b2_2")
    b2_2.AddRect(Rectangle(0,0,2,3))
    b2_orientations = [b2_1, b2_2]
    all_orientations.append(b2_orientations)

    b3_1 = Block("b3_1")
    b3_1.AddRect(Rectangle(0,0,1,2))
    b3_1.AddRect(Rectangle(1,0,1,1))
    b3_1.AddRect(Rectangle(2,0,1,2))
    b3_2 = Block("b3_2")
    b3_2.AddRect(Rectangle(0,0,2,1))
    b3_2.AddRect(Rectangle(0,1,1,1))
    b3_2.AddRect(Rectangle(0,2,2,1))
    b3_3 = Block("b3_3")
    b3_3.AddRect(Rectangle(0,0,1,2))
    b3_3.AddRect(Rectangle(1,1,1,1))
    b3_3.AddRect(Rectangle(2,0,1,2))
    b3_4 = Block("b3_4")
    b3_4.AddRect(Rectangle(0,0,2,1))
    b3_4.AddRect(Rectangle(1,1,1,1))
    b3_4.AddRect(Rectangle(0,2,2,1))
    b3_orientations = [b3_1, b3_2, b3_3, b3_4]
    all_orientations.append(b3_orientations)

    b4_1 = Block("b4_1")
    b4_1.AddRect(Rectangle(0,0,2,2))
    b4_1.AddRect(Rectangle(2,0,1,1))
    b4_2 = Block("b4_2")
    b4_2.AddRect(Rectangle(0,1,2,2))
    b4_2.AddRect(Rectangle(0,0,1,1))
    b4_3 = Block("b4_3")
    b4_3.AddRect(Rectangle(1,0,2,2))
    b4_3.AddRect(Rectangle(0,1,1,1))
    b4_4 = Block("b4_4")
    b4_4.AddRect(Rectangle(0,0,2,2))
    b4_4.AddRect(Rectangle(1,2,1,1))
    b4_5 = Block("b4_5")
    b4_5.AddRect(Rectangle(0,0,2,2))
    b4_5.AddRect(Rectangle(2,1,1,1))
    b4_6 = Block("b4_6")
    b4_6.AddRect(Rectangle(0,0,2,2))
    b4_6.AddRect(Rectangle(0,2,1,1))
    b4_7 = Block("b4_7")
    b4_7.AddRect(Rectangle(1,0,2,2))
    b4_7.AddRect(Rectangle(0,0,1,1))
    b4_8 = Block("b4_8")
    b4_8.AddRect(Rectangle(0,1,2,2))
    b4_8.AddRect(Rectangle(1,0,1,1))
    b4_orientations = [b4_1, b4_2, b4_3, b4_4,b4_5,b4_6,b4_7,b4_8]
    all_orientations.append(b4_orientations)

    b5_1 = Block("b5_1")
    b5_1.AddRect(Rectangle(0,0,3,1))
    b5_1.AddRect(Rectangle(0,1,1,2))
    b5_2 = Block("b5_2")
    b5_2.AddRect(Rectangle(0,2,3,1))
    b5_2.AddRect(Rectangle(0,0,1,2))
    b5_3 = Block("b5_3")
    b5_3.AddRect(Rectangle(0,2,3,1))
    b5_3.AddRect(Rectangle(2,0,1,2))
    b5_4 = Block("b5_4")
    b5_4.AddRect(Rectangle(0,0,3,1))
    b5_4.AddRect(Rectangle(2,1,1,2))
    b5_orientations = [b5_1, b5_2, b5_3, b5_4]
    all_orientations.append(b5_orientations)

    b6_1 = Block("b6_1")
    b6_1.AddRect(Rectangle(0,0,4,1))
    b6_1.AddRect(Rectangle(0,1,1,1))
    b6_2 = Block("b6_2")
    b6_2.AddRect(Rectangle(0,0,1,4))
    b6_2.AddRect(Rectangle(1,3,1,1))
    b6_3 = Block("b6_3")
    b6_3.AddRect(Rectangle(0,1,4,1))
    b6_3.AddRect(Rectangle(3,0,1,1))
    b6_4 = Block("b6_4")
    b6_4.AddRect(Rectangle(1,0,1,4))
    b6_4.AddRect(Rectangle(0,0,1,1))
    b6_5 = Block("b6_5")
    b6_5.AddRect(Rectangle(0,1,4,1))
    b6_5.AddRect(Rectangle(0,0,1,1))
    b6_6 = Block("b6_6")
    b6_6.AddRect(Rectangle(0,0,1,4))
    b6_6.AddRect(Rectangle(1,0,1,1))
    b6_7 = Block("b6_7")
    b6_7.AddRect(Rectangle(0,0,4,1))
    b6_7.AddRect(Rectangle(3,1,1,1))
    b6_8 = Block("b6_8")
    b6_8.AddRect(Rectangle(1,0,1,4))
    b6_8.AddRect(Rectangle(0,3,1,1))
    b6_orientations = [b6_1, b6_2, b6_3, b6_4,b6_5,b6_6,b6_7,b6_8]
    all_orientations.append(b6_orientations)

    b7_1 = Block("b7_1")
    b7_1.AddRect(Rectangle(0,1,3,1))
    b7_1.AddRect(Rectangle(0,0,1,1))
    b7_1.AddRect(Rectangle(2,2,1,1))
    b7_2 = Block("b7_2")
    b7_2.AddRect(Rectangle(1,0,1,3))
    b7_2.AddRect(Rectangle(0,2,1,1))
    b7_2.AddRect(Rectangle(2,0,1,1))
    b7_3 = Block("b7_3")
    b7_3.AddRect(Rectangle(0,1,3,1))
    b7_3.AddRect(Rectangle(0,2,1,1))
    b7_3.AddRect(Rectangle(2,0,1,1))
    b7_4 = Block("b7_4")
    b7_4.AddRect(Rectangle(1,0,1,3))
    b7_4.AddRect(Rectangle(0,0,1,1))
    b7_4.AddRect(Rectangle(2,2,1,1))
    b7_orientations = [b7_1, b7_2, b7_3, b7_4]
    all_orientations.append(b7_orientations)

    b8_1 = Block("b8_1")
    b8_1.AddRect(Rectangle(0,0,4,1))
    b8_1.AddRect(Rectangle(1,1,1,1))
    b8_2 = Block("b8_2")
    b8_2.AddRect(Rectangle(0,0,1,4))
    b8_2.AddRect(Rectangle(1,2,1,1))
    b8_3 = Block("b8_3")
    b8_3.AddRect(Rectangle(0,1,4,1))
    b8_3.AddRect(Rectangle(2,0,1,1))
    b8_4 = Block("b8_4")
    b8_4.AddRect(Rectangle(1,0,1,4))
    b8_4.AddRect(Rectangle(0,1,1,1))
    b8_5 = Block("b8_5")
    b8_5.AddRect(Rectangle(0,1,4,1))
    b8_5.AddRect(Rectangle(1,0,1,1))
    b8_6 = Block("b8_6")
    b8_6.AddRect(Rectangle(0,0,1,4))
    b8_6.AddRect(Rectangle(1,1,1,1))
    b8_7 = Block("b8_7")
    b8_7.AddRect(Rectangle(0,0,4,1))
    b8_7.AddRect(Rectangle(2,1,1,1))
    b8_8 = Block("b8_8")
    b8_8.AddRect(Rectangle(1,0,1,4))
    b8_8.AddRect(Rectangle(0,2,1,1))
    b8_orientations = [b8_1, b8_2, b8_3, b8_4,b8_5,b8_6,b8_7,b8_8]
    all_orientations.append(b8_orientations)
    return all_orientations

if __name__ == "__main__":
    main(sys.argv[1:])