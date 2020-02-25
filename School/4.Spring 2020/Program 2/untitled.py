import random

def simulated_anneal(system, temperature):

    current_state = system.initial_state
    t = temperature
    
    while t > 0:

        t = t * alpha
        next_state = randomly_choosen_state
        energy_delta = energy(next_state) - energy(current_state)
        if (energy_delta < 0 or (math.exp( -energy_delta / t) >= random.randint(0,10))):
            current_state = next_state
    final_state = current_state
    return final_state

accept = 1 / (1 + 0)
state = random.uniform(0, 1)


def Simulated_Annealing(max_iter, initial_temperature, alpha, final_temperature, initial_state, unused_labels):
    
    t = initial_temperature
    current_state = initial_state.copy()
    
    print("Original State:", current_state)
    print("Energy of Original State:", value(current_state))
    
    while(t >= final_temperature):
    
        for i in range(1, max_iter):
            next_state = action_on(current_state)
            energy_delta = value(next_state) - value(current_state)
            if ((energy_delta < 0) or (math.exp( -energy_delta / t) >= random.randint(0,10))):
                current_state = next_state
        t = alpha * t
    
    print("Final", current_state)
    print("Energy of final state:", value(current_state))