#!/usr/bin/python3

"""
Program:   car.py
Version:   1.0
Date:      ***
Author:    David Cleary
Licencing: Copyright 2023 SuniTAFE. All rights reserved.
"""

import random
import time
import curses
from curses import wrapper
from curses.textpad import Textbox, rectangle

BLUEWHITE = 1
BLACKWHITE = 2
REDWHITE = 3
YELLOWBLUE = 4
WHITEBLUE = 5
REDBLUE = 6
BLACKBLUE = 7
YELLOWBLACK = 8
GREENWHITE = 9
MAGENTAWHITE = 10

DRAWTIMEOUT = 10000

def getDims(win, pause):
    """ 
    Interactive mode function
    Get screen dimensions in rows and columns.
        
    Parameters:
        win (curses screen): return dimensions of this screen
        
        pause (Boolean): True -> display dimensions and pause
    
    Returns:
        rows (integer): screen rows
        
        cols (integer): screen columns
    """
    rows = curses.LINES
    cols = curses.COLS
    win.addstr(f"Lines: {rows}, Rows: {cols}\n")
    win.refresh()
    if pause:
        win.addstr("Press any key to continue.")
        win.getch()
    return rows, cols

def hideCursor(win, rows, cols):
    win.addstr(rows - 1, cols - 1, "")
    
def drawCar(win, row, col, rows, track, health, moveKey = None):
    global hitEdge
    posTrack = track[rows - 2]["pos"]
    widthTrack = track[rows - 2]["width"]
    if col <= posTrack:
        col = posTrack + 1
        hitEdge = LEFT
        health -= 1
    elif col >= (posTrack + widthTrack - 3):
        col = posTrack + widthTrack- 4
        hitEdge = RIGHT
        health -= 1
    win.addstr(row, col + 1, chr(0x256d) + chr(0x2500) + chr(0x256e), curses.color_pair(WHITEBLUE))
    win.addstr(row + 1, col, chr(0x2593), curses.color_pair(BLACKBLUE))
    win.addstr(row + 1, col + 1, chr(0x2534), curses.color_pair(WHITEBLUE))
    win.addstr(row + 1, col + 2, chr(0x2580), curses.color_pair(REDBLUE))
    win.addstr(row + 1, col + 3, chr(0x2534), curses.color_pair(WHITEBLUE))
    win.addstr(row + 1, col + 4, chr(0x2593), curses.color_pair(BLACKBLUE))
    if moveKey == curses.KEY_LEFT:
        win.addstr(row, col + 4, chr(32), curses.color_pair(BLACKBLUE))
        win.addstr(row + 1, col + 5, chr(32), curses.color_pair(BLACKBLUE))
    elif moveKey == curses.KEY_RIGHT:
        win.addstr(row, col, chr(32), curses.color_pair(BLACKBLUE))
        win.addstr(row + 1, col - 1, chr(32), curses.color_pair(BLACKBLUE))
    return col, health

def createTrack(rows, cols):
    left = int((cols - TRACKWIDTH) / 2) + 1
    track = []
    for r in range(rows - 1):
        track.append({"pos" : left, "fuel" : False, "width" : TRACKWIDTH})
    return track

STRAIGHT = 0
LEFT = 1
RIGHT = 2
SHRINK = 3
NONE = 4

TRACKWIDTH = 15
curveTrack = STRAIGHT 
curveCount = 0
hitEdge = NONE

def drawInfo(win, cols, health, fuel, elapsedTime):
    win.addstr(0, 0, "SuniTAFE Rally Driver", curses.color_pair(REDWHITE) | curses.A_BOLD) 
    win.addstr(0, 22, "Health: ", curses.color_pair(GREENWHITE)) 
    win.addstr(str(health), curses.color_pair(MAGENTAWHITE) | curses.A_BOLD) 
    win.addstr(" Fuel: ", curses.color_pair(GREENWHITE)) 
    win.addstr(str(fuel), curses.color_pair(MAGENTAWHITE) | curses.A_BOLD) 
    win.addstr(" Time: ", curses.color_pair(GREENWHITE)) 
    win.addstr(elapsedTime, curses.color_pair(MAGENTAWHITE) | curses.A_BOLD) 

def drawTrack(win, track, cols):
    global curveTrack
    global curveCount
    global hitEdge
    posTrack = track[0]["pos"]
    widthTrack = track[0]["width"]
    if curveTrack == LEFT and posTrack > 0:
        newCol = posTrack - 1
        curveCount -= 1
        curveTrack = STRAIGHT if curveCount == 0 else curveTrack
    elif curveTrack == RIGHT and posTrack < (cols - 3) - widthTrack:
        newCol = posTrack + 1
        curveCount -= 1
        curveTrack = STRAIGHT if curveCount == 0 else curveTrack
    elif curveTrack == SHRINK:
        newCol = posTrack
        widthTrack = widthTrack - 1 if widthTrack > 7 else widthTrack
        curveTrack = STRAIGHT
    else:
        newCol = posTrack
        curveCount = int(random.random() * 100)
        if curveCount < 10:
            curveTrack = int(random.random() * 3) + 1
        else:
            curveTrack = STRAIGHT
    newFuel = int(random.random() * 20) == 1
    if newFuel:
        fuelPos = int(random.random() * 3) + 1
    track.insert(0, {"pos" : newCol, "fuel" : fuelPos if newFuel else 0, "width" : widthTrack})
    track.pop(-1)
    
    win.erase()
    row = 1
    leftEdge = "|"
    rightEdge = "|"
    for t in track:
        pos = t["pos"]
        width = t["width"]
        fuelPos = t["fuel"]
        if row == len(track):
            leftEdge = "X" if hitEdge == LEFT else "|"
            rightEdge = "X" if hitEdge == RIGHT else "|"
            hitEdge = NONE
        win.addstr(row, pos, leftEdge, curses.color_pair(YELLOWBLUE) | curses.A_BOLD)
        win.addstr(row, pos + 1, " " * width, curses.color_pair(YELLOWBLUE))
        win.addstr(row, pos + width + 1, rightEdge, curses.color_pair(YELLOWBLUE) | curses.A_BOLD)
        if fuelPos > 0:
            if fuelPos == 1:
                win.addstr(row, pos + 1, "F", curses.color_pair(REDWHITE) | curses.A_REVERSE)
            elif fuelPos == 2:
                win.addstr(row, pos + int(width / 2), "F", curses.color_pair(REDWHITE) | curses.A_REVERSE)
            else:
                win.addstr(row, pos + width, "F", curses.color_pair(REDWHITE) | curses.A_REVERSE)
        row += 1 

def collideFuel(posCar, track):
    collide = False
    posTrack = track[-1]["pos"]
    widthTrack = track[-1]["width"]
    posFuel = track[-1]["fuel"]
    posFuelExact = int(widthTrack / 2)
    if posFuel > 0:
        if posFuel == 1 and posCar == posTrack + 1:
            collide = True
        elif posFuel == 2 and posFuelExact >= posCar and posFuelExact <= posCar + 4:
            collide = True
        elif posFuel == 3 and posCar + 4 == posTrack + widthTrack:
            collide = True
    return collide
    
def cursesMain(stdScr):
    stdScr = curses.initscr()
    curses.init_pair(BLUEWHITE, curses.COLOR_BLUE, curses.COLOR_WHITE)
    curses.init_pair(BLACKWHITE, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(REDWHITE, curses.COLOR_RED, curses.COLOR_WHITE)
    curses.init_pair(GREENWHITE, curses.COLOR_GREEN, curses.COLOR_WHITE)
    curses.init_pair(MAGENTAWHITE, curses.COLOR_MAGENTA, curses.COLOR_WHITE)
    curses.init_pair(YELLOWBLUE, curses.COLOR_YELLOW, curses.COLOR_BLUE)
    curses.init_pair(WHITEBLUE, curses.COLOR_WHITE, curses.COLOR_BLUE)
    curses.init_pair(REDBLUE, curses.COLOR_RED, curses.COLOR_BLUE)
    curses.init_pair(BLACKBLUE, curses.COLOR_BLACK, curses.COLOR_BLUE)
    curses.init_pair(YELLOWBLACK, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    stdScr.bkgd(' ', curses.color_pair(BLUEWHITE))
    rows, cols = getDims(stdScr, False)
    stdScr.nodelay(True)
    stdScr.clear()
    
    startTime = time.time()
    currentTime = time.time()

    track = createTrack(rows, cols)
  
    carR = rows - 2
    carC = int((cols - 2) / 2)
    health = 10
    fuel = 10
    key = None
    drawTimer = DRAWTIMEOUT
    prevElapsedTime = -1
    while (health > 0):
        if drawTimer < 0: 
            drawTrack(stdScr, track, cols)
            drawTimer = DRAWTIMEOUT
            currentTime = time.time()
            elapsedTime = int(currentTime - startTime)
            if (prevElapsedTime != elapsedTime) and (elapsedTime % 10 == 0):
                fuel -= 1
                prevElapsedTime = elapsedTime
            if collideFuel(carC, track):
                fuel += 1
            drawInfo(stdScr, cols, health, fuel, f"{int(elapsedTime / 60):02d}:{(elapsedTime % 60):02d}")
        carC, health = drawCar(stdScr, carR, carC, rows, track, health, key)
        hideCursor(stdScr, rows, cols)
        stdScr.refresh()
        key = stdScr.getch()
        if key == curses.KEY_LEFT:
            carC = carC - 1 if carC > 0 else carC
        elif key == curses.KEY_RIGHT:
            carC = carC + 1 if carC < cols - 6 else carC
        drawTimer -= 1
            
    stdScr.nodelay(False)
    stdScr.addstr(2, 0, "Press any key to continue.")
    stdScr.getch()
    
    curses.endwin()

def main():
    wrapper(cursesMain)
    pass

## call main function  
if __name__ == "__main__":
    main()
