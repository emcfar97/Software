import ui, random, time, sqlite3

SELECT = 'SELECT * from scaleDegrees'
UPDATE = 'UPDATE scaleDegrees SET timer=?, question=?, attempts=?, last=?, high=?'

def setup():
    
    timer_slider.value = data[0]
    question_slider.value = data[1]
    attempts.value = bool(data[2])
    last = data[3].split()
    high = data[4].split()
    
    slider(timer_slider)
    slider(question_slider)
    slider(attempts)    
    
    results['ratio_last'].text = last[0]
    results['percent_last'].text = '{}%'.format(last[1])
    results['timer_last'].text = '{}:{:02d}'.format(int(last[2])//60, int(last[2])%60)
    
    results['ratio_high'].text = high[0]
    results['percent_high'].text = '{}%'.format(high[1])
    results['timer_high'].text = '{}:{:02d}'.format(int(high[2])//60, int(high[2])%60)
    
    nav.present('sheet', hide_title_bar=True)
    #choice()
    
def close():
    
    global data

    data[:3] = [
        round(timer_slider.value, 3),
        round(question_slider.value, 3),
        int(attempts.value)
        ]
    data.append(' '.join(*ratio, ratio[0]/ratio[1]*100, 0))
    #percent = int(data['high']['percent']) > ratio[0]/ratio[1]*100
    #timer = int(data['high']['timer'][0]) < 0
    
    #if percent:
    #       data[4] = ' '.join(*ratio, ratio[0]/ratio[1]*100, 0)

    datab.execute(UPDATE, (data))
    datab.commit().close()
    
    results['ratio_last'].text = '{}/{}'.format(data[3].split('-')[0])
    results['percent_last'].text = '{:.0f}%'.format(data[3].split('-')[1])
    results['timer_last'].text = '{}:{:02d}'.format(data[3].split('-')[2])
    
    results['ratio_high'].text = '{}/{}'.format(data[4].split('-')[0])
    results['percent_high'].text = '{:.0f}%'.format(data[4].split('-')[1])
    results['timer_high'].text = '{}:{:02d}'.format(data[4].split('-')[2])
    
    nav.push_view(view['results'], False)
    
def choice():

    global correct
    question = main['question']['question1']
    
    for button in main['buttons'].subviews:
        button.background_color='414141'
        button.touch_enabled = True
        button.font = ('Farah', 20)
        
    octave = random.choice(list(octaves.keys()))
    mode = random.choice(list(modes.keys()))
    scale = [octaves[octave][i] for i in modes[mode]]
    note = random.randint(1, 6)
    
    if random.randint(0,1) == 0:
        correct = scale[note]
        question.text = 'What is the {} of {} {}?'.format(degrees[note], octave, mode)
        
    else:
        correct = octaves[octave][0]
        question.text = '{} is the {} of what {} scale?'.format(
        scale[note][0], degrees[note], mode
        )
        
@ui.in_background
def next(sender):

    ratio[1] += 1
    sender.touch_enabled = False
    
    if sender.title in correct:
        ratio[0] += 1
        sender.background_color='00c000'
        time.sleep(1)
        
        if ratio[0] == value[1]:# or timer in [None, 0]:
            close()
        else:
            choice()
    elif attempts.value:
        sender.background_color='c00000'
    else:
        sender.background_color='c00000'
        time.sleep(1)
        choice()
        
    main['ratio'].text = '{}/{}'.format(*ratio)
    main['percent'].text = '{:.0f}%'.format(ratio[0]/ratio[1]*100)
    #main['timer'].text = '{}:{:02d}'.format(timer, timer)
    
def options(sender):

    nav.push_view(options)
    
def start(sender):

    nav.push_view(main)
    
def slider(sender):

    global ratio, timer, value
    
    if 'timer' in sender.name:
        value[0] = int(sender.value * 5)
        timer_label.text = '{:.0f} min'.format(value[0])
        timer = int(time.time()) - int(time.time() + (value[0] * 60))
        main['timer'].text = '{}:{:02d}'.format(value[0]//60, value[0]%60)
        if sender.value == 0:
            timer_label.text = 'Off'
            timer = 0
            
    elif 'question' in sender.name:
        value[1] = int(sender.value * 100)
        question_label.text = '{:.0f}'.format(value[1])
        if sender.value == 0:
            question_label.text = 'Off'
            
    ratio = [0,0]
    choice()
    
octaves = {
    'C' :[
        ['C','B♯'],['C♯','D♭'],['D'],['D♯','E♭'],['E','F♭'],['F','E♯'],['F♯','G♭'],['G'],['G♯','A♭'],['A'],['A♯','B♭'],['B','C♭']
        ],
    'C♯':[
        ['C♯','D♭'],['D'],['D♯','E♭'],['E','F♭'],['F','E♯'],['F♯','G♭'],['G'],['G♯','A♭'],['A'],['A♯','B♭'],['B','C♭'],['C','B♯']
        ],
    'D♭':[
        ['D♭','C♯'],['D'],['E♭','D♯'],['E','F♭'],['F','E♯'],['G♭','F♯'],['G'],['A♭','G♯'],['A'],['B♭','A♯'],['C♭','B'],['C','B♯']
        ],
    'D' :[
        ['D'],['D♯','E♭'],['E','F♭'],['F','E♯'],['F♯','G♭'],['G'],['G♯','A♭'],['A'],['A♯','B♭'],['B','C♭'],['C','B♯'],['C♯','D♭']
        ],
    'D♯':[
        ['D♯','E♭'],['E','F♭'],['F','E♯'],['F♯','G♭'],['G'],['G♯','A♭'],['A'],['A♯','B♭'],['B','C♭'],['C','B♯'],['C♯','D♭'],['D']
        ],
    'E♭':[
        ['E♭','D♯'],['E','F♭'],['F','E♯'],['G♭','F♯'],['G'],['A♭','G♯'],['A'],['B♭','A♯'],['B','C♭'],['C','B♯'],['D♭','C♯'],['D']
        ],
    'E' :[
        ['E','F♭'],['F','E♯'],['F♯','G♭'],['G'],['G♯','A♭'],['A'],['A♯','B♭'],['B','C♭'],['C','B♯'],['C♯','D♭'],['D'],['D♯','E♭']
        ],
    'F' :[
        ['F','E♯'],['F♯','G♭'],['G'],['G♯','A♭'],['A'],['A♯','B♭'],['B','C♭'],['C','B♯'],['C♯','D♭'],['D'],['D♯','E♭'],['E','F♭']
        ],
    'F♯':[
        ['F♯','G♭'],['G'],['G♯','A♭'],['A'],['A♯','B♭'],['B','C♭'],['C','B♯'],['C♯','D♭'],['D'],['D♯','E♭'],['E','F♭'],['F','E♯']
        ],
    'G♭':[
        ['G♭','F♯'],['G'],['A♭','G♯'],['A'],['B♭','A♯'],['B','C♭'],['C','B♯'],['D♭','C♯'],['D'],['E♭','D♯'],['E','F♭'],['F','E♯']
        ],
    'G' :[
        ['G'],['G♯','A♭'],['A'],['A♯','B♭'],['B','C♭'],['C','B♯'],['C♯','D♭'],['D'],['D♯','E♭'],['E','F♭'],['F','E♯'],['F♯','G♭']
        ],
    'A♭':[
        ['A♭','G♯'],['A'],['B♭','A♯'],['B','C♭'],['C','B♯'],['D♭','C♯'],['D'],['E♭','D♯'],['E','F♭'],['F','E♯'],['G♭','F♯'],['G']
        ],
    'A' :[
        ['A'],['A♯','B♭'],['B','C♭'],['C','B♯'],['C♯','D♭'],['D'],['D♯','E♭'],['E','F♭'],['F','E♯'],['F♯','G♭'],['G'],['G♯','A♭']
        ],
    'A♯':[
        ['A♯','B♭'],['B','C♭'],['C','B♯'],['C♯','D♭'],['D'],['D♯','E♭'],['E','F♭'],['F','E♯'],['F♯','G♭'],['G'],['G♯','A♭'],['A']
        ],
    'B♭':[
        ['B♭','A♯'],['C♭','B'],['C','B♯'],['D♭','C♯'],['D'],['E♭','D♯'],['E','F♭'],['F','E♯'],['G♭','F♯'],['G'],['A♭','G♯'],['A']
        ],
    'B' :[
        ['B','C♭'],['C','B♯'],['C♯','D♭'],['D'],['D♯','E♭'],['E','F♭'],['F','E♯'],['F♯','G♭'],['G'],['G♯','A♭'],['A'],['A♯','B♭']
        ],
    'C♭':[
        ['C♭','B'],['C','B♯'],['D♭','C♯'],['D'],['E♭','D♯'],['E','F♭'],['F','E♯'],['G♭','F♯'],['G'],['A♭','G♯'],['A'],['B♭','A♯']
        ]
    }
degrees = [
        'I', 'II', 'III',
        'IV', 'V', 'VI', 'VII'
        ]
modes = {
        'Lydian':  [0, 2, 4, 6, 7, 9, 11],
        'Ionian':  [0, 2, 4, 5, 7, 9, 11],
        'Mixolydian':[0, 2, 4, 5, 7, 9, 10],
        'Dorian':  [0, 2, 3, 5, 7, 9, 10],
        'Aeolian': [0, 2, 3, 5, 7, 8, 10],
        'Phrygian':[0, 1, 3, 5, 7, 8, 10],
        # 'Locrian':[0, 1, 3, 5, 6, 8, 10]
        }

datab = sqlite3.connect('Data.sqlite')
data = datab.execute(SELECT).fetchone()

ratio = value = [0,0]
correct = None
timer = 0

view = ui.load_view('Scale Degrees.pyui')
nav = ui.NavigationView(view)

options = view['options']
main = view['main']
results = view['results']['results1']
timer_label = options['timer']['timer1']
timer_slider = options['timer']['timer2']
question_label = options['question']['question1']
question_slider = options['question']['question2']
attempts = options['attempts']['attempts2']

setup()

