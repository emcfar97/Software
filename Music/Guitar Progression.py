import random#, sound
from midiutil import MIDIFile

def progression_generator(prog, roots, key):

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
	guitar = [ # maj min maj7 maj^7 min7
		[ #E-string
			[0, 7, 12, 16, 19, 24],
			[0, 7, 12, 15, 19, 24],
			[0, 7, 10, 16, 19, 24],
			[0, 7, 11, 16, 19, 24],
			[0, 7, 10, 15, 19, 24]
		],
		[ #A-string
			[0, 7, 12, 16, 19],
			[0, 7, 12, 15, 19],
			[0, 7, 10, 15, 19],
			[0, 7, 11, 16, 19],
			[0, 7, 10, 16, 19]
		],
		[ #D-string
			[0, 7, 12, 16],
			[0, 7, 12, 15],
			[0, 7, 10, 16],
			[0, 7, 11, 16],
			[0, 7, 10, 15]
		]
	]
	roots = [fretboard[key][0] + i for i in roots]
	strings = [random.choice([0, 1]) for i in roots]
	rhythm = rhythm_generator(chord, False)

	for chord, root, string, bar in zip(prog, roots, strings, rhythm):
		quality = chords[chord][0]
		chord = guitar[string][quality]
		if root == roots[-1]:
			chord_generator(chord, root, bar, True)
			break
		chord_generator(chord, root, bar)

def chord_generator(chord, root, bar, final=False):
	
	if final is True or final is False:
		if upstroke is False:
			for note in chord:
				note += root
				midi.addNote(0, 0, note, beat, 2, 100)
				print('midi.addNote(0, 0', note, beat, 5, '100)')
				beat += .2
			
		else:
			for note in chord:
				note += root
				midi.addNote(0, 0, note, beat, .5, 100)
				print('midi.addNote(0, 0', note, round(beat, 2), .5, '100)')
				beat += .2

	# else:
		# for note in chord + chord[-2:1:-1]:
			# note += root
			# midi.addNote(0, 0, note, beat, .5, 100)
			# print('midi.addNote(0, 0', note, round(beat, 2), .5, '100)')
			# beat += .1
	# beat += .2
		
def rhythm_generator(beat=0):

	note_durations = [
		(tempo*.0625)/tempo,
		(tempo*.125)/tempo,
		(tempo*.25)/tempo,
		(tempo*.5)/tempo,
		(tempo)/tempo
		]

	rhythm = []

	for i in range(4):
		rhythm.append([])
		while sum(rhythm[i]) < 1:
			note_length = random.choice(note_durations)
			if sum(rhythm[i]) + note_length > 1:
				continue
			rhythm[i].append(note_length)
			beat += note_length

	return rhythm

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

chords = { # 'chord quality':[interval distance]
	'I': [0, 0], 'i': [1, 0], 'I7': [2, 0], 'I^7': [3, 0], 'i7': [4, 0],
	'II': [0, 1], 'ii': [1, 1], 'II7': [2, 1], 'II^7': [3, 1], 'ii7': [4, 1],
	'III': [0, 2], 'iii': [1, 2], 'III7': [2, 2], 'III^7': [3, 2], 'iii7': [4, 2],
	'IV': [0, 3], 'iv': [1, 3], 'IV7': [2, 3], 'IV^7': [3, 3], 'iv7': [4, 3],
	'V': [0, 4], 'v': [1, 4], 'V7': [2, 4], 'V^7': [3, 4], 'v7': [4, 4],
	'VI': [0, 5], 'vi': [1, 5], 'VI7': [2, 5], 'VI^7': [3, 5], 'vi7': [4, 5],
	'VII': [0, 6], 'vii': [1, 6], 'VII7': [2, 6], 'VII^7': [3, 6], 'vii7': [6, 6]
}

tempo = 80

key = name = 'Eb major'.split()
mode = modes[key[1].lower()]
key = key[0].capitalize()

progression = 'ii7 V7 I^7'.split()
name += [i for i in progression]
roots = [mode[chords[i][1]] for i in progression]

with open('output.mid'.format(*name), 'wb') as file:
	midi = MIDIFile(1, adjust_origin=True)
	midi.addTempo(0, 0, tempo)
	midi.addProgramChange(0, 0, 0, 24)
	progression_generator(progression, roots, key)
	midi.writeFile(file)
	player = sound.MIDIPlayer('output.mid')
	player.play()

while True:
	break
	menuOp = input(
		'1.Create Progression\n'
		'2.Play Progression\n'
		'3.Exit\n'
	)
	if menuOp == '1':
		try:
			tempo = input('Enter tempo')
		
			key = name = input('Enter scale').split()
			key = key[0].capitalize()
			mode = modes[key[1].lower()]
		
			progression = input('Enter progression').split()
			roots = [mode[chords[i][1]] for i in progression]
			name += [i for i in progression]
		
			with open('{}.mid'.format(*name), 'wb') as file:
				midi = MIDIFile(1, adjust_origin=True)
				midi.addTempo(0, 0, tempo)
				midi.addProgramChange(0, 0, 0, 24)
				progression_generator(progression, roots, key)
				midi.writeFile(file)
			
		except Exception as error:
			print('Error:', error)

	elif menuOp == '2':
		try:
			file = input('Enter file name\n')

			player = sound.MIDIPlayer('{}.mid'.format(file))
			player.play()
			
		except Exception as error:
			print('Error:', error)
	
	elif menuOp == '3':
		break

	else:
		continue
