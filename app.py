from flask import Flask, render_template, request, jsonify, send_from_directory
import chess
import random
import os

app = Flask(__name__, static_url_path='/static')

# Store the game state (in memory - will reset on server restart)
games = {}

def random_move(board):
    return random.choice(list(board.legal_moves))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/static/img/chesspieces/<piece>')
def serve_piece(piece):
    return send_from_directory('static/img/chesspieces', piece)

@app.route('/new_game', methods=['POST'])
def new_game():
    game_id = str(random.randint(1000, 9999))
    games[game_id] = chess.Board()
    return jsonify({'game_id': game_id, 'fen': games[game_id].fen()})

@app.route('/make_move', methods=['POST'])
def make_move():
    data = request.get_json()
    game_id = data.get('game_id')
    move = data.get('move')
    
    if game_id not in games:
        return jsonify({'error': 'Invalid game'}), 400
    
    board = games[game_id]
    
    try:
        # Player's move
        board.push_san(move)
        
        # Check if game is over after player's move
        if board.is_game_over():
            result = get_game_result(board)
            return jsonify({
                'fen': board.fen(),
                'game_over': True,
                'result': result
            })
        
        # Bot's move
        bot_move = random_move(board)
        board.push(bot_move)
        
        # Check if game is over after bot's move
        if board.is_game_over():
            result = get_game_result(board)
            return jsonify({
                'fen': board.fen(),
                'game_over': True,
                'result': result,
                'bot_move': bot_move.uci()
            })
        
        return jsonify({
            'fen': board.fen(),
            'game_over': False,
            'bot_move': bot_move.uci()
        })
        
    except ValueError:
        return jsonify({'error': 'Invalid move'}), 400

def get_game_result(board):
    if board.is_checkmate():
        return 'Checkmate!'
    elif board.is_stalemate():
        return 'Stalemate!'
    elif board.is_insufficient_material():
        return 'Draw by insufficient material!'
    else:
        return 'Game Over!'

if __name__ == '__main__':
    # Create required directories if they don't exist
    os.makedirs('static/img/chesspieces', exist_ok=True)
    app.run(debug=True)