import os, shutil
from os.path import splitext, join, exists
import mysql.connector as sql

# DATAB = sql.connect(
#     user='root', password='SchooL1@', database='userData', 
#     host='192.168.1.43' if __file__.startswith(('e:\\', 'e:/')) else '127.0.0.1'
#     )
# CURSOR = DATAB.cursor(buffered=True)

path = r'C:\Users\Emc11\Downloads\Katawa Shoujo'
dest = r'C:\Users\Emc11\Dropbox\Videos\ん\エラティカ 三'
sprites = {}

# for i in range(3):

    #     for file in os.listdir(path):

    #         if not file.endswith('jpg'): continue
    #         file = splitext(file)[0]
    #         try: 
    #             char, pose, expr = file.split('_')[1:]
    #             if not char.startswith(("shiz", "mish", "lill", "hanak", "emi", "rin")): continue
    #         except ValueError: continue
            
    #         if i == 0: 
    #             if char == 'emiwheel': continue
    #             if char == 'shizuyu': continue
    #             if char == 'rinpan': continue
                
    #             sprites[char] = {}
            
    #         elif i == 1: 
    #             if char == 'shizuyu':
    #                 pose = char
    #                 char = 'shizu'
    #             if char == 'emiwheel':
    #                 pose = char
    #                 char = 'emi'
    #             if char == 'rinpan': 
    #                 pose = char
    #                 char = 'rin'
                
    #             sprites[char][pose] = []

    #         elif i == 2: 
    #             if char == 'shizuyu':
    #                 pose = char
    #                 char = 'shizu'
    #             if char == 'emiwheel':
    #                 pose = char
    #                 char = 'emi'
    #             if char == 'rinpan': 
    #                 pose = char
    #                 char = 'rin'
                
    #             sprites[char][pose].append(expr)

# Houses
# 1 2 3 4 5

from constraint import *
problem = Problem()

nationality = ["English", "Spanish", "Ukrainian", "Norwegian", "Japanese"]
pet = ["dog", "snails", "fox", "horse", "zebra"]
cigarette = ["Old Gold", "Kools", 
"Chesterfields", "Lucky Strike", "Parliaments"]
colour = ["red", "green", "yellow", "blue", "ivory"]
beverage = ["coffee", "milk", "orange juice", "water", "tea"]

criteria = nationality + pet + cigarette + colour + beverage
problem.addVariables(criteria,[1,2,3,4,5])

problem.addConstraint(AllDifferentConstraint(), nationality)
problem.addConstraint(AllDifferentConstraint(), pet)
problem.addConstraint(AllDifferentConstraint(), cigarette)
problem.addConstraint(AllDifferentConstraint(), colour)
problem.addConstraint(AllDifferentConstraint(), beverage)

problem.addConstraint(lambda e, r: e == r, ["English","red"])
problem.addConstraint(lambda s, d: s == d, ("Spanish","dog"))
problem.addConstraint(lambda c, g: c == g, ("coffee","green"))
problem.addConstraint(lambda u, t: u == t, ("Ukrainian","tea"))
problem.addConstraint(lambda g, i: g-i == 1, ("green","ivory"))
problem.addConstraint(lambda o, s: o == s, ("Old Gold","snails"))
problem.addConstraint(lambda k, y: k == y, ("Kools","yellow"))
problem.addConstraint(InSetConstraint([3]), ["milk"])
problem.addConstraint(InSetConstraint([1]), ["Norwegian"])
problem.addConstraint(lambda c, f: abs(c-f) == 1, ("Chesterfields","fox"))
problem.addConstraint(lambda k, h: abs(k-h) == 1, ("Kools","horse"))
problem.addConstraint(lambda l, o: l == o, ["Lucky Strike","orange juice"])
problem.addConstraint(lambda j, p: j == p, ["Japanese","Parliaments"])
problem.addConstraint(lambda k, h: abs(k-h) == 1, ("Norwegian","blue"))

solution = problem.getSolutions()[0]

for i in range(1,6):
    for x in solution:
        if solution[x] == i:
            print str(i), x