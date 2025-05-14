import random
import math

# Colors
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

# Size
ROW_COUNT = 6
COLUMN_COUNT = 7

# Player turn
PLAYER = 0
AI = 1

# Disk mode
EMPTY = 0
PLAYER_PIECE = 1
AI_PIECE = 2

# Max depth
DEPTH = 5

# Scores
WIN_SCORE = 1000000000
LOSE_SCORE = -100000000000000000000000

FOUR_IN_ROW = 10000
THREE_IN_ROW = 10
TWO_IN_ROW = 3
MIDDLE_COLUMN = 3

OPP_FOUR_IN_ROW = -100000000000000000000000
OPP_THREE_IN_ROW = -10000
OPP_TWO_IN_ROW = -4

AGING_PENALTY = 3

# Window length for score
WINDOW_LENGTH = 4


def evaluate_window(window, piece):
    score = 0
    opp_piece = PLAYER_PIECE if piece == AI_PIECE else AI_PIECE

    if window.count(piece) == 4:
        score += FOUR_IN_ROW
    elif window.count(piece) == 3 and window.count(EMPTY) == 1:
        score += THREE_IN_ROW
    elif window.count(piece) == 2 and window.count(EMPTY) == 2:
        score += TWO_IN_ROW

    if window.count(opp_piece) == 4:
        score += OPP_FOUR_IN_ROW
    elif window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
        score += OPP_THREE_IN_ROW
    elif window.count(opp_piece) == 2 and window.count(EMPTY) == 2:
        score += OPP_TWO_IN_ROW

    return score


def score_position(board, piece):
    score = 0

    # Score center column
    center_array = [int(i) for i in list(board[:, COLUMN_COUNT // 2])]
    center_count = center_array.count(piece)
    score += center_count * MIDDLE_COLUMN

    # Score Horizontal
    for r in range(ROW_COUNT):
        row_array = [int(i) for i in list(board[r, :])]
        for c in range(COLUMN_COUNT - 3):
            window = row_array[c:c + WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    # Score Vertical
    for c in range(COLUMN_COUNT):
        col_array = [int(i) for i in list(board[:, c])]
        for r in range(ROW_COUNT - 3):
            window = col_array[r:r + WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    # Score diagonals
    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            window = [board[r + i][c + i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            window = [board[r + 3 - i][c + i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    return score


class Minimax:

    def minimax(self, board, depth, alpha, beta, maximizing_player, turns):
        is_terminal = board.is_terminal_node()

        if turns % 5 != 0:
            if is_terminal:
                if board.check_victory(PLAYER_PIECE):
                    return None, LOSE_SCORE - depth * AGING_PENALTY
                elif board.check_victory(AI_PIECE):
                    return None, WIN_SCORE + depth * AGING_PENALTY
                else:  # Game is over, no more valid moves
                    return None, 0

        if turns % 5 == 0:
            board.grid = board.flip_board()

        valid_locations = board.get_valid_locations()
        is_terminal = board.is_terminal_node()
        if depth == 0 or is_terminal:
            if is_terminal:
                if board.check_victory(PLAYER_PIECE):
                    return None, LOSE_SCORE - depth * AGING_PENALTY
                elif board.check_victory(AI_PIECE):
                    return None, WIN_SCORE + depth * AGING_PENALTY
                else:  # Game is over, no more valid moves
                    return None, 0
            else:  # Depth is zero
                return None, score_position(board.grid, AI_PIECE)

        if maximizing_player:
            value = -math.inf
            column = random.choice(valid_locations)

            for col in valid_locations:
                row = board.get_next_open_row(col)
                b_copy = board.copy_board()
                b_copy.place_disk(row, col, AI_PIECE)
                _, new_score = self.minimax(b_copy, depth - 1, alpha, beta, False, turns + 1)
                if new_score > value:
                    value = new_score
                    column = col
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            return column, value

        else:  # Minimizing player
            value = math.inf
            column = random.choice(valid_locations)

            for col in valid_locations:
                row = board.get_next_open_row(col)
                b_copy = board.copy_board()
                b_copy.place_disk(row, col, PLAYER_PIECE)

                _, new_score = self.minimax(b_copy, depth - 1, alpha, beta, True, turns + 1)
                if new_score < value:
                    value = new_score
                    column = col
                beta = min(beta, value)
                if alpha >= beta:
                    break
            return column, value
