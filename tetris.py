import sys
import random
import pygame

# Board configuration
GRID_WIDTH = 10
GRID_HEIGHT = 20
BLOCK_SIZE = 32  # pixels
PLAY_WIDTH = GRID_WIDTH * BLOCK_SIZE
PLAY_HEIGHT = GRID_HEIGHT * BLOCK_SIZE
SIDE_PANEL = 180
WINDOW_WIDTH = PLAY_WIDTH + SIDE_PANEL
WINDOW_HEIGHT = PLAY_HEIGHT

# RGB colors
BLACK = (10, 10, 10)
GRAY = (40, 40, 40)
WHITE = (240, 240, 240)
COLORS = [
    (0, 240, 240),   # I
    (0, 240, 0),     # O
    (240, 160, 0),   # L
    (0, 0, 240),     # J
    (240, 0, 240),   # T
    (240, 0, 0),     # Z
    (0, 240, 240),   # S (reuse cyan to stay bright)
]

# Shape layouts (lists of rotation states)
SHAPES = [
    [[".....",
      ".....",
      "1111.",
      ".....",
      "....."],
     ["..1..",
      "..1..",
      "..1..",
      "..1..",
      "....."]],

    [[".....",
      ".....",
      ".11..",
      ".11..",
      "....."]],

    [[".....",
      ".1...",
      ".111.",
      ".....",
      "....."],
     [".....",
      "..11.",
      "..1..",
      "..1..",
      "....."],
     [".....",
      ".....",
      ".111.",
      "...1.",
      "....."],
     [".....",
      "..1..",
      "..1..",
      ".11..",
      "....."]],

    [[".....",
      "...1.",
      ".111.",
      ".....",
      "....."],
     [".....",
      "..1..",
      "..1..",
      "..11.",
      "....."],
     [".....",
      ".....",
      ".111.",
      ".1...",
      "....."],
     [".....",
      ".11..",
      "..1..",
      "..1..",
      "....."]],

    [[".....",
      "..1..",
      ".111.",
      ".....",
      "....."],
     [".....",
      "..1..",
      "..11.",
      "..1..",
      "....."],
     [".....",
      ".....",
      ".111.",
      "..1..",
      "....."],
     [".....",
      "..1..",
      ".11..",
      "..1..",
      "....."]],

    [[".....",
      ".11..",
      "..11.",
      ".....",
      "....."],
     [".....",
      "..1..",
      ".11..",
      ".1...",
      "....."]],

    [[".....",
      "..11.",
      ".11..",
      ".....",
      "....."],
     [".....",
      ".1...",
      ".11..",
      "..1..",
      "....."]],
]


class Piece:
    def __init__(self, x, y, shape_index):
        self.x = x
        self.y = y
        self.shape_index = shape_index
        self.rotation = 0

    @property
    def shape(self):
        return SHAPES[self.shape_index][self.rotation % len(SHAPES[self.shape_index])]

    @property
    def color(self):
        return COLORS[self.shape_index % len(COLORS)]


def create_grid(locked_positions):
    grid = [[BLACK for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    for (x, y), color in locked_positions.items():
        if 0 <= y < GRID_HEIGHT and 0 <= x < GRID_WIDTH:
            grid[y][x] = color
    return grid


def convert_shape_format(piece):
    positions = []
    layout = piece.shape
    for i, row in enumerate(layout):
        for j, cell in enumerate(row):
            if cell == "1":
                # Offset less on Y so the new piece starts fully visible on screen
                positions.append((piece.x + j - 2, piece.y + i - 2))
    return positions


def valid_space(piece, grid):
    # Allow pieces to spawn partially above the visible board (y < 0), only block collisions inside bounds
    formatted = convert_shape_format(piece)
    for x, y in formatted:
        if x < 0 or x >= GRID_WIDTH or y >= GRID_HEIGHT:
            return False
        if y >= 0 and grid[y][x] != BLACK:
            return False
    return True


def check_lost(locked_positions):
    return any(y < 1 for (_, y) in locked_positions)


def get_shape():
    return Piece(GRID_WIDTH // 2 - 1, 0, random.randrange(len(SHAPES)))


def clear_rows(grid, locked_positions):
    cleared = 0
    for y in range(GRID_HEIGHT - 1, -1, -1):
        if BLACK not in grid[y]:
            cleared += 1
            for x in range(GRID_WIDTH):
                locked_positions.pop((x, y), None)
            for yy in sorted([pos_y for (_, pos_y) in locked_positions if pos_y < y], reverse=True):
                for x in range(GRID_WIDTH):
                    if (x, yy) in locked_positions:
                        locked_positions[(x, yy + 1)] = locked_positions.pop((x, yy))
    return cleared


def draw_grid(surface):
    for i in range(GRID_HEIGHT + 1):
        pygame.draw.line(surface, GRAY, (0, i * BLOCK_SIZE), (PLAY_WIDTH, i * BLOCK_SIZE))
    for j in range(GRID_WIDTH + 1):
        pygame.draw.line(surface, GRAY, (j * BLOCK_SIZE, 0), (j * BLOCK_SIZE, PLAY_HEIGHT))


def draw_next_shape(surface, next_piece, font):
    label = font.render("NEXT", True, WHITE)
    sx = PLAY_WIDTH + 20
    sy = 40
    surface.blit(label, (sx, sy))
    layout = next_piece.shape
    for i, row in enumerate(layout):
        for j, cell in enumerate(row):
            if cell == "1":
                pygame.draw.rect(
                    surface,
                    next_piece.color,
                    pygame.Rect(sx + j * BLOCK_SIZE // 2, sy + 30 + i * BLOCK_SIZE // 2, BLOCK_SIZE // 2, BLOCK_SIZE // 2),
                )


def draw_score(surface, score, font):
    label = font.render(f"Score: {score}", True, WHITE)
    surface.blit(label, (PLAY_WIDTH + 20, WINDOW_HEIGHT - 60))


def draw_window(surface, grid, score, next_piece, font):
    surface.fill(BLACK)
    pygame.draw.rect(surface, GRAY, pygame.Rect(0, 0, PLAY_WIDTH, PLAY_HEIGHT), width=3)

    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            pygame.draw.rect(
                surface,
                grid[y][x],
                pygame.Rect(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE),
            )

    draw_grid(surface)
    draw_next_shape(surface, next_piece, font)
    draw_score(surface, score, font)


def animate_row_clear(surface, grid, rows, score, next_piece, font):
    # Simple flash animation on rows being cleared
    for _ in range(3):
        draw_window(surface, grid, score, next_piece, font)
        for y in rows:
            pygame.draw.rect(
                surface,
                (255, 255, 255),
                pygame.Rect(0, y * BLOCK_SIZE, PLAY_WIDTH, BLOCK_SIZE),
                width=0,
            )
        pygame.display.update()
        pygame.time.delay(80)
        pygame.event.pump()


def hard_drop(piece, grid, locked):
    while valid_space(piece, grid):
        piece.y += 1
    piece.y -= 1
    for x, y in convert_shape_format(piece):
        if y >= 0:
            locked[(x, y)] = piece.color


def run_game():
    pygame.init()
    pygame.key.set_repeat(120, 80)  # allow holding arrow keys for continuous movement
    surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Tetris - Python")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("arial", 22)
    big_font = pygame.font.SysFont("arial", 36)

    locked_positions = {}
    grid = create_grid(locked_positions)

    change_piece = False
    run = True
    current_piece = get_shape()
    next_piece = get_shape()
    fall_time = 0
    fall_speed = 0.5
    score = 0

    while run:
        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime()
        clock.tick()

        if fall_time / 1000 >= fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not valid_space(current_piece, grid):
                current_piece.y -= 1
                change_piece = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not valid_space(current_piece, grid):
                        current_piece.x += 1
                elif event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if not valid_space(current_piece, grid):
                        current_piece.x -= 1
                elif event.key == pygame.K_DOWN:
                    current_piece.y += 1
                    if not valid_space(current_piece, grid):
                        current_piece.y -= 1
                elif event.key == pygame.K_UP:
                    if getattr(event, "repeat", False):
                        continue  # avoid double-rotating on key repeat
                    current_piece.rotation = (current_piece.rotation - 1) % len(SHAPES[current_piece.shape_index])
                    if not valid_space(current_piece, grid):
                        current_piece.rotation = (current_piece.rotation + 1) % len(SHAPES[current_piece.shape_index])
                elif event.key == pygame.K_SPACE:
                    hard_drop(current_piece, grid, locked_positions)
                    change_piece = True

        shape_positions = convert_shape_format(current_piece)
        for x, y in shape_positions:
            if y >= 0:
                grid[y][x] = current_piece.color

        if change_piece:
            for x, y in shape_positions:
                if y >= 0:
                    locked_positions[(x, y)] = current_piece.color
            grid = create_grid(locked_positions)
            full_rows = [y for y in range(GRID_HEIGHT) if BLACK not in grid[y]]
            if full_rows:
                animate_row_clear(surface, grid, full_rows, score, next_piece, font)
            cleared = clear_rows(grid, locked_positions)
            if cleared:
                score += cleared * 100
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False
            if check_lost(locked_positions):
                run = False

        draw_window(surface, grid, score, next_piece, font)
        pygame.display.update()

    surface.fill(BLACK)
    label = big_font.render("Game Over - Press R", True, WHITE)
    surface.blit(label, (PLAY_WIDTH // 2 - label.get_width() // 2, PLAY_HEIGHT // 2 - label.get_height() // 2))
    pygame.display.update()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                waiting = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    run_game()
                elif event.key == pygame.K_ESCAPE:
                    waiting = False

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    try:
        run_game()
    except pygame.error as exc:
        print("Failed to start pygame. Try installing it with: pip install pygame")
        raise exc
