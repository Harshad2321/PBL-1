# Backend-UI Integration Guide

This guide explains how to connect the Python backend with the GameMaker UI.

## Architecture Overview

```
GameMaker UI (Frontend)
    ↓ HTTP Requests
Flask API Server (Middle Layer)
    ↓ Python Calls
Nurture Game Engine (Backend)
```

## Setup Instructions

### 1. Install Python Dependencies

```bash
# From the PBL-1 directory
pip install flask flask-cors
```

### 2. Start the API Server

```bash
# Start the backend server
python nurture/api_server.py
```

The server will start on `http://localhost:5000`

### 3. Configure GameMaker

1. Open your GameMaker project (`pbl_game/PBL.yyp`)
2. Create a new script called `scr_api_integration`
3. Copy the code from `gml_http_example.gml` into this script
4. Create a persistent controller object (e.g., `obj_game_controller`)
5. Add HTTP async event handler to this object

### 4. Test the Connection

In GameMaker's Create event:

```gml
// Initialize the game
create_new_game("FATHER");
```

In an Alarm[0] event (set alarm to 30 in Create):

```gml
// Get first scenario
get_scenario();
```

## API Endpoints Reference

### POST /api/game/new
Create a new game session.

**Request:**
```json
{
  "session_id": "unique_player_id",
  "role": "FATHER"  // or "MOTHER"
}
```

**Response:**
```json
{
  "success": true,
  "session_id": "unique_player_id",
  "message": "Game created with role: FATHER"
}
```

### GET /api/game/scenario
Get the current scenario.

**Query Parameters:**
- `session_id` - Your session identifier

**Response:**
```json
{
  "success": true,
  "scenario": {
    "act": "ACT 1",
    "day": 1,
    "total_days_in_act": 12,
    "title": "First Night Home",
    "description": "Your first night as new parents...",
    "scenario_text": "The baby is crying...",
    "choices": [
      {
        "text": "Wake partner immediately",
        "choice_id": "first_night_wake"
      },
      {
        "text": "Let partner sleep, handle it yourself",
        "choice_id": "first_night_solo"
      },
      {
        "text": "Try to soothe baby together",
        "choice_id": "first_night_together"
      }
    ]
  }
}
```

### POST /api/game/choice
Process a player's choice.

**Request:**
```json
{
  "session_id": "unique_player_id",
  "choice_number": 1  // 1, 2, or 3
}
```

**Response:**
```json
{
  "success": true,
  "message": "Choice processed"
}
```

### POST /api/game/message
Send a message to the AI partner.

**Request:**
```json
{
  "session_id": "unique_player_id",
  "message": "I think we should work together on this"
}
```

**Response:**
```json
{
  "success": true,
  "response": "You're right, I'm sorry for being distant. Let's do this together."
}
```

### GET /api/game/status
Get game status including relationship metrics.

**Query Parameters:**
- `session_id` - Your session identifier

**Response:**
```json
{
  "success": true,
  "story_status": {
    "current_act": 1,
    "current_day": 3,
    "total_choices": 8
  },
  "relationship_status": {
    "trust": 65.0,
    "emotional_closeness": 72.0,
    "communication_openness": 58.0
  },
  "learning_status": {
    "adaptation_level": "45.2%",
    "interactions": 15,
    "dominant_style": "supportive"
  }
}
```

### POST /api/game/save
Save the current game state.

**Request:**
```json
{
  "session_id": "unique_player_id",
  "filename": "my_save.json"  // optional
}
```

### POST /api/game/load
Load a saved game.

**Request:**
```json
{
  "session_id": "unique_player_id",
  "filepath": "./saves/my_save.json"
}
```

## GameMaker Integration Pattern

### Basic Flow

1. **Game Start**
   ```gml
   // obj_game_controller Create Event
   create_new_game("FATHER");
   alarm[0] = 30;  // Wait then get scenario
   ```

2. **Display Scenario**
   ```gml
   // HTTP Async Event
   if (variable_struct_exists(json_data, "scenario")) {
       current_scenario = json_data.scenario;
       // Update UI with scenario.title, scenario.description
       // Show choices: scenario.choices[0].text, etc.
   }
   ```

3. **Player Makes Choice**
   ```gml
   // Button Click Event
   make_choice(selected_choice_number);
   ```

4. **Optional: Conversation**
   ```gml
   // Text input submit
   send_message_to_ai(player_input_text);
   ```

5. **Get Next Scenario**
   ```gml
   // After choice is processed
   get_scenario();
   ```

## Troubleshooting

### Connection Refused
- Make sure the API server is running: `python nurture/api_server.py`
- Check firewall settings
- Verify the URL is `http://localhost:5000`

### CORS Errors
- The Flask server already has CORS enabled via `flask-cors`
- If testing from web export, make sure the server allows your domain

### Session Not Found
- Make sure you're using the same `session_id` across requests
- Check that the game was created successfully first

### No Response
- Add debug logging: `show_debug_message(result)` in HTTP event
- Check server console for errors
- Verify JSON formatting in requests

## Alternative: WebSocket Integration (Advanced)

For real-time updates and bi-directional communication:

1. Install: `pip install flask-socketio`
2. Use Socket.IO extension for GameMaker
3. Implement event-based communication

See `websocket_integration.md` for details (coming soon).

## Next Steps

1. Create UI elements in GameMaker to display scenarios
2. Design choice buttons that call `make_choice()`
3. Implement conversation interface for AI partner dialogue
4. Add visual feedback for relationship status
5. Create save/load UI

## Need Help?

- Check the example scripts in `gml_http_example.gml`
- Review the API server code in `nurture/api_server.py`
- Test endpoints using Postman or curl first
