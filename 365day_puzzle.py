from __future__ import annotations
from ortools.sat.python import cp_model
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
        self.x_var = None
        self.y_var = None
        self.x_inter_var = None
        self.y_inter_var = None

class Block:
    def __init__(self, name: str, model: cp_model.CpModel) -> None:
        self.name = name
        self.model = model
        self.maxx = 10000
        self.maxy = 10000
        self.xvar = self.model.NewIntVar(0,self.maxx,self.name + "_x")
        self.yvar = self.model.NewIntVar(0,self.maxy,self.name + "_y")
        self.present = self.model.NewBoolVar(self.name + "_present")
        self.rects = []
        

    def AddRect(self, rect: Rectangle):
        self.rects.append(rect)
        rect_ind = len(self.rects)
        rect.x_var = self.model.NewIntVar(0,self.maxx ,
                                 self.name + "_x_" + str(rect_ind))
        self.model.Add(self.xvar + rect.startx == rect.x_var)
        self.model.Add(rect.x_var + rect.xlen <= board_max_x)
        rect.x_inter_var = self.model.NewOptionalFixedSizeIntervalVar(rect.x_var, rect.xlen, self.present, 
                                                                 self.name + "_x_" + str(rect_ind) + "_inter")
        
        rect.y_var = self.model.NewIntVar(0,self.maxy ,
                                 self.name + "_y_" + str(rect_ind))
        self.model.Add(self.yvar + rect.starty == rect.y_var)
        self.model.Add(rect.y_var + rect.ylen <= board_max_y)
        rect.y_inter_var = self.model.NewOptionalFixedSizeIntervalVar(rect.y_var, rect.ylen, self.present, 
                                                                 self.name + "_y_" + str(rect_ind) + "_inter")

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

    model = cp_model.CpModel()
    all_orientations = DefineAllOrientations(model)

    for orientation in all_orientations:
        AddOrientationCons(model, orientation)

    for o1_ind in range(len(all_orientations)):
        for o2_ind in range(o1_ind+1, len(all_orientations)):
            AddNoOverlap(model, all_orientations[o1_ind], all_orientations[o2_ind])
    

    empty1_x_interval = model.NewFixedSizeIntervalVar(0,2,"f1_x")
    empty1_y_interval = model.NewFixedSizeIntervalVar(6,1,"f1_y")

    empty2_x_interval = model.NewFixedSizeIntervalVar(6,1,"f2_x")
    empty2_y_interval = model.NewFixedSizeIntervalVar(3,4,"f2_y")

    AddEmptyBlocks(model, all_orientations, empty1_x_interval, empty1_y_interval)
    AddEmptyBlocks(model, all_orientations, empty2_x_interval, empty2_y_interval)

    grid = [['X' for i in range(board_max_y)] for j in range(board_max_x)]

    grid[0] = ['JAN','FEB','MAR','APR','MAY','JUN',' X ']
    grid[1] = ['JUL','AUG','SEP','OCT','NOV','DEC',' X ']
    grid[2] = [' 01',' 02',' 03',' 04',' 05',' 06',' 07']
    grid[3] = [' 08',' 09',' 10',' 11',' 12',' 13',' 14']
    grid[4] = [' 15',' 16',' 17',' 18',' 19',' 20',' 21']
    grid[5] = [' 22',' 23',' 24',' 25',' 26',' 27',' 28']
    grid[6] = [' 29',' 30',' 31',' X ',' X ',' X ',' X ']

    for row in grid:
        print(row)
    
    month_x_interval, month_y_interval = GetGridIntervals(model, grid, month)
    date_x_interval, date_y_interval = GetGridIntervals(model, grid, date)

    AddEmptyBlocks(model, all_orientations, month_x_interval, month_y_interval)
    AddEmptyBlocks(model, all_orientations, date_x_interval, date_y_interval)
        
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = 1
    status = solver.Solve(model)
    print('\nStatistics')
    print(f'  status   : {solver.StatusName(status)}')
    print(f'  conflicts: {solver.NumConflicts()}')
    print(f'  branches : {solver.NumBranches()}')
    print(f'  wall time: {solver.WallTime()} s')

    box_id = 1
    for orientation in all_orientations:
        for box in orientation:
            if (solver.Value(box.present) > 0):
                print(box.name)
                for rect in box.rects:
                    for ind in range(rect.xlen):
                        for ind2 in range(rect.ylen):
                            assert not grid[solver.Value(rect.x_var) + ind][solver.Value(rect.y_var)+ ind2].startswith('*')
                            grid[solver.Value(rect.x_var) + ind][solver.Value(rect.y_var)+ ind2] = '*' + str(box_id) + '*'
        box_id += 1
    
    for row in grid:
        print(row)

def print_options():
    print('365day_puzzle_bf.py')
    print(' -D <date>')
    print(' -M <month>')

def AddOrientationCons(model: cp_model.CpModel, orien: list[Block]):
    bool_vars = [block.present for block in orien]
    # print(len(bool_vars))
    model.AddExactlyOne(bool_vars)
    


def AddNoOverlap(model: cp_model.CpModel, orien1: list[Block], orien2: list[Block]):
    for b1 in orien1:
        b1_x_intervals = [rect.x_inter_var for rect in b1.rects]
        b1_y_intervals = [rect.y_inter_var for rect in b1.rects]
        for b2 in orien2:
            
            b2_x_intervals = [rect.x_inter_var for rect in b2.rects]
            b2_y_intervals = [rect.y_inter_var for rect in b2.rects]
            x_intervals = b1_x_intervals + b2_x_intervals
            y_intervals = b1_y_intervals + b2_y_intervals
            model.AddNoOverlap2D(x_intervals,y_intervals)

def AddEmptyBlocks(model: cp_model.CpModel, oriens: list[list[Block]], 
                   empty_x_interval: cp_model.IntervalVar, empty_y_interval: cp_model.IntervalVar):
    for orien in oriens:
        for b1 in orien:
            b1_x_intervals = [rect.x_inter_var for rect in b1.rects]
            b1_x_intervals.append(empty_x_interval)
            b1_y_intervals = [rect.y_inter_var for rect in b1.rects]
            b1_y_intervals.append(empty_y_interval)

            model.AddNoOverlap2D(b1_x_intervals, b1_y_intervals)

def GetGridIntervals(model: cp_model.CpModel, grid: list[list[str]], entry: str):
    x_interval = None
    y_interval = None
    for x in range(board_max_x):
        for y in range(board_max_y):
            if grid[x][y] == entry:
                print("Reserving ", grid[x][y], x, y)
                x_interval = model.NewFixedSizeIntervalVar(x,1,"m_x")
                y_interval = model.NewFixedSizeIntervalVar(y,1,"m_y")
                return (x_interval,y_interval)
    return (x_interval,y_interval)

def DefineAllOrientations(model: cp_model.CpModel):
    all_orientations = []

    b1_1 = Block("b1_1", model)
    b1_1.AddRect(Rectangle(0,1,2,1))
    b1_1.AddRect(Rectangle(1,0,3,1))
    b1_2 = Block("b1_2", model)
    b1_2.AddRect(Rectangle(0,0,1,3))
    b1_2.AddRect(Rectangle(1,2,1,2))
    b1_3 = Block("b1_3", model)
    b1_3.AddRect(Rectangle(0,1,3,1))
    b1_3.AddRect(Rectangle(2,0,2,1))
    b1_4 = Block("b1_4", model)
    b1_4.AddRect(Rectangle(0,0,1,2))
    b1_4.AddRect(Rectangle(1,1,1,3))
    b1_5 = Block("b1_5", model)
    b1_5.AddRect(Rectangle(0,0,2,1))
    b1_5.AddRect(Rectangle(1,1,3,1))
    b1_6 = Block("b1_6", model)
    b1_6.AddRect(Rectangle(0,1,1,3))
    b1_6.AddRect(Rectangle(1,0,1,2))
    b1_7 = Block("b1_7", model)
    b1_7.AddRect(Rectangle(0,2,1,2))
    b1_7.AddRect(Rectangle(1,0,1,3))
    b1_8 = Block("b1_8", model)
    b1_8.AddRect(Rectangle(0,0,3,1))
    b1_8.AddRect(Rectangle(2,1,2,1))
    b1_orientations = [b1_1, b1_2, b1_3, b1_4,b1_5,b1_6,b1_7,b1_8]
    all_orientations.append(b1_orientations)

    b2_1 = Block("b2_1", model)
    b2_1.AddRect(Rectangle(0,0,3,2))
    b2_2 = Block("b2_2", model)
    b2_2.AddRect(Rectangle(0,0,2,3))
    b2_orientations = [b2_1, b2_2]
    all_orientations.append(b2_orientations)

    b3_1 = Block("b3_1", model)
    b3_1.AddRect(Rectangle(0,0,1,2))
    b3_1.AddRect(Rectangle(1,0,1,1))
    b3_1.AddRect(Rectangle(2,0,1,2))
    b3_2 = Block("b3_2", model)
    b3_2.AddRect(Rectangle(0,0,2,1))
    b3_2.AddRect(Rectangle(0,1,1,1))
    b3_2.AddRect(Rectangle(0,2,2,1))
    b3_3 = Block("b3_3", model)
    b3_3.AddRect(Rectangle(0,0,1,2))
    b3_3.AddRect(Rectangle(1,1,1,1))
    b3_3.AddRect(Rectangle(2,0,1,2))
    b3_4 = Block("b3_4", model)
    b3_4.AddRect(Rectangle(0,0,2,1))
    b3_4.AddRect(Rectangle(1,1,1,1))
    b3_4.AddRect(Rectangle(0,2,2,1))
    b3_orientations = [b3_1, b3_2, b3_3, b3_4]
    all_orientations.append(b3_orientations)

    b4_1 = Block("b4_1", model)
    b4_1.AddRect(Rectangle(0,0,2,2))
    b4_1.AddRect(Rectangle(2,0,1,1))
    b4_2 = Block("b4_2", model)
    b4_2.AddRect(Rectangle(0,1,2,2))
    b4_2.AddRect(Rectangle(0,0,1,1))
    b4_3 = Block("b4_3", model)
    b4_3.AddRect(Rectangle(1,0,2,2))
    b4_3.AddRect(Rectangle(0,1,1,1))
    b4_4 = Block("b4_4", model)
    b4_4.AddRect(Rectangle(0,0,2,2))
    b4_4.AddRect(Rectangle(1,2,1,1))
    b4_5 = Block("b4_5", model)
    b4_5.AddRect(Rectangle(0,0,2,2))
    b4_5.AddRect(Rectangle(2,1,1,1))
    b4_6 = Block("b4_6", model)
    b4_6.AddRect(Rectangle(0,0,2,2))
    b4_6.AddRect(Rectangle(0,2,1,1))
    b4_7 = Block("b4_7", model)
    b4_7.AddRect(Rectangle(1,0,2,2))
    b4_7.AddRect(Rectangle(0,0,1,1))
    b4_8 = Block("b4_8", model)
    b4_8.AddRect(Rectangle(0,1,2,2))
    b4_8.AddRect(Rectangle(1,0,1,1))
    b4_orientations = [b4_1, b4_2, b4_3, b4_4,b4_5,b4_6,b4_7,b4_8]
    all_orientations.append(b4_orientations)

    b5_1 = Block("b5_1", model)
    b5_1.AddRect(Rectangle(0,0,3,1))
    b5_1.AddRect(Rectangle(0,1,1,2))
    b5_2 = Block("b5_2", model)
    b5_2.AddRect(Rectangle(0,2,3,1))
    b5_2.AddRect(Rectangle(0,0,1,2))
    b5_3 = Block("b5_3", model)
    b5_3.AddRect(Rectangle(0,2,3,1))
    b5_3.AddRect(Rectangle(2,0,1,2))
    b5_4 = Block("b5_4", model)
    b5_4.AddRect(Rectangle(0,0,3,1))
    b5_4.AddRect(Rectangle(2,1,1,2))
    b5_orientations = [b5_1, b5_2, b5_3, b5_4]
    all_orientations.append(b5_orientations)

    b6_1 = Block("b6_1", model)
    b6_1.AddRect(Rectangle(0,0,4,1))
    b6_1.AddRect(Rectangle(0,1,1,1))
    b6_2 = Block("b6_2", model)
    b6_2.AddRect(Rectangle(0,0,1,4))
    b6_2.AddRect(Rectangle(1,3,1,1))
    b6_3 = Block("b6_3", model)
    b6_3.AddRect(Rectangle(0,1,4,1))
    b6_3.AddRect(Rectangle(3,0,1,1))
    b6_4 = Block("b6_4", model)
    b6_4.AddRect(Rectangle(1,0,1,4))
    b6_4.AddRect(Rectangle(0,0,1,1))
    b6_5 = Block("b6_5", model)
    b6_5.AddRect(Rectangle(0,1,4,1))
    b6_5.AddRect(Rectangle(0,0,1,1))
    b6_6 = Block("b6_6", model)
    b6_6.AddRect(Rectangle(0,0,1,4))
    b6_6.AddRect(Rectangle(1,0,1,1))
    b6_7 = Block("b6_7", model)
    b6_7.AddRect(Rectangle(0,0,4,1))
    b6_7.AddRect(Rectangle(3,1,1,1))
    b6_8 = Block("b6_8", model)
    b6_8.AddRect(Rectangle(1,0,1,4))
    b6_8.AddRect(Rectangle(0,3,1,1))
    b6_orientations = [b6_1, b6_2, b6_3, b6_4,b6_5,b6_6,b6_7,b6_8]
    all_orientations.append(b6_orientations)

    b7_1 = Block("b7_1", model)
    b7_1.AddRect(Rectangle(0,1,3,1))
    b7_1.AddRect(Rectangle(0,0,1,1))
    b7_1.AddRect(Rectangle(2,2,1,1))
    b7_2 = Block("b7_2", model)
    b7_2.AddRect(Rectangle(1,0,1,3))
    b7_2.AddRect(Rectangle(0,2,1,1))
    b7_2.AddRect(Rectangle(2,0,1,1))
    b7_3 = Block("b7_3", model)
    b7_3.AddRect(Rectangle(0,1,3,1))
    b7_3.AddRect(Rectangle(0,2,1,1))
    b7_3.AddRect(Rectangle(2,0,1,1))
    b7_4 = Block("b7_4", model)
    b7_4.AddRect(Rectangle(1,0,1,3))
    b7_4.AddRect(Rectangle(0,0,1,1))
    b7_4.AddRect(Rectangle(2,2,1,1))
    b7_orientations = [b7_1, b7_2, b7_3, b7_4]
    all_orientations.append(b7_orientations)

    b8_1 = Block("b8_1", model)
    b8_1.AddRect(Rectangle(0,0,4,1))
    b8_1.AddRect(Rectangle(1,1,1,1))
    b8_2 = Block("b8_2", model)
    b8_2.AddRect(Rectangle(0,0,1,4))
    b8_2.AddRect(Rectangle(1,2,1,1))
    b8_3 = Block("b8_3", model)
    b8_3.AddRect(Rectangle(0,1,4,1))
    b8_3.AddRect(Rectangle(2,0,1,1))
    b8_4 = Block("b8_4", model)
    b8_4.AddRect(Rectangle(1,0,1,4))
    b8_4.AddRect(Rectangle(0,1,1,1))
    b8_5 = Block("b8_5", model)
    b8_5.AddRect(Rectangle(0,1,4,1))
    b8_5.AddRect(Rectangle(1,0,1,1))
    b8_6 = Block("b8_6", model)
    b8_6.AddRect(Rectangle(0,0,1,4))
    b8_6.AddRect(Rectangle(1,1,1,1))
    b8_7 = Block("b8_7", model)
    b8_7.AddRect(Rectangle(0,0,4,1))
    b8_7.AddRect(Rectangle(2,1,1,1))
    b8_8 = Block("b8_8", model)
    b8_8.AddRect(Rectangle(1,0,1,4))
    b8_8.AddRect(Rectangle(0,2,1,1))
    b8_orientations = [b8_1, b8_2, b8_3, b8_4,b8_5,b8_6,b8_7,b8_8]
    all_orientations.append(b8_orientations)
    return all_orientations

if __name__ == "__main__":
    main(sys.argv[1:])
