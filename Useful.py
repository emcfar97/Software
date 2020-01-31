from math import sqrt, radians, sin, cos, atan , degrees

def exchange(matrix, start, end):
    
    print(
        'Exchange R{0} with R{1}'
        .format(sub[start], sub[end])
        )
    [print(i) for i in matrix]
    print()
    
    exchange = matrix[start-1]
    matrix[start-1] = matrix[end-1]
    matrix[end-1] = exchange
    
    [print(i) for i in matrix]
    print()

def multiplication(matrix, start, num):
    
    print(
        'Multiply {1}R{0}'
        .format(sub[start], num)
        )
    [print(i) for i in matrix]
    print()
    
    for i, j in enumerate(matrix[start-1]):
        matrix[start-1][i] = j * num
    
    [print(i) for i in x]
    print()

def addition(matrix, start, end, num):
    
    print(
        'Add {2}R{0} to R{1}'
        .format(sub[start], sub[end], num)
        )
    [print(i) for i in matrix]
    print()

    for i, j in zip(matrix[start-1], range(len(matrix[end-1]))):
        matrix[end-1][j] = (i*num) + matrix[end-1][j]
    
    [print(i) for i in matrix]
    print()

sub = ['₀', '₁', '₂', '₃', '₄', '₅', '₆', '₇', '₈', '₉']

def transpose(x):
    
    return [[x[j][i] for j in range(i)] for i, _ in enumerate(x)]

def quest_28(p_vec, vel, acc, time):
        
    # position vector
    p_x_comp = (p_vec[0]*cos(radians(p_vec[1]))) + (time*vel[0]*cos(radians(vel[1]))) + (0.5*25*acc[0]*cos(radians(acc[1])))
    p_y_comp = (p_vec[0]*sin(radians(p_vec[1]))) + (time*vel[0]*sin(radians(vel[1]))) + (0.5*25*acc[0]*sin(radians(acc[1])))
    
    p_magnitude = sqrt(p_x_comp**2 + p_y_comp**2)
    p_direction = degrees(atan((p_y_comp) / (p_x_comp)))
    
    # velocity vector
    vel_x_comp = (vel[0] * cos(radians(vel[1]))) + (acc[0] * time * cos(radians(acc[1])))
    vel_y_comp = (vel[0] * sin(radians(vel[1]))) + (acc[0] * time * sin(radians(acc[1])))
    
    vel_magnitude = sqrt(vel_x_comp**2 + vel_y_comp**2)
    vel_direction = degrees(atan((vel_y_comp / vel_x_comp)))
    
    print(
	'(a)\n'
	'{:.2f} m/s\n'
	'\n(b)\n'
	'{:.2f} m\n'
    .format(vel_magnitude,p_magnitude)
    )
   
position_vector = 31.1, 95.0 #from x-axis
velocity = 4.33, 40.0
acceleration = 2.02, 200
time = 5.00

def quest_29(dis, vel):
    
    g = (vel**2) / dis
    
    print(
    '(a)\n'
	'({:.2f}**2) / (2 * {:.2f}) = {:.2f} m/s'
	.format(vel, dis, g)
    )
   
h_dist = 19.0
speed = 2.60

def quest_34(g, ft_s):
    
    k = sqrt(g * ft_s / 29)
    
    x = (k / 2 * pi) / 10
    
    print(
    '{:.2f}'
    .format(x)
    )

g = 14.0
ft_s = 32.2

def quest_36(len_1, len_2, rev_s1, rev_s2):
    
    v1 = 2 * pi * rev_s1 * len_1
    v2 = 2 * pi * rev_s2 * len_2
    
    x = v1**2 / rev_s1
    y = v2**2 / rev_s2
    
    print(
    '(b)\n'
    '2 * {8:.2f} * {0:.2f} * {1:.2f} = {2:.2f}\n'
    '{2:.2f}^2 / {0:.2f} = {3:.2f}\n'
    '\n(c)\n'
    '2 * {8:.2f} * {4:.2f} * {5:.2f} = {6:.2f}\n'
    '{6:.2f}^2 / {4:.2f} = {7:.2f}'
    .format(len_1, rev_s1, v1, x, len_2, rev_s2, v2, y, pi)
    )

lengths = 8.32, 6.59
revolutions = .600, .900

def quest_37(orb, acc, rad):
    
    x = orb**2 / rad
    v_2 = orb * 7
    
    print(
    '{} m/s\n'
    '{}min'
    .format()
    )

orbit = 500
accel = 8.15
radius = 6400

def quest_38(acc, rad, deg):
    
    a_r = (cos(radians(deg)) * acc)
    
    v = (sqrt(a_r * rad))
    x = 17.5*sin(radians(deg))
    a_t = 17.5*sin(radians(deg))
    
    print(
    '(a)\n'
    'cos({:.2f}) * {:.2f} = {:.2f} m/s^2\n'
    '\n(b)\n'
    'sqrt({:.2f} * {:.2f}) = {:.2f} m/s\n'
    '\n(c)\n'
    'sqrt({:.2f}**2 - {:.2f}**2) = {:.2f} m/s^2\n'
    .format(
        deg, acc, a_r, 
        a_r, rad, v, 
        acc, a_r, a_t)
    )

lal = 11.5
r = 1.70
deg = 30

def displacement(v1, v2, mass, sec):
    
    v = (v1[0] + v2[0]), (v1[1] + v2[1])
    vector = v[0] / mass, v[1] / mass
    x = vector[0] * sec, vector[1] * sec
    accel = (.5/mass) * (sec**2)
    
    direction = 360 + degrees(atan(v[1] / v[0]))
    displace = accel * v[0], accel * v[1]
    coordinates = rest[0] - accel, rest[1] - accel
    
    print(
        '(a)\n'
        'v = {:.2f}i {:.2f}j m/s\n\n'

        '(b) In what direction is the particle moving at t = 11.1 s?\n'
        '{:.2f}° counterclockwise from the +x-axis\n\n'

        '(c) What displacement does the particle undergo during the first 11.1 s?\n'
        'Δr = {:.2f}i {:.2f}jm\n\n'

        '(d) What are the coordinates of the particle at t = 11.1 s?\n'
        'x = {:.2f}m\n'
        'y = {:.2f}m\n'
        .format(*x, direction, *displace, *coordinates)
        )

f1 = -6.25, -3.65
f2 = -3.15, -4.70
mass = 2.20
rest = -2.05, 4.10
time = 11.1

displacement(f1, f2, mass, time)

m = 9.00
g = 9.8
doA = 6.5
doAC = 6.5

Fg = m * g
WoAC = Fg * doA * cos(radians(90)) + Fg * doAC * cos(radians(180))

WoC = (Fg * doA * sqrt(m)) * -(sqrt(m) / m)

print(
    '(a)\n({} * {} * cos({})) + ({} * {} * cos({})) = {} J\n'
    .format(Fg, doA, 90, Fg, doAC, 180, WoAC)
    )

print(
    '(b)\n({} * {} * cos({})) + ({} * {} * cos({})) = {} J\n'
    .format(Fg, doA, 180, Fg, doAC, 90, WoAC)
    )
    
print(
    '(c)\n({} * {} * sqrt({})) * -(sqrt({}) / {}) = {} J'
    .format(Fg, doA, m, m, m, WoC)
    )


m = 9.0, 11.1
g = 9.8, 9.8
vi = 1.4, 1.53
d = 4.94, 4.93
co = .4, .4
theta = 20.4, 19.1
F = 98, 111

x = 0

Wg = m[x] * g[x] * d[x] * cos(radians(theta[x] + 90))

n = m[x] * g[x] * cos(radians(theta[x]))
fk = co[x] * n
Eint = fk * d[x]

WF = F[x] * d[x] * cos(radians(0))
delK = WF + Wg - Eint

vf = sqrt((2 * delK) / m[x] + vi[x]**2)

def angle_calc(a, b):
    
    def dot_prod(u, v):
    
        return (u[0] * v[0]) + (u[1] * v[1])

    def magnitude(u):
    
        return sqrt(u[0]**2 + u[1]**2)
    
    c = dot_prod(a, b) / (magnitude(a) * magnitude(b))
    return degrees(acos(c))


class Flow():
    
    def __init__(self, flow=0, capacity=0, add=False):
        if add: self.out = capacity
        else: self.out = capacity - flow
        self.in_ = flow
    
    def __add__(self, right):
        return Flow(self.in_ + right.out, self.out + right.in_, True)
    
    def __str__(self):
        return 'Out: {}\nIn:{}'.format(self.out, self.in_)
    
x = {
    's → v₁': Flow(18,29),
    's → v₂': Flow(4,4),
    's → v₃': Flow(5,11),
        
    'v₁ → v₂': Flow(7,9),
    'v₁ → v₄': Flow(11,13),
        
    'v₂ ↔ v₃': Flow(4,12) + Flow(0,14),
    'v₂ ↔ v₄': Flow(0,19) + Flow(7,8),
    'v₂ → v₅': Flow(0,7),
        
    'v₃ → v₅': Flow(9,27),
    
    'v₄ → v₆': Flow(15,15),
    'v₄ ↔ v₇': Flow(3,3) + Flow(0,9),
    
    'v₅ → v₄': Flow(0,23),
    'v₅ → v₇': Flow(2,18),
    'v₅ → v₈': Flow(7,16),
    
    'v₆ → v₇': Flow(4,6),
    'v₆ → t': Flow(11,11),
        
    'v₇ ↔ v₈': Flow(0,4),
    'v₇ → t': Flow(1,5),
        
    'v₈ → t': Flow(8,30),
}
for i,j in x.items():
    print(i)
    print(j)
    print()

# PHYSICS 250

l = 2.34 * 10**-6
l_2 = l * .0126
x = (l-l_2)
 
e = 1.62 * 10**-19
Ke = 8.99 * 10**9
F = (Ke * e**2) / l**2
 
k = F / x
print(f'{k:e}')

 
q = 5.24
r12 = .320
m = .01
q1 = 6
q2 = -3
Ke = 8.99 * 10**9
 
F12 = Ke * (abs(q)*abs(q1) * 10 **-18 / r12**2)
F13 = Ke * (abs(q)*abs(q2) * 10 **-18 / m**2)
FR = sqrt(F12**2 + F13**2)
 
theta = degrees(atan(F13/F12))
 
print(f'{FR:e}')
print(f'{theta}')


Ke = 8.99 * 10**9
m = 0.202
q = 7.7 * 10**-9
theta = 5.10

m = 0.186
q = 7.7 * 10**-9
theta = 4.55

Tv = m * 9.8
Th = Tv * tan(radians(theta))
d = sqrt(Ke * q**2 * Th)
print(f'{d:e}')


Ke = 8.99 * 10**9
m = 0.355
q1 = 12.0 * 10**-9
q2 = 19.0 * 10**-9

Q = q1 + q2
q = Q/2

F = Ke * (q1*q2 / m**2)
print(f'{F:e}')
F = (Ke *q**2) / m**2
print(f'{F:e}')

i = ['F', 'T']
j = '\np|q|r | \n'
for p in range(2):
    for q in range(2):
        for r in range(2):
        #     for s in range(2):
            j += f'{i[p]} {i[q]} {i[r]}  {i[p]}\n'