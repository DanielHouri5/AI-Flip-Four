import sys
import os
import pickle
import pygame
from GameManager import GameManager
from UIManager import UIManager
from QLearningAgent import QLearningAgent

WHITE = (255, 255, 255)
GRAY = (177, 196, 253)

TRAINING = 1
NOT_TRAINING = 2

pygame.init()

pygame.display.set_caption("FLIP FOUR")
screen = pygame.display.set_mode((1200, 750), pygame.RESIZABLE)
WIDTH, HEIGHT = screen.get_size()

ui_manager = UIManager(screen)

loading = [True]
learning_data_file = 'learning_data.pkl'


def load_learning_data():
    try:
        if os.path.exists(learning_data_file):
            with open(learning_data_file, 'rb') as f:
                return pickle.load(f)
    except FileNotFoundError as f:
        print("Error - ", f)
    except Exception as e:
        print("Error - ", e)
    finally:
        loading[0] = False


ui_manager.show_heavy_function_message(loading, "Loading...", load_learning_data)
learning_data = load_learning_data()


def save_learning_data():
    temp_filename = learning_data_file + '.temp'
    temp_q_table = learning_data
    try:
        with open(temp_filename, 'wb') as temp_file:
            pickle.dump(temp_q_table, temp_file)
        os.replace(temp_filename, learning_data_file)
        print("Data saved successfully.")
    except FileNotFoundError as f:
        print("Error - ", f)
    except Exception as e:
        print("Error - ", e)
        if os.path.exists(temp_filename):
            os.remove(temp_filename)
    finally:
        loading[0] = False


def play_against_minimax():
    manager = GameManager(ui_manager)
    manager.play_mode(1)


def play_against_q_learning():
    global learning_data
    agent = QLearningAgent(learning_data, 0.1, 0.9, 0.1, 0.99)
    mode = NOT_TRAINING
    if mode == TRAINING:
        agent.train_qla()
    elif mode == NOT_TRAINING:
        manager = GameManager(ui_manager)
        manager.play_mode(2, agent)
    learning_data = agent.q_table


def finish_game():
    pygame.quit()
    sys.exit()


def play():
    menu(play_against_minimax, play_against_q_learning, finish_game, "Play Against Minimax", "Play Against Q-Learning")


def watch_algorithms_game():
    global learning_data
    agent = QLearningAgent(learning_data, 0.1, 0.9, 0.1, 0.99)
    manager = GameManager(ui_manager)
    manager.play_mode(3, agent)
    learning_data = agent.q_table


def finish_program():
    loading[0] = True
    ui_manager.show_heavy_function_message(loading, "Saving...", save_learning_data)
    save_learning_data()
    finish_game()


def menu(f1, f2, f3, button1_label, button2_label):
    global learning_data, ui_manager, screen, WIDTH, HEIGHT
    while True:
        ui_manager.draw_background()

        title_rect = ui_manager.draw_title("FLIP FOUR")

        button_width = 400
        button_height = 60
        button_margin = 50
        play_button_y = 300
        watch_button_y = play_button_y + button_height + button_margin

        width, height = screen.get_size()

        play_button_rect = ui_manager.draw_button(button1_label, (width - button_width) // 2, play_button_y,
                                                  button_width, button_height, GRAY, WHITE)
        watch_button_rect = ui_manager.draw_button(button2_label, (width - button_width) // 2, watch_button_y,
                                                   button_width, button_height, GRAY, WHITE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                f3()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if not loading[0] and title_rect.collidepoint(event.pos):
                    main()
                if play_button_rect.collidepoint(event.pos):
                    f1()
                if watch_button_rect.collidepoint(event.pos):
                    f2()
            if event.type == pygame.VIDEORESIZE:
                if event.type == pygame.VIDEORESIZE:
                    screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                    WIDTH, HEIGHT = screen.get_size()
                    ui_manager.screen = screen
                    pygame.display.update()

        pygame.display.update()


def main():
    menu(play, watch_algorithms_game, finish_program, "Play", "Watch Algorithms Game")


if __name__ == "__main__":
    main()
