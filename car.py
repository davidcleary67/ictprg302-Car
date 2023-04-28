#!/usr/bin/python3

"""
Program:   car.py
Version:   1.0
Date:      ***
Author:    David Cleary
Licencing: Copyright 2023 SuniTAFE. All rights reserved.
"""

import curses
from curses import wrapper
from curses.textpad import Textbox, rectangle

BLUEWHITE = 1
BLACKWHITE = 2
REDWHITE = 3

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
    
def drawCar(win, row, col, moveKey = None):
    win.addstr(row, col + 1, chr(0x256d) + chr(0x2500) + chr(0x256e))
    win.addstr(row + 1, col, chr(0x2593), curses.color_pair(BLACKWHITE))
    win.addstr(row + 1, col + 4, chr(0x2593), curses.color_pair(BLACKWHITE))
    win.addstr(row + 1, col + 1, chr(0x2534))
    win.addstr(row + 1, col + 3, chr(0x2534))
    win.addstr(row + 1, col + 2, chr(0x2580), curses.color_pair(REDWHITE))
    if moveKey == curses.KEY_LEFT:
        win.addstr(row, col + 4, chr(32))
        win.addstr(row + 1, col + 5, chr(32))
    elif moveKey == curses.KEY_RIGHT:
        win.addstr(row, col, chr(32))
        win.addstr(row + 1, col - 1, chr(32))

def cursesMain(stdScr):
    stdScr = curses.initscr()
    curses.init_pair(BLUEWHITE, curses.COLOR_BLUE, curses.COLOR_WHITE)
    curses.init_pair(BLACKWHITE, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(REDWHITE, curses.COLOR_RED, curses.COLOR_WHITE)
    stdScr.bkgd(' ', curses.color_pair(BLUEWHITE))
    rows, cols = getDims(stdScr, True)
    stdScr.clear()

    carR = rows - 2
    carC = int((cols - 2) / 2)
    key = None
    while True:
        drawCar(stdScr, carR, carC, key)
        hideCursor(stdScr, rows, cols)
        stdScr.refresh()
        key = stdScr.getch()
        if key == curses.KEY_LEFT:
            carC -= 1
        elif key == curses.KEY_RIGHT:
            carC += 1
            
    stdScr.addstr(2, 0, "Press any key to continue.")
    stdScr.getch()
    
    curses.endwin()

def main():
    wrapper(cursesMain)
    pass

## call main function  
if __name__ == "__main__":
    main()