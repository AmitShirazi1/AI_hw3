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
        self.rival_ships = list()
        self.simulator = Simulator(initial_state)
        # Saving the ships of the player and the rival player.
        for ship_name, ship in initial_state['pirate_ships'].items():
            if ship['player'] == player_number:
                self.my_ships.append(ship_name)
            else:
                self.rival_ships.append(ship_name)


    def act(self, state):
        collected_treasures = []
        whole_action = list()  # A list that holds the action we choose for each of our pirate ships.

        for ship in self.my_ships:  # For each pirate ship of our player, we will choose an action.
            found_action = False

            # If the ship is in the base and has treasures, we will deposit them.
            for treasure in state["treasures"].keys():
                if (state["pirate_ships"][ship]["location"] == state["base"]
                        and state["treasures"][treasure]["location"] == ship):
                    whole_action.append(("deposit", ship, treasure))
                    found_action = True
                    break
            if found_action:
                continue

            # If the ship is adjacent to a treasure, we will collect it.
            if state["pirate_ships"][ship]["capacity"] > 0:
                for treasure in state["treasures"].keys():
                    if state["pirate_ships"][ship]["location"] in self.simulator.neighbors(
                            state["treasures"][treasure]["location"]) and treasure not in collected_treasures:
                        whole_action.append(("collect", ship, treasure))
                        collected_treasures.append(treasure)
                        found_action = True
                        break
            if found_action:
                continue
            
            # If the ship is in the same location as an enemy ship, we will plunder it.
            for enemy_ship_name in self.rival_ships:
                if (state["pirate_ships"][ship]["location"] == state["pirate_ships"][enemy_ship_name]["location"] and
                        self.player_number != state["pirate_ships"][enemy_ship_name]["player"]):
                    if state["pirate_ships"][enemy_ship_name]["capacity"] < 2:
                        whole_action.append(("plunder", ship, enemy_ship_name))
                        found_action = True
                        break
            if found_action:
                continue

            # If we didn't choose any of our "favourite" actions above,
            # we move on to check other actions this pirate ship can make - 'sail' or 'wait'.
            whole_action.append(self.choose_sail_action(ship, state))
        return tuple(whole_action)  # Returning the chosen actions for all of our pirate ships in a tuple format.


    def marine_location(self, state):
        """ Returns a list of the current locations of the marine ships. """
        marine_locations = []
        for marine_stats in state["marine_ships"].values():
            index = marine_stats["index"]
            marine_locations.append(marine_stats["path"][index])
        return marine_locations

    def collision_with_marine(self, location, marine_locations):
        """ Returns True if the location we want to sail to currently has a marine ship, otherwise False. """
        if location in marine_locations:
            return True
        else:
            return False

    def choose_sail_action(self, pirate_ship, state):
        """ Returns the action we choose for a specific pirate ship - sail or wait.
            Choosing the action is based on the distance from the pirate ship to the base and the treasures,
            the reward we can get from each treasure,
            and the locations of the marine ships.
        """
        my_capacity = state["pirate_ships"][pirate_ship]["capacity"] # if 2, my two hands are empty
        # Initialized with infinity values (so that the distance of an unreachable treasure will be infinity) and updated with the actual distances.
        min_distances_to_treasure, min_distances_to_base = float('inf'), float('inf')
        base_location = state["base"]
        pirate_location = state["pirate_ships"][pirate_ship]["location"]
        marine_locations = self.marine_location(state)
        
        # If the pirate ship holds treasures, we will sail to the base to deposit them.
        if my_capacity < 2:
            # Find the direction closest to the base as the direction we want to sail to.
            for neighbor in self.simulator.neighbors(pirate_location):
                temp_dist_to_base = abs(neighbor[0]-base_location[0]) + abs(neighbor[1]-base_location[1])
                if temp_dist_to_base < min_distances_to_base:
                    min_distances_to_base = temp_dist_to_base
                    min_dist_to_base_neighbor = neighbor
            # If the location we want to sail to has a marine ship, we will wait.
            if self.collision_with_marine(min_dist_to_base_neighbor, marine_locations):
                return ('wait', pirate_ship)
            return ('sail', pirate_ship, min_dist_to_base_neighbor)
        
        available_treasures = [v for v in state["treasures"].values() if type(v['location']) == tuple]
        scores = [(0,)] * len(available_treasures)  # A list that holds a tuple of the score we calculated for each treasure and the location we want to sail to in order to reach it.
        # For each treasure, we will calculate the score we can get from it and the location we want to sail to in order to reach it.
        for t, t_info in enumerate(available_treasures):
            treasure_location = t_info["location"]
            treasure_reward = t_info["reward"]
            # For each adjacent cell of the treasure (from which we can collect this treasure), we will calculate the distance from the pirate ship to it.
            for adjacent in self.simulator.neighbors(treasure_location):
                # Find the direction closest to the treasure as the direction we want to sail to.
                for neighbor in self.simulator.neighbors(pirate_location):
                    temp_dist_to_treasure = 1 + abs(neighbor[0]-adjacent[0]) + abs(neighbor[1]-adjacent[1])  # The L1-distance from the adjacent cell to the base (Manhattan Distance).

                    # Update the distance from the treasure to the base if the new distance is shorter.
                    if temp_dist_to_treasure < min_distances_to_treasure:
                        min_distances_to_treasure = temp_dist_to_treasure
                        min_dist_to_treasure_neighbor = neighbor

            # We define the score for each treasure as the ratio between the reward we can get from it and the shortest distance from the pirate ship to it.
            scores[t] = (treasure_reward / min_distances_to_treasure, min_dist_to_treasure_neighbor)
        sail_to = max(scores, key=lambda x: x[0])[1]  # The location we want to sail to in order to reach the treasure is the one with the highest score.
        # If the location we want to sail to has a marine ship, we will wait.
        if self.collision_with_marine(sail_to, marine_locations):
            return ('wait', pirate_ship)
        return ('sail', pirate_ship, sail_to)


        

class UCTNode:
    """
    A class for a single node. not mandatory to use but may help you.
    """
    def __init__(self, parent=None, action=None, player_number=0):
        # Initialize the node with the parent node, the action that was taken to reach this node and the player number.
        # We also have a list of the children of this node, the sum of the scores and the number of visits.
        self.parent = parent
        self.action = action
        self.player_number = player_number
        self.children = list()
        self.sum_score = 0
        self.visits = 0
    
    def select_using_uct(self):
        # UCT formula
        if self.visits == 0:
            return float('inf')
        return self.sum_score / self.visits + (2 * math.log(self.parent.visits) / self.visits) ** 0.5
    
    def update_node(self, result):
        # result is a dictionary with player 1 and player 2 scores.
        # we calculate here the score of the node
        # 3 - self.player_number is the rival player number
        self.visits += 1
        is_winner = result['player '+str(self.player_number)] > result['player '+str(3 - self.player_number)]
        if is_winner > 0:
            self.sum_score += 1

# class UCTTree:
#     """
#     A class for a Tree. not mandatory to use but may help you.
#     """
#     def __init__(self):
#         raise NotImplementedError

class UCTAgent:
    # We decided to initialize the agent with the initial state and the player number that are given.
    # We also have a list of the ships that belong to the agent and a list of the ships that belong to the rival.
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
        '''
        The selection function is used to select a child node to explore, acordingly to the UCT formula and MCTS algorithm.
        '''
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
        '''
        The get_legal_actions function is used to get all the legal actions that the agent can take in the current state.
        '''
        actions = {}
        collected_treasures = []
        ships = self.my_ships if player_number == self.player_number else self.rival_ships
        for ship in ships:
            actions[ship] = set()
            # Get all the neighboring tiles of the ship - only the ones that are sea tiles.
            neighboring_tiles = self.simulator.neighbors(state["pirate_ships"][ship]["location"])
            for tile in neighboring_tiles:
                actions[ship].add(("sail", ship, tile))
            # check if we can do a collect action
            if state["pirate_ships"][ship]["capacity"] > 0:
                for treasure in state["treasures"].keys():
                    if state["pirate_ships"][ship]["location"] in self.simulator.neighbors(state["treasures"][treasure]["location"])\
                        and treasure not in collected_treasures:
                        actions[ship].add(("collect", ship, treasure))
                        collected_treasures.append(treasure)
            for treasure in state["treasures"].keys():
                # check if we can do a deposit action
                if (state["pirate_ships"][ship]["location"] == state["base"]
                        and state["treasures"][treasure]["location"] == ship):
                    actions[ship].add(("deposit", ship, treasure))
            for enemy_ship_name in state["pirate_ships"].keys():
                # check if we can do a plunder action
                if (state["pirate_ships"][ship]["location"] == state["pirate_ships"][enemy_ship_name]["location"] and
                        self.player_number != state["pirate_ships"][enemy_ship_name]["player"]):
                    actions[ship].add(("plunder", ship, enemy_ship_name))
            actions[ship].add(("wait", ship))
        return list(product(*actions.values()))

        
    # def expansion(self, UCT_tree, parent_node):
    def expansion(self, state, parent_node):
        ''' 
        The expansion is as learned in class based on MCTS algorithm. 
        It is used to expand the tree and choose randomly a child node to explore.
        '''
        for action in self.get_legal_actions(state, parent_node.player_number):
            new_node = UCTNode(parent_node, action, 3 - parent_node.player_number)
            parent_node.children.append(new_node)
        return random.choice(parent_node.children)

    def simulation(self, node, turns_to_go, simulator):
        '''
        The simulation function is based on the MCTS algorithm as we learned in class.
        It is used to simulate the game until the end and return the score so we can backpropagate it.
        '''
        if turns_to_go == 0:
            return simulator.get_score()  # Score is a dictionary with player 1 and player 2 scores.
        if node.children:
            treasures = self.simulator.state["treasures"].keys()
            children_nodes = list()
            for child in node.children:
                # check if we can do a collect action, if not, we won't choose this child node to explore.
                # This is because the function in simulator do not check if the treasure is already collected/vinish.
                flag = False
                for atomic_action in child.action:
                    if ((atomic_action[0] == "collect") and (atomic_action[2] not in treasures)):
                        flag = True
                        break
                if not flag:
                    children_nodes.append(child)
            child_node = random.choice(children_nodes)
        else:
            # If there are no children nodes, we will expand the tree and choose randomly a child node to explore.
            child_node = self.expansion(simulator.state, node)
        simulator.act(child_node.action, node.player_number)
        return self.simulation(child_node, (turns_to_go - 1), simulator)


    def backpropagation(self, node, simulation_result):
        '''
        The backpropagation function is used to update the nodes in the tree with the simulation result,
        as we learned in class, based on the MCTS algorithm.'''
        while node is not None:
            node.update_node(simulation_result)
            node = node.parent


    def act(self, state):
        '''
        The act function is used to run the MCTS algorithm and return the best action to take.
        We also check the time so we won't exceed the time limit.
        In the end we choose the best child node to explore and return the action of this node.
        '''
        start_time = time()
        root = UCTNode(player_number=self.player_number)

        while time() - start_time < 4.2:
            node = self.selection(root)
            if self.simulator.turns_to_go == 0:
                # If we reached the end of the game, we will backpropagate the score and return the best action.
                self.backpropagation(node, self.simulator.get_score())
            else:
                self.expansion(state, node)
                simulation_result = self.simulation(node, self.simulator.turns_to_go, Simulator(state))
                self.backpropagation(node, simulation_result)

        child = max(root.children, key=lambda child: child.sum_score / child.visits if child.visits else float("inf"))  # No exploration
        return child.action

