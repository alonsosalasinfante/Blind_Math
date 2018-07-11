import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvas
from tkinter import *
from tkinter.ttk import *

def graph(text):
    tmptext = entry.get()
    tmptext = "$"+tmptext+"$"

    ax.clear()
    ax.text(0.2, 0.6, tmptext, fontsize = 50)  
    canvas.draw()


root = Tk()

mainframe = Frame(root)
mainframe.pack()

text = StringVar()
entry = Entry(mainframe, width=70, textvariable=text)
entry.pack()

label = Label(mainframe)
label.pack()

fig = matplotlib.figure.Figure(figsize=(5, 4), dpi=100)
ax = fig.add_subplot(111)

canvas = FigureCanvas(fig, master=label)
canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
canvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=1)

ax.get_xaxis().set_visible(False)
ax.get_yaxis().set_visible(False)

root.bind('<Return>', graph)
root.mainloop()







# import multiprocessing as mp
# def test():
# 	import matplotlib
# 	matplotlib.use('TkAgg')

# 	import matplotlib.pyplot as plt
# 	from matplotlib.backends.backend_tkagg import FigureCanvas

# 	import tkinter
# 	import tkinter.ttk 
# 	def graph(text):
# 		tmptext = entry.get()
# 		tmptext = "$"+tmptext+"$"

# 		ax.clear()
# 		ax.text(0.2, 0.6, tmptext, fontsize = 50)  
# 		canvas.draw()

# 	root = tkinter.Tk()
# 	mainframe = tkinter.Frame(root)
# 	mainframe.pack()


# 	text = tkinter.StringVar()
# 	entry = tkinter.Entry(mainframe, width=110, textvariable=text)
# 	entry.pack()

# 	label = tkinter.Label(mainframe)
# 	label.pack()

# 	fig = matplotlib.figure.Figure(figsize=(6, 6), dpi=100)
# 	ax = fig.add_subplot(111)

# 	canvas = FigureCanvas(fig, master=label)
# 	canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
# 	canvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=1)

# 	ax.get_xaxis().set_visible(False)
# 	ax.get_yaxis().set_visible(False)

# 	root.bind('<Return>', graph)
# 	root.mainloop()


# thing = mp.Process(target = test)
# thing.start()