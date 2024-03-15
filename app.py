import json
from flask import Flask, render_template
from flask_socketio import SocketIO, send, emit
import subprocess

class GameState:
    def __init__(self, snake, food, score, direction, game_over=False):
        self.snake = snake
        self.food = food
        self.score = score
        self.direction = direction
        self.game_over = game_over

app = Flask(__name__)
socketio = SocketIO(app, logger=True)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def test_conect():
    print('my response', {'data': 'Connected'})

@socketio.on('message')
def handle_message(message):
    # GameState = GameState({'snake': [], 'food': [], 'score': 0, 'direction': 'right', 'game_over': False})
    # print('my response', GameState)
    # socketio.emit('message', GameState)
    print(message)
    socketio.emit('message', {'data': message})


if __name__ == '__main__':
    socketio.run(app)