import sound

file = input('Enter file name\n')

player = sound.MIDIPlayer('{}.mid'.format(file))
player.play()
