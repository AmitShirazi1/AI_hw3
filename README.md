# Pirate Treasure Hunting Simulation

## Overview

This project simulates a treasure-hunting competition between two pirate fleets, each striving to collect the most treasure, in a random and constantly-changing environment: The locations of treasures and marines (that chase the pirates and confiscate their treasure) are random, and these locations may randomly change at any given point in time.    
The fleets operate under different strategies, with one using a Upper Confidence Bounds for Trees (UCT) agent and the other using a general agent. This simulation showcases various AI techniques, including Monte Carlo Tree Search (MCTS), to model decision-making in competitive environments.

## Project Structure

The project consists of the following Python files:

- **`exp3_322720103_314779166.py`**: 
  This file contains the implementations of the agents used in the simulation. It includes:
  
  - **`Agent` Class**: 
    This class defines a sophisticated pirate ship agent capable of making strategic decisions based on the current state of the game. The agent operates under the following principles:
    - **State Management**: The agent maintains knowledge of its own ships and the rival's ships, along with the current game state provided by the simulator.
    - **Action Decision Logic**: 
      - The agent prioritizes actions based on predefined preferences:
        - If a ship is at the base and has treasure, it deposits the treasure.
        - If a ship is adjacent to a treasure and has capacity, it collects the treasure.
        - If a ship encounters a rival ship, it may plunder if advantageous.
        - If no preferred actions are possible, it calculates a sailing action based on distances to treasures and the base while avoiding marine ship collisions.
    - **Sailing Strategy**: The agent evaluates potential sailing directions to optimize treasure collection, using a scoring system that balances the treasure's reward against the distance to reach it.

  - **UCTAgent Class**: Implements the UCT (Upper Confidence Bound for Trees) algorithm. This class is responsible for:
    - Building a search tree of possible future states based on the current game state.
    - Utilizing MCTS to explore potential actions and outcomes, balancing exploration and exploitation to make optimal decisions.
    - Keeping track of the number of visits and win rates for actions to inform future decisions.
    
- **`main.py`**: The entry point for the simulation. This file orchestrates the setup of the game and manages the interaction between the different agents and the environment.
  
- **`sample_agent.py`**: Provides a basic implementation of a sample agent that can be used for comparison with the UCT-based agent.
  
- **`simulator.py`**: Handles the simulation of the treasure-hunting environment, including the rules for collecting treasure and interactions between the fleets.
  
- **`tictactoe.py`**: Implements a simple Tic-Tac-Toe game using MCTS and UCT. This serves as an additional example of decision-making strategies in a competitive setting.

- **`utils.py`**: Contains utility functions that assist in various operations across the project, such as logging and data handling.


## Usage

To run the simulation, execute the `main.py` file. This will initialize the fleets and start the competition:

```bash
python main.py
```


## Results

The simulation will output the results of each run, which is the sum of the treasures collected by each fleet (minus collision with marines). Analyze the results to evaluate the effectiveness of the different agent strategies.
