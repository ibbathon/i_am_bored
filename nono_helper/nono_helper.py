#!/usr/bin/env python3

import sys

MIN_WIDTH = 0
MAX_WIDTH = 1000

class Fill:
    def __init__(self, start, length, color):
        self.start = start
        self.length = length
        self.color = color

class BlockGroup:
    def __init__(self, lengths, colors):
        self._num = len(lengths)
        self._lengths = lengths
        self._colors = colors
        self._min_indexes = [MIN_WIDTH for _ in range(self._num)]
        self._max_indexes = [MAX_WIDTH for _ in range(self._num)]

    def calc_filled_spaces(self, board_width):
        self._calc_valid_area(board_width)
        fills = []
        for i in range(self._num):
            area = self._max_indexes[i] - self._min_indexes[i] + 1
            spacing = area - self._lengths[i]
            # Only add a fill if there is guaranteed known colored area
            known_fill = max(0, self._lengths[i] - spacing)
            if known_fill > 0:
                fills.append(Fill(
                    self._min_indexes[i] + spacing,
                    known_fill,
                    self._colors[i]
                ))

        return fills

    def _calc_valid_area(self, board_width):
        self._max_indexes[self._num-1] = board_width-1
        for i in range(self._num-1):
            ri = self._num-1-i
            # Calc min starts
            self._min_indexes[i+1] = self._min_indexes[i] + self._lengths[i]
            if self._colors[i] == self._colors[i+1]:
                self._min_indexes[i+1] += 1
            # Calc max ends
            self._max_indexes[ri-1] = self._max_indexes[ri] - self._lengths[ri]
            if self._colors[ri] == self._colors[ri-1]:
                self._max_indexes[ri-1] -= 1

def input_block_group(rctype, num):
    line = input("Enter {} {}: ".format(rctype, num))
    if line == "":
        sys.exit(1)
    line = line.split(" ")
    lengths = []
    colors = []
    for i in range(len(line)):
        length = None
        color = '#'
        # First attempt is to assume each item is just a number (no color)
        try:
            length = int(line[i])
        except Exception as e:
            pass
        # Second attempt is to assume last char is the color
        if length == None:
            color = line[i][-1]
            line[i] = line[i][:-1]
            length = int(line[i])
        # Assuming we didn't encounter an exception, add them to the stack
        lengths.append(length)
        colors.append(color)
    return (lengths, colors)

def input_puzzle():
    # Get puzzle size first
    size = (None, None)
    while size[1] == None:
        try:
            sizes_input = input(
                "Input height and width, separated by a space: ")
            if sizes_input == "":
                sys.exit(1)
            sizes_input = sizes_input.split(" ")
            size = tuple(map(int,sizes_input))
        except Exception as e:
            print("Invalid values. Try again.")

    # Now get the rows/columns of blocks
    print("Each block group must be input in the following form:")
    print(" dc dc dc dc ...")
    print("Where 'd' is a number and 'c' is a single character " + \
        "representing the color. 'c' can be omitted and defaults to '#'.")
    print()
    groups = [None for _ in range(size[0]+size[1])]
    for i in range(len(groups)):
        lengths, colors = None, None
        while colors == None:
            try:
                lengths, colors = input_block_group(
                    "row" if i < size[0] else "column",
                    i+1 if i < size[0] else i+1-size[0])
            except Exception as e:
                print("Invalid block group. Review instructions and try again.")
        groups[i] = BlockGroup(lengths,colors)

    # Return the groups for more processing, split into rows and cols
    return groups[:size[0]], groups[size[0]:]

def calc_and_print_fills(rows, cols):
    row_fills = [None for _ in range(len(rows))]
    col_fills = [None for _ in range(len(cols))]
    # Calculate all the fills
    for i in range(len(rows)):
        row_fills[i] = rows[i].calc_filled_spaces(len(cols))
    for i in range(len(cols)):
        col_fills[i] = cols[i].calc_filled_spaces(len(rows))

    # Create the matrix of characters
    chars = [[' ' for _ in range(len(cols))] for _ in range(len(rows))]

    # Use the fills to fill in the matrix
    for i in range(len(row_fills)):
        for j in range(len(row_fills[i])):
            fill = row_fills[i][j]
            chars[i][fill.start : fill.start+fill.length] = \
                [fill.color for _ in range(fill.length)]
    for i in range(len(col_fills)):
        for j in range(len(col_fills[i])):
            fill = col_fills[i][j]
            for k in range(fill.start, fill.start+fill.length):
                chars[k][i] = fill.color

    # Finally print the matrix, with simple headers
    # Column headers first
    print(" "+"".join([str(i%10) for i in range(len(cols))]))
    # Now print the matrix, starting each row with header
    for i in range(len(chars)):
        print(str(i%10)+"".join(chars[i]))
    print()

def driver():
    rows, cols = input_puzzle()
    print()
    calc_and_print_fills(rows, cols)


if __name__ == '__main__':
    driver()
