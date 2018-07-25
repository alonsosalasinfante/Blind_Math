# from gtts import gTTS
# import multiprocessing
# from pygame import mixer # Load the required library

# tts = gTTS('hello hello hello hello', lang='en')
# tts.save('hello.mp3')

# def thing():
# 	mixer.music.load('hello.mp3')
# 	mixer.music.play()
# 	while mixer.music.get_busy():
# 		pass
# mixer.init()
# thing_p = multiprocessing.Process(target = thing)
# thing_p.start()
import pyttsx3
print("11111")
engine = pyttsx3.init()
print("22222")

import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvas
from tkinter import *
from tkinter.ttk import *
import multiprocessing

def graph(text):
	tmptext = entry.get()
	tmptext, new_expression = "$"+tmptext+"$", "$"+tmptext+"$"

	ax.clear()
	ax.text(0.2, 0.6, tmptext, fontsize = 50)  
	canvas.draw()

def thing():
	print("##############################")
	engine.say("test test test test")
	engine.runAndWait()
	print("FUUUUUUUUUUUUUUUUCCKKKKKK")


process_thing = multiprocessing.Process(target = thing)
process_thing.start()

# root = Tk()

# mainframe = Frame(root)
# mainframe.pack()

# text = StringVar()
# entry = Entry(mainframe, width=70, textvariable=text)
# entry.pack()

# label = Label(mainframe)
# label.pack()

# fig = matplotlib.figure.Figure(figsize=(5, 4), dpi=100)
# ax = fig.add_subplot(111)

# canvas = FigureCanvas(fig, master=label)
# canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
# canvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=1)

# ax.get_xaxis().set_visible(False)
# ax.get_yaxis().set_visible(False)

# root.bind('<Return>', graph)
# root.mainloop()







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