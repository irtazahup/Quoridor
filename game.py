import pygame
import os
from collections import deque
from player import Player
from ai import AI


class QuoridorGame:
    def __init__(self):
        pygame.init()

        self.CELL_SIZE = 60
        self.GRID_SIZE = 9
        self.WIDTH = self.HEIGHT = self.CELL_SIZE * self.GRID_SIZE
        self.FPS = 60

        self.WHITE = (255, 255, 255)
        self.GRAY = (200, 200, 200)
        self.BLACK = (0, 0, 0)
        self.GREEN = (76, 187, 23)
        self.BLUE = (0, 121, 241)
        self.RED = (255, 67, 67)
        self.DARK_GREEN = (10, 122, 13)
        self.BACKGROUND = (240, 240, 245)
        self.GRID_COLOR = (180, 180, 190)
        self.PLAYER_WALL_COLOR = (25, 118, 210)
        self.AI_WALL_COLOR = (198, 40, 40)
        self.BUTTON_HIGHLIGHT = (96, 207, 43)

        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT + 60))
        pygame.display.set_caption("Quoridor Game")
        self.clock = pygame.time.Clock()

        self.load_fonts()

        self.horizontal_walls = set()
        self.vertical_walls = set()
        self.wall_owners = {}

        self.player = Player([4, 8], self.BLUE, 10)
        self.ai = AI([4, 0], self.RED, 10, self.GRID_SIZE)

        self.player_turn = True
        self.game_over = False
        self.winner = None
        self.show_start_screen = True
        self.show_end_popup = False

    def load_fonts(self):
        fonts_dir = os.path.join(os.path.dirname(__file__), "fonts")

        if not os.path.exists(fonts_dir):
            os.makedirs(fonts_dir)

        default_font = pygame.font.get_default_font()

        system_fonts = pygame.font.get_fonts()

        preferred_fonts = ["arial", "verdana", "tahoma", "dejavusans"]

        self.font_name = default_font
        for font in preferred_fonts:
            if font in system_fonts:
                self.font_name = font
                break

        self.font = pygame.font.SysFont(self.font_name, 28)
        self.title_font = pygame.font.SysFont(self.font_name, 64, bold=True)
        self.button_font = pygame.font.SysFont(self.font_name, 42, bold=True)
        self.ui_font = pygame.font.SysFont(self.font_name, 24)

    def draw_rounded_rect(
        self, surface, color, rect, radius=15, border=0, border_color=None
    ):
        x, y, width, height = rect

        pygame.draw.rect(surface, color, (x + radius, y, width - 2 * radius, height))
        pygame.draw.rect(surface, color, (x, y + radius, width, height - 2 * radius))

        pygame.draw.circle(surface, color, (x + radius, y + radius), radius)
        pygame.draw.circle(surface, color, (x + width - radius, y + radius), radius)
        pygame.draw.circle(surface, color, (x + radius, y + height - radius), radius)
        pygame.draw.circle(
            surface, color, (x + width - radius, y + height - radius), radius
        )

        if border > 0 and border_color:
            pygame.draw.rect(
                surface,
                border_color,
                (x + radius, y, width - 2 * radius, height),
                border,
            )
            pygame.draw.rect(
                surface,
                border_color,
                (x, y + radius, width, height - 2 * radius),
                border,
            )
            pygame.draw.circle(
                surface, border_color, (x + radius, y + radius), radius, border
            )
            pygame.draw.circle(
                surface, border_color, (x + width - radius, y + radius), radius, border
            )
            pygame.draw.circle(
                surface, border_color, (x + radius, y + height - radius), radius, border
            )
            pygame.draw.circle(
                surface,
                border_color,
                (x + width - radius, y + height - radius),
                radius,
                border,
            )

    def draw_grid(self):
        self.screen.fill(self.BACKGROUND)
        for x in range(0, self.WIDTH, self.CELL_SIZE):
            pygame.draw.line(self.screen, self.GRID_COLOR, (x, 0), (x, self.HEIGHT), 2)
        for y in range(0, self.HEIGHT, self.CELL_SIZE):
            pygame.draw.line(self.screen, self.GRID_COLOR, (0, y), (self.WIDTH, y), 2)

    def draw_players(self):
        x = self.player.position[0] * self.CELL_SIZE
        y = self.player.position[1] * self.CELL_SIZE

        self.draw_rounded_rect(
            self.screen,
            self.player.color,
            (x + 10, y + 10, self.CELL_SIZE - 20, self.CELL_SIZE - 20),
            radius=5,
        )

        x = self.ai.position[0] * self.CELL_SIZE
        y = self.ai.position[1] * self.CELL_SIZE

        self.draw_rounded_rect(
            self.screen,
            self.ai.color,
            (x + 10, y + 10, self.CELL_SIZE - 20, self.CELL_SIZE - 20),
            radius=5,
        )

    def draw_walls(self):
        for x, y in self.horizontal_walls:
            wall_color = (
                self.PLAYER_WALL_COLOR
                if (x, y) in self.wall_owners and self.wall_owners[(x, y)] == "player"
                else self.AI_WALL_COLOR
            )
            pygame.draw.rect(
                self.screen,
                wall_color,
                (
                    x * self.CELL_SIZE + 6,
                    y * self.CELL_SIZE - 4,
                    self.CELL_SIZE * 2 - 10,
                    10,
                ),
            )

        for x, y in self.vertical_walls:
            wall_color = (
                self.PLAYER_WALL_COLOR
                if (x, y) in self.wall_owners and self.wall_owners[(x, y)] == "player"
                else self.AI_WALL_COLOR
            )
            pygame.draw.rect(
                self.screen,
                wall_color,
                (
                    x * self.CELL_SIZE - 4,
                    y * self.CELL_SIZE + 6,
                    10,
                    self.CELL_SIZE * 2 - 10,
                ),
            )

        if self.player_turn:
            mx, my = pygame.mouse.get_pos()
            if my < self.HEIGHT:
                grid_x = mx // self.CELL_SIZE
                grid_y = my // self.CELL_SIZE
                dx = mx % self.CELL_SIZE
                dy = my % self.CELL_SIZE

                hint_color = (120, 120, 140, 150)

                if dy < 20 and grid_y > 0:
                    if self.is_valid_wall("horizontal", grid_x, grid_y):
                        pygame.draw.rect(
                            self.screen,
                            hint_color,
                            (
                                grid_x * self.CELL_SIZE + 6,
                                grid_y * self.CELL_SIZE - 4,
                                self.CELL_SIZE * 2 - 10,
                                10,
                            ),
                            1,
                        )
                elif dy > self.CELL_SIZE - 20 and grid_y < self.GRID_SIZE - 1:
                    if self.is_valid_wall("horizontal", grid_x, grid_y + 1):
                        pygame.draw.rect(
                            self.screen,
                            hint_color,
                            (
                                grid_x * self.CELL_SIZE + 6,
                                (grid_y + 1) * self.CELL_SIZE - 4,
                                self.CELL_SIZE * 2 - 10,
                                10,
                            ),
                            1,
                        )

                elif dx < 20 and grid_x > 0:
                    if self.is_valid_wall("vertical", grid_x, grid_y):
                        pygame.draw.rect(
                            self.screen,
                            hint_color,
                            (
                                grid_x * self.CELL_SIZE - 4,
                                grid_y * self.CELL_SIZE + 6,
                                10,
                                self.CELL_SIZE * 2 - 10,
                            ),
                            1,
                        )
                elif dx > self.CELL_SIZE - 20 and grid_x < self.GRID_SIZE - 1:
                    if self.is_valid_wall("vertical", grid_x + 1, grid_y):
                        pygame.draw.rect(
                            self.screen,
                            hint_color,
                            (
                                (grid_x + 1) * self.CELL_SIZE - 4,
                                grid_y * self.CELL_SIZE + 6,
                                10,
                                self.CELL_SIZE * 2 - 10,
                            ),
                            1,
                        )

    def draw_ui(self):
        pygame.draw.rect(self.screen, self.WHITE, (0, self.HEIGHT, self.WIDTH, 60))
        pygame.draw.line(
            self.screen, self.GRAY, (0, self.HEIGHT), (self.WIDTH, self.HEIGHT), 2
        )

        player_text = self.ui_font.render(
            f"Your Walls: {self.player.walls}", True, self.player.color
        )
        ai_text = self.ui_font.render(f"AI Walls: {self.ai.walls}", True, self.ai.color)

        if not self.game_over:
            turn_text = self.ui_font.render(
                f"{'Your' if self.player_turn else 'AI'} Turn", True, self.GREEN
            )
        else:
            turn_text = self.ui_font.render(f"{self.winner} wins!", True, self.GREEN)

        self.screen.blit(player_text, (20, self.HEIGHT + 20))
        self.screen.blit(ai_text, (200, self.HEIGHT + 20))
        self.screen.blit(turn_text, (400, self.HEIGHT + 20))

    def draw_start_screen(self):
        self.screen.fill(self.BACKGROUND)

        title_shadow = self.title_font.render("QUORIDOR", True, (30, 30, 30))
        title_text = self.title_font.render("QUORIDOR", True, self.DARK_GREEN)
        shadow_rect = title_text.get_rect(
            center=(self.WIDTH // 2 + 3, self.HEIGHT // 3 + 3)
        )
        title_rect = title_text.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 3))
        self.screen.blit(title_shadow, shadow_rect)
        self.screen.blit(title_text, title_rect)

        button_width, button_height = 200, 80
        button_x = self.WIDTH // 2 - button_width // 2
        button_y = self.HEIGHT // 2

        self.draw_rounded_rect(
            self.screen,
            self.GREEN,
            (button_x, button_y, button_width, button_height),
            radius=15,
            border=3,
            border_color=self.BLACK,
        )

        start_text = self.button_font.render("START", True, self.WHITE)
        start_rect = start_text.get_rect(
            center=(self.WIDTH // 2, self.HEIGHT // 2 + button_height // 2)
        )
        self.screen.blit(start_text, start_rect)

        instructions = [
            "Use arrow keys to move your pawn",
            "Click between cells to place walls",
            "Reach the opposite side to win",
            "You have 10 walls to block your opponent",
        ]

        instruction_box_width = 460
        instruction_box_height = 170
        instruction_box_x = self.WIDTH // 2 - instruction_box_width // 2
        instruction_box_y = self.HEIGHT * 2 // 3

        self.draw_rounded_rect(
            self.screen,
            (240, 240, 255),
            (
                instruction_box_x,
                instruction_box_y,
                instruction_box_width,
                instruction_box_height,
            ),
            radius=10,
            border=2,
            border_color=self.GRAY,
        )

        for i, instruction in enumerate(instructions):
            inst_text = self.font.render(instruction, True, self.BLACK)
            inst_rect = inst_text.get_rect(
                center=(self.WIDTH // 2, instruction_box_y + 30 + i * 35)
            )
            self.screen.blit(inst_text, inst_rect)

        return button_x, button_y, button_width, button_height

    def draw_end_popup(self):
        overlay = pygame.Surface((self.WIDTH, self.HEIGHT + 60), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (0, 0))

        popup_width, popup_height = 400, 300
        popup_x = self.WIDTH // 2 - popup_width // 2
        popup_y = self.HEIGHT // 2 - popup_height // 2

        self.draw_rounded_rect(
            self.screen,
            self.WHITE,
            (popup_x, popup_y, popup_width, popup_height),
            radius=20,
            border=3,
            border_color=self.BLACK,
        )

        winner_color = self.BLUE if self.winner == "Player" else self.RED
        winner_shadow = self.title_font.render(
            f"{self.winner} WINS!", True, (30, 30, 30)
        )
        winner_text = self.title_font.render(f"{self.winner} WINS!", True, winner_color)
        shadow_rect = winner_shadow.get_rect(center=(self.WIDTH // 2 + 3, popup_y + 83))
        winner_rect = winner_text.get_rect(center=(self.WIDTH // 2, popup_y + 80))
        self.screen.blit(winner_shadow, shadow_rect)
        self.screen.blit(winner_text, winner_rect)

        button_width, button_height = 270, 80
        button_x = self.WIDTH // 2 - button_width // 2
        button_y = popup_y + popup_height - button_height - 40

        self.draw_rounded_rect(
            self.screen,
            self.GREEN,
            (button_x, button_y, button_width, button_height),
            radius=15,
            border=3,
            border_color=self.BLACK,
        )

        again_text = self.button_font.render("PLAY AGAIN", True, self.WHITE)
        again_rect = again_text.get_rect(
            center=(self.WIDTH // 2, button_y + button_height // 2)
        )
        self.screen.blit(again_text, again_rect)

        return button_x, button_y, button_width, button_height

    def is_valid_wall(self, wall_type, x, y):
        if wall_type == "horizontal":
            if x >= self.GRID_SIZE - 1 or y <= 0 or y >= self.GRID_SIZE:
                return False
        elif wall_type == "vertical":
            if x <= 0 or y >= self.GRID_SIZE - 1 or x >= self.GRID_SIZE:
                return False

        if wall_type == "horizontal" and (x, y) in self.horizontal_walls:
            return False
        if wall_type == "vertical" and (x, y) in self.vertical_walls:
            return False

        if wall_type == "horizontal":
            if (x - 1, y) in self.horizontal_walls or (
                x + 1,
                y,
            ) in self.horizontal_walls:
                return False

            if (x + 1, y - 1) in self.vertical_walls:
                return False

        elif wall_type == "vertical":
            if (x, y - 1) in self.vertical_walls or (x, y + 1) in self.vertical_walls:
                return False

            if (x - 1, y + 1) in self.horizontal_walls:
                return False

        temp_horizontal = self.horizontal_walls.copy()
        temp_vertical = self.vertical_walls.copy()

        if wall_type == "horizontal":
            temp_horizontal.add((x, y))
        else:
            temp_vertical.add((x, y))

        if not self.has_path_to_goal(
            self.player.position, 0, temp_horizontal, temp_vertical
        ) or not self.has_path_to_goal(
            self.ai.position, self.GRID_SIZE - 1, temp_horizontal, temp_vertical
        ):
            return False

        return True

    def place_wall(self, mx, my):
        if self.player.walls <= 0:
            return False

        grid_x = mx // self.CELL_SIZE
        grid_y = my // self.CELL_SIZE
        dx = mx % self.CELL_SIZE
        dy = my % self.CELL_SIZE

        if dy < 20 and grid_y > 0:
            if self.is_valid_wall("horizontal", grid_x, grid_y):
                self.horizontal_walls.add((grid_x, grid_y))
                self.wall_owners[(grid_x, grid_y)] = "player"
                self.player.walls -= 1
                return True
        elif dy > self.CELL_SIZE - 20 and grid_y < self.GRID_SIZE - 1:
            if self.is_valid_wall("horizontal", grid_x, grid_y + 1):
                self.horizontal_walls.add((grid_x, grid_y + 1))
                self.wall_owners[(grid_x, grid_y + 1)] = "player"
                self.player.walls -= 1
                return True
        elif dx < 20 and grid_x > 0:
            if self.is_valid_wall("vertical", grid_x, grid_y):
                self.vertical_walls.add((grid_x, grid_y))
                self.wall_owners[(grid_x, grid_y)] = "player"
                self.player.walls -= 1
                return True
        elif dx > self.CELL_SIZE - 20 and grid_x < self.GRID_SIZE - 1:
            if self.is_valid_wall("vertical", grid_x + 1, grid_y):
                self.vertical_walls.add((grid_x + 1, grid_y))
                self.wall_owners[(grid_x + 1, grid_y)] = "player"
                self.player.walls -= 1
                return True

        return False

    def is_blocked_by_wall(self, current_x, current_y, target_x, target_y):
        dx = target_x - current_x
        dy = target_y - current_y

        if dx == 0 and dy == -1:
            return (current_x, current_y) in self.horizontal_walls or (
                current_x - 1,
                current_y,
            ) in self.horizontal_walls
        elif dx == 1 and dy == 0:
            return (current_x + 1, current_y) in self.vertical_walls or (
                current_x + 1,
                current_y - 1,
            ) in self.vertical_walls
        elif dx == 0 and dy == 1:
            return (current_x, current_y + 1) in self.horizontal_walls or (
                current_x - 1,
                current_y + 1,
            ) in self.horizontal_walls
        elif dx == -1 and dy == 0:
            return (current_x, current_y) in self.vertical_walls or (
                current_x,
                current_y - 1,
            ) in self.vertical_walls

        return False

    def get_valid_moves(self, pos):
        x, y = pos
        moves = []

        directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]
        for dx, dy in directions:
            nx, ny = x + dx, y + dy

            if not (0 <= nx < self.GRID_SIZE and 0 <= ny < self.GRID_SIZE):
                continue

            if self.is_blocked_by_wall(x, y, nx, ny):
                continue

            other_pos = (
                self.ai.position
                if pos == self.player.position
                else self.player.position
            )
            if [nx, ny] == other_pos:
                jx, jy = nx + dx, ny + dy

                if not (0 <= jx < self.GRID_SIZE and 0 <= jy < self.GRID_SIZE):
                    continue

                if self.is_blocked_by_wall(nx, ny, jx, jy):
                    continue

                moves.append((jx, jy))
            else:
                moves.append((nx, ny))

        return moves

    def has_path_to_goal(self, pos, goal_row, h_walls, v_walls):
        queue = deque([tuple(pos)])
        visited = set([tuple(pos)])

        while queue:
            x, y = queue.popleft()

            if goal_row == 0 and y == 0:
                return True
            if goal_row == self.GRID_SIZE - 1 and y == self.GRID_SIZE - 1:
                return True

            for nx, ny in self.get_valid_moves_for_pathfinding(
                (x, y), h_walls, v_walls
            ):
                if (nx, ny) not in visited:
                    visited.add((nx, ny))
                    queue.append((nx, ny))

        return False

    def is_blocked_by_wall_for_pathfinding(
        self, current_x, current_y, target_x, target_y, h_walls, v_walls
    ):
        dx = target_x - current_x
        dy = target_y - current_y

        if dx == 0 and dy == -1:
            return (current_x, current_y) in h_walls or (
                current_x - 1,
                current_y,
            ) in h_walls
        elif dx == 1 and dy == 0:
            return (current_x + 1, current_y) in v_walls or (
                current_x + 1,
                current_y - 1,
            ) in v_walls
        elif dx == 0 and dy == 1:
            return (current_x, current_y + 1) in h_walls or (
                current_x - 1,
                current_y + 1,
            ) in h_walls
        elif dx == -1 and dy == 0:
            return (current_x, current_y) in v_walls or (
                current_x,
                current_y - 1,
            ) in v_walls

        return False

    def get_valid_moves_for_pathfinding(self, pos, h_walls, v_walls):
        x, y = pos
        moves = []

        directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]
        for dx, dy in directions:
            nx, ny = x + dx, y + dy

            if not (0 <= nx < self.GRID_SIZE and 0 <= ny < self.GRID_SIZE):
                continue

            if self.is_blocked_by_wall_for_pathfinding(x, y, nx, ny, h_walls, v_walls):
                continue

            moves.append((nx, ny))

        return moves

    def check_win(self):
        if self.player.position[1] == 0:
            self.game_over = True
            self.winner = "Player"
            self.show_end_popup = True
            return True

        if self.ai.position[1] == self.GRID_SIZE - 1:
            self.game_over = True
            self.winner = "AI"
            self.show_end_popup = True
            return True

        return False

    def reset_game(self):
        self.horizontal_walls = set()
        self.vertical_walls = set()
        self.wall_owners = {}
        self.player.position = [4, 8]
        self.ai.position = [4, 0]
        self.player.walls = 10
        self.ai.walls = 10
        self.player_turn = True
        self.game_over = False
        self.winner = None
        self.show_end_popup = False

    def run_game(self):
        running = True
        while running:
            if self.show_start_screen:
                button_x, button_y, button_width, button_height = (
                    self.draw_start_screen()
                )

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        mx, my = event.pos
                        if (
                            button_x <= mx <= button_x + button_width
                            and button_y <= my <= button_y + button_height
                        ):
                            self.show_start_screen = False
            else:
                self.screen.fill(self.WHITE)
                self.draw_grid()
                self.draw_players()
                self.draw_walls()
                self.draw_ui()

                if self.show_end_popup:
                    button_x, button_y, button_width, button_height = (
                        self.draw_end_popup()
                    )

                if not self.game_over and not self.show_end_popup:
                    self.check_win()

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False

                    if self.show_end_popup:
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            mx, my = event.pos
                            if (
                                button_x <= mx <= button_x + button_width
                                and button_y <= my <= button_y + button_height
                            ):
                                self.reset_game()
                        continue

                    if self.game_over:
                        continue

                    if self.player_turn:
                        if event.type == pygame.KEYDOWN:
                            moved = False

                            if event.key == pygame.K_LEFT:
                                valid_moves = self.get_valid_moves(self.player.position)
                                if (
                                    self.player.position[0] - 1,
                                    self.player.position[1],
                                ) in valid_moves:
                                    self.player.position[0] -= 1
                                    moved = True
                                elif (
                                    self.player.position[0] - 2,
                                    self.player.position[1],
                                ) in valid_moves:
                                    self.player.position[0] -= 2
                                    moved = True

                            elif event.key == pygame.K_RIGHT:
                                valid_moves = self.get_valid_moves(self.player.position)
                                if (
                                    self.player.position[0] + 1,
                                    self.player.position[1],
                                ) in valid_moves:
                                    self.player.position[0] += 1
                                    moved = True
                                elif (
                                    self.player.position[0] + 2,
                                    self.player.position[1],
                                ) in valid_moves:
                                    self.player.position[0] += 2
                                    moved = True

                            elif event.key == pygame.K_UP:
                                valid_moves = self.get_valid_moves(self.player.position)
                                if (
                                    self.player.position[0],
                                    self.player.position[1] - 1,
                                ) in valid_moves:
                                    self.player.position[1] -= 1
                                    moved = True
                                elif (
                                    self.player.position[0],
                                    self.player.position[1] - 2,
                                ) in valid_moves:
                                    self.player.position[1] -= 2
                                    moved = True

                            elif event.key == pygame.K_DOWN:
                                valid_moves = self.get_valid_moves(self.player.position)
                                if (
                                    self.player.position[0],
                                    self.player.position[1] + 1,
                                ) in valid_moves:
                                    self.player.position[1] += 1
                                    moved = True
                                elif (
                                    self.player.position[0],
                                    self.player.position[1] + 2,
                                ) in valid_moves:
                                    self.player.position[1] += 2
                                    moved = True

                            if moved:
                                self.player_turn = False

                        elif event.type == pygame.MOUSEBUTTONDOWN:
                            if event.button == 1:
                                mx, my = event.pos
                                if my < self.HEIGHT:
                                    if self.place_wall(mx, my):
                                        self.player_turn = False
                    else:

                        best_move = self.ai.make_move(self, self.player)

                        if best_move == "wall":
                            for wall in self.horizontal_walls:
                                if wall not in self.wall_owners:
                                    self.wall_owners[wall] = "ai"

                            for wall in self.vertical_walls:
                                if wall not in self.wall_owners:
                                    self.wall_owners[wall] = "ai"

                        self.player_turn = True

            pygame.display.flip()
            self.clock.tick(self.FPS)

        pygame.quit()


if __name__ == "__main__":
    game = QuoridorGame()
    game.run_game()
