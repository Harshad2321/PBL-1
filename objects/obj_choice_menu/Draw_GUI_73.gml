var _gui_width = display_get_gui_width();
var _gui_height = display_get_gui_height();

// Draw scenario text at top
draw_set_color(c_white);
draw_set_font(-1);
draw_set_halign(fa_center);
draw_set_valign(fa_top);

// Word-wrapped scenario text
var _scenario_x = _gui_width / 2;
var _scenario_y = 100;
var _wrap_width = 700;
draw_text_ext(_scenario_x, _scenario_y, global.current_scenario, 24, _wrap_width);

// Draw choice buttons
var _choices = [global.choice0, global.choice1, global.choice2];

for (var i = 0; i < 3; i++) {
    var _is_hovered = (choice_hover == i + 1);
    
    // Button background
    if (_is_hovered) {
        draw_set_color(c_dkgray);
    } else {
        draw_set_color(c_black);
    }
    draw_set_alpha(0.75);
    draw_rectangle(btn_x, btn_y[i], btn_x + btn_w, btn_y[i] + btn_h, false);
    draw_set_alpha(1);
    
    // Button outline
    draw_set_color(c_white);
    draw_rectangle(btn_x, btn_y[i], btn_x + btn_w, btn_y[i] + btn_h, true);
    
    // Button text
    draw_set_halign(fa_center);
    draw_set_valign(fa_middle);
    draw_text_ext(btn_x + btn_w / 2, btn_y[i] + btn_h / 2, _choices[i], 18, btn_w - 20);
}

// Reset draw settings
draw_set_halign(fa_left);
draw_set_valign(fa_top);
draw_set_alpha(1);
