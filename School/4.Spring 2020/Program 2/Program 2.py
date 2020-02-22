##############################################################################
##
## CS 461
## Program #1
## Ethan McFarland
## Em463@mail.umkc.edu
##
##############################################################################

courses = {
    'CS 101A': 40,
    'CS 101B': 25,
    'CS 201A': 30,
    'CS 201B': 30,
    'CS 191A': 60,
    'CS 191B': 20,
    'CS 291B': 40,
    'CS 291A': 20,
    'CS 303': 50,
    'CS 341': 40,
    'CS 449': 55,
    'CS 461': 40,
    }
instructors = {
    'Hare': ['CS 101', 'CS 201', 'CS 291', 'CS 303', 'CS 449', 'CS 461'],
    'Bingham': ['CS 101', 'CS 201', 'CS 191', 'CS 291', 'CS 449'],
    'Kuhail': ['CS 303', 'CS 341'],
    'Mitchell': ['CS 191', 'CS 291', 'CS 303', 'CS 341'],
    'Rao': ['CS 291', 'CS 303', 'CS 341', 'CS 461'],
    'Staff': [],
    }
time = [
    '10A', 
    '11A', 
    '12P', 
    '1P', 
    '2P', 
    '3P', 
    '4P'
    ]
rooms = {
    'Haag 301': 70,
    'Haag 206': 30,
    'Royall 204': 70,
    'Katz 209': 50,
    'Flarsheim 310': 80,
    'Flarsheim 260': 25,
    'Bloch 0009': 30
    }

def fitness(x):

    u ~ Uniform(0, 1, size = d)
    y = sgn(u - 0.5) * T * ((1 + 1/T)**abs(2*u - 1) - 1.0)

    xc = y * (upper - lower)
    x_new = x_old + xc

    c = n * exp(-n * quench)
    T_new = T0 * exp(-c * k**quench)

interval = (-10, 10)

def f(x):
    """ Function to minimize."""
    return x ** 2

def clip(x):
    """ Force x to be in the interval."""
    a, b = interval
    return max(min(x, b), a)

def random_start():
    """ Random point in the interval."""
    a, b = interval
    return a + (b - a) * rn.random_sample()

def cost_function(x):
    """ Cost of x = f(x)."""
    return f(x)

def random_neighbour(x, fraction=1):
    """Move a little bit x, from the left or the right."""
    amplitude = (max(interval) - min(interval)) * fraction / 10
    delta = (-amplitude/2.) + amplitude * rn.random_sample()
    return clip(x + delta)

def acceptance_probability(cost, new_cost, temperature):
    if new_cost < cost:
        # print("    - Acceptance probabilty = 1 as new_cost = {} < cost = {}...".format(new_cost, cost))
        return 1
    else:
        p = np.exp(- (new_cost - cost) / temperature)
        # print("    - Acceptance probabilty = {:.3g}...".format(p))
        return p
        
def temperature(fraction):
    """ Example of temperature dicreasing as the process goes on."""
    return max(0.01, min(1, 1 - fraction))
