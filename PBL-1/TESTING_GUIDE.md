# NURTURE Integration - Testing Guide

## ✅ Backend is Working!

The Python FastAPI backend is now running and tested successfully.

---

## 📋 Testing Steps

### **1. Backend Testing (Already Done ✅)**

The backend is currently running on `http://127.0.0.1:8000`

To manually start/stop the backend:

**Start:**
```powershell
cd "d:\STUDY\PBL\NUTURE\PBL-1"
python api_server.py
```

**Stop:**
Find the python process and kill it, or press Ctrl+C in the terminal

**Test API Endpoints:**
```powershell
# Test /start
$body = @{player_role="father"} | ConvertTo-Json
Invoke-RestMethod -Uri "http://127.0.0.1:8000/start" -Method POST -Body $body -ContentType "application/json"

# Test /status
Invoke-RestMethod -Uri "http://127.0.0.1:8000/status" -Method GET

# Test /message
$body = @{message="Hello"} | ConvertTo-Json
Invoke-RestMethod -Uri "http://127.0.0.1:8000/message" -Method POST -Body $body -ContentType "application/json"
```

---

### **2. GameMaker Studio 2 Setup**

Now you need to configure the GameMaker project:

#### **Step 1: Open the Project**
1. Launch **GameMaker Studio 2**
2. Open `D:\STUDY\PBL\NUTURE\PBL.yyp`

#### **Step 2: Add the New Objects to Your Room**

The new objects need to be registered in the GameMaker IDE:

**Required Objects** (already created as folders):
- `obj_api_controller` - API communication handler
- `obj_chat_input` - Live chat interface
- `obj_choice_menu` - 3-button choice menu
- `obj_status_bars` - Top-right status display
- `obj_game_init` - Launches backend and spawns objects

**How to add them:**

1. In GameMaker IDE, right-click on **"Objects"** folder in the Asset Browser
2. For each object folder (e.g., `obj_api_controller`):
   - Right-click the object folder → **Create → Object**
   - Name it exactly as the folder name
   - Click on the object to open it
   - Set properties:
     - **Persistent**: `true` for `obj_api_controller` and `obj_status_bars`
     - **Visible**: `false` for `obj_api_controller`, `true` for others
   
3. Add events to each object by dragging the .gml files or by:
   - Click **Add Event**
   - Select the event type (Create, Step, Draw GUI, Async HTTP, Mouse)
   - The .gml file should already exist in the folder

#### **Step 3: Create Scripts in GameMaker**

Do the same for scripts:

1. Right-click **"Scripts"** folder
2. For each script folder (`scr_api_post`, `scr_api_get`, `scr_api_parse`):
   - Right-click the script folder → **Create → Script**
   - Name it exactly as the folder name
   - The .gml file should already be in the folder

#### **Step 4: Add obj_game_init to Room**

1. Open your first room (likely `Room1` or similar)
2. In the **Layers** panel, select the **Instances** layer
3. Drag `obj_game_init` from the Asset Browser into the room
4. Place it anywhere (position doesn't matter - it launches the backend)

**Important:** `obj_game_init` should be:
- **Persistent**: `false` (only runs once at game start)
- **Visible**: `false`

The other objects (`obj_api_controller`, `obj_status_bars`, `obj_choice_menu`, `obj_chat_input`) will be spawned automatically by `obj_game_init` - DO NOT place them in the room manually.

---

### **3. Run the Game**

#### **Before Running:**
1. Make sure the Python backend is NOT already running (or it will fail to start)
2. The game will automatically launch `launcher.bat` which starts the backend

#### **Run Steps:**
1. In GameMaker, click the **Play** button (▶️) or press **F5**
2. Wait 3-5 seconds for the backend to start
3. The game should connect and display:
   - **Scenario text** in the center
   - **3 choice buttons** below the scenario
   - **4 status bars** in the top-right (Trust, Resentment, Closeness, Stress)

#### **Expected Behavior:**
1. **On Start**: Choice menu appears with a scenario and 3 options
2. **After Clicking a Choice**: 
   - Choice menu disappears
   - Chat window appears at bottom (40% of screen)
   - You can type messages and press Enter to talk with the AI child
3. **Type `/done`**: Ends the day, shows summary, loads next day's scenario

---

### **4. Troubleshooting**

#### **"Connection refused" or API errors:**
- Backend may not have started - check Task Manager for `python.exe` process
- Manually run `d:\STUDY\PBL\NUTURE\PBL-1\launcher.bat` to see errors
- Check port 8000 is available: `Get-NetTCPConnection -LocalPort 8000`

#### **"Object not found" errors:**
- Objects/scripts weren't properly added to GameMaker
- Use **Tools → Refresh Asset List** in GameMaker
- Verify the .yy files exist in each object/script folder

#### **Status bars not showing:**
- `obj_status_bars` may not be spawned - check `obj_game_init` ran
- Check the Draw GUI event is set to event #73 (Draw GUI)

#### **Chat window not appearing:**
- Check `obj_chat_input` is spawned
- After making a choice, it should become `visible = true`

#### **Black screen:**
- Backend may be still loading - wait 5 seconds
- Check GameMaker Output/Compiler tab for errors

---

### **5. Testing Checklist**

- [ ] Backend starts successfully (see Python window briefly)
- [ ] Scenario text appears in game
- [ ] 3 choice buttons visible and hoverable
- [ ] Status bars visible in top-right corner
- [ ] Clicking a choice hides menu
- [ ] Chat window appears after choice
- [ ] Can type in chat input box
- [ ] Pressing Enter sends message
- [ ] AI replies appear in chat history
- [ ] `/done` command ends the conversation
- [ ] Next scenario loads after `/done`
- [ ] Status bars update over time

---

### **6. File Structure Reference**

```
D:\STUDY\PBL\NUTURE\
├── PBL.yyp                           ← GameMaker project file
├── scripts\
│   ├── scr_api_post\
│   │   └── scr_api_post.gml         ✅ Created
│   ├── scr_api_get\
│   │   └── scr_api_get.gml          ✅ Created
│   └── scr_api_parse\
│       └── scr_api_parse.gml        ✅ Created
├── objects\
│   ├── obj_api_controller\
│   │   ├── Create_0.gml             ✅ Created
│   │   ├── Step_0.gml               ✅ Created
│   │   └── Async_HTTP_1.gml         ✅ Created
│   ├── obj_chat_input\
│   │   ├── Create_0.gml             ✅ Created
│   │   ├── Step_0.gml               ✅ Created
│   │   └── Draw_GUI_73.gml          ✅ Created
│   ├── obj_choice_menu\
│   │   ├── Create_0.gml             ✅ Created
│   │   ├── Step_0.gml               ✅ Created
│   │   ├── Draw_GUI_73.gml          ✅ Created
│   │   └── Mouse_Left_Pressed_4.gml ✅ Created
│   ├── obj_status_bars\
│   │   └── Draw_GUI_73.gml          ✅ Created
│   └── obj_game_init\
│       └── Create_0.gml             ✅ Created
└── PBL-1\
    ├── api_server.py                ✅ Created & Fixed
    ├── launcher.bat                 ✅ Created
    └── launcher.sh                  ✅ Created
```

---

## 🎮 Quick Start Command

**Kill current backend and restart everything:**
```powershell
# Kill any existing backend
Get-Process python | Where-Object {$_.Path -like "*NUTURE*"} | Stop-Process -Force

# Start fresh
cd "d:\STUDY\PBL\NUTURE\PBL-1"
python api_server.py
```

Then open GameMaker and press **F5** to run the game.

---

## 📝 Notes

- The backend must be running BEFORE GameMaker makes API calls
- `obj_game_init` will try to auto-launch it, but you can also start manually
- All game state is tracked in `global.` variables in GameMaker
- The Python `NurtureGame` class handles the AI logic
- Communication is purely HTTP REST API (no websockets)

**Current Backend PID:** 29804 (running on port 8000)

---

Good luck with testing! 🚀
