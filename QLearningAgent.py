import math
import random
import numpy as np
from Board import Board
from Minimax import Minimax

ROW_COUNT = 6
COLUMN_COUNT = 7
WINDOW_LENGTH = 4

EMPTY = 0
PLAYER_PIECE = 1
AI_PIECE = 2

OPPONENT = 1
DQN = 2
RANDOM = 3
MINIMAX = 4

DEPTH = 5

WIN_SCORE = 1000
LOSE_SCORE = -1000

NONE = 0

FOUR_IN_ROW = 10000
THREE_IN_ROW = 30
TWO_IN_ROW = 5
MIDDLE_COLUMN = 3

OPP_FOUR_IN_ROW = 10000
OPP_THREE_IN_ROW = 30
OPP_TWO_IN_ROW = 3

BLOCK_THREE = 100
BLOCK_TWO = 3
GRAY = (177, 196, 253)


def evaluate_window(window, piece):
    opp_piece = PLAYER_PIECE

    ai_score, opp_score = 0, 0
    ai_key, opp_key = "NONE", "NONE"
    if window.count(piece) == 4:
        ai_score += 1
        ai_key = "FOUR_IN_ROW"
    elif window.count(piece) == 3 and window.count(EMPTY) == 1:
        ai_score += 1
        ai_key = "THREE_IN_ROW"
    elif window.count(piece) == 2 and window.count(EMPTY) == 2:
        ai_score += 1
        ai_key = "TWO_IN_ROW"

    if window.count(opp_piece) == 4:
        opp_score += 1
        opp_key = "OPP_FOUR_IN_ROW"
    elif window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
        opp_score += 1
        opp_key = "OPP_THREE_IN_ROW"
    elif window.count(opp_piece) == 2 and window.count(EMPTY) == 2:
        opp_score += 1
        opp_key = "OPP_TWO_IN_ROW"

    return (ai_key, ai_score), (opp_key, opp_score)


def get_best_col(state, piece):
    # Score Horizontal
    for r in range(ROW_COUNT):
        row_array = [int(i) for i in state[r]]
        for c in range(COLUMN_COUNT - 3):
            window = row_array[c:c + WINDOW_LENGTH]
            if window.count(piece) == 3 and window.count(EMPTY) == 1:
                for i in range(len(window)):
                    if window[i] == EMPTY and (r == 5 or state[r + 1][c + i] != EMPTY):
                        print("Horizontal")
                        return c + i
    # Score Vertical
    for c in range(COLUMN_COUNT):
        col_array = [int(i) for i in [state[r][c] for r in range(ROW_COUNT)]]
        for r in range(ROW_COUNT - 3):
            window = col_array[r:r + WINDOW_LENGTH]
            if window.count(piece) == 3 and window.count(EMPTY) == 1:
                print("Vertical")
                return c
    # Score diagonals
    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            window = [state[r + i][c + i] for i in range(WINDOW_LENGTH)]
            if window.count(piece) == 3 and window.count(EMPTY) == 1:
                for i in range(len(window)):
                    if window[i] == EMPTY and (r + i == 5 or state[r + i + 1][c + i] != EMPTY):
                        print("diagonals")
                        return c + i
    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 1, 3, -1):
            window = [state[r + i][c - i] for i in range(WINDOW_LENGTH)]
            if window.count(piece) == 3 and window.count(EMPTY) == 1:
                for i in range(len(window)):
                    if window[i] == EMPTY and (r + i == 5 or state[r + i + 1][c - i] != EMPTY):
                        print("reversed diagonals")
                        return c - i
    print(None)
    return None


def score_board(state, piece):
    ai_scores = {
        "FOUR_IN_ROW": 0,
        "THREE_IN_ROW": 0,
        "TWO_IN_ROW": 0,
        "NONE": 0
    }
    opp_scores = {
        "OPP_FOUR_IN_ROW": 0,
        "OPP_THREE_IN_ROW": 0,
        "OPP_TWO_IN_ROW": 0,
        "NONE": 0
    }

    # Score Horizontal
    for r in range(ROW_COUNT):
        row_array = [int(i) for i in state[r]]
        for c in range(COLUMN_COUNT - 3):
            window = row_array[c:c + WINDOW_LENGTH]
            ai_score, opp_score = evaluate_window(window, piece)
            ai_scores[ai_score[0]] += ai_score[1]
            opp_scores[opp_score[0]] += opp_score[1]
    # Score Vertical
    for c in range(COLUMN_COUNT):
        col_array = [int(i) for i in [state[r][c] for r in range(ROW_COUNT)]]
        for r in range(ROW_COUNT - 3):
            window = col_array[r:r + WINDOW_LENGTH]
            ai_score, opp_score = evaluate_window(window, piece)
            ai_scores[ai_score[0]] += ai_score[1]
            opp_scores[opp_score[0]] += opp_score[1]

    # Score diagonals
    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            window = [state[r + i][c + i] for i in range(WINDOW_LENGTH)]
            ai_score, opp_score = evaluate_window(window, piece)
            ai_scores[ai_score[0]] += ai_score[1]
            opp_scores[opp_score[0]] += opp_score[1]

    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            window = [state[r + 3 - i][c + i] for i in range(WINDOW_LENGTH)]
            ai_score, opp_score = evaluate_window(window, piece)
            ai_scores[ai_score[0]] += ai_score[1]
            opp_scores[opp_score[0]] += opp_score[1]
    return ai_scores, opp_scores


def reward_for_move(state, turns, pre_ai_score, pre_opp_score):
    ai_scores, opp_scores = score_board(state.grid, AI_PIECE)
    if ai_scores["FOUR_IN_ROW"] > 0:  # Win before flip
        return WIN_SCORE
    if turns % 5 == 0:
        ai_scores_flip, opp_scores_flip = score_board(state.flip_board(), AI_PIECE)
        if ai_scores_flip["FOUR_IN_ROW"] > 0:  # Win after flip
            return WIN_SCORE
        if opp_scores_flip["OPP_FOUR_IN_ROW"] > 0:  # Lose after flip
            return LOSE_SCORE

    reward = 0

    # Three block
    if pre_opp_score["OPP_THREE_IN_ROW"] > 0:
        if opp_scores["OPP_THREE_IN_ROW"] == pre_opp_score["OPP_THREE_IN_ROW"]:  # Didn't block opp three in a row
            if get_best_col(state.grid, PLAYER_PIECE) is not None:
                return LOSE_SCORE
        else:  # Blocked opp three in a row
            reward += BLOCK_THREE

    # Score center column
    center_array = [int(i) for i in list(np.array(state.grid)[:, COLUMN_COUNT // 2])]
    center_count = center_array.count(AI_PIECE)
    reward += center_count * MIDDLE_COLUMN

    # Create three
    if ai_scores["THREE_IN_ROW"] > pre_ai_score["THREE_IN_ROW"]:  # Created three in a row
        reward += THREE_IN_ROW

    # Difference between player threes and twos to opp threes and twos
    state_score = ((ai_scores["THREE_IN_ROW"] * THREE_IN_ROW)
                   - (opp_scores["OPP_THREE_IN_ROW"] * OPP_THREE_IN_ROW)
                   + (ai_scores["TWO_IN_ROW"] * TWO_IN_ROW)
                   - (opp_scores["OPP_TWO_IN_ROW"] * OPP_TWO_IN_ROW))

    # Two block
    if pre_opp_score["OPP_TWO_IN_ROW"] > 0:
        if opp_scores["OPP_TWO_IN_ROW"] == pre_opp_score["OPP_TWO_IN_ROW"]:  # Didn't block opp two in a row
            reward += state_score
        else:  # Blocked opp two in a row
            reward += BLOCK_TWO

    # Create two
    if ai_scores["TWO_IN_ROW"] > pre_ai_score["TWO_IN_ROW"]:  # Created two in a row
        reward += TWO_IN_ROW

    return reward if reward > 0 else state_score


class QLearningAgent:
    def __init__(self, q_table, learning_rate=0.1, discount_factor=0.9, exploration_rate=1.0, exploration_decay=0.9999):
        self.q_table = q_table
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate
        self.exploration_decay = exploration_decay
        self.opponent_symbol = 1

    def update_q_value(self, state, action, turns_till_flip, reward, next_state, valid_actions):
        current_q = self.q_table.get((state, action, turns_till_flip), 0)
        max_next_q = max([self.q_table.get((next_state, a, turns_till_flip), 0) for a in valid_actions], default=0)
        new_q = current_q + self.learning_rate * (reward + self.discount_factor * max_next_q - current_q)
        self.q_table[(state, action, turns_till_flip)] = new_q

    def choose_action(self, board, turns_mode, valid_actions):
        random_rate = random.uniform(0, 1)
        if random_rate < self.exploration_rate:
            print("Random uniform: ", random_rate)
            return random.choice(valid_actions)
        else:
            flatten_state = tuple(board.grid.flatten())
            q_values = {a: self.q_table.get((flatten_state, a, turns_mode), -math.inf) for a in valid_actions}

            positive_found_actions = {}
            not_found_actions = {}
            for key in q_values.keys():
                if q_values[key] == -math.inf:
                    not_found_actions[key] = q_values[key]
                else:
                    if q_values[key] >= 0:
                        positive_found_actions[key] = q_values[key]

            if not positive_found_actions:
                print("Random!")
                win_col = get_best_col(board.grid, AI_PIECE)
                if win_col is not None:
                    return win_col
                block_col = get_best_col(board.grid, PLAYER_PIECE)
                if block_col is not None:
                    return block_col
                if not not_found_actions:
                    return random.choice(valid_actions)
                else:
                    random_col = random.choice(list(not_found_actions.keys()))
                return random_col

            print("Learning!")
            best_col = max(positive_found_actions, key=positive_found_actions.get)
            return best_col

    def train_qla(self, num_games=200000):
        dqn_mode = DQN
        opp_mode = RANDOM
        minmax_player = Minimax()  # Minimax AI for player
        for i in range(num_games):
            print(f'\nAuto game num: {i}')
            turns = 0
            board = Board()  # Create a new board for each game
            turn = random.choice([DQN, OPPONENT])  # Randomly decide who starts
            col = 0

            while True:
                if turn == DQN:
                    valid_actions = board.get_valid_locations()
                    if not valid_actions:
                        print("Draw!")
                        break
                    state = tuple(board.grid.flatten())
                    pre_ai_score, pre_opp_score = score_board(board.grid, AI_PIECE)
                    if dqn_mode == DQN:
                        col = self.choose_action(board, True if (turns + 1) % 5 == 0 else False, valid_actions)
                    elif dqn_mode == MINIMAX:
                        col, minimax_score = minmax_player.minimax(
                            board.copy_board(), DEPTH - (turns % 5), -math.inf, math.inf, True, turns)
                    elif dqn_mode == RANDOM:
                        col = random.choice(valid_actions)

                    row = board.get_next_open_row(col)
                    print("***************************************************************************")
                    print("State before drop disk:\n", np.array(board.grid))
                    board.place_disk(row, col, AI_PIECE)  # Place AI piece
                    turns += 1
                    reward = reward_for_move(board, turns, pre_ai_score, pre_opp_score)
                    print("State after drop disk:\n", np.array(board.grid))
                    print("Reward is: ", reward)

                    next_state = tuple(board.grid.flatten())
                    self.update_q_value(
                        state, col, True if turns % 5 == 0 else False, reward, next_state, valid_actions)
                    turn = OPPONENT

                    # Check victory conditions
                    if board.check_victory(AI_PIECE):
                        break
                    if turns % 5 == 0:
                        board.grid = board.flip_board()
                        if board.check_victory(AI_PIECE) or board.check_victory(PLAYER_PIECE):
                            break

                if turn == OPPONENT:
                    valid_actions = board.get_valid_locations()
                    if not valid_actions:
                        print("Draw!")
                        break
                    if opp_mode == MINIMAX:
                        col, minimax_score = minmax_player.minimax(
                            board.copy_board(), DEPTH - (turns % 5), -math.inf, math.inf, True, turns)
                    elif opp_mode == RANDOM:
                        col = random.choice(valid_actions)

                    row = board.get_next_open_row(col)
                    board.place_disk(row, col, PLAYER_PIECE)
                    turns += 1

                    turn = DQN

                    # Check victory conditions
                    if board.check_victory(PLAYER_PIECE):
                        break
                    if turns % 5 == 0:
                        board.grid = board.flip_board()
                        if board.check_victory(AI_PIECE) or board.check_victory(PLAYER_PIECE):
                            break

            self.exploration_rate = self.exploration_rate * self.exploration_decay

        self.exploration_rate = 0.1
