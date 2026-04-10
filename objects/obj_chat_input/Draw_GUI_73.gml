// Only draw if visible
if (!visible) exit;

// Get GUI dimensions
var _gui_width = display_get_gui_width();
var _gui_height = display_get_gui_height();

// Panel dimensions (bottom 40% of screen)
var _panel_height = _gui_height * 0.4;
var _panel_y = _gui_height - _panel_height;

// Draw dark semi-transparent panel
draw_set_color(c_black);
draw_set_alpha(0.85);
draw_rectangle(0, _panel_y, _gui_width, _gui_height, false);
draw_set_alpha(1);

// Chat history area
var _chat_area_height = _panel_height - 80;
var _line_height = 20;
var _max_visible_lines = floor(_chat_area_height / _line_height);
var _start_index = max(0, array_length(chat_history) - _max_visible_lines);

draw_set_color(c_white);
draw_set_font(-1);
draw_set_halign(fa_left);
draw_set_valign(fa_top);

// Draw chat history
for (var i = _start_index; i < array_length(chat_history); i++) {
    var _entry = chat_history[i];
    var _y_pos = _panel_y + 10 + ((i - _start_index) * _line_height);
    var _prefix_color = (_entry.speaker == "You") ? c_aqua : c_lime;
    
    draw_set_color(_prefix_color);
    draw_text(20, _y_pos, _entry.speaker + ": ");
    
    draw_set_color(c_white);
    var _prefix_width = string_width(_entry.speaker + ": ");
    draw_text(20 + _prefix_width, _y_pos, _entry.text);
}

// Input box at bottom
var _input_box_y = _gui_height - 60;
var _input_box_height = 40;

// Input box background
draw_set_color(c_dkgray);
draw_rectangle(10, _input_box_y, _gui_width - 10, _input_box_y + _input_box_height, false);

// Input box outline
draw_set_color(c_white);
draw_rectangle(10, _input_box_y, _gui_width - 10, _input_box_y + _input_box_height, true);

// Input text with cursor
draw_set_color(c_white);
var _display_text = input_string;
if (cursor_visible) {
    _display_text += "|";
}
draw_text(20, _input_box_y + 10, _display_text);

// Hint text
draw_set_color(c_gray);
draw_set_halign(fa_center);
draw_text(_gui_width / 2, _panel_y - 20, "Press Enter to send  |  Type /done to end the day");

// Reset draw settings
draw_set_halign(fa_left);
draw_set_valign(fa_top);
draw_set_color(c_white);
draw_set_alpha(1);
