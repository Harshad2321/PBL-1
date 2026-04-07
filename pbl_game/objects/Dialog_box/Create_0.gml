// Create a surface (like a drawable image)
boxw = 600;
boxh = 120;

dialog_surface = surface_create(boxw, boxh);

// Draw onto the surface ONCE
surface_set_target(dialog_surface);

// Background
draw_set_color(make_color_rgb(20, 20, 40));
draw_roundrect(0, 0, boxw, boxh, false);

// Border
draw_set_color(c_white);
draw_roundrect(0, 0, boxw, boxh, true);

// Reset target
surface_reset_target();

// Assign like sprite
spr_box = dialog_surface;