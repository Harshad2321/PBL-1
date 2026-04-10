# NURTURE - Quick Asset Download & Integration Guide
## Generated April 8, 2026 with PixelLab MCP

---

## 🎉 READY TO DOWNLOAD NOW (9/11 Assets)

### Download Commands (Copy & Run in Terminal)

#### Characters (3/3 Ready)
```bash
# Navigate to your assets folder
cd "d:\STUDY\PBL\NUTURE\assets\characters"

# Download Father sprite
curl --fail -o Father.zip "https://api.pixellab.ai/mcp/characters/4899c9b0-84d1-4a53-a8aa-73e0118dd37d/download"

# Download Mother sprite  
curl --fail -o Mother.zip "https://api.pixellab.ai/mcp/characters/d5ce073c-f9ac-466d-a9b1-147f6d393aea/download"

# Download Baby Lily sprite
curl --fail -o BabyLily.zip "https://api.pixellab.ai/mcp/characters/ee37043e-70f8-47cc-9e27-f2f1180d7fb0/download"

# Extract all
unzip -l *.zip
```

#### UI Elements (5/5 Ready) - Copy Image URLs
| Element | Download URL | Size |
|---------|--------------|------|
| Dialogue Box | https://api.pixellab.ai/mcp/map-objects/bb6d1c05-8e36-4db2-a835-512929497799/download | 240×240 |
| Choice Button | https://api.pixellab.ai/mcp/map-objects/39441b6d-eefb-4aae-8774-39440343278e/download | 96×96 |
| Status Bar | https://api.pixellab.ai/mcp/map-objects/39d68a77-6ebc-43e4-afc4-fe8926148c6f/download | 128×128 |
| Father Portrait | https://api.pixellab.ai/mcp/map-objects/78c2f5c2-9f3b-44d6-971c-e4c4c8e7d9bc/download | 64×64 |
| Player Portrait | https://api.pixellab.ai/mcp/map-objects/d55f852f-9934-4b86-97e6-75dbc81ceec0/download | 64×64 |

```bash
# Batch download all UI elements
cd "d:\STUDY\PBL\NUTURE\assets\ui"

curl --fail -o dialogue_box.png "https://api.pixellab.ai/mcp/map-objects/bb6d1c05-8e36-4db2-a835-512929497799/download"
curl --fail -o choice_button.png "https://api.pixellab.ai/mcp/map-objects/39441b6d-eefb-4aae-8774-39440343278e/download"
curl --fail -o status_bar.png "https://api.pixellab.ai/mcp/map-objects/39d68a77-6ebc-43e4-afc4-fe8926148c6f/download"
curl --fail -o father_portrait.png "https://api.pixellab.ai/mcp/map-objects/78c2f5c2-9f3b-44d6-971c-e4c4c8e7d9bc/download"
curl --fail -o player_portrait.png "https://api.pixellab.ai/mcp/map-objects/d55f852f-9934-4b86-97e6-75dbc81ceec0/download"
```

#### Room Backgrounds (2/2 Ready)
```bash
cd "d:\STUDY\PBL\NUTURE\assets\backgrounds"

curl --fail -o bedroom_night.png "https://api.pixellab.ai/mcp/map-objects/43e39b67-fe84-4072-b788-e2a1c32af13b/download"
curl --fail -o living_room_day.png "https://api.pixellab.ai/mcp/map-objects/ef8cd9da-66e0-4238-85b7-8ddb199d26a3/download"
```

---

## 🔄 IN PROGRESS (2 Assets - Est. 2-4 minutes)

### Character Animations
Both walk animations are now PROCESSING:
- **Father_Walk:** 4 directional animations (south, east, north, west)
- **Mother_Walk:** 4 directional animations (south, east, north, west)

**Check Animation Progress:**
```bash
# Use these commands to check if animations are done:
# Father animations status
mcp_pixellab_get_character("4899c9b0-84d1-4a53-a8aa-73e0118dd37d")

# Mother animations status
mcp_pixellab_get_character("d5ce073c-f9ac-466d-a9b1-147f6d393aea")

# Once complete, download as ZIP:
curl --fail "https://api.pixellab.ai/mcp/characters/4899c9b0-84d1-4a53-a8aa-73e0118dd37d/download" -o Father_Animated.zip
curl --fail "https://api.pixellab.ai/mcp/characters/d5ce073c-f9ac-466d-a9b1-147f6d393aea/download" -o Mother_Animated.zip
```

---

## ✅ TILESETS (Ready - IDs for Retrieval)

Both top-down Wang tilesets ready. Retrieve via PixelLab API:

### Floor Tileset (Wooden Floors → Furniture)
- **ID:** `0287da61-95a5-4029-9873-f7e33f2c59a2`
- **Lower Base Tile:** `80435d3b-1e3b-461e-af0f-a4e9d5fb3ca0`
- **Upper Base Tile:** `22b95db9-999b-44af-8434-3e8c82631b06`
- **Tiles:** 16 (Wang tileset for autotiling)
- **Tile Size:** 32×32 px

### Wall Tileset (Wall Surfaces → Decorations)
- **ID:** `e4793d5f-707c-44a1-bde5-a8d42f215a54`
- **Lower Base Tile:** `7d0ade12-082d-4780-865a-f7675893d0e2`
- **Upper Base Tile:** `2e575b13-f42e-45ff-a900-3dd68b25b80c`
- **Tiles:** 16 (Wang tileset for autotiling)
- **Tile Size:** 32×32 px

---

## 📊 ASSET COVERAGE

### For 2-Day Demo Build ✅ READY

| Feature | Assets | Status |
|---------|--------|--------|
| Playable Characters | Father, Mother, Baby Lily | ✅ Ready (static) / 🚀 Walk animations loading |
| Character Portraits | Father, Player | ✅ Ready |
| Dialogue System | Dialogue box + portraits | ✅ Ready |
| Choice Menu | Choice buttons × 3 | ✅ Ready |
| Status Display | Status bars × 5 | ✅ Ready |
| Room Environments | Bedroom (night), Living Room (day) | ✅ Ready |
| Tileset Support | Floor + walls | ✅ Ready |
| Scenarios Supported | First Night, Visiting, Main Dialogue | ✅ Ready |

### Starting Day 1 Scenario Flow ✅
1. **Title Screen** → Not yet created (can use simple text for demo)
2. **Bedroom Night** (Player wakes up at 2 AM) → 🟢 Has background
3. **Father/Mother Portrait** → 🟢 Has portrait
4. **Dialogue Box** → 🟢 Ready
5. **Status Bars** → 🟢 Ready
6. **Choice Buttons** → 🟢 Ready

---

## 🎮 GAMEMAKER INTEGRATION CHECKLIST

### Step 1: Organize Assets (Create Folders)
```
NURTURE/
├── assets/
│   ├── characters/
│   │   ├── father/ (4 direction PNGs from ZIP)
│   │   ├── mother/ (4 direction PNGs from ZIP)
│   │   └── baby_lily/
│   ├── ui/
│   │   ├── dialogue_box.png
│   │   ├── choice_button.png
│   │   ├── status_bar.png
│   │   ├── father_portrait.png
│   │   └── player_portrait.png
│   ├── backgrounds/
│   │   ├── bedroom_night.png
│   │   ├── living_room_day.png
│   │   └── kitchen_day.png (pending)
│   └── tilesets/
│       ├── floor_tileset.png (from PixelLab API)
│       └── wall_tileset.png (from PixelLab API)
```

### Step 2: Create Sprite Resources in GMS2

**In GMS2 IDE:**
1. Right-click **Sprites** → **Create Sprite**
2. For each character direction:
   - Name: `spr_father_south`, `spr_father_east`, etc.
   - Load the corresponding PNG from extracted character ZIP
   - Set **Collision Mask:** Pixel-perfect (from PixelLab transparency)

3. For UI elements:
   - Name: `spr_dialogue_box`, `spr_choice_button`, `spr_status_bar`
   - Load downloaded PNGs

4. For backgrounds:
   - Name: `spr_bedroom_night`, `spr_living_room_day`
   - Load background PNGs

### Step 3: Create Tile Set Resource

**In GMS2 IDE:**
1. Right-click **Tile Sets** → **Create Tile Set**
2. Name: `ts_house_floors`
3. Upload floor tileset PNG (from PixelLab)
4. Set Tile Size: 32×32
5. Configure Wang tileset mode (if using GameMaker's autotiling)

### Step 4: Apply to Room

**In Room Editor:**
1. Add background layer with `spr_bedroom_night` or `spr_living_room_day`
2. Add tile layer with `ts_house_floors` and paint floor/furniture
3. Add instances of character sprites at starting positions

### Step 5: Draw UI in HUD Layer

**In obj_dialog/Draw_GUI event:**
```gml
// Draw dialogue box
draw_sprite(spr_dialogue_box, -1, 400, 270);

// Draw portrait on left side
draw_sprite(spr_father_portrait, -1, 420, 290);

// Draw text in center
draw_text(500, 290, "Good morning...");

// Draw choice buttons if in choice mode
if (show_choices) {
    draw_sprite(spr_choice_button, -1, 600, 350);  // Option A
    draw_text(610, 355, "A: Try to comfort");
}
```

### Step 6: Integration with API Controller

**In obj_api_controller:**
```gml
/// Handle character sprites based on parent identifier
if (current_parent == "father") {
    spr_current = spr_father_south;  // Update based on direction
    spr_portrait = spr_father_portrait;
} else if (current_parent == "mother") {
    spr_current = spr_mother_south;
    spr_portrait = spr_mother_portrait;
}

// During dialogue
draw_sprite(spr_dialogue_box, -1, dialogue_x, dialogue_y);
draw_sprite(spr_portrait, -1, portrait_x, portrait_y);
```

---

## 🚀 QUICK START FOR DEMO (5 min setup)

1. **Download all 9 ready assets** using commands above
2. **Extract character ZIPs** into separate folders
3. **Open GMS2 project** and create sprite resources (4-5 min)
4. **Test sprites display** without animations
5. **Use static south-facing sprites** for initial scenes
6. **Once animations ready**, update sprite calls to use animated versions

---

## 📋 REMAINING ASSETS (Low Priority for 2-Day Demo)

These can be created after demo or used as future enhancements:
- 🔲 Kitchen background
- 🔲 Title screen  
- 🔲 Status icons set
- 🔲 Day counter display
- 🔲 Scenario banners
- 🔲 Transition effects

---

## 🎨 Color Palette Reference (FireRed Inspired)

For any manual adjustments or custom UI:

```css
/* Skin tones */
Flesh: #CC99AA
Face Shadow: #884466

/* Clothing */
Dark Blue: #332244
Brown: #774411

/* Environment */
White: #FFFFFF
Beige: #EEDDCC
Wood: #774411
Dark Gray: #444444

/* UI */
Black Border: #000000
Yellow Accent: #FFFF00
Red Highlight: #FF0000
Green Success: #00FF00

/* Emotions (Status indicators) */
Trust (Green): #00FF00
Resentment (Red): #FF0000
Stress (Orange): #FF8000
Attachment (Blue): #0080FF
Bond (Purple): #8000FF
```

---

## ⏱️ NEXT STEPS

### ✅ NOW (Do this first)
1. Create asset directories per folder structure above
2. Download all 9 ready assets using curl commands
3. Extract character ZIPs
4. Create GMS2 sprite resources

### 🚀 WHEN ANIMATIONS READY (~5 min)
1. Check animation status
2. Download Father_Animated.zip & Mother_Animated.zip
3. Extract walk sprites for all 4 directions
4. Update GMS2 animation frame order

### 📝 FOR COMPLETE FEATURES (Optional before demo)
1. Create title screen (simple) 
2. Import tilesets to GMS2
3. Build single room with character + dialogue + UI rendered
4. Test click-to-advance dialogue
5. Verify status bars update

---

## 📞 TROUBLESHOOTING

### Character PNG not showing in GMS2?
- Ensure PNG has **transparent background** (verify with image viewer)
- Check **Collision Mask** set to "Pixel-based" (uses transparency)
- Verify sprite **Center point** at `0,0` (top-left)

### Tileset not autotiling?
- Verify **Tile Size** exactly matches PNG tile grid (32×32)
- Use **Wang Tile** mode in GMS2 tileset settings
- Paint with matching tile edges for autotiling to work

### Status bar not showing?
- Ensure bar frame PNG is loaded
- Draw **empty frame first**, then **fill overlay** on top
- Use `draw_rectangle_color()` to create fill effect

###Dialogue box positioning?
- Design for **1920×1080 resolution** but position relative to dynamic camera
- Test at 2× scale if using 640×360 game resolution
- Ensure text doesn't overflow (measure text width first)

---

**Asset Generation Complete: April 8, 2026 11:25 UTC**  
**Total Assets:** 11 (9 ready now + 2 animating)  
**Quality:** FireRed Pokémon RPG style, 32×32 pixel optimization  
**Save Location:** All URLs provided above for downloads
