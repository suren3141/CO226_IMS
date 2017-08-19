import matplotlib
matplotlib.use('TkAgg')

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
# implement the default mpl key bindings
from matplotlib.backend_bases import key_press_handler


from matplotlib.figure import Figure

from tkinter import *


class Plotter(object):

    def __init__(self, root, x, y):

        child = Toplevel(root)
        child.wm_title("Graph")

        f = Figure(figsize=(5, 4), dpi=100)
        a = f.add_subplot(111)
        a.plot(x, y)

        self.set_up_canvas(child, f)

        button = Button(child, text='Quit', command= child.destroy)
        button.pack(side=BOTTOM)


    def on_key_event(self, event, canvas, toolbar):
        key_press_handler(event, canvas, toolbar)


    def set_up_canvas(self, child, fig):

        canvas = FigureCanvasTkAgg(fig, master=child)
        canvas.show()
        canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)

        toolbar = NavigationToolbar2TkAgg(canvas, child)
        toolbar.update()
        canvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=1)

        canvas.mpl_connect('key_press_event', self.on_key_event)

