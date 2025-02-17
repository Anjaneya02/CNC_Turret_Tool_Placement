from __future__ import annotations

import typing as t
from dataclasses import dataclass


@dataclass
class Tool:
    id: int = 0
    life: int = -1

    @property
    def use(self) -> bool:
        self.life = (self.life - 1) if self.life >= 0 else self.life
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

    def find(self, tool_id: int, start_idx: int = 0) -> t.List[t.Tuple[int, int]]:
        """
        Find all unique indexes and their respective minimum absolute distances
        (clockwise: +ve, anticlockwise: -ve) for the given tool_id.
        :param tool_id: The tool ID to search for.
        :param start_idx: The starting index from which to calculate distance.
        :return: A list of tuples (index, distance) with unique indexes and their
        corresponding minimum absolute distances, where distance is positive if
        clockwise, and negative if anticlockwise.
        """

        all_distances = []

        # Search clockwise and anticlockwise at the same time
        for i in range(self.size):
            # Clockwise index
            cw_idx = (start_idx + i) % self.size
            if self.array[cw_idx].id == tool_id:
                all_distances.append((cw_idx, i))  # i is positive for clockwise

            # Anticlockwise index
            if i != 0:  # Avoid counting the start_idx twice (skip when i == 0)
                acw_idx = (start_idx - i) % self.size
                if self.array[acw_idx].id == tool_id:
                    all_distances.append(
                        (acw_idx, -i)
                    )  # -i is negative for anticlockwise

        # Create a dictionary to store the minimum distance for each index
        unique_distances: dict[int, tuple[int, int]] = {}

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

    def score(self, parts: int, ops: t.List[int], point: int = 0):
        # Always start scoring if we are pointing at the correct index
        if ops[0] != self.array[point].id:
            raise ValueError(
                f"""{self.array[point]} was present at position,
                but operation starts from Tool with id {ops[0]}"""
            )
        score = 0
        path_string_prev = ""
        while parts > 0:
            path = 0
            path_string_curr = ""
            for tool_id in ops:
                finds = self.find(tool_id, point)
                finds.sort(key=lambda x: abs(x[1]))  # Sort on the basis of distances
                if finds == []:
                    print(f"Bad Parts ({parts} {path} remaining) - skipping ...")
                    return score

                for index, distance in finds:
                    if self.array[index].use:
                        path_string_curr += str(index + 1)
                        path += abs(distance)
                        point = index
                        break
                    # print(f"Tool ID {tool_id} at {index +1 } is out of life.")
                    self.array[index].id = 0
            parts -= 1
            score += path
            if path_string_curr != path_string_prev:
                print("Pathstring changed from")
                print(f"{path_string_prev} -> {path_string_curr} ({path} weight)")
                print(f"while {parts} parts were remaining.")
                for idx, tool in enumerate(self.array):
                    print(f"Position: {idx+1} - {tool}")
                path_string_prev = path_string_curr
        return score
