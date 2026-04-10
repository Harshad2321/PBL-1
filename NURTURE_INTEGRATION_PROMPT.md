# NURTURE Game — GameMaker ↔ Python Backend Integration

## Your Identity & Approach
You are a senior full-stack game developer with deep expertise in:
- Python FastAPI backend systems
- GameMaker Studio 2 (GMS2) and GML scripting
- Local HTTP API integration between game engines and Python

You write **complete, production-ready code only**. You never write placeholders,
never write `# TODO`, never write `// add logic here`. Every function has a full body.
You output **all files in a single response** without stopping.

---

## Project Map

```
D:\STUDY\PBL\NUTURE\                        ← Open THIS folder in VS Code
├── PBL.yyp                                  ← GameMaker project file
├── objects\
│   ├── Colision\
│   ├── Dialog_box\                          ← DO NOT TOUCH
│   ├── Obj_dialog\                          ← DO NOT TOUCH (scripted cutscene player)
│   ├── obj_npc_parent\                      ← DO NOT TOUCH
│   ├── obj_npc1\                            ← DO NOT TOUCH
│   ├── obj_npc2\                            ← DO NOT TOUCH
│   └── Obj_Player\                          ← DO NOT TOUCH
└── PBL-1\                                   ← Python backend
    ├── api_server.py                        ← CREATE THIS
    ├── launcher.bat                         ← CREATE THIS
    ├── launcher.sh                          ← CREATE THIS
    └── nurture\
        ├── main.py                          ← NurtureGame class (already exists)
        ├── story_engine.py                  ← already exists
        ├── core\
        │   └── data_structures.py          ← already exists
        └── utils\
            └── llm_interface.py            ← Ollama mistral:7b-instruct-v0.3-q4_K_M
```

---

## What Already Exists — Do NOT Recreate

| Object | What it does | Rule |
|---|---|---|
| `Obj_dialog` | Cycles pre-written `messages[]` array with spacebar | **Never modify** |
| `Dialog_box` | UI shell for dialogue display | **Never modify** |
| `obj_npc_parent` | NPC parent object | **Never modify** |
| `obj_npc1`, `obj_npc2` | NPC instances | **Never modify** |
| `Obj_Player` | Player object | **Never modify** |

---

## What You Must Create — Every File, Complete

### Python Files

#### `PBL-1/api_server.py`
- FastAPI app with uvicorn
- Import `NurtureGame` from `nurture.main` — instantiate **once** at module level
- CORS middleware: `allow_origins=["*"]`
- Every endpoint wrapped in `try/except`, returns `{"error": str(e)}` with HTTP 500 on failure
- All request bodies use Pydantic `BaseModel`

**Endpoints — exact shapes:**

```
POST /start
  Request:  { "player_role": "father" | "mother" }
  Response: { "scenario": str, "choices": [str, str, str], "day": int }

POST /choose
  Request:  { "day": int, "choice": int }   ← choice is 1, 2, or 3
  Response: { "state_delta": dict, "ai_reaction": str }

POST /message
  Request:  { "message": str }
  Response: { "reply": str }

GET /status
  Response: {
    "day": int, "act": int,
    "trust": float, "resentment": float,
    "closeness": float, "stress": float,
    "game_over": bool, "collapse_reason": str | null
  }

POST /end_conversation
  Request:  {} (empty body — still use BaseModel)
  Response: { "day_summary": str, "trust_delta": float, "next_scenario": str | null }
```

#### `PBL-1/launcher.bat` (Windows)
```bat
@echo off
cd /d "%~dp0"
start "" python -m uvicorn api_server:app --host 127.0.0.1 --port 8000
timeout /t 3
echo Backend started on port 8000
```

#### `PBL-1/launcher.sh` (Mac/Linux)
```bash
#!/bin/bash
cd "$(dirname "$0")"
python3 -m uvicorn api_server:app --host 127.0.0.1 --port 8000 &
sleep 3
echo "Backend started on port 8000"
```

---

### GML Scripts (inside `NUTURE/scripts/`)

#### `scr_api_post(url, body_map)`
- `body_map` is a `ds_map`
- Build JSON string manually from the ds_map keys OR use `json_stringify`
- Create header ds_map with `"Content-Type": "application/json"`
- Call `http_request(url, "POST", header_map, json_body)`
- Destroy both ds_maps after the call
- Return the request ID

#### `scr_api_get(url)`
- Call `http_get(url)`
- Return the request ID

#### `scr_api_parse(async_map)`
- Read `async_map[? "status"]` — if not `0`, return `undefined`
- Read `async_map[? "result"]` as string
- If empty or not a string, return `undefined`
- Return `json_parse(result_string)` — this gives a struct in GMS2

---

### GML Objects (inside `NUTURE/objects/`)

#### `obj_api_controller`
- **Persistent: TRUE | Visible: FALSE**

**Create Event — declare ALL of these:**
```gml
// Request ID trackers
req_start    = -1
req_choose   = -1
req_message  = -1
req_status   = -1
req_end_conv = -1

// Global state
global.ai_reply          = ""
global.last_ai_reply     = ""
global.current_scenario  = ""
global.choice0           = ""
global.choice1           = ""
global.choice2           = ""
global.trust             = 0.5
global.resentment        = 0.0
global.closeness         = 0.5
global.stress            = 0.3
global.current_day       = 1
global.game_over         = false
global.day_summary       = ""
global.status_timer      = 0

// Auto-start game
var _body = ds_map_create();
ds_map_add(_body, "player_role", "father");
req_start = scr_api_post("http://127.0.0.1:8000/start", _body);
```

**Step Event:**
```gml
global.status_timer++;
if (global.status_timer >= 180) {
    req_status = scr_api_get("http://127.0.0.1:8000/status");
    global.status_timer = 0;
}
```

**Async HTTP Event — handle ALL 5 request IDs:**
```
req_start    → populate global.current_scenario, global.choice0/1/2, global.current_day
               → if obj_choice_menu exists: set visible = true

req_choose   → global.ai_reply = _data.ai_reaction
               → hide obj_choice_menu, show obj_chat_input

req_message  → global.ai_reply = _data.reply

req_status   → update global.trust, resentment, closeness, stress, game_over, current_day

req_end_conv → global.day_summary = _data.day_summary
               → auto-call /start again to load next day
```

---

#### `obj_chat_input`
- **Persistent: FALSE | Visible: TRUE**
- This is the LIVE CHAT BOX — completely new, totally separate from Obj_dialog

**Create Event variables:**
```gml
input_string    = ""
display_reply   = ""
cursor_visible  = true
cursor_timer    = 0
max_input_chars = 120
chat_history    = []   // array of structs: {speaker, text}
keyboard_string = ""   // clear GMS2 keyboard buffer
```

**Step Event logic (write complete code):**
- `cursor_timer++` → every 30 steps flip `cursor_visible`
- Append `keyboard_string` to `input_string` each step, then reset `keyboard_string = ""`
- Clamp `input_string` to `max_input_chars`
- Backspace: `keyboard_check_pressed(vk_backspace)` → delete last character
- Enter pressed (`keyboard_check_pressed(vk_return)`):
  - If `input_string == "/done"` → call `/end_conversation`, set `visible = false`
  - Else if `input_string != ""`:
    - `array_push(chat_history, {speaker: "You", text: input_string})`
    - Call `scr_api_post("/message", {message: input_string})`
    - Assign result to `obj_api_controller.req_message`
    - Clear `input_string = ""`
- Every step: if `global.ai_reply != global.last_ai_reply`:
  - `array_push(chat_history, {speaker: "AI", text: global.ai_reply})`
  - `global.last_ai_reply = global.ai_reply`

**Draw GUI Event (complete drawing code):**
- Dark semi-transparent panel covering bottom 40% of GUI screen
- Scroll through `chat_history` array, draw each line with speaker prefix
- Most recent message at bottom
- Input box outline at very bottom of panel
- `input_string` + blinking cursor inside input box
- Small hint text: `"Press Enter to send  |  Type /done to end the day"`

---

#### `obj_choice_menu`
- **Persistent: FALSE | Visible: TRUE**

**Create Event:**
```gml
choice_hover = 0  // 0=none, 1/2/3 = which button is hovered
btn_x = display_get_gui_width() / 2 - 300
btn_y = [300, 380, 460]   // y positions for 3 buttons
btn_w = 600
btn_h = 60
```

**Step Event:** detect mouse over each button rect → set `choice_hover`

**Draw GUI Event:**
- Draw `global.current_scenario` at top-center, word-wrapped
- Draw 3 buttons using button rects defined in Create
- Each button shows `global.choice0`, `global.choice1`, `global.choice2`
- Hovered button draws brighter background

**Mouse Left Pressed Event:**
- Detect which button rect contains `mouse_x, mouse_y`
- On valid click (1, 2, or 3):
  ```gml
  var _body = ds_map_create();
  ds_map_add(_body, "day", global.current_day);
  ds_map_add(_body, "choice", chosen_number);
  obj_api_controller.req_choose = scr_api_post("http://127.0.0.1:8000/choose", _body);
  visible = false;
  ```

---

#### `obj_status_bars`
- **Persistent: TRUE | Visible: TRUE**

**Draw GUI Event — draw all 4 bars:**
```
Position: top-right corner of GUI
x_start = display_get_gui_width() - 220
Bar width = 200px, Bar height = 16px, Spacing = 28px

Bar 1 — Trust:      color c_lime,                  fill = 200 * global.trust
Bar 2 — Resentment: color c_red,                   fill = 200 * global.resentment
Bar 3 — Closeness:  color c_aqua,                  fill = 200 * global.closeness
Bar 4 — Stress:     color make_colour_rgb(255,140,0), fill = 200 * global.stress

For each bar:
  1. draw_rectangle() dark gray background (empty bar)
  2. draw_rectangle() colored fill (value bar)
  3. draw_text() label to the LEFT
  4. draw_text() numeric value (2 decimal places) to the RIGHT
```

---

#### `obj_game_init` (place in Room 1, Persistent: FALSE)

**Create Event:**
```gml
// Launch Python backend
var _launcher = working_directory + "PBL-1\launcher.bat";
execute_shell("cmd.exe", "/c start /B """ + _launcher + """", false);

// Spawn persistent objects if not already present
if (!instance_exists(obj_api_controller))
    instance_create_layer(0, 0, "Instances", obj_api_controller);
if (!instance_exists(obj_status_bars))
    instance_create_layer(0, 0, "Instances", obj_status_bars);
if (!instance_exists(obj_choice_menu))
    instance_create_layer(0, 0, "Instances", obj_choice_menu);
if (!instance_exists(obj_chat_input))
    instance_create_layer(0, 0, "Instances", obj_chat_input);
```

---

## Hard Rules — Never Break These

| Rule | Detail |
|---|---|
| Never use `http_post_string()` | Use `http_request()` for all POST calls |
| Never modify `Obj_dialog` | It is a scripted cutscene system — untouched |
| Never use `global.choices[]` array | Use `global.choice0`, `global.choice1`, `global.choice2` |
| Never use ds_map for JSON parsing | Use `json_parse()` which returns a struct in GMS2 |
| All globals use `global.` prefix | No bare variable names for shared state |
| All URLs hardcoded | `"http://127.0.0.1:8000"` — no config files |
| Status bars in Draw GUI event | GUI coordinates, not room coordinates |
| `obj_chat_input` uses `keyboard_string` | GMS2 standard for text capture |
| No empty function bodies | Every event has complete working code |

---

## Output Format

Output every file using this exact structure:

```
FILE: <exact relative path from NUTURE\ folder>
─────────────────────────────────────────────────
<complete file contents>
─────────────────────────────────────────────────
```

**Output files in this exact order:**
1. `PBL-1/api_server.py`
2. `PBL-1/launcher.bat`
3. `PBL-1/launcher.sh`
4. `NUTURE/scripts/scr_api_post/scr_api_post.gml`
5. `NUTURE/scripts/scr_api_get/scr_api_get.gml`
6. `NUTURE/scripts/scr_api_parse/scr_api_parse.gml`
7. `NUTURE/objects/obj_api_controller/Create_0.gml`
8. `NUTURE/objects/obj_api_controller/Step_0.gml`
9. `NUTURE/objects/obj_api_controller/Async_HTTP_1.gml`
10. `NUTURE/objects/obj_chat_input/Create_0.gml`
11. `NUTURE/objects/obj_chat_input/Step_0.gml`
12. `NUTURE/objects/obj_chat_input/Draw_GUI_73.gml`
13. `NUTURE/objects/obj_choice_menu/Create_0.gml`
14. `NUTURE/objects/obj_choice_menu/Step_0.gml`
15. `NUTURE/objects/obj_choice_menu/Draw_GUI_73.gml`
16. `NUTURE/objects/obj_choice_menu/Mouse_Left_Pressed_4.gml`
17. `NUTURE/objects/obj_status_bars/Draw_GUI_73.gml`
18. `NUTURE/objects/obj_game_init/Create_0.gml`

Do not stop between files. Do not summarize. Output all 18 files completely.

---

## Pre-Output Self-Check

Before writing a single line of output, verify mentally:
- [ ] Every POST endpoint in `api_server.py` has a matching `scr_api_post()` call in GML
- [ ] Async HTTP event covers all 5 request IDs: `req_start`, `req_choose`, `req_message`, `req_status`, `req_end_conv`
- [ ] `global.choice0/1/2` used everywhere — never `global.choices[]`
- [ ] `obj_chat_input` uses `keyboard_string` for text capture
- [ ] Status bars use `Draw GUI` event with `display_get_gui_width/height()`
- [ ] `Obj_dialog` is never referenced or modified in any output file
- [ ] `launcher.bat` uses `%~dp0` to navigate to `PBL-1\` correctly
