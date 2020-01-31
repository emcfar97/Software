import sqlite3, networkx
import matplotlib.pyplot as plt
from math import log10, floor
from random import randrange, randint, choice, choices, uniform

INSERT = "INSERT INTO jenatalPop(age, sex, alive, clan, lineage, cohort, caste) VALUES (?, ?, ?, ?, ?, ?, ?)"
UPDATE = "UPDATE jenatalPop set ? = ? WHERE lineage = ?"
MEMBERS = "SELECT * FROM jenatalPop WHERE ="
ALIVE = "SELECT * FROM jenatalPop WHERE = AND alive = 1"
DEAD = "SELECT * FROM jenatalPop WHERE = AND alive = 0"
MEN = "SELECT * FROM jenatalPop WHERE = AND sex = 'Male'"
WOMEN = "SELECT * FROM jenatalPop WHERE = AND sex = 'Female'"
FERTILE = "SELECT * FROM jenatalPop WHERE = AND sex = 'Female' AND 20 <= age < 30"
SMATTI = "SELECT * FROM jenatalPop WHERE = AND caste = 'smatti'"
LAKTEI = "SELECT * FROM jenatalPop WHERE = AND caste = 'laktei'"
BABIES = "SELECT * FROM jenatalPop WHERE = AND age < 4"
CHILDREN = "SELECT * FROM jenatalPop WHERE = AND 4 <= age < 13"
TEENS = "SELECT * FROM jenatalPop WHERE = AND 13 <= age < 20"
ADULTS = "SELECT * FROM jenatalPop WHERE = AND 20 <= age < 60"
ELDERLY = "SELECT * FROM jenatalPop WHERE = AND 60 <= age"

class Society():
	
	def __init__(self):
		self.clans = [Clan(clan) for clan in range(randint(5, 10))]
		self.members = [clan.members for clan in self.clans]
		self.alive = self.members
		self.dead = []
		self.men = [i.men for i in self.clans]
		self.women = [i.women for i in self.clans]
		self.fertile = [i.fertile for i in self.clans]
		self.babies = [i.babies for i in self.clans]
		self.children = [i.children for i in self.clans]
		self.teens = [i.teens for i in self.clans]
		self.adults = [i.adults for i in self.clans]
		self.elderly = [i.elderly for i in self.clans]

	def __str__(self):
    		return (
			'Clans: {} Size: {} Alive: {} Dead: {} Males: {} Females: {}\nFertile: {} Babies: {} Children: {} Teens: {} Adults: {} Elderly: {}\n'
			.format(
				len(self.clans),
				sum(len(i) for i in self.members), 
				sum(len(i) for i in self.alive),
				sum(len(i) for i in self.dead),
				sum(len(i) for i in self.men),
				sum(len(i) for i in self.women),
				sum(len(i) for i in self.fertile),
				sum(len(i) for i in self.babies),
				sum(len(i) for i in self.children),
				sum(len(i) for i in self.teens),
				sum(len(i) for i in self.adults),
				sum(len(i) for i in self.elderly)
				)
			)
	
	def __repr__(self):
		return self.__str__()	

	def refresh(self):
    		
		[clan.cycle() for clan in self.clans]
		self.alive = [i.alive for i in self.clans]
		self.dead = [i.dead for i in self.clans]
		self.men = [i.men for i in self.clans]
		self.women = [i.women for i in self.clans]
		self.fertile = [i.fertile for i in self.clans]
		self.babies = [i.babies for i in self.clans]
		self.children = [i.children for i in self.clans]
		self.teens = [i.teens for i in self.clans]
		self.adults = [i.adults for i in self.clans]
		self.elderly = [i.elderly for i in self.clans]

	def cycle(self):
    	
		for clan in [clan for clan in self.clans if clan.extant]:
			if clan.split():
				half = floor(len(clan.alive) / round(uniform(1.75,2.25), 2))
				members = clan.alive[half:]
				for num, member in enumerate(members):
					members[num].alive = None
				self.clans[clan.ID] = clan.alive[:half] + members
				self.clans.append(Clan(len(self.clans), clan.alive[half:]))
				print('Divide')

			elif clan.unify():
				sort = sorted(self.clans, key=lambda clan:len(clan.alive))[1:]
				merge_clan = choice(sort[:floor(len(sort)/2)])
				self.clans[merge_clan.ID].members += clan.alive
				self.clans[clan.ID].extant = False
				print('Merge')
		self.refresh()

class Clan():
	
	def __init__(self, ID, members=[]):
		self.ID = ID
		self.extant = True
		self.members = self.populate() if not members else members
		self.alive = self.members
		self.dead = []
		self.men = [i for i in self.alive if i.sex == 'Male']
		self.women = [i for i in self.alive if i.sex == 'Female']
		self.fertile = [i for i in self.women if 20 <= i.age < 30]
		self.babies = [i for i in self.alive if i.age < 4]
		self.children = [i for i in self.alive if 4 <= i.age < 13]
		self.teens = [i for i in self.alive if 13 <= i.age < 20]
		self.adults = [i for i in self.alive if 20 <= i.age < 60]
		self.elderly = [i for i in self.alive if 60 <= i.age]

	def __str__(self):
		return (
			'Size: {} Alive: {} Dead: {} Males: {} Females: {}\nFertile: {} Babies: {} Children: {} Teens: {} Adults: {} Elderly: {}\n'
			.format(
				len(self.members), len(self.alive), len(self.dead), 
				len(self.men), len(self.women), len(self.fertile), 
				len(self.babies), len(self.children), len(self.teens), 
				len(self.adults), len(self.elderly)
				)
			)
	
	def __repr__(self):
		return self.__str__()	

	def populate(self):
		
		# members = {
		# 	(self.ID, person):Person((self.ID, person), randint(0,70))
		# 	for person in range(randint(60,90))
		# 	}
		# fertile = [i for i in members.values() if 20 <= i.age < 30 and i.sex == 'Female']
		members = [
			Person((self.ID, person), randint(0,70))
			for person in range(randint(60,90))
			]
		fertile = [i for i in members if 20 <= i.age < 30 and i.sex == 'Female']
		for woman in fertile:
			for child in range(int(((woman.age/2)-1)-10), 0, -1):
				line = (self.ID, *woman.lineage[1:], len(members))
				members.append(Person(line, child*2))#, members[woman.lineage])
				members[woman.lineage[-1]].children += members[-1]
				#child = Person(line, child*2, members[woman.lineage[1]])
				#members[woman.lineage[1]].children.append(child)
				#members.append(child)
		return members

	def cycle(self):
		
		for woman in self.fertile:
			if woman.reproduce():
				line = (self.ID, *woman.lineage[1:])
				child = Person((line, len(self.members)))
				self.members[child.lineage] = child
				self.members[woman.lineage].children.append(child)
		[member.survive() for member in self.alive]
		self.alive = [i for i in self.members.values() if i.alive]
		self.dead = [i for i in self.members.values() if i.alive == False]
		self.men = [i for i in self.alive if i.sex == 'Male']
		self.women = [i for i in self.alive if i.sex == 'Female']
		self.fertile = [i for i in self.women if 20 <= i.age < 30]
		self.babies = [i for i in self.alive if i.age < 3]
		self.children = [i for i in self.alive if 4 <= i.age < 12]
		self.teens = [i for i in self.alive if 13 <= i.age < 19]
		self.adults = [i for i in self.alive if 20 <= i.age < 59]
		self.elderly = [i for i in self.alive if 60 <= i.age]

	def split(self):
    	
		probability = round(1.04**(0.5*(len(self.alive)-400)), 2)
		if probability <= 1:
			return choices([True, False],[probability, 1-probability])[0]
		return True

	def unify(self):
		
		probability = round(1.50**(0.3*(-len(self.alive)+50)), 2)
		if probability <= 1:
			return choices([True, False],[probability, 1-probability])[0]
		return True

	def get_descendants(self, woman):
		return sorted([
			person for person in self.members 
			if person < woman
			], key=lambda person: person.cohort
			)
	def get_ancestors(self, woman):
		return sorted([
			person for person in self.members 
			if person > woman
			], key=lambda person: person.cohort
			)
			
class Person():
	
	def __init__(self, lineage, age=0, children=[]):#, mother=[], children=[]):
		self.age = age
		self.lineage = lineage
		self.cohort = len(lineage[1:])
		#self.mother = mother
		self.sex = choice(['Female', 'Male'])
		#if self.sex == 'Female':
		# self.children = children
		self.alive = True
		
	def __str__(self):
		return 'Sex: {}\nAge: {}\nAlive: {}\nLineage({}): {}\n'.format(self.sex, self.age, self.alive, self.cohort, self.lineage)
		
	def __repr__(self):
		return self.__str__()
	
	# def __gt__(self, other):
		
	# 	try:
	# 		offset = len(self.lineage[1:])
	# 		if self.lineage[1:] == other.lineage[-offset:] and self != other:
	# 			return True
	# 		return False
	# 	except IndexError:
	# 		return False
			
	# def __ge__(self, other):
		
	# 	try:
	# 		cohort = self.cohort+1 == other.cohort
	# 		lineage = self.lineage[1] == other.lineage[2]
			
	# 		if cohort and lineage:
	# 			return True
	# 		return False			
	# 	except IndexError:
	# 		return False
		
	# def __eq__(self, other):
		
	# 	if self.lineage == other.lineage:
	# 		return True
	# 	return False
		
	# def __ne__(self, other):
		
	# 	return not self.__eq__(other)
		
	# def __lt__(self, other):
		
	# 	try:
	# 		offset = len(other.lineage[1:])
	# 		# x = other.lineage[1:]
	# 		# y = self.lineage[-offset:]
	# 		if self.lineage[-offset:] == other.lineage[1:] and self != other:
	# 			return True
	# 		return False
	# 	except IndexError:
	# 		return False
		
	# def __le__(self, other):
		
	# 	try:
	# 		cohort = self.cohort-1 == other.cohort
	# 		lineage = self.lineage[2] == other.lineage[1]
            
	# 		if cohort and lineage:
	# 			return True
	# 		return False
	# 	except IndexError:
	# 		return False
	
	def reproduce(self):
		
		children = self.children		
		if len(children) > 0:
			alive = [i for i in children if i.alive]
			if len(alive) < 5 and children[0].age == 1:
				if len([i for i in children if not i.alive and i.age<=1]) > 0:
					return True
				else:
					return True		
		else:
			return True
		return False

	def survive(self):
		
		try:
			survival = round(
				(log10(self.age+.9)-0.2)/8 + (log10(-self.age+120)-0.29)/2,
                4)
			self.alive = choices([True, False], [survival, 1-survival])[0]
			self.age += 1
			
		except ValueError:
			self.alive = False

# society = Society()

# print('Processing...\n')
# for year in range(250):
# 	print(year)
# 	society.cycle()
# 	print()
# print()

clan = networkx.DiGraph()

for i in range(10):
    x = Person((0,randint(0,25)), randint(0,20))
    clan.add_node(x)
    
plt.subplot(121)
networkx.draw(clan, with_labels=True, font_weight='bold')
plt.subplot(122)
networkx.draw_shell(clan, nlist=[range(5, 10), range(5)], with_labels=True, font_weight='bold')
