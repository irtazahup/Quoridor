import random
from collections import deque


class AI:
    def __init__(self, position, color, walls, grid_size):
        self.position = position
        self.color = color
        self.walls = walls
        self.grid_size = grid_size
        self.search_depth = 2

    def make_move(self, game, player):
        best_move = self.minimax(
            game, player, self.search_depth, float("-inf"), float("inf"), True
        )

        if best_move[0] == "move":
            self.position = list(best_move[1])
            return "move"
        else:
            wall_type, x, y = best_move[1]
            if wall_type == "horizontal":
                game.horizontal_walls.add((x, y))
                game.wall_owners[(x, y)] = "ai"
            else:
                game.vertical_walls.add((x, y))
                game.wall_owners[(x, y)] = "ai"
            self.walls -= 1
            return "wall"

    def minimax(self, game, player, depth, alpha, beta, is_maximizing):
        if depth == 0:
            return ("none", None, self.evaluate_state(game, player))

        if is_maximizing:
            best_score = float("-inf")
            best_move = None
            best_action = None

            for move in game.get_valid_moves(self.position):
                original_position = self.position.copy()
                self.position = [move[0], move[1]]

                _, _, score = self.minimax(game, player, depth - 1, alpha, beta, False)

                self.position = original_position

                if score > best_score:
                    best_score = score
                    best_move = move
                    best_action = "move"

                alpha = max(alpha, best_score)
                if beta <= alpha:
                    break

            if self.walls > 0:
                wall_options = self.get_wall_options(game, player)
                for wall_option in wall_options:
                    wall_type, x, y = wall_option

                    if game.is_valid_wall(wall_type, x, y):
                        if wall_type == "horizontal":
                            game.horizontal_walls.add((x, y))
                        else:
                            game.vertical_walls.add((x, y))

                        self.walls -= 1

                        _, _, score = self.minimax(
                            game, player, depth - 1, alpha, beta, False
                        )

                        if wall_type == "horizontal":
                            game.horizontal_walls.remove((x, y))
                        else:
                            game.vertical_walls.remove((x, y))

                        self.walls += 1

                        if score > best_score:
                            best_score = score
                            best_move = wall_option
                            best_action = "wall"

                        alpha = max(alpha, best_score)
                        if beta <= alpha:
                            break

            return (best_action, best_move, best_score)

        else:
            best_score = float("inf")
            best_move = None
            best_action = None

            for move in game.get_valid_moves(player.position):
                original_position = player.position.copy()
                player.position = [move[0], move[1]]

                _, _, score = self.minimax(game, player, depth - 1, alpha, beta, True)

                player.position = original_position

                if score < best_score:
                    best_score = score
                    best_move = move
                    best_action = "move"

                beta = min(beta, best_score)
                if beta <= alpha:
                    break

            if player.walls > 0:
                wall_options = self.get_wall_options(game, self)
                for wall_option in wall_options:
                    wall_type, x, y = wall_option

                    if game.is_valid_wall(wall_type, x, y):
                        if wall_type == "horizontal":
                            game.horizontal_walls.add((x, y))
                        else:
                            game.vertical_walls.add((x, y))

                        player.walls -= 1

                        _, _, score = self.minimax(
                            game, player, depth - 1, alpha, beta, True
                        )

                        if wall_type == "horizontal":
                            game.horizontal_walls.remove((x, y))
                        else:
                            game.vertical_walls.remove((x, y))

                        player.walls += 1

                        if score < best_score:
                            best_score = score
                            best_move = wall_option
                            best_action = "wall"

                        beta = min(beta, best_score)
                        if beta <= alpha:
                            break

            return (best_action, best_move, best_score)

    def evaluate_state(self, game, player):
        ai_path_length = self.calculate_shortest_path(
            self.position, game.GRID_SIZE - 1, game
        )
        player_path_length = self.calculate_shortest_path(player.position, 0, game)

        if ai_path_length is None:
            return -1000
        if player_path_length is None:
            return 1000

        score = player_path_length - ai_path_length

        score += 0.1 * self.walls - 0.1 * player.walls

        return score

    def calculate_shortest_path(self, position, goal_row, game):
        queue = deque([(tuple(position), 0)])
        visited = set([tuple(position)])

        while queue:
            (x, y), distance = queue.popleft()

            if y == goal_row:
                return distance

            for nx, ny in game.get_valid_moves((x, y)):
                if (nx, ny) not in visited:
                    visited.add((nx, ny))
                    queue.append(((nx, ny), distance + 1))

        return None

    def get_wall_options(self, game, opponent):
        wall_options = []

        current_path = self.find_path(
            opponent.position,
            0 if opponent == game.player else game.GRID_SIZE - 1,
            game,
        )

        if not current_path or len(current_path) < 2:
            return wall_options

        for i in range(1, min(4, len(current_path))):
            prev_x, prev_y = current_path[i - 1]
            x, y = current_path[i]

            dx, dy = x - prev_x, y - prev_y

            if dx == 0:
                if dy < 0:
                    wall_options.append(("horizontal", prev_x, prev_y))
                    if prev_x > 0:
                        wall_options.append(("horizontal", prev_x - 1, prev_y))
                else:
                    wall_options.append(("horizontal", prev_x, prev_y + 1))
                    if prev_x > 0:
                        wall_options.append(("horizontal", prev_x - 1, prev_y + 1))
            else:
                if dx < 0:
                    wall_options.append(("vertical", prev_x, prev_y))
                    if prev_y > 0:
                        wall_options.append(("vertical", prev_x, prev_y - 1))
                else:
                    wall_options.append(("vertical", prev_x + 1, prev_y))
                    if prev_y > 0:
                        wall_options.append(("vertical", prev_x + 1, prev_y - 1))

        for _ in range(5):
            wall_type = random.choice(["horizontal", "vertical"])
            if wall_type == "horizontal":
                x = random.randint(0, game.GRID_SIZE - 2)
                y = random.randint(1, game.GRID_SIZE - 1)
            else:
                x = random.randint(1, game.GRID_SIZE - 1)
                y = random.randint(0, game.GRID_SIZE - 2)
            wall_options.append((wall_type, x, y))

        return wall_options

    def find_path(self, position, goal_row, game):
        queue = deque([(tuple(position), [tuple(position)])])
        visited = set([tuple(position)])

        while queue:
            (x, y), path = queue.popleft()

            if y == goal_row:
                return path

            for nx, ny in game.get_valid_moves((x, y)):
                if (nx, ny) not in visited:
                    visited.add((nx, ny))
                    new_path = path + [(nx, ny)]
                    queue.append(((nx, ny), new_path))

        return None
