import json
import numpy as np
import matplotlib.pyplot as plt
from GeneticAlgorithm import DNA, Population
from NeptunesPrideUtilities import Player, NeptunesPrideData

API_KEY = "Nktay1"
GAME_ID = 6113070671462400

# Get the game data from API_KEY and GAME_ID (unique to the player and game)
game_data = NeptunesPrideData(API_KEY, GAME_ID)

# Generate a list of "Players" which will serve as the starting population for the Genetic Algorithm
pop_list = []
DAYS_TO_SIMULATE = 20
NUMBER_OF_POPS = 100
for i in range(NUMBER_OF_POPS):
    # Each DNA consists of a DNA Strand for each day.
    # Each DNA Strand consists of one Gene which is a uniformly random value between 0.0 and 1.0
    # In this case, the DNA represents the distribution in Economy to spend each day (the rest goes to Industry)
    dna = DNA(1, DAYS_TO_SIMULATE)
    pop = Player(dna, name="TheGreatFez", game_data=game_data.game_data)
    pop_list.append(pop)

# Generate the Population used for the Genetic Algorithm
population = Population(pop_list)

# Run a simple Genetic Algorithm For 100,000 generations, or until the fitness range between highest and lowest is below 10
MAX_GENERATIONS = 1000
FITNESS_RANGE_LIMIT = 10
for i in range(MAX_GENERATIONS):
    # Create a new population candidate
    new_dna = population.generate_child_dna()
    new_pop = Player(new_dna, name="TheGreatFez", game_data=game_data.game_data)

    # Calculate the initial fitness of the candidate
    new_pop.fitness_function()
    
    # Try and add to the population (either replaces the lowest if higher than the lowest)
    population.add_pop(new_pop)

    # Calculate the fitness range, output the current results
    max_fitness = population.pop_list[-1].fitness
    min_fitness = population.pop_list[0].fitness
    fitness_range = population.pop_list[-1].fitness - population.pop_list[0].fitness
    print(f"Generation: {i}, Max Fitness: {max_fitness}, Min Fitness: {min_fitness}, Fitness Range: {fitness_range}")

    # Exit early if the Fitness Range Limit is reached
    if fitness_range < FITNESS_RANGE_LIMIT:
        break

# Plot data of the population's Genes
fig, ax = plt.subplots()

for pop in population.pop_list:
    steps = range(len(pop.dna.genes))
    ax.plot(steps, pop.dna.genes)

ax.set(xlabel='Production Cycles (day)', ylabel='Economy Distribution (%)',
    title='Amount of cash to spend on Economy Infrastructure (the rest goes to Industry)')
ax.grid()

fig.savefig("test.png")
plt.show()