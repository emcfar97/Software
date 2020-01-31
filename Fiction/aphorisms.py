from random import randint, uniform
#from _main_ import Person

def cheese_production(days, pop=100, rate=875):
    '''Aphorisms on Love'''

    mliters = sum(days * (rate+uniform(-125, 125)) for woman in range(pop))
    grams = mliters * 1.03
    cheese = grams * .64
    
    return f'After {days} days, {pop} laktei produce {mliters/1000:.2f} L of milk, which can produce {cheese/1000:.2f} kg of cheese.'
