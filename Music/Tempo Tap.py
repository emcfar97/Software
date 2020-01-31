import ui
import time

def calculate_tempo(sender):
	global elapse_2
	
	elapse_1 = round(time.time(), 2)
	tempo.append(60 / (elapse_1 - elapse_2))
	
	view['main']['tempo'].text = 'Tempo\n{:.1f} BPM'.format(sum(tempo) / len(tempo))
	view['main']['measures'].text = 'Measures\n{:.0f}'.format(len(tempo) // time_sign)
	elapse_2 = elapse_1

def slider(sender):
	global time_sign
	
	label = view['set_time']['time_sign']
	time_sign = int(sender.value * 7) + 1
	label.text = '{:.0f}'.format(time_sign)
	view['main']['measures'].text = 'Measures\n{}'.format(len(tempo) // time_sign)

def reset(sender):
	
	tempo.clear()
	elapse_2 = 0
	
	view['main']['tempo'].text = 'Tempo\n0 BPM'
	view['main']['measures'].text = 'Measures\n0'

tempo = []
elapse_2 = 0
time_sign = 4

view = ui.load_view('Tempo Tap.pyui')
reset(True)
view.present('sheet')


