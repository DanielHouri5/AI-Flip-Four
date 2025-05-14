import math
import sys
import random
import pygame

from Minimax import Minimax
from Board import Board
import QLearningAgent

PLAYER = 0
AI = 1

PLAYER_PIECE = 1
AI_PIECE = 2

MINIMAX = 1
Q_LEARNING = 2
WATCH_GAME = 3
TRAIN_AGENT = 4

MINIMAX_PIECE = 1
Q_LEARNING_PIECE = 2

RED = (255, 0, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
GRAY = (177, 196, 253)

SQUARE_SIZE = 100

ROW_COUNT = 6
COLUMN_COUNT = 7

DEPTH = 5

pygame.init()
clock = pygame.time.Clock()


class GameManager:
    def __init__(self, ui_manager):
        self.board = Board()
        self.ui_manager = ui_manager
        self.is_mouse_pressed = False
        self.is_animating = False

    def drop_disk(self, row, col, current_player):
        if row is not None:
            self.ui_manager.drop_disk_with_animation(row, col, current_player, self.board)
            self.board.place_disk(row, col, current_player)

    def double_check_winning(self, player_won_message, opponent_won_message, player_piece, opp_piece, player_color,
                             opp_color, turns):
        if self.board.check_victory(player_piece):
            self.ui_manager.wining_message(player_won_message, player_color, self.board)
            return True
        if turns % 5 == 0:
            self.ui_manager.flipping_message(self.board)
            self.board.grid = self.board.flip_board()
            self.ui_manager.flipping_animation(self.board)
            if self.board.check_victory(player_piece):

                valid_actions = [col for col in range(self.board.cols) if
                                 self.board.get_next_open_row(col) is not None]

                if self.board.check_victory(opp_piece) or not valid_actions:
                    self.ui_manager.wining_message("Draw!", GRAY, self.board)
                else:
                    self.ui_manager.wining_message(player_won_message, player_color, self.board)

                return True

            elif self.board.check_victory(opp_piece):
                self.ui_manager.wining_message(opponent_won_message, opp_color, self.board)
                return True

        return False

    def player_move(self, event):
        if not self.is_mouse_pressed and not self.is_animating:
            self.is_mouse_pressed = True
            col = self.ui_manager.get_column_from_click(event.pos)
            if col is not None:
                row = self.board.get_next_open_row(col)
                if row is not None:
                    self.is_animating = True
                    self.drop_disk(row, col, PLAYER_PIECE)
                    self.is_animating = False
                    return True
        return False

    def minimax_move(self, minimax_player, turns, piece):
        col, minimax_score = (
            minimax_player.minimax(self.board.copy_board(), DEPTH - (turns % 5), -math.inf, math.inf, True, turns))
        row = self.board.get_next_open_row(col)

        self.is_animating = True
        self.drop_disk(row, col, piece)
        self.is_animating = False

    def q_learning_move(self, agent, turns, piece):
        state = tuple(self.board.grid.flatten())
        pre_ai_score, pre_opp_score = QLearningAgent.score_board(self.board.grid, piece)
        valid_actions = self.board.get_valid_locations()
        col = agent.choose_action(self.board, True if (turns + 1) % 5 == 0 else False, valid_actions)
        row = self.board.get_next_open_row(col)

        self.is_animating = True
        self.drop_disk(row, col, piece)
        self.is_animating = False

        reward = QLearningAgent.reward_for_move(self.board, turns + 1, pre_ai_score, pre_opp_score)
        next_state = tuple(self.board.grid.flatten())
        agent.update_q_value(state, col, True if (turns + 1) % 5 == 0 else False, reward, next_state, valid_actions)

    def play_mode(self, mode, updated_agent=None):
        if mode == MINIMAX:
            minimax_player = Minimax()
            self.ui_manager.player1_name, self.ui_manager.player2_name = "You", "Minimax"
            self.run_the_game_against_algo(minimax_player, mode)
        elif mode == Q_LEARNING:
            self.ui_manager.player1_name, self.ui_manager.player2_name = "You", "Q-Learning"
            agent = updated_agent
            self.run_the_game_against_algo(agent, mode)
        elif mode == WATCH_GAME:
            self.ui_manager.player1_name, self.ui_manager.player2_name = "Minimax", "Q-Learning"
            self.run_algorithms_game(updated_agent)

    def run_the_game_against_algo(self, ai_player, algo):
        turns = 0
        turn = random.randint(PLAYER, AI)
        game_over = False
        message = "Minimax" if algo == MINIMAX else "Q-learning"

        while not game_over:
            self.ui_manager.render_game(self.board.grid)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if turn == PLAYER:
                        if self.player_move(event):
                            turns += 1
                            game_over = self.double_check_winning(
                                "You Won!", f"{message} Won!", PLAYER_PIECE, AI_PIECE, YELLOW, RED, turns)
                            turn = AI
                            break

            if turn == AI and not game_over:

                if algo == MINIMAX:
                    self.minimax_move(ai_player, turns, AI_PIECE)

                if algo == Q_LEARNING:
                    self.q_learning_move(ai_player, turns, AI_PIECE)

                turns += 1
                game_over = self.double_check_winning(f"{message} Won!", "You Won!", AI_PIECE, PLAYER_PIECE, RED,
                                                      YELLOW, turns)
                turn = PLAYER

                self.is_mouse_pressed = False

            pygame.display.update()
            clock.tick(60)

            if game_over:
                pygame.time.wait(3000)

    def run_algorithms_game(self, agent):
        minimax_player = Minimax()

        turns = 0
        turn = random.randint(MINIMAX, Q_LEARNING)
        game_over = False

        self.ui_manager.render_game(self.board.grid)
        while not game_over:
            if turn == Q_LEARNING and not game_over:
                self.q_learning_move(agent, turns, Q_LEARNING_PIECE)
                turns += 1

                game_over = self.double_check_winning(
                    "Q-Learning won!!", "MINIMAX won!!", Q_LEARNING_PIECE, MINIMAX_PIECE, YELLOW, RED, turns)

                turn = MINIMAX

            if turn == MINIMAX and not game_over:
                self.minimax_move(minimax_player, turns, MINIMAX_PIECE)
                turns += 1

                game_over = self.double_check_winning(
                    "MINIMAX won!!", "Q-Learning won!!", MINIMAX_PIECE, Q_LEARNING_PIECE, RED, YELLOW, turns)

                turn = Q_LEARNING

            pygame.display.update()
            clock.tick(60)

            if game_over:
                pygame.time.wait(3000)
