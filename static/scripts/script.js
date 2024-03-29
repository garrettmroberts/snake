// HTML ElementInternals
const board = document.getElementById('anaconda-board');
const instructionText = document.getElementById('instruction-text');
const currentScore = document.getElementById('score');
const currentHighScore = document.getElementById('high-score');
const highScoreContainer = document.getElementById('high-score-container');

// Game variables
const gridSize = 20;
let snake = [];
let food = [];
let score = 0;
let highScore = 0;
let direction = 'right';
let gameIsStarted = false;
let gameSpeedDelay = 200;
let gameOver = false;
let gameInterval;

// Game state class (for websocket transfer)
class GameState {
  constructor(snake, food, score, direction, game_over) {
    this.snake = snake;
    this.food = food;
    this.score = score;
    this.direction = direction;
    this.game_over = game_over;
  }
}

// Drawing Functions
const draw = () => {
  board.innerHTML = '';
  drawSnake();
  drawFood();
  updateScore();
};

const drawSnake = () => {
  snake.map(segment => {
    const snakeElement = createGameElement('div', 'snake');
    setPosition(snakeElement, segment);
    board.appendChild(snakeElement);
  });
};

// Movement Functions
const move = () => {
  const head = snake[0];
  let newHead;
  switch (direction) {
    case 'up':
      newHead = [head[0], head[1] - 1];
      break;
    case 'down':
      newHead = [head[0], head[1] + 1];
      break;
    case 'left':
      newHead = [head[0] - 1, head[1]];
      break;
    case 'right':
      newHead = [head[0] + 1, head[1]];
      break;
  }
  snake.unshift(newHead);
  if (newHead[0] == food[0] && newHead[1] == food[1]) {
    food = generateFood();
    increaseSpeed();
    clearInterval(gameInterval);
    gameInterval = setInterval(() => {
      socket.emit(
        'message',
        new GameState(snake, food, score, direction, gameOver)
      );
      move();
      checkCollision();
      draw();
    }, gameSpeedDelay);
  } else {
    snake.pop();
  }
};

const increaseSpeed = () => {
  if (gameSpeedDelay > 150) {
    gameSpeedDelay -= 5;
  } else if (gameSpeedDelay > 100) {
    gameSpeedDelay -= 3;
  } else if (gameSpeedDelay > 50) {
    gameSpeedDelay -= 2;
  } else if (gameSpeedDelay > 25) {
    gameSpeedDelay -= 1;
  }
};

const checkCollision = () => {
  const head = snake[0];
  if (head[0] < 0 || head[0] > gridSize || head[1] < 0 || head[1] > gridSize) {
    resetGame();
  }

  for (i = 1; i < snake.length; i += 1) {
    if (head[0] === snake[i][0] && head[1] === snake[i][1]) {
      resetGame();
    }
  }
};

// Food Functions
function generateFood() {
  let x, y;
  do {
    x = Math.floor(Math.random() * (gridSize - 2)) + 1;
    y = Math.floor(Math.random() * (gridSize - 2)) + 1;
  } while (snake.some(segment => segment[0] === x && segment[1] === y));
  return [x, y];
}

const drawFood = () => {
  if (gameIsStarted) {
    const foodElement = createGameElement('div', 'food');
    setPosition(foodElement, food);
    board.appendChild(foodElement);
  }
};

// Utility Functions
const createGameElement = (tag, className) => {
  const element = document.createElement(tag);
  element.className = className;
  return element;
};

const setPosition = (element, position) => {
  element.style.gridColumn = position[0];
  element.style.gridRow = position[1];
};

// Score Functions
const updateScore = () => {
  score = snake.length;
  currentScore.textContent = score.toString().padStart(3, '0');
  if (score > highScore) {
    highScore = score;
    currentHighScore.textContent = score.toString().padStart(3, '0');
    highScoreContainer.style.display = 'block';
  }
};

// Game Operation Functions
const startGame = () => {
  gameIsStarted = true;
  instructionText.style.display = 'none';
  snake.push([10, 10]);
  food = generateFood();
  gameOver = false;
  gameInterval = setInterval(() => {
    socket.emit(
      'message',
      new GameState(snake, food, score, direction, gameOver)
    );
    move();
    checkCollision();
    draw();
  }, gameSpeedDelay);
};

const resetGame = () => {
  gameIsStarted = false;
  instructionText.style.display = 'block';
  snake = [];
  food = [];
  direction = 'right';
  gameSpeedDelay = 200;
  score = 0;
  gameOver = true;
  clearInterval(gameInterval);
};

// Websocket
const socket = io();

socket.on('message', function (message) {
  updatedGameState = JSON.parse(message);
  if (updatedGameState.direction == [1, 0, 0]) {
    // left
    if (direction === 'up') {
      direction = 'left';
    } else if (direction === 'left') {
      direction = 'down';
    } else if (direction === 'down') {
      direction = 'right';
    } else if (direction === 'right') {
      direction = 'up';
    }
  } else if (updatedGameState.direction == [0, 1, 0]) {
    // straight
    pass;
  } else if (updatedGameState.direction == [0, 0, 1]) {
    // right
    if (direction === 'up') {
      direction = 'right';
    } else if (direction === 'right') {
      direction = 'down';
    } else if (direction === 'down') {
      direction = 'left';
    } else if (direction === 'left') {
      direction = 'up';
    }
  }
});

// Keypress Functions
const handleKeyPress = e => {
  if (e.code === 'Space' && !gameIsStarted) {
    startGame();
  }
  switch (e.key) {
    case 'ArrowUp':
      direction = 'up';
      break;
    case 'ArrowDown':
      direction = 'down';
      break;
    case 'ArrowLeft':
      direction = 'left';
      break;
    case 'ArrowRight':
      direction = 'right';
      break;
  }
};

// Event Listeners
document.addEventListener('keydown', handleKeyPress);
