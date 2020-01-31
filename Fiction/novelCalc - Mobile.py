import ui, sqlite3, sys, os
sys.path.append(os.getcwd() + '/Modules')

from _main_ import *
from hybrids import *
from aphorisms import *

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

def select_person(sender):
	
	nav.push_view('SelectView',False)
	
	
def add_person(sender):
	blank = ui.load_view('BlankView')
	blank.name = 'Add Person'
	nav.push_view(blank, False)
	
	person = ui.TextField(
		placeholder='Enter name and optional sizes',
		delegate=MyTextFieldDelegate(),
		action=text_return,
		frame=textField_dimen,
		flex='LR'
		)

def delete_person(sender):
	blank = ui.load_view('BlankView')
	blank.name = 'Delete Person'
	nav.push_view(blank, False)
	
	person = ui.TextField(
		placeholder='Enter name',
		action=text_return,
		frame=textField_dimen,
		flex='LR'
		)

def select_hybrids(sender):
	global table
	global person
	
	table = 'hybrids'
	person = 'Tarah'
	nav.push_view(ui.load_view('HybridsView'), False)
	select_person = ui.Button().action
	add_person = ui.Button().action
	delete_person = ui.Button().action
	hybridize = ui.Button().action
	gamete_production = ui.Button().action
	fluid_production = ui.Button().action
	glucose_production = ui.Button().action
	ammonia_production = ui.Button().action
	body_percentages = ui.Button().action

def hybridize(sender):
	blank = ui.load_view('BlankView')
	blank.name = 'Hybridize'
	nav.push_view(blank, False)
	
	person = ui.Textfield(
		placeholder='Enter name',
		action=text_return,
		frame=textField_dimen,
		flex='LR'
		)

def gamete_production(sender):
	blank = ui.load_view('BlankView')
	blank.name = 'Gamete Production'
	
	blank['data'].text = people[table][person].__str__()
	blank['sizes'].text = str(people[table][person].return_sizes())
	blank['void'].text = people[table][person].gamete_production()
	
	nav.push_view(blank, False)

def fluid_production(sender):
	blank = ui.load_view('BlankView')
	blank.name = 'Fluid Production'
	
	blank['data'].text = people[table][person].__str__()
	blank['sizes'].text = str(people[table][person].return_sizes())
	blank['void'].text = people[table][person].fluid_production()
	
	nav.push_view(blank, False)

def glucose_production(sender):
	blank = ui.load_view('BlankView')
	blank.name = 'Glucose Production'
	
	blank['data'].text = people[table][person].__str__()
	blank['sizes'].text = str(people[table][person].return_sizes())
	blank['void'].text = people[table][person].glucose_production()
	
	nav.push_view(blank, False)

def ammonia_production(sender):
	blank = ui.load_view('BlankView')
	blank.name = 'Ammonia Production'
	
	blank['data'].text = people[table][person].__str__()
	blank['sizes'].text = str(people[table][person].return_sizes())
	blank['void'].text = people[table][person].ammonia_production()
	
	nav.push_view(blank, False)

def body_percentages(sender):
	blank = ui.load_view('BlankView')
	blank.name = 'Body Percentages'
	
	blank['data'].text = people[table][person].__str__()
	blank['sizes'].text = str(people[table][person].return_sizes())
	blank['void'].text = people[table][person].body_percentages()
	
	nav.push_view(blank, False)

def select_aphorisms(sender):
	global table
	global person
	
	table = 'aphorisms'
	person = 'Kama'
	nav.push_view(ui.load_view('AphorismsView'), False)
	select_person = ui.Button().action
	add_person = ui.Button().action
	delete_person = ui.Button().action
	cheese_production = ui.Button().action

def cheese_production(sender):
	blank = ui.load_view('BlankView')
	blank.name = 'Cheese Production'
	nav.push_view(blank, False)

people = initialize()
table = 'hybrids'
person = 'Tarah'

# main view
view = ui.load_view('Novel.pyui')
nav = ui.NavigationView(view)

hybrids = view['HybridsView']
aphorisms = view['AphorismsView']
select = view['SelectView']
main = view['MainView']

nav.present('full_screen', hide_title_bar=True)
