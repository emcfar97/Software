import time, random, ui

def set_turn():
    octave = random.choice(list(octaves.keys()))
    choices = [
        random.choice(list(intervals.items())) for i in range(4)
        ]
    interval = random.choice(choices)

    view['question'].text = 'What is the {} of the {}?'.format(interval[1], octave)

def card_return(sender):
	correct = octaves[octave][interval[0]]
	
	if sender.title == correct:
		score[0] += 1
		score[1] += 1
		view['question'].text = 'Correct. It\'s {}'.format(correct)
		time.sleep(2)
		set_turn()
	score[0] += 1
	view['question'].text = 'Incorrect. It\'s {}'.format(correct)
	time.sleep(2)
	set_turn()

def end_game():
	view['time'].text = ''
	view['question'].text = 'Total/Correct\n{}/{}'.format(*score)
	
octaves = {
    'C octave' :['C','C♯','D','D♯','E','F','F♯','G','G♯','A','A♯','B'],
    'C♯ octave':['C♯','D','D♯','E','F','F♯','G','G♯','A','A♯','B','C'],
    'D♭ octave':['D♭','D','E♭','E','F','G♭','G','A♭','A','B♭','C♭','C'],
    'D octave' :['D','D♯','E','F','F♯','G','G♯','A','A♯','B','C','C♯'],
    'D♯ octave':['D♯','E','F','F♯','G','G♯','A','A♯','B','C','C♯','D'],
    'E♭ octave':['E♭','E','F','G♭','G','A♭','A','B♭','B','C','D♭','D'],
    'E octave' :['E','F','F♯','G','G♯','A','A♯','B','C','C♯','D','D♯'],
    'F octave' :['F','F♯','G','G♯','A','A♯','B','C','C♯','D','D♯','E'],
    'F♯ octave':['F♯','G','G♯','A','A♯','B','C','C♯','D','D♯','E','F'],
    'G♭ octave':['G♭','G','A♭','A','B♭','B','C','D♭','D','E♭','E','F'],
    'G octave' :['G','G♯','A','A♯','B','C','C♯','D','D♯','E','F','F♯'],
    'A♭ octave':['A♭','A','B♭','B','C','D♭','D','E♭','E','F','G♭','G'],
    'A octave' :['A','A♯','B','C','C♯','D','D♯','E','F','F♯','G','G♯'],
    'A♯ octave':['A♯','B','C','C♯','D','D♯','E','F','F♯','G','G♯','A'],
    'B♭ Octave':['B♭','C♭','C','D♭','D','E♭','E','F','G♭','G','A♭','A'],
    'B Octave' :['B','C','C♯','D','D♯','E','F','F♯','G','G♯','A','A♯'],
    'C♭ Octave':['C♭', 'C','D♭','D','E♭','E','F','G♭','G','A♭','A','B♭']
    }

intervals = {
    0:'Octave',
    1:'Minor\nSecond',
    2:'Major\nSecond',
    3:'Minor\nThird',
    4:'Major\nThird',
    5:'Perfect\nFourth',
    6:'Tritone',
    7:'Perfect\nFifth',
    8:'Minor\nSixth',
    9:'Major\nSixth',
    10:'Minor\nSeventh',
    11:'Major\nSeventh',
    }

timeout = time.time() + 60
#int(input('enter value in seconds: '))
score = [0, 0]

view = ui.load_view('Interval')
view.present('Sheet')
octave = random.choice(list(octaves.keys()))
choices = [
    random.choice(list(intervals.items())) for i in range(4)
    ]
interval = random.choice(choices)

view['question'].text = 'What is the {} of the {}?'.format(interval[1], octave)

while timeout > time.time():
    view['time'].text = '{:>2.0f} seconds left'.format(timeout - time.time())
    
    view['option1'].title = octaves[octave][choices[0][0]]
    view['option2'].title = octaves[octave][choices[1][0]]
    view['option3'].title = octaves[octave][choices[2][0]]
    view['option4'].title = octaves[octave][choices[3][0]]

end_game()
