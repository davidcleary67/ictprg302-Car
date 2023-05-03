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
    if col <= posTrack:
        col = posTrack + 1
        hitEdge = LEFT
        health -= 1
    elif col >= (posTrack + TRACKWIDTH - 3):
        col = posTrack + TRACKWIDTH - 4
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
        track.append({"pos" : left, "fuel" : False})
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
    global TRACKWIDTH
    global hitEdge
    if curveTrack == LEFT and track[0]["pos"] > 0:
        newCol = track[0]["pos"] - 1
        curveCount -= 1
        curveTrack = STRAIGHT if curveCount == 0 else curveTrack
    elif curveTrack == RIGHT and track[0]["pos"] < (cols - 3) - TRACKWIDTH:
        newCol = track[0]["pos"] + 1
        curveCount -= 1
        curveTrack = STRAIGHT if curveCount == 0 else curveTrack
    elif curveTrack == SHRINK:
        newCol = track[0]["pos"]
        TRACKWIDTH = TRACKWIDTH - 1 if TRACKWIDTH > 7 else TRACKWIDTH
        curveTrack = STRAIGHT
    else:
        newCol = track[0]["pos"]
        curveCount = int(random.random() * 100)
        if curveCount < 10:
            curveTrack = int(random.random() * 3) + 1
        else:
            curveTrack = STRAIGHT
    newFuel = int(random.random() * 20) == 1
    if newFuel:
        fuelPos = int(random.random() * 3) + 1
    track.insert(0, {"pos" : newCol, "fuel" : fuelPos if newFuel else 0})
    track.pop(-1)
    
    win.erase()
    row = 1
    leftEdge = "|"
    rightEdge = "|"
    for t in track:
        col = t["pos"]
        if row == len(track):
            leftEdge = "X" if hitEdge == LEFT else "|"
            rightEdge = "X" if hitEdge == RIGHT else "|"
            hitEdge = NONE
        win.addstr(row, col, leftEdge, curses.color_pair(YELLOWBLUE) | curses.A_BOLD)
        win.addstr(row, col + 1, " " * TRACKWIDTH, curses.color_pair(YELLOWBLUE))
        win.addstr(row, col + TRACKWIDTH + 1, rightEdge, curses.color_pair(YELLOWBLUE) | curses.A_BOLD)
        fuelPos = t["fuel"]
        if fuelPos > 0:
            if fuelPos == 1:
                win.addstr(row, col + 1, "F", curses.color_pair(REDWHITE) | curses.A_REVERSE)
            elif fuelPos == 2:
                win.addstr(row, col + int(TRACKWIDTH / 2), "F", curses.color_pair(REDWHITE) | curses.A_REVERSE)
            else:
                win.addstr(row, col + TRACKWIDTH, "F", curses.color_pair(REDWHITE) | curses.A_REVERSE)
        row += 1 

def collideFuel(posFuel, posTrack, posCar):
    collide = False
    if posFuel > 0:
        if posFuel == 1 and posCar == posTrack + 1:
            collide = True
        elif posFuel == 3 and posCar + 4 == posTrack + TRACKWIDTH:
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