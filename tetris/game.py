import pygame
import sys
import numpy as np
from tetris.tile import Tile
from pygame import QUIT, KEYDOWN, K_ESCAPE, K_q, K_p, K_n, K_UP, K_DOWN, K_RIGHT, K_LEFT
from tetris.constants import (
    tile_size,
    window_width,
    rows,
    cols,
    window_height,
    play_width,
    play_height,
    tl_x,
    tl_y,
    fall_speed,
    control_threshold,
)


class Tetris(object):
    """Main Tetris Game."""

    def __init__(self, *args, **kwargs) -> None:
        pygame.init()
        pygame.key.set_repeat(95, 95)
        self.window = pygame.display.set_mode((window_width, window_height))
        self.window.fill((0, 0, 0))
        self.playground = pygame.Surface((play_width, play_height))
        self.tile = Tile()
        self.lock_tiles_list = np.array([[]])
        self.clock = pygame.time.Clock()
        self.time = 0
        self.control_tick = 0
        self.run = True
        self.pause = False

    def play(self):
        self.control()
        self.clear()
        self.display()

    def control(self):
        """Main keyboard listen method.
        q, esc -> quit
        arrow keys -> control
        space -> lock to bottom
        """
        self.tile_fall(fall_speed)
        self.caliberation(self.key_down_detection())

    def clear(self):
        clear_list = []
        if self.lock_tiles_list.size:
            for row in range(rows - 1, -1, -1):
                mask = (self.lock_tiles_list[:, 1] == row)
                if len(self.lock_tiles_list[mask, :]) == 15:
                    clear_list.append(row)

        for row in clear_list:
            ...

    def caliberation(self, pressed_key):
        """Correct tile position and check locking."""
        x_max = np.max(self.tile.pos_and_color[:, 0])
        x_min = np.min(self.tile.pos_and_color[:, 0])
        y_max = np.max(self.tile.pos_and_color[:, 1])

        encounter_lock_pos = False
        for x, y in self.tile.pos_and_color[:,:2]:
            encounter_lock_pos |= [x,y] in self.lock_tiles_list[:,:2].tolist()

        if pressed_key:
            if (x_max > (cols - 1)):
                self.tile.x -= x_max - cols + 1
            elif (x_min < 0):
                self.tile.x += 0 - x_min

            if encounter_lock_pos:
                if pressed_key == K_RIGHT:
                    self.tile.x -= 1
                elif pressed_key == K_LEFT:
                    self.tile.x += 1
                elif pressed_key == K_DOWN:
                    self.tile.y -= 1
                    self.tile_lock()
                elif pressed_key == K_UP:
                    self.tile.rotate_order -= 1
                    self.tile.y -= 1
            else:
                if y_max > (rows - 1):
                    self.tile.y -= 1
                    self.tile_lock()
        else:
            if y_max > (rows - 1) or encounter_lock_pos:
                self.tile.y -= 1
                self.tile_lock()

    def tile_lock(self):
        self.tile.locked = True
        self.lock_tiles_list = (
            self.tile.pos_and_color
            if self.lock_tiles_list.size == 0
            else np.append(self.lock_tiles_list, self.tile.pos_and_color, axis=0)
        )
        self.get_new_tile()

    def display(self):
        """Display the game window."""
        self.playground.fill((0, 0, 0))
        self.render_grids_and_tiles()
        self.window.blit(self.playground, (tl_x, tl_y))
        pygame.display.update()

    def get_new_tile(self):
        self.tile = Tile()

    def tile_fall(self, fall_speed):
        self.clock.tick()
        self.time += self.clock.get_rawtime()
        if self.time > fall_speed:
            self.time = 0
            self.tile.y += 1

    def render_grids_and_tiles(self):
        # render locked tiles
        if self.lock_tiles_list.size:
            for col, row, color in self.lock_tiles_list:
                pygame.draw.rect(
                    self.playground,
                    color,
                    (col * tile_size, row * tile_size, tile_size, tile_size),
                    0,
                )
        # render current tile
        for col, row, color in self.tile.pos_and_color:
            pygame.draw.rect(
                self.playground,
                color,
                (col * tile_size, row * tile_size, tile_size, tile_size),
                0,
            )

        # render grid lines
        for row in range(1, rows):
            y = tile_size * row
            pygame.draw.line(
                self.playground,
                color=(100, 100, 100),
                start_pos=(0, y),
                end_pos=(play_width, y),
            )
        for col in range(1, cols):
            x = tile_size * col
            pygame.draw.line(
                self.playground,
                color=(100, 100, 100),
                start_pos=(x, 0),
                end_pos=(x, play_height),
            )


    def pause_game(self):
        self.pause = True
        while self.pause:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.run = False
                if event.type == KEYDOWN:
                    key = event.key
                    if key == K_p:
                        self.pause = False
                    if key == K_ESCAPE or key == K_q:
                        self.run = False
                        self.pause = False

    def quit(self):
        pygame.quit()
        sys.exit()

    def trigger_movement(self, func):
        self.control_tick += 1
        if self.control_tick > control_threshold:
            self.control_tick = 0
            func()

    def key_down_detection(self):
        """Detect single key press"""
        if pygame.event.get(QUIT):
            self.run = False
        # for single key down press
        events = pygame.event.get(KEYDOWN)
        for event in events:
            if event.key == K_ESCAPE or event.key == K_q:
                self.run = False
            if event.key == K_p:
                self.pause_game()
            if event.key == K_n:
                self.get_new_tile()
            if event.key in self.tile.event_control_map:
                self.control_tick = 0
                func = self.tile.event_control_map[event.key]
                func()
                return event.key
