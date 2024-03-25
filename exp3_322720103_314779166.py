IDS = ["322720103", "314779166"]
from simulator import Simulator
import random
import math


class Agent:
    def __init__(self, initial_state, player_number):
        self.ids = IDS
        self.player_number = player_number
        self.my_ships = []
        self.simulator = Simulator(initial_state)
        for ship_name, ship in initial_state['pirate_ships'].items():
            if ship['player'] == player_number:
                self.my_ships.append(ship_name)

    def act(self, state):
        raise NotImplementedError


class UCTNode:
    """
    A class for a single node. not mandatory to use but may help you.
    """
    def __init__(self):
        self.parent = None
        self.children = []
        self.successes = 0
        self.visits = 0
    
    def select_using_uct(self):
        if self.visits == 0:
            return float('inf')
        return self.successes / self.visits + (2 * math.log(self.parent.visits) / self.visits) ** 0.5


class UCTTree:
    """
    A class for a Tree. not mandatory to use but may help you.
    """
    def __init__(self):
        raise NotImplementedError


class UCTAgent:
    def __init__(self, initial_state, player_number):
        self.ids = IDS
        self.player_number = player_number
        self.my_ships = []
        self.simulator = Simulator(initial_state)
        for ship_name, ship in initial_state['pirate_ships'].items():
            if ship['player'] == player_number:
                self.my_ships.append(ship_name)

    # def selection(self, UCT_tree):
    def selection(self, node):
        curr_node = node
        while len(curr_node.children) > 0:
            curr_node = max(curr_node.children, key=lambda x: x.select_using_uct())
        return curr_node

    def is_deposit_action_legal(deposit_action, player):
        pirate_name = deposit_action[1]
        treasure_name = deposit_action[2]
        # check same position
        if player != self.state['pirate_ships'][pirate_name]['player']:
            return False
        if self.state["pirate_ships"][pirate_name]["location"] != self.base_location:
            return False
        if self.state['treasures'][treasure_name]['location'] != pirate_name:
            return False
        return True

    def is_plunder_action_legal(plunder_action, player):
        pirate_1_name = plunder_action[1]
        pirate_2_name = plunder_action[2]
        if player != self.state["pirate_ships"][pirate_1_name]["player"]:
            return False
        if self.state["pirate_ships"][pirate_1_name]["location"] != self.state["pirate_ships"][pirate_2_name]["location"]:
            return False
        return True

    def get_legal_actions(self, node):
        legal_actions = []
        state = self.simulator.get_state()
        for ship in self.my_ships:
            neighboring_tiles = self.simulator.neighbors(state["pirate_ships"][ship]["location"])
            for tile in neighboring_tiles:
                legal_actions.append(("sail", ship, tile))
            if state["pirate_ships"][ship]["capacity"] > 0:
                for treasure in state["treasures"].keys():
                    if state["pirate_ships"][ship]["location"] in self.simulator.neighbors(state["treasures"][treasure]["location"]):
                        legal_actions.append(("collect", ship, treasure))
                for treasure in state["treasures"].keys():
                    if state["pirate_ships"][ship]["location"] == state["base"] and \
                            state["treasures"][treasure]["location"] == ship:
                        legal_actions.append(("deposit", ship, treasure))
                for enemy_ship_name in state["pirate_ships"].keys():
                    if state["pirate_ships"][ship]["location"] == state["pirate_ships"][enemy_ship_name]["location"] and \
                            self.player_number != state["pirate_ships"][enemy_ship_name]["player"]:
                        legal_actions.append(("plunder", ship, enemy_ship_name))
                legal_actions.append(("wait", ship))
        return legal_actions

    # def expansion(self, UCT_tree, parent_node):
    def expansion(self, node, parent_node):
        for action in self.get_legal_actions(node):
            # TODO: create a get_actions function, and then call act.
            new_node = UCTNode()
            new_node.parent = parent_node
            parent_node.children.append(new_node)

    def simulation(self):
        raise NotImplementedError

    def backpropagation(self, simulation_result):
        raise NotImplementedError

    def act(self, state):
        raise NotImplementedError
