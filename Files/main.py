from cncParts import Turret
import random

from geneticAlgorithm import GA

# magazine = Turret([1, 1, 3, 2, 2, 3, 4, 2], {1: 150, 2: 100, 3: 150, 4: 600})
# ops = [4, 2, 3, 4, 1]
# start_idx = 6
# print(magazine.score(300, ops))

# tool_life_table = {1: 150, 2: 100, 3: 150, 4: 600}
# djkParent = [1, 1, 3, 2, 2, 3, 4, 2]
# ops = [4, 2, 3, 4, 1]


# Example operations and tool life table
ops = [1, 2, 3, 4, 5]  # Tool operation sequence (IDs of tools)
tool_life_table = {
    1: 10,  # Tool ID 1 has a life of 10
    2: 8,   # Tool ID 2 has a life of 8
    3: 12,  # Tool ID 3 has a life of 12
    4: 15,  # Tool ID 4 has a life of 15
    5: 7    # Tool ID 5 has a life of 7
}

# Example parent turret configuration
djkParent = [1, 2, 3, 4, 5, 1, 2]  # Parent configuration
distr = {
    1:2,
    2:2,
    3:1,
    4:1,
    5:1,
}
# Create a GA instance
ga = GA(U=3, ops=ops, tool_life_table=tool_life_table)

# Step 1: Create the initial population
population_size = 100
population = ga.create_initial_population(population_size, djkParent)

print("Initial Population (Tool IDs with Scores):")
for idx, turret in enumerate(population):
    score = ga.fitness_function(turret)
    print(f"Turret {idx}: {[tool.id for tool in turret.array]}, Score: {score}")

# Run the GA for a few generations
num_generations = 5
mutation_rate = 0.05

for generation in range(num_generations):
    print(f"\nGeneration {generation + 1}")

    # Step 2: Selection - Select the best U parents
    parents = ga.selection(population)
    print("Selected Parents (Tool IDs with Scores):")
    for idx, parent in enumerate(parents):
        score = ga.fitness_function(parent)
        print(f"Parent {idx}: {[tool.id for tool in parent.array]}, Score: {score}")

    # Step 3: Crossover - Create offspring from parents
    new_population = []
    while len(new_population) < population_size:
        # Select two random parents for crossover
        parent1, parent2 = random.sample(parents, 2)
        offspring = ga.crossover(parent1, parent2)

        # Step 4: Mutation - Mutate the offspring
        offspring = ga.mutate(offspring, mutation_rate)

        # Step 5: Repair - Ensure the offspring is valid
        offspring = ga.repair(offspring, distr)

        # Add offspring to the new population
        new_population.append(offspring)

    # Replace the old population with the new one
    population = new_population

    print("New Population (Tool IDs with Scores):")
    for idx, turret in enumerate(population):
        score = ga.fitness_function(turret)
        print(f"Turret {idx}: {[tool.id for tool in turret.array]}, Score: {score}")

# Final generation population
print(f"\nFinal Population after {num_generations} generations (Tool IDs with Scores):")
for idx, turret in enumerate(population):
    score = ga.fitness_function(turret)
    print(f"Turret {idx}: {[tool.id for tool in turret.array]}, Score: {score}")
