import numpy as np

PLAYER_PIECE = 1
AI_PIECE = 2


class Board:
    def __init__(self, rows=6, cols=7):
        self.rows = rows
        self.cols = cols
        self.grid = np.zeros((rows, cols), dtype=int)
        self.current_player = 1

    def copy_board(self):
        new_board = Board()
        new_board.grid = self.grid.copy()
        return new_board

    def is_valid_location(self, col):
        return np.any(self.grid[:, col] == 0)

    def get_valid_locations(self):
        valid_locations = []
        for col in range(self.cols):
            if self.is_valid_location(col):
                valid_locations.append(col)
        return valid_locations

    def get_next_open_row(self, col):
        for row in range(self.rows - 1, -1, -1):
            if self.grid[row][col] == 0:
                return row
        return None

    def place_disk(self, row, col, player_id):
        if row is not None:
            self.grid[row][col] = player_id

    def check_victory(self, player_id):
        for row in range(self.rows):
            for col in range(self.cols - 3):
                if all(self.grid[row][col + i] == player_id for i in range(4)):
                    return True

        for col in range(self.cols):
            for row in range(self.rows - 3):
                if all(self.grid[row + i][col] == player_id for i in range(4)):
                    return True

        for row in range(self.rows - 3):
            for col in range(self.cols - 3):
                if all(self.grid[row + i][col + i] == player_id for i in range(4)):
                    return True

        for row in range(self.rows - 3):
            for col in range(3, self.cols):
                if all(self.grid[row + i][col - i] == player_id for i in range(4)):
                    return True

        return False

    def is_terminal_node(self):
        return (self.check_victory(PLAYER_PIECE)
                or self.check_victory(AI_PIECE)
                or len(self.get_valid_locations()) == 0)

    def flip_board(self):
        rows = len(self.grid)
        cols = len(self.grid[0])
        rotated_board = [[self.grid[rows - 1 - i][cols - 1 - j] for j in range(cols)] for i in range(rows)]

        for col in range(cols):
            column = [rotated_board[row][col] for row in range(rows)]
            non_zeros = [num for num in column if num != 0]
            new_column = [0] * (rows - len(non_zeros)) + non_zeros
            for row in range(rows):
                rotated_board[row][col] = new_column[row]

        return np.array(rotated_board)
