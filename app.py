import pygame
import sys

# Initialize Pygame
pygame.init()
horizontal_walls = set()
vertical_walls = set()
placing_horizontal = True  # Toggle later
placing_vertical = False  # Toggle later

# Constants
CELL_SIZE = 60
GRID_SIZE = 9
WIDTH = HEIGHT = CELL_SIZE * GRID_SIZE
FPS = 60

# Colors
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
BLUE = (0, 100, 255)
RED = (255, 0, 0)

# Setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Quoridor Grid")
clock = pygame.time.Clock()

# Player position (grid coordinates)
player1_pos = [4, 0]
player2_pos = [4, 8]


def draw_grid():
    for x in range(0, WIDTH, CELL_SIZE):
        pygame.draw.line(screen, GRAY, (x, 0), (x, HEIGHT), 5)
    for y in range(0, HEIGHT, CELL_SIZE):
        pygame.draw.line(screen, GRAY, (0, y), (WIDTH, y), 5)


def draw_player1():
    x = player1_pos[0] * CELL_SIZE
    y = player1_pos[1] * CELL_SIZE
    pygame.draw.rect(screen, BLUE, (x + 10, y + 10, CELL_SIZE - 20, CELL_SIZE - 20))


def draw_player2():
    x = player2_pos[0] * CELL_SIZE
    y = player2_pos[1] * CELL_SIZE
    pygame.draw.rect(screen, RED, (x + 10, y + 10, CELL_SIZE - 20, CELL_SIZE - 20))


def draw_walls():
    for x, y in horizontal_walls:
        pygame.draw.rect(
            screen, (0, 0, 0), (x * CELL_SIZE, y * CELL_SIZE - 5, CELL_SIZE * 2, 10)
        )
    for x, y in vertical_walls:
        pygame.draw.rect(
            screen, (0, 0, 0), (x * CELL_SIZE - 5, y * CELL_SIZE, 10, CELL_SIZE * 2)
        )


# Check where the mouse click is and decide on wall placement
def place_wall(grid_x, grid_y, dx, dy):
    if dy < dx and dy < CELL_SIZE - dx:
        # Place horizontal wall on the top edge
        if grid_y > 0:  # Ensure not going out of bounds
            horizontal_walls.add((grid_x, grid_y - 1))
    elif dy > dx and dy > CELL_SIZE - dx:
        # Place horizontal wall on the bottom edge
        if grid_y < GRID_SIZE - 1:  # Ensure not going out of bounds
            horizontal_walls.add((grid_x, grid_y))
    elif dx < dy and dx < CELL_SIZE - dy:
        # Place vertical wall on the left edge
        if grid_x > 0:  # Ensure not going out of bounds
            vertical_walls.add((grid_x - 1, grid_y))
    else:
        # Place vertical wall on the right edge
        if grid_x < GRID_SIZE - 1:  # Ensure not going out of bounds
            vertical_walls.add((grid_x, grid_y))


# Main loop
while True:
    screen.fill(WHITE)
    draw_grid()
    draw_player1()
    draw_player2()
    draw_walls()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        elif event.type == pygame.KEYDOWN:
            # PLAYER 1 CONTROLS
            if event.key == pygame.K_LEFT:
                if (
                    player1_pos[0] - 1 == player2_pos[0]
                    and player1_pos[1] == player2_pos[1]
                ):
                    if player2_pos[0] - 1 >= 0:
                        player1_pos[0] -= 2  # jump over
                elif player1_pos[0] > 0:
                    player1_pos[0] -= 1

            elif event.key == pygame.K_RIGHT:
                if (
                    player1_pos[0] + 1 == player2_pos[0]
                    and player1_pos[1] == player2_pos[1]
                ):
                    if player2_pos[0] + 1 < GRID_SIZE:
                        player1_pos[0] += 2  # jump over
                elif player1_pos[0] < GRID_SIZE - 1:
                    player1_pos[0] += 1

            elif event.key == pygame.K_UP:
                if (
                    player1_pos[1] - 1 == player2_pos[1]
                    and player1_pos[0] == player2_pos[0]
                ):
                    if player2_pos[1] - 1 >= 0:
                        player1_pos[1] -= 2  # jump over
                elif player1_pos[1] > 0:
                    player1_pos[1] -= 1

            elif event.key == pygame.K_DOWN:
                if (
                    player1_pos[1] + 1 == player2_pos[1]
                    and player1_pos[0] == player2_pos[0]
                ):
                    if player2_pos[1] + 1 < GRID_SIZE:
                        player1_pos[1] += 2  # jump over
                elif player1_pos[1] < GRID_SIZE - 1:
                    player1_pos[1] += 1

            # PLAYER 2 CONTROLS (WASD)
            if event.key == pygame.K_a:
                if (
                    player2_pos[0] - 1 == player1_pos[0]
                    and player2_pos[1] == player1_pos[1]
                ):
                    if player1_pos[0] - 1 >= 0:
                        player2_pos[0] -= 2
                elif player2_pos[0] > 0:
                    player2_pos[0] -= 1

            elif event.key == pygame.K_d:
                if (
                    player2_pos[0] + 1 == player1_pos[0]
                    and player2_pos[1] == player1_pos[1]
                ):
                    if player1_pos[0] + 1 < GRID_SIZE:
                        player2_pos[0] += 2
                elif player2_pos[0] < GRID_SIZE - 1:
                    player2_pos[0] += 1

            elif event.key == pygame.K_w:
                if (
                    player2_pos[1] - 1 == player1_pos[1]
                    and player2_pos[0] == player1_pos[0]
                ):
                    if player1_pos[1] - 1 >= 0:
                        player2_pos[1] -= 2
                elif player2_pos[1] > 0:
                    player2_pos[1] -= 1

            elif event.key == pygame.K_s:
                if (
                    player2_pos[1] + 1 == player1_pos[1]
                    and player2_pos[0] == player1_pos[0]
                ):
                    if player1_pos[1] + 1 < GRID_SIZE:
                        player2_pos[1] += 2
                elif player2_pos[1] < GRID_SIZE - 1:
                    player2_pos[1] += 1

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            grid_x = mx // CELL_SIZE
            grid_y = my // CELL_SIZE

    # Get remainder within the cell
            dx = mx % CELL_SIZE
            dy = my % CELL_SIZE

            place_wall(grid_x, grid_y, dx, dy)

    pygame.display.flip()
    clock.tick(FPS)
