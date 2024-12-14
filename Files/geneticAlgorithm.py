import random
import typing as t
from collections import Counter

from cncParts import Tool, Turret


class GA:

    def __init__(self, U: int, ops: t.List[int],
                 tool_life_table: t.Dict[int, int]) -> None:
        """
        Initialize the genetic algorithm.

        :param U: Number of individuals to select for breeding (best + U-1).
        :param ops: List of tool operations to perform.
        :param tool_life_table: Dictionary mapping tool ID to tool life.
        """
        self.U: int = U  # Number of individuals to select (best + U-1)
        self.ops: t.List[int] = ops  # List of operations
        self.tool_life_table: t.Dict[int,
                                     int] = tool_life_table  # Tool life table

    def selection(self, population: t.List[Turret]) -> t.List[Turret]:
        """
        Select the best individuals from the population for breeding.

        :param population: List of Turret instances representing the current population.
        :return: List of selected parent Turrets.
        """
        fitness_scores: t.List[t.Tuple[Turret, int]] = [
            (turret, self.fitness_function(turret)) for turret in population
        ]

        # Sort the population based on fitness scores (lower score is better)
        fitness_scores.sort(key=lambda x: x[1])

        # Select the best turret
        selected_parents: t.List[Turret] = [fitness_scores[0][0]
                                            ]  # Best individual

        # Select U - 1 additional parents randomly from the remaining individuals
        remaining_parents: t.List[t.Tuple[Turret, int]] = fitness_scores[
            1:]  # Exclude the best individual

        # Randomly choose U - 1 individuals from the remaining population
        additional_parents: t.List[t.Tuple[Turret, int]] = random.sample(
            remaining_parents, min(self.U - 1, len(remaining_parents)))

        # Append these additional parents to the selected list
        selected_parents.extend(turret for turret, _ in additional_parents)

        return selected_parents

    def crossover(self, parent1: Turret, parent2: Turret) -> Turret:
        """
        Perform crossover between two parent Turrets to create an offspring.

        :param parent1: First parent Turret.
        :param parent2: Second parent Turret.
        :return: New Turret instance created from the parents.
        """
        # Ensure both parents have the same number of slots
        if len(parent1.array) != len(parent2.array):
            raise ValueError(
                "Parents must have the same number of slots for crossover.")

        # Randomly choose a crossover point
        crossover_point: int = random.randint(1, len(parent1.array) - 1)

        # Create a new slots array for the offspring
        new_slots: t.List[int] = [
            tool.id for tool in parent1.array[:crossover_point]
        ] + [tool.id for tool in parent2.array[crossover_point:]]

        # Create a new tool_data dictionary by merging both parent tool data
        new_tool_data: t.Dict[int, int] = {
            tool.id: tool.life
            for tool in parent1.array + parent2.array
        }

        # Create a new Turret instance using the new slots and merged tool data
        offspring: Turret = Turret(new_slots, new_tool_data)

        return offspring

    def fitness_function(self, turret: Turret) -> int:
        """
        Fitness function to evaluate the performance of a Turret configuration.

        :param turret_array: List representing the turret configuration (slots).
        :return: The score for the given turret configuration (lower is better).
        """
        # Evaluate the turret configuration based on the score function of the Turret
        # class
        return turret.score(300, self.ops)

    def create_initial_population(self, size: int,
                                  djkParent: t.List[int]) -> t.List[Turret]:
        """
        Create the initial population for the genetic algorithm.

        :param size: The number of individuals in the population.
        :param djkParent: A base list representing the parent configuration.
        :return: A list of individuals (population), each being a shuffled version of 
        the parent configuration.
        """
        population: t.List[Turret] = [Turret(djkParent, self.tool_life_table)]

        for _ in range(size):
            # Shuffle the parent configuration to create a new individual
            individual: t.List[int] = sorted(djkParent,
                                             key=lambda _: random.random())
            population.append(Turret(individual, self.tool_life_table))

        return population

    def repair(self, turret: Turret,
               expected_tool_distribution: t.Dict[int, int]) -> Turret:
        """
        Repair function to fix the tool distribution in a Turret after crossover. 
        Ensures that the number of each tool matches the expected distribution.

        :param turret: The Turret instance to be repaired.
        :param expected_tool_distribution: A dictionary mapping tool ID to the expected 
        count.
        :return: Repaired Turret instance with corrected tool distribution.
        """
        # Count the current number of each tool in the turret array
        current_distribution = Counter(tool.id for tool in turret.array)

        # Create a list of tools that are in excess or deficit
        excess_tools = []
        missing_tools = []

        # Check for excess and deficit of each tool
        for tool_id, expected_count in expected_tool_distribution.items():
            current_count = current_distribution.get(tool_id, 0)

            if current_count > expected_count:
                # Too many of this tool, mark the excess
                excess_tools.extend([tool_id] *
                                    (current_count - expected_count))
            elif current_count < expected_count:
                # Too few of this tool, mark the missing
                missing_tools.extend([tool_id] *
                                     (expected_count - current_count))

        # Replace excess tools with missing tools to balance the array
        excess_index = 0
        for i, tool in enumerate(turret.array):
            if tool.id in excess_tools:
                # Replace this tool with one of the missing tools
                turret.array[i].id = missing_tools[excess_index]
                excess_index += 1
                if excess_index >= len(missing_tools):
                    break  # No more tools to replace

        return turret

    def mutate(self, turret: Turret, mutation_rate: float = 0.01) -> Turret:
        """
        Mutates a given Turret by swapping two tools or changing a tool at a random 
        position
        based on the mutation rate.

        :param turret: The Turret instance to be mutated.
        :param mutation_rate: The probability of mutation for each tool in the turret 
        array (default is 1%).
        :return: A new Turret instance with the mutation applied.
        """
        # Create a copy of the turret's tool array to apply mutations
        new_tool_array: t.List[Tool] = turret.array.copy()

        # Apply mutation based on mutation rate
        for i in range(len(new_tool_array)):
            if random.random() < mutation_rate:
                # Randomly decide the type of mutation: swap or replace a tool
                if random.random() < 0.5:
                    # Mutation Type 1: Swap this tool with another random tool
                    swap_idx = random.randint(0, len(new_tool_array) - 1)
                    new_tool_array[i], new_tool_array[
                        swap_idx] = new_tool_array[swap_idx], new_tool_array[i]
                else:
                    # Mutation Type 2: Replace the tool with a new random tool from the
                    # valid set
                    new_tool_id = random.choice(
                        list(self.tool_life_table.keys()))
                    new_tool_array[i] = Tool(new_tool_id,
                                             self.tool_life_table[new_tool_id])

        # Return a new Turret with the mutated tool array
        return Turret([tool.id for tool in new_tool_array],
                      self.tool_life_table)
