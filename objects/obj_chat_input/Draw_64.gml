if (!visible) exit;
if (!instance_exists(obj_controller)) exit;
if (obj_controller.game_mode != "chat") exit;

// Safe defaults so Draw never crashes on missing fields
if (!variable_instance_exists(id, "chat_history")) chat_history = [];
if (!variable_instance_exists(id, "input_string")) input_string = "";
if (!variable_instance_exists(id, "cursor_visible")) cursor_visible = true;

var gw = display_get_gui_width();
var gh = display_get_gui_height();

// Bottom panel
var panel_h = gh * 0.40;
var panel_y = gh - panel_h;

draw_set_color(c_black);
draw_set_alpha(0.85);
draw_rectangle(0, panel_y, gw, gh, false);
draw_set_alpha(1);

// Chat text
draw_set_font(-1);
draw_set_halign(fa_left);
draw_set_valign(fa_top);

var line_h = 20;
var max_lines = floor((panel_h - 90) / line_h);
var start_i = max(0, array_length(chat_history) - max_lines);

for (var i = start_i; i < array_length(chat_history); i++) {
	var e = chat_history[i];
	var yy = panel_y + 10 + ((i - start_i) * line_h);

	var speaker = "";
	var text = "";
	if (is_struct(e)) {
		if (variable_struct_exists(e, "speaker")) speaker = string(e.speaker);
		if (variable_struct_exists(e, "text")) text = string(e.text);
	}

	draw_set_color(c_aqua);
	draw_text(20, yy, speaker + ": ");

	draw_set_color(c_white);
	draw_text(20 + string_width(speaker + ": "), yy, text);
}

// Input box
var box_y = gh - 58;
draw_set_color(c_dkgray);
draw_rectangle(10, box_y, gw - 10, box_y + 40, false);

draw_set_color(c_white);
draw_rectangle(10, box_y, gw - 10, box_y + 40, true);

var shown = input_string;
if (cursor_visible) shown += "|";
draw_text(20, box_y + 10, shown);

draw_set_color(c_gray);
draw_set_halign(fa_center);
draw_text(gw * 0.5, panel_y - 20, "Press Enter to send");

// Reset draw state
draw_set_halign(fa_left);
draw_set_valign(fa_top);
draw_set_color(c_white);
draw_set_alpha(1);