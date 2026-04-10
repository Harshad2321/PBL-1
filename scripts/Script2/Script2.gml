function create_dialog_box(w, h) {
    var surf = surface_create(w, h);

    surface_set_target(surf);

    draw_set_color(make_color_rgb(20, 20, 40));
    draw_roundrect(0, 0, w, h, false);

    draw_set_color(c_white);
    draw_roundrect(0, 0, w, h, true);

    surface_reset_target();

    return surf;
}