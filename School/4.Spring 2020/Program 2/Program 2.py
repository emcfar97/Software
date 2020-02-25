##############################################################################
##
## CS 461
## Program #1
## Ethan McFarland
## Em463@mail.umkc.edu
##
##############################################################################

import random, math

class Schedule():

    def __init__(self, times, courses, instructors, rooms):

        self.times = times
        self.courses = courses
        self.instructors = instructors
        self.rooms = rooms
        self.timeslots = []
        self.choose()

    def choose(self): 
        
        if self.timeslots: pass

        else:
            
            for instructor, courses in self.instructors.items():
                
                for course in courses:

                    pass

    def fitness(self): pass

class Timeslot():

    def __init__(self, time, course, instructor, room):

        self.time = time
        self.course = course
        self.instructor = instructor
        self.room = room

    def __repr__(self):

        return f'{self.course}\n{self.time}\n{self.instructor}\n{self.room}\n'

class Course():
    
    def __init__(self, course, enroll, section=''): 

        self.course = course
        self.enroll =  enroll
        self.section = section
    
    def __repr__(self): return f'{self.course}{self.section} ({self.enroll})'

class Instructor():
    
    def __init__(self, instructor, courses):

        self.instructor = instructor
        self.courses = courses

    def __repr__(self): return f'{self.instructor} ({self.courses})'

class Room():
    
    def __init__(self, room, capacity):

        self.room = room
        self.capacity = capacity

    def __repr__(self): return f'{self.room} ({self.capacity})'

courses = {
    'CS 101A': Course('CS 101', 40, 'A'),
    'CS 101B': Course('CS 101', 25, 'B'),
    'CS 201A': Course('CS 201', 30, 'A'),
    'CS 201B': Course('CS 201', 30, 'B'),
    'CS 191A': Course('CS 191', 60, 'A'),
    'CS 191B': Course('CS 191', 20, 'B'),
    'CS 291B': Course('CS 291', 40, 'B'),
    'CS 291A': Course('CS 291', 20, 'A'),
    'CS 303': Course('CS 303', 50),
    'CS 341': Course('CS 341', 40),
    'CS 449': Course('CS 449', 55),
    'CS 461': Course('CS 461', 40),
    }
instructors = {
    'Hare': Instructor(
        'Hare', [courses['CS 101A'], courses['CS 101B'], courses['CS 201A'], courses['CS 201B'], courses['CS 291A'], courses['CS 291B'], courses['CS 303'], courses['CS 449'], courses['CS 461']]
        ),
    'Bingham': Instructor(
        'Bingham', [courses['CS 101A'], courses['CS 101B'], courses['CS 201A'], courses['CS 201B'], courses['CS 191A'], courses['CS 191B'], courses['CS 291A'], courses['CS 291B'], courses['CS 449']]
        ),
    'Kuhail': Instructor(
        'Kuhail', [courses['CS 303'], courses['CS 341']]
        ),
    'Mitchell': Instructor(
        'Mitchell', [courses['CS 191A'], courses['CS 191B'], courses['CS 291A'], courses['CS 291B'], courses['CS 303'], courses['CS 341']]
        ),
    'Rao': Instructor(
        'Rao', [courses['CS 291A'], courses['CS 291B'], courses['CS 303'], courses['CS 341'], courses['CS 461']]
        ),
    'Staff': Instructor(
        'Staff', [list(courses.values())]
        ),
    }
times = [
    '10A', 
    '11A', 
    '12P', 
    '1P', 
    '2P', 
    '3P', 
    '4P'
    ]
rooms = {
    'Haag 301': Room('Haag 301', 70),
    'Haag 206': Room('Haag 206', 30),
    'Royall 204': Room('Royall 204', 70),
    'Katz 209': Room('Katz 209', 50),
    'Flarsheim 310': Room('Flarsheim 310', 80),
    'Flarsheim 260': Room('Flarsheim 260', 25),
    'Bloch 0009': Room('Bloch 0009', 30)
    }

scheduler = Schedule(times, courses, instructors, rooms)

temperature = None
current_state = None

# while temperature >= 0:

#     for i in range(1, max_iter):

#         next_state = action_on(current_state)
#         energy_delta = value(next_state) - value(current_state)
#         if (energy_delta < 0) or (math.exp(-energy_delta / temperature) >= random.randint(0, 10)):
#             current_state = next_state

#     temperature = alpha * temperature