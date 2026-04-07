"""
API Server for Nurture Game
Exposes game functionality via REST API for GameMaker integration
"""

import sys
import os
from pathlib import Path

# Add parent directory to path so we can import nurture module
current_dir = Path(__file__).resolve().parent
parent_dir = current_dir.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
from typing import Dict, Any

from nurture.main import NurtureGame
from nurture.core.enums import ParentRole

app = Flask(__name__)
CORS(app)  # Enable CORS for GameMaker requests

# Global game instance
game_instance: Dict[str, NurtureGame] = {}


@app.route('/api/game/new', methods=['POST'])
def new_game():
    """Create a new game session."""
    try:
        data = request.json
        session_id = data.get('session_id', 'default')
        role = data.get('role', 'FATHER').upper()

        # Create new game
        game = NurtureGame()
        game.select_role(ParentRole[role])

        # Store in sessions
        game_instance[session_id] = game

        return jsonify({
            'success': True,
            'session_id': session_id,
            'message': f'Game created with role: {role}'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/game/scenario', methods=['GET'])
def get_scenario():
    """Get current scenario."""
    try:
        session_id = request.args.get('session_id', 'default')
        game = game_instance.get(session_id)

        if not game:
            return jsonify({'success': False, 'error': 'Game not found'}), 404

        scenario = game.get_current_scenario()
        return jsonify({
            'success': True,
            'scenario': scenario
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/game/choice', methods=['POST'])
def make_choice():
    """Process player's choice."""
    try:
        data = request.json
        session_id = data.get('session_id', 'default')
        choice_number = data.get('choice_number', 1)

        game = game_instance.get(session_id)
        if not game:
            return jsonify({'success': False, 'error': 'Game not found'}), 404

        success = game.respond_to_scenario(choice_number)

        return jsonify({
            'success': success,
            'message': 'Choice processed' if success else 'Invalid choice'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/game/message', methods=['POST'])
def send_message():
    """Send message to AI partner."""
    try:
        data = request.json
        session_id = data.get('session_id', 'default')
        message = data.get('message', '')

        game = game_instance.get(session_id)
        if not game:
            return jsonify({'success': False, 'error': 'Game not found'}), 404

        response = game.send_message(message)

        return jsonify({
            'success': True,
            'response': response
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/game/status', methods=['GET'])
def get_status():
    """Get game status including relationship and learning metrics."""
    try:
        session_id = request.args.get('session_id', 'default')
        game = game_instance.get(session_id)

        if not game:
            return jsonify({'success': False, 'error': 'Game not found'}), 404

        return jsonify({
            'success': True,
            'story_status': game.get_story_status(),
            'relationship_status': game.get_relationship_status(),
            'learning_status': game.get_learning_status()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/game/save', methods=['POST'])
def save_game():
    """Save game state."""
    try:
        data = request.json
        session_id = data.get('session_id', 'default')
        filename = data.get('filename')

        game = game_instance.get(session_id)
        if not game:
            return jsonify({'success': False, 'error': 'Game not found'}), 404

        filepath = game.save_game(filename)

        return jsonify({
            'success': True,
            'filepath': filepath
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/game/load', methods=['POST'])
def load_game():
    """Load saved game."""
    try:
        data = request.json
        session_id = data.get('session_id', 'default')
        filepath = data.get('filepath')

        game = NurtureGame()
        success = game.load_game(filepath)

        if success:
            game_instance[session_id] = game
            return jsonify({'success': True, 'message': 'Game loaded'})
        else:
            return jsonify({'success': False, 'error': 'Failed to load game'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'active_sessions': len(game_instance)
    })


if __name__ == '__main__':
    print("Starting Nurture API Server...")
    print("Available at: http://localhost:5000")
    print("\nEndpoints:")
    print("  POST /api/game/new - Create new game")
    print("  GET  /api/game/scenario - Get current scenario")
    print("  POST /api/game/choice - Make a choice")
    print("  POST /api/game/message - Send message to AI")
    print("  GET  /api/game/status - Get game status")
    print("  POST /api/game/save - Save game")
    print("  POST /api/game/load - Load game")
    print("  GET  /api/health - Health check")

    app.run(host='0.0.0.0', port=5000, debug=True)
