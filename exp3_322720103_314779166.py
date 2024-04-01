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
        actions = {}
        self.simulator.set_state(state)
        collected_treasures = []
        for ship in self.my_ships:
            actions[ship] = set()
            neighboring_tiles = self.simulator.neighbors(state["pirate_ships"][ship]["location"])
            for tile in neighboring_tiles:
                actions[ship].add(("sail", ship, tile))
            if state["pirate_ships"][ship]["capacity"] > 0:
                for treasure in state["treasures"].keys():
                    if state["pirate_ships"][ship]["location"] in self.simulator.neighbors(
                            state["treasures"][treasure]["location"]) and treasure not in collected_treasures:
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

        while True:
            whole_action = []
            for pirate_ship, atomic_actions in actions.items():
                for action in atomic_actions:
                    if action[0] == "deposit":
                        whole_action.append(action)
                        break
                    if action[0] == "collect":
                        whole_action.append(action)
                        break
                else:
                    whole_action.append(self.our_heuristic(list(atomic_actions), pirate_ship, state))
            whole_action = tuple(whole_action)
            if self.simulator.check_if_action_legal(whole_action, self.player_number):
                return whole_action


    def our_heuristic(self, actions, pirate_ship, state):
        # TODO: we need to go through all this function so in the end for each pirate ship we will decide on best action
        """ Summing the minimum distances from each treasure to the base (using Manhattan Distance),
        and dividing by the number of pirates. """
        num_pirates = len(self.my_ships)

        # A list of the minimum distances from each treasure to the base.
        # Initialized with infinity values (so that the distance of an unreachable treasure will be infinity) and updated with the actual distances.
        min_distances_to_base = [float('inf')] * len(state["treasures"].keys())
        max_reward = [0] * len(state["treasures"].keys())
        scores = [0] * len(state["treasures"].keys())
        base_location = state["base"]
        pirate_location = state["pirate_ships"][pirate_ship]["location"]
        for t, t_info in enumerate(state["treasures"].values()):
            treasure_location = t_info["location"]
            treasure_reward = t_info["value"]
            #For each direction, check if there is an adjacent sea cell in this direction and if so, update the distance from this adjacent cell to the base - but only if it's shorter than the current distance.
            for direction, index in zip(['u', 'd', 'l', 'r'], [(-1,0), (1,0), (0,-1), (0,1)]):
                x = treasure_location[0] + index[0]  # The x coordinate of the adjacent cell.
                y = treasure_location[1] + index[1]  # The y coordinate of the adjacent cell.
                if (0 <= x < self.len_rows) and (0 <= y < self.len_cols):
                    if state["map"][x][y] != "I":  # If the adjacent cell is sea.
                        temp_dist = abs(base_location[0]-x) + abs(base_location[1]-y)  # The L1-distance from the adjacent cell to the base (Manhattan Distance).
                        temo_dist += abs(pirate_location[0]-x) + abs(pirate_location[1]-y)

                        # Update the distance from the treasure to the base if the new distance is shorter.
                        if temp_dist < min_distances_to_base[t]:
                            min_distances_to_base[t] = temp_dist
                
            max_reward[t] = treasure_reward
            scores[t] = max_reward[t] / min_distances_to_base[t]
            

            scores.append(



        # return sum(min_distances_to_base) / num_pirates


        

class UCTNode:
    """
    A class for a single node. not mandatory to use but may help you.
    """
    def __init__(self, parent=None, action=None, player_number=0):
        self.parent = parent
        self.action = action
        self.player_number = player_number
        self.children = list()
        self.wins = 0
        self.visits = 0
    
    def select_using_uct(self):
        if self.visits == 0:
            return float('inf')
        return self.wins / self.visits + (2 * math.log(self.parent.visits) / self.visits) ** 0.5
    
    def update_node(self, result):
        self.visits += 1
        is_winner = result['player '+str(self.player_number)] > result['player '+str(3 - self.player_number)]
        if is_winner > 0:
            self.wins += 1

# class UCTTree:
#     """
#     A class for a Tree. not mandatory to use but may help you.
#     """
#     def __init__(self):
#         raise NotImplementedError

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
            new_node = UCTNode(parent_node, action, 3 - parent_node.player_number)
            parent_node.children.append(new_node)
        return random.choice(parent_node.children)

    def simulation(self, node, turns_to_go, simulator):
        if turns_to_go == 0:
            return simulator.get_score()  # Score is a dictionary with player 1 and player 2 scores.
        if node.children:
            treasures = self.simulator.state["treasures"].keys()
            children_nodes = list()
            for child in node.children:
                flag = False
                for atomic_action in child.action:
                    if ((atomic_action[0] == "collect") and (atomic_action[2] not in treasures)):
                        flag = True
                        break
                if not flag:
                    children_nodes.append(child)
            child_node = random.choice(children_nodes)
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
        root = UCTNode(player_number=self.player_number)

        while time() - start_time < 4.2:
            node = self.selection(root)
            if self.simulator.turns_to_go == 0:
                self.backpropagation(node, self.simulator.get_score())
            else:
                self.expansion(state, node)
                simulation_result = self.simulation(node, self.simulator.turns_to_go, Simulator(state))
                self.backpropagation(node, simulation_result)

        child = max(root.children, key=lambda child: child.wins / child.visits if child.visits else float("inf"))  # No exploration
        return child.action

