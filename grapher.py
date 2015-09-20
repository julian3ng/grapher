#!/usr/bin/env python
import curses
from math import *
import time
import sys
import parser
import argparse

def init_curses(screen):
    '''
    load my preferred curses defaults
    '''
    curses.start_color()
    curses.noecho()
    curses.cbreak()
    screen.keypad(1)
    screen.nodelay(1)

def init_colors():
    '''
    load all xterm-256color colors
    '''
    for i in range(16, 256):
        curses.init_pair(i, i, 0)

def end_curses(screen):
    '''
    return screen to its normal state
    '''
    screen.nodelay(0)
    curses.nocbreak()
    screen.keypad(0)
    curses.echo()
    curses.endwin()

def draw_x_axis(y, screen):
    '''
    draw x axis at height y
    '''
    screen.hline(y, 0, '-', screen.getmaxyx()[1])

def draw_y_axis(x, screen):
    '''
    draw y axis at location x
    '''
    screen.vline(0, x, '|', screen.getmaxyx()[0])

def draw_origin(y, x, screen):
    '''
    mark the origin down
    '''
    screen.addch(y, x, '+')

def plot_point(y, x, screen, c='.', color=255, fill=False):
    '''
    plots (y, x) where y and x are coordinates with respect to the axes
    '''
    max_y, max_x = screen.getmaxyx()
    oy, ox = int(max_y/2), int(max_x/2)
    if max_y%2==1:
        oy+=1
    if max_x%2==1:
        ox+=1
    plot_y = int(round(max_y-(y+max_y/2)))
    plot_x = int(x+(max_x/2))
    screen.addch(plot_y, plot_x, c, curses.color_pair(color))

    if fill:
        if plot_y > oy:
            for i in range(0, plot_y-oy):
                screen.addch(oy+i, plot_x, c, curses.color_pair(color))
        else:
            for i in range(0, oy-plot_y):
                screen.addch(plot_y+i+1, plot_x, c, curses.color_pair(color))

def message(m, screen, color=51, y=5):
    start_x = (screen.getmaxyx()[1]/2)-int(len(m)/2)
    screen.addstr(screen.getmaxyx()[0]-y, start_x, m, color)

if __name__ == '__main__':
    argparser = argparse.ArgumentParser()
    argparser.add_argument("eq", help="The equation you want to graph")
    argparser.add_argument("-p", "--point", help="char for your point")
    argparser.add_argument("-c", "--color", help="xterm-256 color (0-255)", type=int)
    argparser.add_argument("-t", "--timestep", help="determines the speed of the graph output", type=float)
    argparser.add_argument("-f", "--fill", help="fills the graph if on", action="store_true")
    args = argparser.parse_args()

    scr = curses.initscr()
    init_curses(scr)
    init_colors()

    max_y, max_x = scr.getmaxyx()

    oy = int(max_y/2)
    if (max_y%2==1):
        oy+=1
    ox = int(max_x/2)
    if (max_x%2==1):
        ox+=1
    eq = args.eq

    code = parser.expr(eq).compile()
    color = 255
    timestep = 0.001
    max_y_axis = max_y
    max_x_axis = max_x
    point = '.'
    if args.color:
        color = args.color
    if args.timestep:
        timestep = args.timestep
    if args.point:
        point = args.point

    t = (-ox)
    while t <= (ox-1):
        if scr.getch() == ord('p'):
            scr.nodelay(0)
            message("[Paused]", scr, 41, 5)
            message("Press 'p' to resume", scr, 41, 4)
            if scr.getch() == ord('p'):
                scr.nodelay(1)

        scr.clear()
        draw_x_axis(oy, scr)
        draw_y_axis(ox, scr)
        draw_origin(oy, ox, scr)

        for x in range(-ox, t):
            #clear out the coords in the upper left
            for i in range(0, 30):
                for j in range(0, 2):
                    scr.addch(j, i, ' ')
            try:
                y = eval(code)
                plot_point(y, x, scr, point, color, fill=args.fill)
                scr.addstr(0, 0, "("+str(x)+", "+str(y)+")", curses.color_pair(51))
            except ValueError:
                scr.addstr(0, 0, "(ValueError, "+str(x)+")", curses.color_pair(199))
            except:
                scr.addstr(0, 0, "("+str(x)+", "+str(y)+")", curses.color_pair(199))


        #plot_point(0, t, scr, '|', color)
        t+=1
        time.sleep(timestep)
        scr.refresh()


    message("Press any key to exit.", scr)
    scr.nodelay(0)
    scr.getch()
    end_curses(scr)
