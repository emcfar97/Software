import random
from _main_ import Person    

Calories = { # per gram
    'ATP':    4,
    'Protein':4,
    'Fat':    9,
    'Carbs':  4,
    'Ethanol':6.9,
    'Glucose':3.75,
    'Starch': 4,
    'Cellulose':4
    }

class Hybrids(Person):


    def __init__(self, name, sex, age, height, weight, sizes, status):
        
        Person.__init__(self, name, sex, age, height, weight, sizes)
        self.status = status
        if status == 'Hybrids':
            self.BMR = int(
                (self.weight * 11.68) if (self.sex == 'Female') else
                (self.weight * 9.60)
                )
        else:
            self.BMR = int(
            	(447.593 + (9.247 * self.weight) + (3.098 * self.height) -
                (4.330 * self.age)) if self.sex == 'Female' else
                (88.362 + (13.397 * self.weight) + (4.799 * self.height) -
                (5.677 * self.age))
                )
            
    def __str__(self):
        
        return (
            f'Name:   {self.name}\nStatus: {self.status}\nSex:    {self.sex}\nAge:    {self.age} years\nHeight: {self.height:.1f} cm\nWeight: {self.weight:.1f} kg\nBMR:    {self.BMR:} Cal\n'
            )
        
    def __repr__(self): return self.__str__()

    def cell_divi(self, divide, size=0, cells=1):
        '''Hybrids'''
        
        for division in range(divide):
            print(f'After {division:>1} divisions, there are {cells} cells of size {size}.')
            cells *= 2
            size /= 2
    
    def hybridize(self):
        '''Hybrids'''
        
        self.age = 23
        self.sizes = sizes[:4] + 'L S ' + sizes[8:]
        self.weight = round(
            (self.height * 0.29) if (self.sex == 'Female') else 
            (self.height * 0.27), 2)

    def gamete_production(self, germ_cell=1, gametes=0, result=''):
        '''Hybrids'''
        
        if self.sex == 'Male':
            
            germ_cells = random.randint(128, 256)
            for hour in range(2):
                result = (
                    f'After {hour * 12} hours and {germ_cell} germ cells, there are {gametes:.0f} sperm cells\n'
                    )
                germ_cell *= 2
                gametes = germ_cell / 2 * 4
                
            return (
                result + f'For total production, there are {gametes * germ_cells:.0f} sperm cells'
                )
        for hour in range(2):
            result = (
                f'After {hour * 12} hours and {germ_cell} germ cells, there are {gametes:.0f} egg cells'
            germ_cell *= 2
            gametes = (germ_cell / 2) * 4
            
        return result

    def fluid_production(self, hour=24, fluid=0):
        '''Hybrids'''    
        
        if self.sex == 'Female':
            
            milk_rate = self.weight * random.uniform(.009, .012) 
            for _ in range(random.randint(4, 6)):
                fluid += milk_rate * random.randint(7, 9)
                fluid += milk_rate * random.randint(7, 9)
        else:
            
            semen_rate = self.weight * random.uniform(.009, .012) 
            for _ in range(random.randint(0,1)):
                fluid += semen_rate * random.randint(0,1)
            
        fluid *= hour
        water =   (fluid * .600) 
        protein = (fluid * .116)
        fat =     (fluid * .104)
        carbs =   (fluid * .180)
        Cal = sum([protein * 4, fat * 9, carbs * 4])

        return (
            f'{self.name} produces {fluid/1000:.2f} L of semen after {hour} hours.\n\n'
            f'Cal:     {Cal:.2f}\n'
            f'Water:   {water:.2f} mL\n'
            f'Protein: {protein:.2f} g\n'
            f'Fat:     {fat:.2f} g\n'
            f'Carbs:   {carbs:.2f} g'
        )

    def glucose_production(self, breaths=17, efficiency=0.4):
        '''Hybrids'''
        
        lung_vol = 2 * self.weight * 470 # total lung capacity in mL
        mL = lung_vol *.0004 # percent CO2 in air
        grams = mL * .0018 # mL of CO2 to g
        moles = grams / 44.0090 # g/mol CO2
        co2_glucose = (moles / 6) * 180.156 # g/mol of glucose
        minute = (co2_glucose * breaths) * efficiency # breaths in minute
        
        grams = {
            'Minutes': minute,
            'Hours': minute * 60,
            'Days':  minute * 60 * 24,
            'Weeks': minute * 60 * 24 * 7,
            'Years': minute * 60 * 24 * 360
            }        
        return (
            '{0[0]}: {0[1]:>7.2f} g of glucose\n'
            '{1[0]}: {1[1]:>9.2f} g of glucose\n'
            '{2[0]}: {2[1]:>10.2f} g of glucose\n'
            '{3[0]}: {3[1]:>9,.2f} g of glucose\n'
            '{4[0]}: {4[1]:,.2f} g of glucose'
            .format(*grams.items())
            )    
    
    def ammonia_production(self, breaths=16, efficiency=0.0002):
        '''Hybrids'''
        
        lung_vol = 2 * self.weight * 250 # total lung capacity in mL          
        mL = lung_vol * .7809 # percent of N2 in air
        grams = mL * .0013 # ml of N2 to g
        moles = grams / 14.0070 # g/mol of N2
        n2_ammonia = (moles * 2) * 17.031 # g/mol of ammonia
        minute = (n2_ammonia * breaths) * efficiency # breaths in minute
    
        grams = {
            'Minutes': minute,
            'Hours': minute * 60,
            'Days':  minute * 60 * 24,
            'Weeks': minute * 60 * 24 * 7,
            'Years': minute * 60 * 24 * 360
            }        
        return (
            '{0[0]}: {0[1]:>7.2f} g of ammonia\n'
            '{1[0]}: {1[1]:>9.2f} g of ammonia\n'
            '{2[0]}: {2[1]:>10.2f} g of ammonia\n'
            '{3[0]}: {3[1]:>9,.2f} g of ammonia\n'
            '{4[0]}: {4[1]:>2,.2f} g of ammonia\n'
            .format(*grams.items())
            )

    def body_percent(self):
        '''Hybrids'''
        sex = 0 if (self.sex == 'Male') else 1

        measure = {
            'Mass': [
                [0.075, 0.075], # Bone Percent
                [0.435, 0.435], # Muscle Percent
                [0.035, 0.035]  # Blood Percent
                ],           
            'Percentage': [
                [0.0826, 0.0820], # Head
                [0.2010, 0.1702], # Thorax
                [0.3106, 0.1224], # Abdomen
                [0.1366, 0.1596], # Pelvis
                [0.0325, 0.0290], # Upper arm
                [0.0187, 0.0157], # Forearm
                [0.0065, 0.0050], # Hand
                [0.1050, 0.1175], # Thigh
                [0.0475, 0.0535], # Leg
                [0.0143, 0.0133]  # Foot
                ]
            }
        masses = [self.weight * i[sex] for i in measure['Mass']]
        percentages = [self.weight * i[sex] for i in measure['Percentage']]
        
        return (
            '{}:    {:>7.2f} kg\n\n'
            'Bone:     {:.2f} kg\n'
            'Muscle:   {:.2f} kg\n'
            'Blood:    {:.2f} kg\n\n'
            'Head:     {:.2f} kg\n'
            'Thorax:   {:.2f} kg\n'
            'Abdomen:  {:.2f} kg\n'
            'Pelvis:   {:.2f} kg\n'
            'Upper Arm:{:.2f} kg\n'
            'Forearm:  {:.2f} kg\n'
            'Hand:     {:.2f} kg\n'
            'Thigh:    {:.2f} kg\n'
            'Calf:     {:.2f} kg\n'
            'Foot:     {:.2f} kg'
            .format(self.name, self.weight, *masses, *percentages)
            )
     
