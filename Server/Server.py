from graphics import *
from enum import Enum
from pynput import keyboard

CELL_SIZE = 80
PADDING = 10

WINDOW_SIZE_X = CELL_SIZE * 8 + PADDING * 2
WINDOW_SIZE_Y = CELL_SIZE * 8 + PADDING * 2

COLOR_WHITE = '#FFFFFF'
COLOR_BLACK = '#000000'
NORMAL_COLOR = '#FFFFFF'

class COLOR(Enum):
    NONE = 0
    WHITE = 1
    BLACK = 2

CURRENT_PLAYING_COLOR = COLOR.WHITE

window = GraphWin("CodeCup 2019 Server", WINDOW_SIZE_X, WINDOW_SIZE_Y)

cellArray = [[0] * 8 for i in range(8)]

cells = []

class Cell:

    def __init__(self, leftCorner, size, name, i, j):
        self.leftCorner = leftCorner
        self.size = size
        self.name = name

        self.i = i
        self.j = j

        self.color = COLOR.NONE

        vertices = []
        vertices.append(Point(leftCorner.x, leftCorner.y))
        vertices.append(Point(leftCorner.x + size, leftCorner.y))
        vertices.append(Point(leftCorner.x + size, leftCorner.y + size))
        vertices.append(Point(leftCorner.x, leftCorner.y + size))

        self.shape = Polygon(vertices)
        self.shape.setFill(NORMAL_COLOR)
        self.shape.setWidth(1)

        self.token = Circle(Point(self.leftCorner.x + CELL_SIZE / 2, self.leftCorner.y + CELL_SIZE / 2), CELL_SIZE * 0.35)
        self.token.setWidth(2)

    def Draw(self, window):
        self.shape.draw(window)

    def Undraw(self):
        self.shape.undraw()

    def SetColor(self, color):
        self.color = color
        if color == COLOR.WHITE:
            self.token.setFill(COLOR_WHITE)
        elif color == COLOR.BLACK:
            self.token.setFill(COLOR_BLACK)
        self.token.undraw()
        self.token.draw(window)

    def Flip(self):
        if self.color == COLOR.NONE:
            return
        
        if self.color == COLOR.WHITE:
            self.token.setFill(COLOR_BLACK)
            self.color = COLOR.BLACK
        elif self.color == COLOR.BLACK:
            self.token.setFill(COLOR_WHITE)
            self.color = COLOR.WHITE
        self.token.undraw()
        self.token.draw(window)

    def HasBeenTouched(self, pt):
        isTouched = pt.x > self.leftCorner.x and pt.x < self.leftCorner.x + CELL_SIZE and pt.y > self.leftCorner.y and pt.y < self.leftCorner.y + CELL_SIZE
        return isTouched

def clearUI():
    startPosX = PADDING
    startPosY = PADDING

    posX = startPosX
    posY = startPosY

    for i in range(0, 8):
        for j in range(0, 8):
            cell = Cell(Point(posX, posY), CELL_SIZE, "", i, j)
            cellArray[i][j] = cell
            cells.append(cell)
            posX = posX + CELL_SIZE
        posY = posY + CELL_SIZE
        posX = startPosX

    for cell in cells:
        cell.Draw(window)
            
def mouseCallback(clickedPoint):
    global CURRENT_PLAYING_COLOR
    for cell in cells:
            if cell.HasBeenTouched(clickedPoint):
                cell.SetColor(CURRENT_PLAYING_COLOR)

                if CURRENT_PLAYING_COLOR == COLOR.WHITE:
                    CURRENT_PLAYING_COLOR = COLOR.BLACK
                else:
                    CURRENT_PLAYING_COLOR = COLOR.WHITE

                # Move on all directions to flip the colors
                i = cell.i
                j = cell.j

                for _i in range(i, 8):
                    cellArray[_i][j].Flip();
                for _i in range(0, i):
                    cellArray[_i][j].Flip();
                for _j in range(j, 8):
                    cellArray[i][_j].Flip();
                for _j in range(0, j):
                    cellArray[i][_j].Flip();


def on_press(key):
    try: k = key.char
    except: k = key.name
    if k == 'c':
        clearUI()

def main():
    window.setMouseHandler(mouseCallback)
    window.mainloop()

if __name__ == "__main__":
    lis = keyboard.Listener(on_press=on_press)
    lis.start()
    clearUI()
    main()
