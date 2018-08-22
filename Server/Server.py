from graphics import *
from enum import Enum
from pynput import keyboard
from threading import Thread
from time import sleep

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

class DIR(Enum):
    N = 0
    NE = 1
    E = 2
    SE = 3
    S = 4
    SV = 5
    V = 6
    NV = 7

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

    def GetColor(self):
        return self.color

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

    # Draw the initial four tokens to allign to
    cellArray[3][3].SetColor(COLOR.BLACK)
    cellArray[3][4].SetColor(COLOR.WHITE)
    cellArray[4][3].SetColor(COLOR.WHITE)
    cellArray[4][4].SetColor(COLOR.BLACK)

def advance(r, c, dir):
    if dir == DIR.N:
        r = r - 1
    elif dir == DIR.NE:
        r = r - 1
        c = c + 1
    elif dir == DIR.E:
        c = c + 1
    elif dir == DIR.SE:
        r = r + 1
        c = c + 1
    elif dir == DIR.S:
        r = r + 1
    elif dir == DIR.SV:
        r = r + 1
        c = c - 1
    elif dir == DIR.V:
        c = c - 1
    elif dir == DIR.NV:
        r = r - 1
        c = c - 1

    if r < 0 or r > 7 or c < 0 or c > 7:
        return [False, r, c]

    return [True, r, c]

def updateTokensInDirection(r, c, dir):
    startR = r
    startC = c

    lastR = -1
    lastC = -1

    while advance(r, c, dir)[0]:
        res = advance(r, c, dir)
        newR = res[1]
        newC = res[2]

        if cellArray[newR][newC].GetColor() == CURRENT_PLAYING_COLOR:
            lastR = newR
            lastC = newC

        r = newR
        c = newC

    allGood = True
    if lastR != -1 and lastC != -1:
        r = startR
        c = startC

        foundEmpty = False

        while advance(r, c, dir)[0]:
            res = advance(r, c, dir)
            newR = res[1]
            newC = res[2]

            if cellArray[newR][newC].GetColor() == COLOR.NONE:
                foundEmpty = True

            if newR == lastR and newC == lastC:
                if foundEmpty:
                    allGood = False
                break;

            r = newR
            c = newC

    if lastR != -1 and lastC != -1 and allGood:
        r = startR
        c = startC

        while advance(r, c, dir)[0]:
            res = advance(r, c, dir)
            newR = res[1]
            newC = res[2]

            if newR == lastR and newC == lastC:
                return

            cellArray[newR][newC].Flip()

            r = newR
            c = newC

def mouseCallback(clickedPoint):
    global CURRENT_PLAYING_COLOR
    for cell in cells:
            if cell.HasBeenTouched(clickedPoint):
                if cell.GetColor() != COLOR.NONE:
                    return

                # Move on all directions to flip the colors
                i = cell.i
                j = cell.j

                updateTokensInDirection(i, j, DIR.N)
                updateTokensInDirection(i, j, DIR.NE)
                updateTokensInDirection(i, j, DIR.E)
                updateTokensInDirection(i, j, DIR.SE)
                updateTokensInDirection(i, j, DIR.S)
                updateTokensInDirection(i, j, DIR.SV)
                updateTokensInDirection(i, j, DIR.V)
                updateTokensInDirection(i, j, DIR.NV)

                cell.SetColor(CURRENT_PLAYING_COLOR)

                # Last thing to do is switch current color
                if CURRENT_PLAYING_COLOR == COLOR.WHITE:
                    CURRENT_PLAYING_COLOR = COLOR.BLACK
                else:
                    CURRENT_PLAYING_COLOR = COLOR.WHITE

def render_thread():
    while True:
        block = None
        time.sleep (16.66 / 1000.0);

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
    RenderThread = Thread(target = render_thread, args = ( ))
    RenderThread.start()
    clearUI()
    main()
