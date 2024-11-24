import torch
import random
import numpy as np
from collections import deque
from game import SnakeGameAI, Direction, Point
from model import Linear_QNet, QTrainer
from helper import plot

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001

class Agent:
    def __init__(self):
        self.n_games = 0 #number of games
        self.epsilon = 0 #randomness
        self.gamma = 0.9 #discount rate  must be samller than 1 
        self.memory = deque(maxlen=MAX_MEMORY) #popleft() automatically remove elements if memory full
        self.model = Linear_QNet(11,256, 3) #11 states, output 3 because action diretion
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)
        self.model.load_state_dict(torch.load('model/model1100.pth'))


    def get_state(self, game):
        head = game.snake[0]
        #points used to check danger
        point_l = Point(head.x - 20, head.y) 
        point_r = Point(head.x + 20, head.y)
        point_u = Point(head.x, head.y - 20)
        point_d = Point(head.x, head.y + 20)
        
        dir_l = game.direction == Direction.LEFT
        dir_r = game.direction == Direction.RIGHT
        dir_u = game.direction == Direction.UP
        dir_d = game.direction == Direction.DOWN

        state = [
            # Danger straight
            (dir_r and game.is_collision(point_r)) or 
            (dir_l and game.is_collision(point_l)) or 
            (dir_u and game.is_collision(point_u)) or 
            (dir_d and game.is_collision(point_d)),

            # Danger right
            (dir_u and game.is_collision(point_r)) or 
            (dir_d and game.is_collision(point_l)) or 
            (dir_l and game.is_collision(point_u)) or 
            (dir_r and game.is_collision(point_d)),

            # Danger left
            (dir_d and game.is_collision(point_r)) or 
            (dir_u and game.is_collision(point_l)) or 
            (dir_r and game.is_collision(point_u)) or 
            (dir_l and game.is_collision(point_d)),
            
            # Move direction
            dir_l,
            dir_r,
            dir_u,
            dir_d,
            
            # Food location 
            game.food.x < game.head.x,  # food left
            game.food.x > game.head.x,  # food right
            game.food.y < game.head.y,  # food up
            game.food.y > game.head.y  # food down
            ]

        return np.array(state, dtype=int)

    def remember(self, state, action, reward, next_state, game_over):
        self.memory.append((state, action, reward, next_state, game_over))
    
    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE) #list of tuples 
        else:
            mini_sample = self.memory   
        
        states, actions, rewards, next_states, game_overs = zip(*mini_sample) #creates vars for each arg, zip func splits data
        self.trainer.train_step(states, actions, rewards, next_states, game_overs)

    def train_short_memory(self, state, action, reward, next_state, game_over):
        self.trainer.train_step(state, action, reward, next_state, game_over)

    def get_action(self, state):
        #do random moves: trade off between exploration / exploitation
        self.epsilon = 0
        final_move = [0,0,0]
        #more games, less randomness
        if random.randint( 1,200) < self.epsilon:
            move = random.randint(0,2) 
            final_move[move] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1    

        return final_move

def train():
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 0
    agent = Agent()
    game = SnakeGameAI(20)
    while True:
        # get old state
        state_old = agent.get_state(game)

        # get move based on currents state 
        final_move = agent.get_action(state_old)

        # perform move and get new state
        reward, game_over, score = game.play_step(final_move)
        state_new = agent.get_state(game)

        #train short memory
        agent.train_short_memory(state_old, final_move, reward, state_new, game_over)

        #remember
        agent.remember(state_old, final_move, reward, state_new, game_over)

        if game_over:
            # train long memory, plot results
            game.reset()
            agent.n_games += 1
            agent.train_long_memory()

            print('Game', agent.n_games, 'Score', score, 'Record:', record)

if __name__ == '__main__':
    train()