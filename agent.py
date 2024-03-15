from collections import deque
import json
import random
import torch

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001


class Agent:

    class State:
        def __init__(self, danger_straight, danger_left, danger_right, food_left, food_right, food_up, food_down, dir_left, dir_right, dir_up, dir_down) -> None:
            self.danger_straight = danger_straight
            self.danger_left = danger_left
            self.danger_right = danger_right
            self.food_left = food_left
            self.food_right = food_right
            self.food_up = food_up
            self.food_down = food_down
            self.dir_left = dir_left
            self.dir_right = dir_right
            self.dir_up = dir_up
            self.dir_down = dir_down
        
        def __repr__(self):
            return json.dumps(self.__dict__)


    def __init__(self, game) -> None:
        self.n_games = 0
        self.epsilon = 0 # randomness
        self.gamma = 0 # discount rate
        self.memory = deque(maxlen=MAX_MEMORY) # popleft()
        self.game_data = game
        self.model = None # TODO
        self.trainer = None # TODO

    def __repr__(self):
        return json.dumps(self.__dict__)

    def get_state(self):
        snake = self.game_data.snake
        head = snake[0]
        point_left = [head[0] - 1, head[1]]
        point_right = [head[0] + 1, head[1]]
        point_up = [head[0], head[1] - 1]
        point_down = [head[0], head[1] + 1]
        direction = self.game_data.direction
        food = self.game_data.food
        danger_straight = (
            direction == 'up' and (point_up in snake or point_up[1] <= 0) or
            direction == 'down' and (point_down in snake or point_down[1] > 20) or
            direction == 'left' and (point_left in snake or point_left[0] <= 0) or
            direction == 'right' and (point_right in snake or point_right[0] > 20)
        )
        danger_left = (
            direction == 'up' and (point_left in snake or point_left[0] <= 0) or
            direction == 'left' and (point_down in snake or point_down[1] > 20) or
            direction == 'down' and (point_right in snake or point_right[0] > 20) or
            direction == 'left' and (point_up in snake or point_up[1] <= 0)
        )
        danger_right = (
            direction == 'up' and (point_right in snake or point_right[0] > 20) or
            direction == 'right' and (point_down in snake or point_down[1] > 20) or
            direction == 'down' and (point_left in snake or point_left[0] <= 0) or
            direction == 'left' and (point_up in snake or point_up[1] <= 0)
        )
        food_left = food[0] < head[0]
        food_right = food[0] > head[0]
        food_up = food[1] < head[1]
        food_down = food[1] > head[1]
        dir_left = direction == 'left'
        dir_right = direction == 'right'
        dir_up = direction == 'up'
        dir_down = direction == 'down'
        state = self.State(
            danger_straight=danger_straight,
            danger_left=danger_left,
            danger_right=danger_right,
            food_left=food_left,
            food_right=food_right,
            food_up=food_up,
            food_down=food_down,
            dir_left=dir_left,
            dir_right=dir_right,
            dir_up=dir_up,
            dir_down=dir_down
        )
        return state

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done)) #popleft is MAX_MEMORY is reached

    def train_long_memory(self): # accepts Tensor or NumPy array
        if len(self.memory) > BATCH_SIZE:
            minimal_sample = random.sample(self.memory, BATCH_SIZE)  # list of tuples
        else:
            minimal_sample = self.memory
        states, actions, rewards, next_states, dones = zip(*minimal_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)

    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)

    def get_action(self, state):
        # random moves: tradeoff exploration / exploitation
        self.epsilon = 80 - self.n_games
        final_move = [0, 0, 0]
        if random.randint(0,200) < self.epsilon:
            move = random.randint(0, 2)
            final_move[move] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model.predict(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1
        return final_move

def train(game):
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    high_score = 0
    agent = Agent(game)
    state_old = agent.get_state()
    print(state_old)
    # while True:
    #     # get old state
    #     state_old = agent.get_state()
    #     # get move
    #     final_move = agent.get_action(state_old)
    #     # perform move and get new state
    #     reward, done, score = game.play_step(final_move)
    #     # remember
    #     state_new = agent.get_state(game)
    #     # train short memory
    #     agent.train_short_memory(state_old, final_move, reward, state_new, done)
    #     # remember
    #     agent.remember(state_old, final_move, reward, state_new, done)
    #     if done:
    #         game.reset()
    #         agent.n_games += 1
    #         # train long memory
    #         agent.train_long_memory()

    #         if score > high_score:
    #             high_score = score
    #             # agent.model.save()

    #         print('Game', agent.n_games, 'Score', score, 'High Score', high_score)

    #         # TODO: plot
