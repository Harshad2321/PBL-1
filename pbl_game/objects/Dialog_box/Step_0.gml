if (!surface_exists(dialog_surface)) {
    
    dialog_surface = surface_create(boxw, boxh);
    
    surface_set_target(dialog_surface);

    draw_set_color(make_color_rgb(20, 20, 40));
    draw_roundrect(0, 0, boxw, boxh, false);

    draw_set_color(c_white);
    draw_roundrect(0, 0, boxw, boxh, true);

    surface_reset_target();

    spr_box = dialog_surface;
}