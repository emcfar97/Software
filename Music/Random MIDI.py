'''Generates a MIDI file with 12 random notes in C major, using the midiutil module. The instrument is also picked randomly. The result is then played with the sound.MIDIPlayer class.
If nothing happens, make sure that your device isn't muted.
'''

from midiutil.MidiFile import MIDIFile
from random import choice, choices, randint
import sound

# Configure a MIDI file with one track:
midi = MIDIFile(1, adjust_origin=True)
midi.addTempo(0, 0, 180)

# Select a random instrument:
program = randint(0, 255)
midi.addProgramChange(0, 0, 0, program)

seed = randint(1, 8)
duration = [seed/8, seed/4, seed/2, seed]
	
modes = {
	'lydian':[0, 2, 4, 6, 7, 9, 11, 12],
	'ionian':[0, 2, 4, 5, 7, 9, 11, 12],
	'mixolydian':[0, 2, 4, 5, 7, 9, 10, 12],
	'dorian':[0, 2, 3, 5, 7, 9, 10, 12],
	'aeolian':[0, 2, 3, 5, 7, 8, 10, 12],
	'phyrgian':[0, 1, 3, 5, 7, 8, 10, 12],
	'locrian':[0, 1, 3, 5, 6, 8, 10, 12]
}

tonic = randint(24, 72)
mode = choice(list(modes.keys()))
octave = [tonic + interval for interval in modes[mode]]
print(mode,octave)
for t in range(50):
	pitch = choices(octave, [7,2,6,4,6,2,4,7])[0]
	length = choices(duration, [4,9,4,1])[0]
	# track, channel, pitch, time, duration, volume
	midi.addNote(0, 0, pitch, (t * length)%90, length, 100)
	
# Write output file:
with open('output.mid', 'wb') as f:
	midi.writeFile(f)

# Play the result:
player = sound.MIDIPlayer('output.mid')
player.play()
