// Draw menu box and options
draw_set_alpha(0.8);
draw_rectangle_color(menu_x - menu_width/2, menu_y, menu_x + menu_width/2, menu_y + menu_height, 
                     c_black, c_black, c_black, c_black, false);
draw_set_alpha(1);

// Draw border
draw_rectangle(menu_x - menu_width/2, menu_y, menu_x + menu_width/2, menu_y + menu_height, true);

// Draw title
draw_set_color(c_yellow);
draw_text(menu_x - 200, menu_y + 10, "What do you say?");

// Draw options
draw_set_color(c_white);
for (var i = 0; i < array_length(options); i++) {
    var opt_y = menu_y + 40 + (i * 35);
    
    // Highlight selected
    if (i == selected_option) {
        draw_set_color(c_yellow);
        draw_rectangle(menu_x - 190, opt_y, menu_x + 190, opt_y + 25, false);
        draw_set_color(c_black);
    } else {
        draw_set_color(c_white);
    }
    
    draw_text(menu_x - 180, opt_y + 5, chr(65 + i) + ": " + options[i]);
}

draw_set_color(c_white);

// Draw waiting message
if (waiting_response) {
    draw_set_color(c_yellow);
    draw_text(menu_x - 150, menu_y + 130, "Waiting for parent response...");
    draw_set_color(c_white);
}
