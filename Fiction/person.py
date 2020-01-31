from random import uniform, choices, normalvariate

standard = {
    'Male':   {'Weight': 75.7, 'BMR': 1826.9},
    'Female': {'Weight': 62.2, 'BMR': 1426.6}
    }
def set_height(sex):
	
	if sex == 'Male': return normalvariate(185.6, 10.16)
	return normalvariate(170.9, 8.89)

def set_weight(sex):
	
	if sex == 'Male': return normalvariate(75.7, 10.16)
	return normalvariate(62.2, 8.89)

class Person(object):

    def __init__(self, name, sex, age, hight=None, weight=None, sizes=None):
    	
        self.name = name.capitalize()
        self.sex = sex.capitalize()
        self.age = int(age)
        self.height = height if height else round(set_height(sex), 2)
        self.weight = weight if weight else round(set_weight(sex), 2)
        self.sizes = sizes if sizes else self.calculate_sizes()

    def __str__(self):
        
        return (
            f'Name:   {self.name}\n'
            f'Sex:    {self.sex}\n'
            f'Age:    {self.age} years\n'
            f'Height: {self.height:.1f} cm\n'
            f'Weight: {self.weight:.1f} kg\n'
            )
        
    def __repr__(self):

        return self.__str__()

    def return_sizes(self):
        
        if self.sex == 'Female':
            
            return (
                'Muscle:   {}\n'
                'Fat:      {}\n'
                'WH Ratio: {}\n'
                'Droop:    {}\n'
                'Breasts:  {}\n'
                'Areola:   {}\n'
                'Buttocks: {}\n'
                'Vulva:    {}\n'
                .format(*self.sizes)
            )
            
        return (
            'Muscle:   {}\n'
            'Fat:      {}\n'
            'WS Ratio: {}\n'
            'Droop:    {}\n'
            'Buttocks: {}\n'
            'Penis:    {}\n'
            .format(*self.sizes)
        )
   
    def calculate_sizes(self, sizes=''):
            
        dimensions = {
        	'Male': range(6),
        	'Female': range(8)
        	}
        weight = standard[self.sex]['Weight']
        
        if weight-5.5 < self.weight <= weight+7.5:
            weights = [1, 2, 1]
        elif self.weight < weight-4.5:
            weights = [1, 2, 3]
        elif weight+7.5 < self.weight:
            weights = [3, 2, 1]
        
        for dimension in dimensions[self.sex]:
            sizes += choices(['L', 'M', 'S'], weights)[0]
        return sizes

def frame_rate(Hz=24):

    seconds = Hz / 24
    minutes = seconds / 60
    hours = minutes / 60
    days = hours / 24
    weeks = days / 7
    years = days / 365.25

    print(f'At {Hz} frames per second:')
    if seconds < 60:
        return f'1 second feels like {seconds:.2f} second(s)\n'
    elif 1 < minutes <= 60:
        return f'1 second feels like {minutes:.2f} minute(s)\n'
    elif 1 < hours <= 24:
        return f'1 second feels like {hours:.2f} hour(s)\n'
    elif 1 < days <= 7:
        return f'1 second feels like {days:.2f} day(s)\n'
    elif 1 < weeks <= 52:
        return f'1 second feels like {weeks:.2f} week(s)\n'
    elif 1 < years:
        return f'1 second feels like {years:.2f} year(s)\n'

def light_speed(self, percent):

    distance = 299792458 * percent / 100 # speed of light in m/s

    return (
        f'At {percent}% speed of light:\n'
        f'Objects travel {distance:.0f} m or {distance/1000:.1f} km per second'
        )

for i in range(10):
	Person(' ', choices(['Male', 'Female'])[0], i)

