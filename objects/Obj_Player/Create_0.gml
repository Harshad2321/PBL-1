move_speed = 0.5;
var lay_outer = layer_tilemap_get_id("Outer_Walls");

var lay_bed   = layer_tilemap_get_id("Bedroom_walls");

tilemap = [lay_outer, lay_bed];

// Use new Father sprites
sprite_index = spr_father_south;
image_xscale = 4.352941;      // Match room scale
image_yscale = 3.2941177;

// Track current direction
current_direction = "south";

