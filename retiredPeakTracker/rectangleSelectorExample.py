from __future__ import print_function
"""
Do a mouseclick somewhere, move the mouse to some destination, release
the button.  This class gives click- and release-events and also draws
a line or a box from the click-point to the actual mouseposition
(within the same axes) until the button is released.  Within the
method 'self.ignore()' it is checked whether the button from eventpress
and eventrelease are the same.

"""
from matplotlib.widgets import RectangleSelector
from matplotlib.widgets import Cursor
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches


savedRectangles = np.empty(shape = [0, 4])


def rectSelectCallback(eclick, erelease):
    global savedRectangles
    'eclick and erelease are the press and release events'
    x1, y1 = eclick.xdata, eclick.ydata
    x2, y2 = erelease.xdata, erelease.ydata
    thisRect = np.array([[x1, y1, x2, y2]])
    savedRectangles = np.append(savedRectangles, thisRect, axis = 0)
    xDis = np.abs(x1 - x2)
    yDis = np.abs(y1 - y2)
    x0 = min(x1, x2)
    y0 = min(y1, y2)
    rect = patches.Rectangle((x0, y0), xDis, yDis, linewidth = 1,
                             edgecolor = 'r', linestyle = '--',
                             facecolor = 'none')
    ax.add_patch(rect)
    plt.draw()


def confirmSelection(event):
    if event.key in ['enter'] and confirmSelection.RS.active:
        print('Done selecting regions.')
        toggle_selector.RS.set_active(False)


fig, ax = plt.subplots()                 # make a new plotting range
N = 100000                                       # If N is large one can see
x = np.linspace(0.0, 10.0, N)                    # improvement by use blitting!

plt.plot(x, +np.sin(.2*np.pi*x), lw=3.5, c='b', alpha=.7)  # plot something
plt.plot(x, +np.cos(.2*np.pi*x), lw=3.5, c='r', alpha=.5)
plt.plot(x, -np.sin(.2*np.pi*x), lw=3.5, c='g', alpha=.3)

print("\n      click  -->  release")

cursor = Cursor(ax, useblit = True, color = '0.5', linewidth = 1, linestyle = ':')
confirmSelection.RS = RectangleSelector(ax, rectSelectCallback,
                                        drawtype = 'box', useblit = True,
                                        button = [1], minspanx = 5,
                                        minspany = 5, spancoords = 'pixels',
                                        interactive = True)
plt.connect('key_press_event', confirmSelection)
plt.show()
