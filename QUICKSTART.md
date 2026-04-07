# Quick Start: Backend-UI Integration

## 🚀 Get Started in 5 Minutes

### Step 1: Install Dependencies
```bash
cd c:\Users\harsh\Desktop\PBL-1
pip install flask flask-cors
```

### Step 2: Start the Backend Server
```bash
# From the PBL-1 directory
python nurture/api_server.py

# OR if you're in the nurture directory:
# cd nurture
# python api_server.py
```

You should see:
```
Starting Nurture API Server...
Available at: http://localhost:5000
[List of endpoints...]
* Running on http://0.0.0.0:5000
```

### Step 3: Test the API
Open a new terminal and test:

```bash
# Create a new game
curl -X POST http://localhost:5000/api/game/new \
  -H "Content-Type: application/json" \
  -d "{\"session_id\": \"test123\", \"role\": \"FATHER\"}"

# Get the first scenario
curl http://localhost:5000/api/game/scenario?session_id=test123
```

### Step 4: Integrate with GameMaker

1. **Open your GameMaker project**: `pbl_game/PBL.yyp`

2. **Create a new script** called `scr_api_integration`:
   - Right-click on "Scripts" folder → Create Script
   - Name it `scr_api_integration`
   - Copy all code from `gml_http_example.gml`

3. **Create a controller object**:
   - Right-click on "Objects" → Create Object
   - Name it `obj_game_controller`
   - Make it persistent (checkbox)

4. **Add Create Event**:
```gml
// Initialize API connection
global.api_url = "http://localhost:5000/api";
global.session_id = "player_" + string(random(10000));

// Start new game
request_id_newgame = create_new_game("FATHER");
alarm[0] = 30; // Wait then get scenario
```

5. **Add Alarm 0 Event**:
```gml
// Get first scenario
request_id_scenario = get_scenario();
```

6. **Add HTTP Event**:
```gml
var response_id = async_load[? "id"];
var status = async_load[? "status"];
var result = async_load[? "result"];

if (status == 0) {  // Success
    show_debug_message("Response: " + result);

    var json_data = json_parse(result);

    if (variable_struct_exists(json_data, "scenario")) {
        // Got a scenario!
        global.current_scenario = json_data.scenario;
        show_debug_message("Scenario: " + global.current_scenario.title);
    }
}
```

7. **Test it**:
   - Add `obj_game_controller` to your first room
   - Run the game
   - Check the Output window for debug messages

## 📋 What You Can Do Now

### Get Scenarios
```gml
get_scenario();
// Returns current day's scenario with choices
```

### Make Choices
```gml
make_choice(1);  // Player picks choice 1
make_choice(2);  // Player picks choice 2
make_choice(3);  // Player picks choice 3
```

### Talk to AI Partner
```gml
send_message_to_ai("I think we should work together on this");
// AI responds based on context and relationship
```

### Check Status
```gml
get_game_status();
// Returns relationship metrics, story progress, etc.
```

## 🎨 UI Design Example

### Display a Scenario
```gml
// Draw Event
if (variable_global_exists("current_scenario")) {
    var scenario = global.current_scenario;

    // Draw background
    draw_set_color(c_white);
    draw_rectangle(50, 50, 750, 550, false);

    // Draw title
    draw_set_color(c_black);
    draw_set_font(fnt_title);
    draw_text(100, 80, scenario.title);

    // Draw description
    draw_set_font(fnt_body);
    draw_text_ext(100, 140, scenario.description, 20, 600);

    // Draw scenario text
    draw_text_ext(100, 220, scenario.scenario_text, 20, 600);

    // Draw choices as buttons
    for (var i = 0; i < array_length(scenario.choices); i++) {
        var btn_y = 350 + (i * 60);

        // Button background
        draw_set_color(c_ltgray);
        draw_rectangle(100, btn_y, 700, btn_y + 50, false);

        // Button text
        draw_set_color(c_black);
        draw_text(120, btn_y + 15, string(i+1) + ". " + scenario.choices[i].text);
    }
}
```

### Handle Choice Clicks
```gml
// Mouse Left Pressed Event
if (variable_global_exists("current_scenario")) {
    var scenario = global.current_scenario;

    for (var i = 0; i < array_length(scenario.choices); i++) {
        var btn_y = 350 + (i * 60);

        if (point_in_rectangle(mouse_x, mouse_y, 100, btn_y, 700, btn_y + 50)) {
            make_choice(i + 1);

            // Wait a bit, then get next scenario
            alarm[1] = 60;
        }
    }
}
```

## 🔍 Troubleshooting

**"Connection refused"**
→ Make sure `python nurture/api_server.py` is running

**"Session not found"**
→ Call `create_new_game()` first before other API calls

**"Nothing happens in GameMaker"**
→ Check the Output window (F4) for debug messages
→ Make sure HTTP event is added to your controller object

**"JSON parse error"**
→ Server might have returned an error - check server console
→ Add `show_debug_message(result)` to see raw response

## 📚 Next Steps

1. ✅ Backend running
2. ✅ GameMaker connected
3. 🎨 Design your UI screens
4. 🎮 Add choice buttons
5. 💬 Create conversation interface
6. 📊 Display relationship metrics
7. 💾 Add save/load functionality

See `INTEGRATION_GUIDE.md` for full API documentation.

---

**Need help?** Check the example code in `gml_http_example.gml`
