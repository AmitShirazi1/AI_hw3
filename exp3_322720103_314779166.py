IDS = ["322720103", "314779166"]
from simulator import Simulator
import random
import math
from sample_agent import Agent
from itertools import product
from copy import deepcopy
from time import time



class Agent:
    def __init__(self, initial_state, player_number):
        self.ids = IDS
        self.player_number = player_number
        self.my_ships = []
        self.simulator = Simulator(initial_state)
        for ship_name, ship in initial_state['pirate_ships'].items():
            if ship['player'] == player_number:
                self.my_ships.append(ship_name)
        print("number of ships: ", len(self.my_ships))

    def act(self, state):
        pass


class UCTNode:
    """
    A class for a single node. not mandatory to use but may help you.
    """
    def __init__(self):
        self.parent = None
        self.action = None
        self.children = []
        self.wins = 0
        self.visits = 0
        self.player_number = 0
    
    def select_using_uct(self):
        if self.visits == 0:
            return float('inf')
        return self.wins / self.visits + (2 * math.log(self.parent.visits) / self.visits) ** 0.5
    
    def update_node(self, result):
        self.visits += 1
        is_winner = result['player '+str(self.player_number)] > result['player '+str(3 - self.player_number)]
        if is_winner > 0:
            self.wins += 1


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
        self.my_ships = list()
        self.rival_ships = list()
        self.simulator = Simulator(initial_state)
        self.agent = Agent(initial_state, player_number)
        for ship_name, ship in initial_state['pirate_ships'].items():
            if ship['player'] == player_number:
                self.my_ships.append(ship_name)
            else:
                self.rival_ships.append(ship_name)

    def selection(self, root):
        curr_node = root
        while curr_node.children:
            max_uct_value = float('-inf')
            max_uct_children = []
            for child in curr_node.children:
                uct_value = child.select_using_uct()
                if uct_value > max_uct_value:
                    max_uct_value = uct_value
                    max_uct_children = [child]
                elif uct_value == max_uct_value:
                    max_uct_children.append(child)
            curr_node = random.choice(max_uct_children)
            # TODO: Maybe keep expanding (building) tree if init is not enough
        return curr_node
    

    def get_legal_actions(self, state, player_number):
        actions = {}
        collected_treasures = []
        ships = self.my_ships if player_number == self.player_number else self.rival_ships
        for ship in ships:
            actions[ship] = set()
            neighboring_tiles = self.simulator.neighbors(state["pirate_ships"][ship]["location"])
            for tile in neighboring_tiles:
                actions[ship].add(("sail", ship, tile))
            if state["pirate_ships"][ship]["capacity"] > 0:
                for treasure in state["treasures"].keys():
                    if state["pirate_ships"][ship]["location"] in self.simulator.neighbors(state["treasures"][treasure]["location"])\
                        and treasure not in collected_treasures:
                        actions[ship].add(("collect", ship, treasure))
                        collected_treasures.append(treasure)
            for treasure in state["treasures"].keys():
                if (state["pirate_ships"][ship]["location"] == state["base"]
                        and state["treasures"][treasure]["location"] == ship):
                    actions[ship].add(("deposit", ship, treasure))
            for enemy_ship_name in state["pirate_ships"].keys():
                if (state["pirate_ships"][ship]["location"] == state["pirate_ships"][enemy_ship_name]["location"] and
                        self.player_number != state["pirate_ships"][enemy_ship_name]["player"]):
                    actions[ship].add(("plunder", ship, enemy_ship_name))
            actions[ship].add(("wait", ship))
        return list(product(*actions.values()))

        
    # def expansion(self, UCT_tree, parent_node):
    def expansion(self, state, parent_node):
        for action in self.get_legal_actions(state, parent_node.player_number):
            new_node = UCTNode()
            new_node.parent = parent_node
            new_node.action = action
            new_node.player_number = 3 - parent_node.player_number
            parent_node.children.append(new_node)
        return random.choice(parent_node.children)
    
    # before calling simulation we will make a deep copy of the simulator so we won't change the original simulator

    def simulation(self, node, turns_to_go, simulator):
        if turns_to_go == 0:
            return simulator.get_score()  # Score is a dictionary with player 1 and player 2 scores.
        if node.children:
            child_node = random.choice(node.children)
        else:
            child_node = self.expansion(simulator.state, node)
        simulator.act(child_node.action, node.player_number)
        return self.simulation(child_node, (turns_to_go - 1), simulator)


    def backpropagation(self, node, simulation_result):
        while node is not None:
            node.update_node(simulation_result)
            node = node.parent


    def act(self, state):
        start_time = time()
        root = UCTNode()
        root.player_number = self.player_number
        while time() - start_time < 4.5:
            node = self.selection(root)
            if self.simulator.turns_to_go == 0:
                self.backpropagation(node, self.simulator.get_score())
            else:
                self.expansion(state, node)
                simulation_result = self.simulation(node, self.simulator.turns_to_go, Simulator(state))
                self.backpropagation(node, simulation_result)
        child = max(root.children, key=lambda child: child.wins / child.visits if child.visits else float("inf"))  # No exploration
        print("---------Choosing my action---------")
        print(child.action)
        return child.action

