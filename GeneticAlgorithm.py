import numpy as np
import random


class DNA():
    def __init__(self, strand_length: int, strands: int) -> None:
        self.strand_length: int = strand_length
        self.strands: int = strands
        self.genes: list[float] = self.generate_dna()
    
    def generate_dna(self) -> list[float]:
        dna_data = []
        for i in range(self.strands):
            for j in range(self.strand_length):
                dna_data.append(np.random.uniform(0.0, 1.0))
        return dna_data
    
    def get_gene(self, strand_index, gene_index) -> float:
        final_gene_index = strand_index*self.strand_length + gene_index
        return self.genes[final_gene_index]

class Organism():
    def __init__(self, dna: DNA) -> None:
        self.dna: DNA = dna
        self.fitness: float = 0.0
    
    def fitness_function() -> None:
        pass
        

class Population():

    def __init__(self, pop_list: list[Organism], mutation_rate: float = 0.01) -> None:
        self.pop_list: list[Organism] = pop_list
        self.max_population = len(self.pop_list)
        self.mutation_rate: float = mutation_rate
        self.__init_pop_fitness()
        self.generation = 0

    def __sort_by_fitness(self):
        self.pop_list.sort(key=lambda x: x.fitness)
    def __init_pop_fitness(self):
        for i in range(len(self.pop_list)):
            self.pop_list[i].fitness_function()
        self.__sort_by_fitness()

    def generate_child_dna(self) -> DNA:
        parent1 = random.choice(self.pop_list)
        parent2 = random.choice(self.pop_list)
        while parent1 == parent2:
            parent2 = random.choice(self.pop_list)
            
        new_dna = DNA(parent1.dna.strand_length, parent1.dna.strands)

        for i in range(len(new_dna.genes)):
            gene_choice = np.random.uniform(0.0, 1.0)

            if gene_choice > 0.5:
                new_dna.genes[i] = parent1.dna.genes[i]
            else:
                new_dna.genes[i] = parent2.dna.genes[i]
            
            mutation = np.random.uniform(-self.mutation_rate, self.mutation_rate)

            new_dna.genes[i] += mutation
            new_dna.genes[i] = min(1.0, max(0.0, new_dna.genes[i]))

        return new_dna
    
    def add_pop(self, new_pop: Organism):
        if new_pop.fitness > self.pop_list[0].fitness:
            self.pop_list[0] = new_pop
            self.__sort_by_fitness()

