import pyttsx3, symbols
if __name__ == '__main__':
	engine = pyttsx3.init()
	voices = engine.getProperty('voices')
	print(voices[0].id, voices[7].id, voices[11].id, voices[26].id, voices[36].id)
	engine.setProperty('voice', voices[26].id)
	engine.say("x plus 231")
	engine.runAndWait()
	engine.say("x")
	engine.say("plus")
	engine.say("231")
	engine.runAndWait()

	# engine = pyttsx3.init()
	# voices = engine.getProperty('voices')
	# i = 0
	# for voice in voices:
	# 	print(i)
	# 	i += 1
	# 	engine.setProperty('voice', voice.id)
	# 	engine.say('The quick brown fox jumped over the lazy dog.')
	# 	engine.runAndWait()

