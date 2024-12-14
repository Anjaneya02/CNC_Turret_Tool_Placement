from __future__ import annotations

import typing as t
from dataclasses import dataclass


@dataclass
class Tool:
    id: int = 0
    life: int = -1

    @property
    def use(self) -> bool:
        self.life -= 1
        return self.life > 0


class Turret:

    def __init__(self, slots: t.List[int], tool_data: t.Dict[int, int]):
        """
        :param slots: List of tool IDs to represent the tool arrangement in the turret.
        :param tool_data: Dictionary mapping tool_id to tool_life.
        """
        self.array: t.List[Tool] = [
            Tool(tool_id, tool_data[tool_id]) for tool_id in slots
        ]
        self.size = len(self.array)

    def find_all_with_distances(self,
                                tool_id: int,
                                idx: int = 0) -> t.List[t.Tuple[int, int]]:
        """
        Find all indexes and their respective distances (clockwise: +ve, anticlockwise: 
        -ve) for the given tool_id.
        :param tool_id: The tool ID to search for.
        :param idx: The starting index from which to calculate distance.
        :return: A list of tuples with (index, distance), where distance is positive if 
        clockwise, and negative if anticlockwise.
        """
        results = []

        # Search clockwise and anticlockwise at the same time
        for i in range(self.size):
            # Clockwise index
            cw_idx = (idx + i) % self.size
            if self.array[cw_idx].id == tool_id:
                results.append((cw_idx, i))  # i is positive for clockwise

            # Anticlockwise index
            if i != 0:  # Avoid counting the start_idx twice (skip when i == 0)
                acw_idx = (idx - i) % self.size
                if self.array[acw_idx].id == tool_id:
                    results.append(
                        (acw_idx, -i))  # -i is negative for anticlockwise

        return results

    def find_nearest(self,
                     tool_id: int,
                     start_idx: int = 0) -> t.Optional[t.Tuple[int, int]]:
        """
           Find the nearest tool by tool_id, checking all distances and returning the
           one with the minimum absolute distance.
           :param tool_id: The tool ID to search for.
           :param start_idx: The starting index from which to calculate distance.
           :return: A tuple with (index, distance), where distance is
           positive if clockwise, and negative if anticlockwise,
                    or None if the tool_id is not found.
           """
        all_distances = self.find_all_with_distances(tool_id, start_idx)

        if not all_distances:
            return None  # No tool found

        # Find the one with the minimum absolute distance
        nearest_tool = min(all_distances, key=lambda x: abs(x[1]))

        return nearest_tool

    def find(self,
             tool_id: int,
             start_idx: int = 0) -> t.List[t.Tuple[int, int]]:
        """
        Find all unique indexes and their respective minimum absolute distances for the given tool_id.
        :param tool_id: The tool ID to search for.
        :param start_idx: The starting index from which to calculate distance.
        :return: A list of tuples with unique indexes and their corresponding minimum absolute distances.
        """
        all_distances = self.find_all_with_distances(tool_id, start_idx)

        # Create a dictionary to store the minimum distance for each index
        unique_distances = {}

        for index, distance in all_distances:
            if index in unique_distances:
                # If the index already exists, check if the current distance is smaller
                if abs(distance) < abs(unique_distances[index][1]):
                    unique_distances[index] = (index, distance)
            else:
                # Add the index with its distance
                unique_distances[index] = (index, distance)

        # Return the values as a list of tuples
        return list(unique_distances.values())

    def create_graph(
            self, ops: t.List[int]) -> t.Dict[int, t.List[t.Tuple[int, int]]]:
        graph = {}
        current_idx = 0  # Start from the first position

        for tool_id in ops:
            distances = self.find_all_with_distances(tool_id, current_idx)
            if not distances:
                print(f"Tool ID {tool_id} not found in turret.")
                continue

            # Create graph edges from the current index to all found distances
            for next_idx, distance in distances:
                if current_idx not in graph:
                    graph[current_idx] = []
                graph[current_idx].append((next_idx, distance))

            # Update the current index to the first found position of the tool_id
            current_idx = distances[0][0]

        return graph

    def score(self, parts: int, ops: t.List[int]):
        score = 0
        while parts > 0:
            first_t = self.find_nearest(ops[0], 0)
            if not first_t:
                # print("No tool found for the first operation.")
                # print("Parts made: ", parts)
                return score
            first_idx, _ = first_t
            current_idx = first_idx
            path = 0
            for tool_id in ops:
                current_rot = self.find_nearest(tool_id, current_idx)
                if not current_rot:
                    # print(f"Tool ID {tool_id} not found in turret.")
                    return score
                position, distance = current_rot
                if not self.array[position].use:
                    # print(f"Tool ID {tool_id} at {position} is out of life.")
                    self.array[position]._id = 0
                current_idx = position
                path += abs(distance)
            parts -= 1
            score += path
        return score
