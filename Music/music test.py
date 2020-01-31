from midiutil import MIDIFile
from random import randint
import sound

def rhythm_generator(beat=0, length=[]):
	
	
	while sum(length) != tempo:
		length.append([])
		for i in range(time_sign):
			bar = beat//time_sign
			length[bar].append(1)
			bar += 1
	return length

tempo = 120
time_sign = 4

midi = MIDIFile(1, adjust_origin=True)
midi.addTempo(0, 0, tempo)
midi.addProgramChange(0, 0, 0, 24)
rhythm = rhythm_generator()

for bar in zip(rhythm[0], rhythm[1]):
	for beat in bar:
		midi.addNote(0, 0, 60, beat, note, 100)

with open('output.mid', 'wb') as file:
	midi.writeFile(file)
	player = sound.MIDIPlayer('output.mid')
	player.play()
