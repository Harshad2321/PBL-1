# NURTURE - Sprite Pack & Asset Inventory
## Generated with PixelLab MCP Server
**Generated Date:** April 8, 2026  
**Project:** NURTURE (Parenting Relationship Simulator)  
**Engine:** GameMaker Studio 2  
**Style:** Pokémon FireRed 2D RPG

---

## 📋 ASSET STATUS SUMMARY

### ✅ CHARACTERS (Ready - 48x48px canvas)
| Asset | ID | Status | Details |
|-------|-----|--------|---------|
| Father Sprite | `4899c9b0-84d1-4a53-a8aa-73e0118dd37d` | ✅ Ready | 4 directions, tired but caring expression |
| Mother Sprite | `d5ce073c-f9ac-466d-a9b1-147f6d393aea` | ✅ Ready | 4 directions, exhausted but warm look |
| Baby Lily | `ee37043e-70f8-47cc-9e27-f2f1180d7fb0` | ✅ Ready | 24x24px canvas, simple baby design |

**Download All Characters:**
```bash
# Father
curl --fail "https://api.pixellab.ai/mcp/characters/4899c9b0-84d1-4a53-a8aa-73e0118dd37d/download" -o Father.zip

# Mother
curl --fail "https://api.pixellab.ai/mcp/characters/d5ce073c-f9ac-466d-a9b1-147f6d393aea/download" -o Mother.zip

# Baby Lily
curl --fail "https://api.pixellab.ai/mcp/characters/ee37043e-70f8-47cc-9e27-f2f1180d7fb0/download" -o BabyLily.zip
```

---

### ⏳ CHARACTER ANIMATIONS (In Progress - Est. 2-4 minutes)
| Animation | Character | Template | Status |
|-----------|-----------|----------|--------|
| Father_Walk | Father | walk | 🚀 Processing (4 directions) |
| Mother_Walk | Mother | walk | 🚀 Processing (4 directions) |
| Baby_Idle | Baby Lily | breathing-idle | ⏳ Pending (job slots available after walk completes) |

**Action:** Check status in 2-4 minutes, then queue Baby_Idle animation.

---

### ✅ TILESETS (Ready)
| Tileset | ID | Status | Type | Details |
|---------|-----|--------|------|---------|
| House Floor & Furniture | `0287da61-95a5-4029-9873-f7e33f2c59a2` | ✅ Ready | Top-Down | Wooden floors → furniture (16 tiles, 0.5 transition) |
| Walls & Decorations | `e4793d5f-707c-44a1-bde5-a8d42f215a54` | ✅ Ready | Top-Down | Wall surfaces → decorations (16 tiles, 0.25 transition) |

**Base Tile IDs (for creating connected tilesets):**
- Floor Lower: `80435d3b-1e3b-461e-af0f-a4e9d5fb3ca0`
- Floor Upper: `22b95db9-999b-44af-8434-3e8c82631b06`
- Wall Lower: `7d0ade12-082d-4780-865a-f7675893d0e2`
- Wall Upper: `2e575b13-f42e-45ff-a900-3dd68b25b80c`

**Check Status:**
```bash
# Make GET requests to retrieve tilesets
mcp_pixellab_get_tileset(tileset_id="0287da61-95a5-4029-9873-f7e33f2c59a2")
mcp_pixellab_get_tileset(tileset_id="e4793d5f-707c-44a1-bde5-a8d42f215a54")
```

---

### ✅ UI ELEMENTS (Ready)
| UI Element | ID | Size | Status | Purpose |
|------------|-----|------|--------|---------|
| Dialogue Box | `bb6d1c05-8e36-4db2-a835-512929497799` | 240×240 | ✅ Ready | Bottom-screen dialogue frame |
| Choice Button | `39441b6d-eefb-4aae-8774-39440343278e` | 96×96 | ✅ Ready | For A/B/C choice menu |
| Status Bar Frame | `39d68a77-6ebc-43e4-afc4-fe8926148c6f` | 128×128 | ✅ Ready | Bar background for stats |
| Father Portrait | `78c2f5c2-9f3b-44d6-971c-e4c4c8e7d9bc` | 64×64 | ✅ Ready | Dialogue portrait (warm expression) |
| Player Portrait | `d55f852f-9934-4b86-97e6-75dbc81ceec0` | 64×64 | ✅ Ready | Dialogue portrait (concerned expression) |

---

### ✅ ROOM BACKGROUNDS (Ready)
| Background | ID | Size | Status | Purpose |
|------------|-----|------|--------|---------|
| Bedroom Night | `43e39b67-fe84-4072-b788-e2a1c32af13b` | 320×320 | ✅ Ready | First night home scene with crib, moon, lamp |
| Living Room Day | `ef8cd9da-66e0-4238-85b7-8ddb199d26a3` | 320×320 | ✅ Ready | Main dialogue area with sofa, TV, kitchen door |

---

## 📦 REMAINING ASSETS TO CREATE

### Title Screen (Max 400×360px)
- **Status:** Not Started
- **Description:** Needs custom creation due to size constraints
- **Components:** Logo, subtitle, "Press START" text

### Kitchen Background (320×180)
- **Status:** Not Started
- **Description:** Daytime kitchen with counter, appliances, dining area

### Small UI Icons (16×16 each)
- **Status:** Not Started
- **Icons Needed:**
  - Heart (Trust)
  - Lightning (Resentment)
  - Sweat Drop (Stress)
  - Music Note (Happiness)
  - Heart+ (Bond Strength)

### Day Counter Display (64×32)
- **Status:** Not Started
- **Description:** "DAY 1" display box

### Input Cursor (8×16)
- **Status:** Not Started
- **Description:** Blinking text cursor

### Scenario Banners (256×32 each)
- **Status:** Not Started
- **Scenarios:** "First Night Home", "Visitors Arrive", "Money Talk", etc.

---

## 🎮 USAGE INSTRUCTIONS FOR GAMEMAKER STUDIO 2

### 1. Import Character Sprites
```gml
// In obj_api_controller or equivalent:
// Download and extract character ZIPs
// Create sprite resources from PNG files
spr_father = sprite_add("path/to/father/south.png", 1, false, false, 0, 0);
spr_mother = sprite_add("path/to/mother/south.png", 1, false, false, 0, 0);
spr_baby = sprite_add("path/to/baby/south.png", 1, false, false, 0, 0);
```

### 2. Apply Tilesets to Room
- Export tilesets from PixelLab
- Create tileset resources in GMS2
- Apply to Room1 or environment
- Use Wang tileset autotiling for seamless transitions

### 3. Add UI Elements
```gml
// Dialogue box example:
draw_sprite(spr_dialogue_box, -1, x, y);
draw_text(x + 80, y + 10, dialogue_text);
```

### 4. Implement Status Bars
```gml
// Status bar example (0-100 scale):
fill_width = (trust / 100) * 128; // max bar width
draw_sprite(spr_status_bar_frame, -1, x, y);
draw_rectangle_color(x + 2, y + 2, x + 2 + fill_width, y + 14, c_green, c_green, c_green, c_green, false);
```

---

## ⏱️ TIMELINE & NEXT STEPS

### Immediate (< 5 minutes) - CHARACTER ANIMATIONS PROCESSING
- ✅ Father walk animation - PROCESSING (4 directions)
- ✅ Mother walk animation - PROCESSING (4 directions)  
- ⏳ Queue Baby Lily idle after walk animations complete

### Very Soon (2-4 minutes)
- 🚀 Character animations complete
- ✅ All major assets ready for download
- 📥 Start downloading completed assets

### Medium-term (5-10 minutes)
- 📝 Create kitchen background (rate limit pending)
- 📝 Create status icons set
- 📝 Create day counter display
- 📝 Create scenario banners (if time/slots allow)

### Before 2-Day Demo (READY NOW!)
- ✅ Download all completed assets (9/11 ready now)
- ✅ Import into GMS2 project
- ✅ Test sprite integration
- ✅ Configure tileset autotiling
- ✅ Test UI rendering
- ⏳ Wait for animations to complete and download

---

## 📥 HOW TO RETRIEVE ASSETS

### For Characters:
```bash
# Use curl to download character ZIP files
# File will contain all 4 directions as PNGs
curl --fail "https://api.pixellab.ai/mcp/characters/[CHARACTER_ID]/download" -o Character.zip
```

### For Tilesets/UI Elements:
```bash
# Check status and get image URLs
mcp_pixellab_get_map_object(object_id="[OBJECT_ID]")
mcp_pixellab_get_tileset(tileset_id="[TILESET_ID]")
```

### For Animations:
```bash
# Once animations complete, retrieve via character endpoint
mcp_pixellab_get_character(character_id="[CHARACTER_ID]")
```

---

## 🎨 ASSET SPECIFICATIONS

### Color Palette (FireRed Inspired)
- **Flesh:** #CC99AA
- **Face Shadow:** #884466
- **Dark Clothing:** #332244
- **Wood Floors:** #774411
- **Walls:** #EEDDCC, #FFFFFF
- **UI Borders:** #000000
- **Text/Accents:** #000000, #FFFF00

### Transparency & Format
- **Format:** PNG with transparency
- **Compression:** Lossless
- **Background:** Transparent (alpha channel)
- **Pixel Alignment:** Crisp edges, no anti-aliasing

### Size Guidelines
- **Characters:** 32×32 canvas (character ~20px)
- **Tiles:** 32×32
- **UI Elements:** Various (64×64 for portraits, 240×64 for dialogue box)
- **Backgrounds:** 320×180 (scales to 640×360 at 2x)

---

## 🔄 STATUS CHECK COMMANDS

Use these to monitor asset generation progress:

```bash
# Check character status
mcp_pixellab_get_character("4899c9b0-84d1-4a53-a8aa-73e0118dd37d")
mcp_pixellab_get_character("d5ce073c-f9ac-466d-a9b1-147f6d393aea")
mcp_pixellab_get_character("ee37043e-70f8-47cc-9e27-f2f1180d7fb0")

# Check tileset status
mcp_pixellab_get_tileset("0287da61-95a5-4029-9873-f7e33f2c59a2")
mcp_pixellab_get_tileset("e4793d5f-707c-44a1-bde5-a8d42f215a54")

# Check UI element status
mcp_pixellab_get_map_object("bb6d1c05-8e36-4db2-a835-512929497799")
mcp_pixellab_get_map_object("39441b6d-eefb-4aae-8774-39440343278e")
# ... etc for other UI elements
```

---

## 📝 NOTES

- **Job Slot Limit:** Currently using 5/8 slots (charged per direction for animations)
- **Asset Storage:** Map objects stored for 8 hours; download promptly
- **Animation Quality:** Template animations (1 generation cost) vs Custom (20-40 generations)
- **Recommended Action:** Download all assets as they complete and test integration immediately

---5 UTC  
**Status:** 🟢 ACTIVE - Most assets ready, animations in progress  
**Next Review:** In 2-4 minutes for animation completion
**Last Updated:** 2026-04-08 11:23 UTC  
**Next Review:** After animations complete (~5-10 minutes)
