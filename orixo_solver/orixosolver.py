"""
Solver for the mobile game "Orixo", which is a simple game that involves
filling in all the cells of a board by swiping number cells up, down, left,
or right.
"""

class Board:
    # Define constants for directions.
    # Values are chosen so I can use arithemetic to handle some of the logic.
    LEFT=0
    RIGHT=1
    DOWN=2
    UP=3

    def __init__ (self, data):
        """data should be an array of arrays, where each element is one of:
        '*' or an integer >=0.
        '*' indicates a non-board spacer. An integer > 0 indicates a number
        cell that can be swiped, while 0 indicates a cell that needs to be
        filled."""
        self._data = data
        self._filled = [
            [data[i][j] != 0 for j in range(len(data[0]))] \
            for i in range(len(data))
        ]

    def execute_move (self, cell, direction):
        """Executes a swipe move from the given cell in the given direction.
        Note that this is a mutator and will modify the data arrays.
        Returns True if the move succeeds, False otherwise."""
        pass

    def generate_number_cells (self):
        """Generates an array of NumberCell objects for each number cell
        in the data, and sets their initial valid directions."""
        pass

class NumberCell:
    pass

class Driver:
    pass

if __name__ == "__main__":
    driver = Driver()
    driver.read_file()
    driver.run_solver()
    driver.output_solutions()
