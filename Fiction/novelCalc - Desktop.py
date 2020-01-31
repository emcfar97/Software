import sqlite3, sys, os
PYTHONPATH = r'C:\Users\Emc11\Dropbox\Software\Fiction'

from Person import *
from aphorisms import *
from hybrids import *

def initialize(dict={}):
    
    try:
        database = sqlite3.connect('Data.sqlite')
        cursor = database.cursor()

        dict.update({'hybrids':{
                person[0]: Hybrids(*person) for person in cursor.execute('SELECT * FROM hybrids')
                    }
                })
        dict.update({'aphorisms':{
                person[0]: Person(*person) for person in cursor.execute('SELECT * FROM aphorisms')
                    }
                })
        database.close()
        return dict

    except Exception as error:
        print('InitializeError:', error)
        
def terminate():

    try:
        database = sqlite3.connect('Characters.dbf')
        cursor = database.cursor()

        for name, table in people.items():
            for person in table:
                dict = tuple(table[person].__dict__.values())[:7]
                data = cursor.execute(
                    "SELECT * FROM {} WHERE name='{}'".format(name, person)
                    ).fetchone()
                if dict is None or data is None:
                    check = [False for i in range(len(dict))] \
                        if (data is None) else \
                        [False for i in range(len(data))] 
                else:
                    check = [
                        True if (dict[i] in data) else 
                        False for i in range(len(data))
                        ]
                if (True not in check): # person in dict but not datab
                    insert(name, dict)
                    continue

                elif (False in check): # any value in dict != value in datab
                    update(name, dict)
                    continue       

                # elif (True in check): # person in datab but not dict
                #     delete(name, dict)
                #     continue
        database.commit()
        database.close()

    except Exception as error:
        print('TerminateError:', error)

def insert(table, data):
    
    try:
        if table == 'hybrids':
            statement = '''INSERT INTO {} (
                name, sex, age, height, weight, sizes, status)
                VALUES ({}?)'''.format(table, '?, ' * (len(data)-1))
            cursor.execute(statement, data)
        
        elif table == 'aphorisms':
            statement = '''INSERT INTO {} (
                name, sex, age, height, weight, sizes)
                VALUES ({}?)'''.format(table, '?, ' * (len(data)-1))
            cursor.execute(statement, data)
    except Exception as error:
        print('InsertionError:', error)

def update(table, data):

    try:  
        for value in data:
            statement = "UPDATE {} SET ? = '{}' WHERE name = '{}'".format(
                table, data, data[0]
                )
            cursor.execute(statement)
    except Exception as error:
        print('UpdateError:', error)

def delete(table, data):

    try:    
        statement = 'DELETE FROM {} WHERE name = ?'.format(table, data[0])
        print(statement)
    except Exception as error:
        print('DeletionError:', error)

people = initialize()

while True:

    menuOp = input(
        '1 - Hybrids\n'
        '2 - Aphorisms on Love\n'
        '3 - Break\n'
        )
    if menuOp  ==  '1': # Hybrids
        table = people['hybrids']
        while True:
            menuOp = input(
                    '1 - View Person\n'
                    '2 - Add Person\n'
                    '3 - Delete Person\n'
                    '4 - Hybridize\n'
                    '5 - Gamete Production\n'
                    '6 - Fluid Production\n'
                    '7 - Glucose Production\n'
                    '8 - Ammonia Production\n'
                    '9 - Body Percentages\n'
                    '10 - Break\n'
                    )
            if menuOp == '1': # View Person
                try:
                    name = input(
                        'Enter name (sizes)\n'
                        ).capitalize().split(' ')
                    print(
                        table[name[0]] if (len(name)< 2 ) else table[name[0]].return_sizes()
                        )
                except Exception as error:
                    print('Error:', error)
            
            elif menuOp == '2': # Add Person
                try:
                    person = input(
                        'Enter name, sex, age (height, weight, status, sizes)\n'
                        ).replace('\'', '').replace(',', '').split(' ')

                    people['hybrids'][person[0]] = Hybrids(*person)

                except  Exception as error:
                    print("Error:", error)
                continue

            elif menuOp == '3': # Delete Person
                try:
                    person = input('Enter name')
                    people['hybrids'][person].pop()

                except  Exception as error:
                    print("Error:", error)
                continue
            
            elif menuOp == '4': # Hybridize
                try:
                    person = input('Enter name\n').capitalize()
                    
                    if table[person].status == 'Hybrid':
                    	raise TypeError
                    
                    people['hybrids'][person].hybridize()
                    print(people['hybrids'][person])
                    
                except Exception as error:
                    print('Error: ', error)
                continue
            
            elif menuOp == '5': # Gamete Production
                try:
                    person = input(
                        'Enter name (germ cells, gametes)\n'
                        ).capitalize().split(' ')
                    
                    if table[person[0]].status == 'Human':
                    	raise TypeError
                    
                    print(
                        table[person[0]].gamete_production(*person[1:]), '\n'
                        )                    
                except Exception as error:
                    print("Error:", error)
                continue

            elif menuOp == '6': # Fluid Production
                try:
                    person = input('Enter name\n').capitalize()
                    
                    if table[person].status == 'Human':
                    	raise TypeError
                    print(table[person].fluid_production(), '\n')
                    
                except Exception as error:
                    print("Error:", error)
                continue

            elif menuOp == '7': # Glucose Production
                try:
                    person = input('Enter name\n').capitalize()

                    if table[person].status == 'Human':
                        raise TypeError
                    print(table[person].glucose_production(), '\n')

                except Exception as error:
                    print("Error:", error)
                continue

            elif menuOp == '8': # Ammonia Production
                try:
                    person = input('Enter name\n').capitalize()

                    if table[person].status == 'Human':
                        raise TypeError
                    print(table[person].ammonia_production(), '\n')

                except Exception as error:
                    print("Error:", error)
                continue

            elif menuOp == '9': # Body Percentages
                try:
                    person = input('Enter name\n').capitalize()
                    print(table[person].body_percent(), '\n')
                    
                except Exception as error:
                    print("Error:", error)
                continue

            elif menuOp == '10': # Break
                break

            else:
                continue

    elif menuOp == '2': # Aphorisms
        table = people['aphorisms']
        while True:
            menuOp = input(
                '1 - View Person\n'
                '2 - Add Person\n'
                '3 - Delete Person\n'
                '4 - Cheese Production\n'
                '5 - Break\n'
                )
            if menuOp == '1': # View Person
                try:
                    name = input(
                        'Enter name (sizes)\n'
                        ).capitalize().split(' ')
                    print(
                        table[name[0]] if len(name)<2 else table[name[0]].return_sizes()
                        )
                except Exception as error:
                    print('Error:', error)
            
            elif menuOp  ==  '2': # Add Person
                
                try:
                    person = input(
                        'Enter name, sex, (age, height, weight, sizes)\n'
                        ).replace('\"', '').replace(',', '').split(' ')

                    people['aphorisms'][person[0]] = Person(*person)

                except Exception as error:
                    print("Error:", error)
                continue

            elif menuOp == '3': # Delete Person
                try:
                    person = input('Enter name')
                    people['aphorisms'][person].pop()
                    
                except  Exception as error:
                    print("Error:", error)
                continue

            elif menuOp == '4': # Cheese Production
                print("Calculation undefined")
                continue

            elif menuOp == '5': # Break
                break

            else:
                continue

    elif menuOp == '3': # Break
        try:
            terminate()
            break
        except:
            continue

    else:
        continue
