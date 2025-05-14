import sys

import pygame
import time
import math
import threading

BLACK = (0, 0, 0)
GRAY = (177, 196, 253)
WHITE = (255, 255, 255)

SQUARE_SIZE = 100

ROW_COUNT = 6
COLUMN_COUNT = 7

pygame.init()

info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h


def draw_spinner(surface, center, radius, angle):
    start_angle = angle
    end_angle = angle + 270
    thickness = 8

    for i in range(20):
        pygame.draw.arc(
            surface,
            GRAY,
            (center[0] - radius, center[1] - radius, radius * 2, radius * 2),
            math.radians(start_angle + i),
            math.radians(end_angle + i),
            thickness)


class UIManager:
    def __init__(self, screen,
                 background_image="background.png", board_image="board.png",
                 disk_images=("blue_disk.png", "red_disk.png")):
        self.screen = screen
        self.background_image = pygame.image.load(background_image)
        self.board_image = pygame.image.load(board_image)
        self.disk_images = {1: pygame.image.load(disk_images[0]), 2: pygame.image.load(disk_images[1])}
        self.font = pygame.font.SysFont("Arial Black", 40)
        self.player1_name = "You"
        self.player2_name = "Minimax"

    #######################################################
    # Game images
    def draw_background(self):
        width, height = self.screen.get_size()
        scaled_background = pygame.transform.scale(self.background_image, (width, height))
        self.screen.blit(scaled_background, (0, 0))

    def draw_board(self):
        width, height = self.screen.get_size()
        board_image_width, board_image_height = self.board_image.get_size()
        self.screen.blit(self.board_image, ((width - board_image_width) // 2, (height - board_image_height) // 2))

    def draw_disks(self, grid):
        width, height = self.screen.get_size()
        board_image_width, board_image_height = self.board_image.get_size()
        rows, cols = grid.shape
        for row in range(rows):
            for col in range(cols):
                if grid[row][col] == 1:
                    self.screen.blit(self.disk_images[1], (col * 75 + 20 + (width - board_image_width) // 2, row * 75 +
                                                           23 + (height - board_image_height) // 2))
                elif grid[row][col] == 2:
                    self.screen.blit(self.disk_images[2], (col * 75 + 20 + (width - board_image_width) // 2, row * 75 +
                                                           23 + (height - board_image_height) // 2))

    def draw_game_screen(self):
        self.draw_background()

        padding = 10
        spacing = 10
        bg_color = GRAY
        text_color = BLACK

        p1_text = self.font.render(self.player1_name, True, text_color)
        p2_text = self.font.render(self.player2_name, True, text_color)
        p1_disk = self.disk_images[1]
        p2_disk = self.disk_images[2]

        block_width = max(p1_text.get_width() + p1_disk.get_width(),
                          p2_text.get_width() + p2_disk.get_width()) + 2 * padding + spacing
        block_height = max(p1_text.get_height(), p2_text.get_height(), p1_disk.get_height()) + 2 * padding

        y = 40
        p1_x = ((self.screen.get_width() - self.board_image.get_width()) // 2 - p1_text.get_width()) // 2
        p2_x = self.screen.get_width() - block_width - (((self.screen.get_width() - self.board_image.get_width()) // 2 - p1_text.get_width()) // 2)

        pygame.draw.rect(self.screen, bg_color, (p1_x, y, block_width, block_height), border_radius=20)
        pygame.draw.rect(self.screen, bg_color, (p2_x, y, block_width, block_height), border_radius=20)

        text1_y = y + (block_height - p1_text.get_height()) // 2
        text2_y = y + (block_height - p2_text.get_height()) // 2

        disk1_y = y + (block_height - p1_disk.get_height()) // 2
        disk2_y = y + (block_height - p2_disk.get_height()) // 2

        self.screen.blit(p1_text, (p1_x + padding, text1_y))
        self.screen.blit(p2_disk, (p2_x + padding, disk2_y))

        self.screen.blit(p1_disk,
                         (p1_x + block_width - padding - p1_disk.get_width(), disk1_y))
        self.screen.blit(p2_text, (p2_x + padding + p2_disk.get_width() + spacing, text2_y))

    def render_game(self, grid):
        self.draw_game_screen()
        self.draw_board()
        self.draw_disks(grid)
        pygame.display.update()

    #######################################################
    # Messages
    def wining_message(self, message, color, board):
        self.render_game(board.grid)
        fade_surface = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
        fade_surface.fill((0, 0, 0))
        fade_surface.set_alpha(128)

        text = self.font.render(f"{message}", True, color)
        text_rect = text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2))

        self.screen.blit(fade_surface, (0, 0))
        self.screen.blit(text, text_rect)

        pygame.display.update()

        pygame.time.delay(3000)

    def flipping_message(self, board):
        count = 3
        while count >= 0:
            self.render_game(board.grid)
            fade_surface = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
            fade_surface.fill((0, 0, 0))
            fade_surface.set_alpha(128)

            text = self.font.render(f"Flipping in {count}", True, GRAY)
            text_rect = text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2))

            self.screen.blit(fade_surface, (0, 0))
            self.screen.blit(text, text_rect)

            pygame.display.update()
            count -= 1
            time.sleep(1)

    #######################################################
    # Animations
    def get_column_from_click(self, pos):
        width, height = self.screen.get_size()
        board_image_width, board_image_height = self.board_image.get_size()
        x, y = pos
        col = (x - + (width - board_image_width) // 2) // 75
        return col if 0 <= col < 7 else None

    def drop_disk_with_animation(self, row, col, current_player, board):
        width, height = self.screen.get_size()
        board_image_width, board_image_height = self.board_image.get_size()
        x = col * 75 + 20 + (width - board_image_width) // 2
        start_y = 60
        end_y = row * 75 + 23 + (height - board_image_height) // 2

        my_clock = pygame.time.Clock()
        y = start_y
        while y < end_y:
            self.render_game(board.grid)

            self.screen.blit(self.disk_images[current_player], (x, y))
            pygame.display.update()

            y += 20
            my_clock.tick(60)

    def render_rotated_board(self, angle):
        board_image = pygame.image.load("board.png")
        rotated_board = pygame.transform.rotate(board_image, angle)

        width, height = self.screen.get_size()
        board_rect = rotated_board.get_rect(center=(width // 2, height // 2))

        self.screen.blit(rotated_board, board_rect)

    def flipping_animation(self, board):
        steps = 30
        angle_step = 180 / steps
        for i in range(steps):
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.type == pygame.QUIT:
                        sys.exit()
                else:
                    continue
            self.draw_game_screen()

            angle = angle_step * i

            self.render_rotated_board(angle)

            pygame.display.update()
            pygame.time.wait(30)

        self.render_game(board.grid)
        pygame.display.update()

    #######################################################
    # Menu
    def draw_title(self, text):
        title_surface = self.font.render(text, True, GRAY)
        title_rect = title_surface.get_rect(center=(self.screen.get_width() // 2, 110))
        self.screen.blit(title_surface, title_rect)
        return title_rect

    def draw_button(self, text, x, y, width, height, color, hover_color, border_radius=20):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        button_rect = pygame.Rect(x, y, width, height)

        if button_rect.collidepoint(mouse_x, mouse_y):
            pygame.draw.rect(self.screen, hover_color, button_rect, border_radius=border_radius)
        else:
            pygame.draw.rect(self.screen, color, button_rect, border_radius=border_radius)

        font = pygame.font.Font(None, 40)
        text_surface = font.render(text, True, BLACK)
        text_rect = text_surface.get_rect(center=button_rect.center)
        self.screen.blit(text_surface, text_rect)

        return button_rect

    #######################################################
    # Heavy function message
    def show_heavy_function_message(self, loading,  message, heavy_func):
        angle = 0
        width, height = self.screen.get_size()
        center_x, center_y = width // 2, height // 2

        heavy_thread = threading.Thread(target=heavy_func)
        heavy_thread.start()

        while loading[0]:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

            self.draw_background()
            self.draw_title("FLIP FOUR")

            text = self.font.render(message, True, GRAY)
            text_rect = text.get_rect(center=(center_x, center_y + 80))
            self.screen.blit(text, text_rect)

            width, height = self.screen.get_size()
            center_x, center_y = width // 2, height // 2
            draw_spinner(self.screen, (center_x, center_y), 50, angle)

            pygame.display.update()

            angle -= 5
            pygame.time.delay(20)

        time.sleep(2)
