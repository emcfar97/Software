import ui

def slider(sender):
	label = view['set_tempo']['tempo_label']
	value = sender.value * 200 + 40
	label.text = '{:.0f}'.format(value)
	tempo = value

fretboard = {
		'Eb': [40, 52, 64],
		'E': [40, 52, 64],
		'F': [41, 53, 65],
		'F#': [40, 52, 64],
		'Gb': [40, 52, 64],
		'G': [42, 54, 66],
		'G#': [40, 52, 64],
		'Ab': [40, 52, 64],
		'A': [45, 56, 68],
		'A#': [40, 52, 64],
		'Bb': [40, 52, 64],
		'B': [47, 58, 70],
		'C': [48, 60, 72],
		'C#': [40, 52, 64],
		'Db': [40, 52, 64],
		'D': [50, 62, 74],
		'D#': [40, 52, 64],
	}

modes = {
	'lydian':[0, 2, 4, 6, 7, 9, 11, 12],
	'ionian':[0, 2, 4, 5, 7, 9, 11, 12],
	'major':[0, 2, 4, 5, 7, 9, 11, 12],
	'mixolydian':[0, 2, 4, 5, 7, 9, 10, 12],
	'dorian':[0, 2, 3, 5, 7, 9, 10, 12],
	'aeolian':[0, 2, 3, 5, 7, 8, 10, 12],
	'minor':[0, 2, 3, 5, 7, 8, 10, 12],
	'phyrgian':[0, 1, 3, 5, 7, 8, 10, 12],
	'locrian':[0, 1, 3, 5, 6, 8, 10, 12]
}

view = ui.load_view()
view.present('sheet')

tempo = None
view['set_key']['modes'].data_source = modes.keys()
view['set_key']['key'].data_source = fretboard.keys()
