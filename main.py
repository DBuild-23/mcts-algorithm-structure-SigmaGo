import copy
import random

import numpy as np


def ucb1(node, exploration_weight=1.41):
    """
    Upper Confidence Bound for Trees (UCB1) formula.
    """
    return (node.wins / node.visits) + exploration_weight * np.sqrt(np.log(node.parent.visits) / node.visits)


class Node:
    def __init__(self, state, parent=None):
        self.state = state
        self.parent = parent
        self.children = []
        self.wins = 0
        self.visits = 0

    def is_fully_expanded(self):
        """
        Check if all possible moves from the current state have been explored.
        """
        legal_moves = self.state.get_legal_moves()
        return len(self.children) == len(legal_moves)

    def best_child(self, exploration_weight=1.41):
        """
        Select the best child node based on the UCB1 formula.
        """
        choices_weights = [ucb1(child, exploration_weight) for child in self.children]
        return self.children[np.argmax(choices_weights)]


def random_policy(state):
    """
    Simulation policy that chooses random moves until the game reaches a terminal state.
    """
    while not state.is_terminal():
        legal_moves = state.get_legal_moves()
        move = random.choice(legal_moves)
        state.play(move)
    return state.get_result()


class MCTS:
    def __init__(self, game, n_simulations):
        self.game = game
        self.n_simulations = n_simulations

    def search(self, initial_state):
        root = Node(initial_state)
        for _ in range(self.n_simulations):
            node = self._select(root)
            if not self.game.is_terminal(node.state):
                node = self._expand(node)
            result = random_policy(node.state)
            self._backpropagate(node, result)
        return root.best_child(exploration_weight=0)

    def _select(self, node):
        while not self.game.is_terminal(node.state) and node.is_fully_expanded():
            node = node.best_child()
        return node

    def _expand(self, node):
        legal_moves = node.state.get_legal_moves()
        for move in legal_moves:
            if move not in [child.state for child in node.children]:
                new_state = copy.deepcopy(node.state)
                new_state.play(move)
                new_node = Node(new_state, node)
                node.children.append(new_node)
                return new_node
        return node

    def _backpropagate(self, node, result):
        while node is not None:
            node.visits += 1
            if node.state.current_player == result:
                node.wins += 1
            node = node.parent


class GoGame:
    def __init__(self, board_size):
        self.board_size = board_size
        self.board = np.zeros((board_size, board_size))
        self.current_player = 1

    def get_legal_moves(self):
        legal_moves = []
        for x in range(self.board_size):
            for y in range(self.board_size):
                if self.board[x][y] == 0:
                    legal_moves.append((x, y))
        return legal_moves

    def play(self, move):
        x, y = move
        self.board[x][y] = self.current_player
        self.current_player = 3 - self.current_player

    def is_terminal(self, state):
        return len(state.get_legal_moves()) == 0

    def get_result(self, state):
        return 1 if np.sum(state.board) > 0 else 2


# Example usage
game = GoGame(board_size=9)
mcts = MCTS(game, n_simulations=1000)
initial_state = game
best_move = mcts.search(initial_state)
print(f"Best Move: {best_move.state.board}")
