""" Solver voor puzzel uit Eureka april 2011.
http://www.physics.leidenuniv.nl/eureka/pdf-magazines/eureka32.pdf

(c) 2011, Merlijn van Deen
Licensed under the MIT license.

"""

import sys
import numpy as np
import termcolor
from termcolor import colored

if len(sys.argv) != 2:
    print "Usage: %s <filename>" % sys.argv[0]

filename = sys.argv[1]

class STATE:
  UNKNOWN = '?'
  PLUS  = '+'
  MINUS = '-'
  EMPTY = ' '

f = open(filename)

# dimensions
nr = int(f.readline().split()[0])
nc = int(f.readline().split()[0])

# initialize storage
store = np.empty((nr, nc), dtype='a1') # single character string
store[:] = STATE.UNKNOWN

blockstore = np.empty((nr+1, nc+1), dtype='a1')
blockstore[:] = STATE.UNKNOWN

def ul(s):
    return colored(s, attrs=["underline"])

def printpuzzle():
    sys.stdout.write(" "+colored(" "*(nc*2-1), attrs=["underline"]) + "\n")
    for row in range(nr):
        sys.stdout.write("|")
        for col in range(nc):
            u = (blockstore[row,col] != blockstore[row+1,col])
            pipe = (blockstore[row, col+1] != blockstore[row, col])
            
            s = store[row,col]
            s = ul(s) if u else s
            
            if pipe:
                s += "|"
            else:
                s += ul(" ") if u else " "

            sys.stdout.write(s)
        sys.stdout.write("\n")

# read puzzle block
puzzle = f.readlines()

blockdata = [row[:nc] for row in puzzle[:nr]]
blockdict = {}
for ir, row in enumerate(blockdata):
    for ic, char in enumerate(row):
        blockdict.setdefault(char, []).append((ir, ic))
        blockstore[ir,ic] = char

printpuzzle()

for char, block in blockdict.iteritems():
    assert(len(block) == 2)

blocks = [x for x in blockdict.itervalues()]

# constraints on # of plus/minus per row/col
rplus  = [int(row[nc  ]) for row in puzzle[:nr]]
rminus = [int(row[nc+1]) for row in puzzle[:nr]]
cplus  = [int(char) for char in puzzle[nr  ][:nc]]
cminus = [int(char) for char in puzzle[nr+1][:nc]]

def checkdata(data, targetplus, targetminus):
    nplus  = np.sum(data == STATE.PLUS)
    nminus = np.sum(data == STATE.MINUS)
    if np.sum(data == STATE.UNKNOWN) == 0:
        return (nplus == targetplus) and (nminus == targetminus)
    else:
        return (nplus <= targetplus) and (nminus <= targetminus)

def checkrow(row):
    return checkdata(store[row], rplus[row], rminus[row])

def checkcol(col):
    return checkdata(store[:,col], cplus[col], cminus[col])

def checkcell(row, col):
    """ Returns TRUE if the value of cell (row, col) is legal considering
        its neighbors and the row/column properties """
    val = store[row, col]

    if val != STATE.UNKNOWN and val != STATE.EMPTY:
        for dr, dc in [(-1,0), (1,0), (0, -1), (0, 1)]:
            if (row+dr >= 0  and\
                row+dr < nr and\
                col+dc >= 0  and\
                col+dc < nr):
                if store[row+dr, col+dc] == val:
                    return False

    return (checkrow(row) and checkcol(col))

values = [(STATE.EMPTY, STATE.EMPTY),
          (STATE.PLUS, STATE.MINUS),
          (STATE.MINUS, STATE.PLUS),
         ]

steps = 0
def step(bi):
    global steps
    steps += 1
    if steps % 100 == 0:
        print ".",
        sys.stdout.flush()
    if bi == len(blocks):
        return True

    block1 = blocks[bi][0]
    block2 = blocks[bi][1]
    for value in values:
        store[block1] = value[0]
        store[block2] = value[1]
        if checkcell(*block1) and checkcell(*block2):
            if step(bi+1):
               return True

    store[block1] = STATE.UNKNOWN
    store[block2] = STATE.UNKNOWN
    return False

if step(0):
    print ""
    print "Result:"
    printpuzzle()
else:
    print "No result found"
