import json
from flask import Flask, render_template
from flask_socketio import SocketIO, send, emit
from agent import train

class GameState:
    def __init__(self, snake, food, score, direction, game_over=False):
        self.snake = snake
        self.food = food
        self.score = score
        self.direction = direction
        self.game_over = game_over
    
    def __repr__(self):
        return json.dumps(self.__dict__)

app = Flask(__name__)
socketio = SocketIO(app, logger=True)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def test_connect():
    print('Connection established')

@socketio.on('message')
def handle_message(message):
    gameState = GameState(message['snake'], message['food'], message['score'], message['direction'], message['game_over'])
    train(gameState)
    updatedGameState = gameState
    updatedGameState.direction = [0,1,0]
    socketio.emit('message', json.dumps(updatedGameState.__dict__))


if __name__ == '__main__':
    socketio.run(app)