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

var margin_x = 20;
var chat_w = gw - (margin_x * 2);
var line_sep = 24;
var msg_gap = 6;

var box_y = gh - 58;
var chat_top_y = panel_y + 10;
var chat_h = max(30, box_y - chat_top_y - 10);

var total_msgs = array_length(chat_history);
var start_i = 0;
var used_h = 0;

for (var j = total_msgs - 1; j >= 0; j--)
{
    var _entry = chat_history[j];
    var _speaker = "";
    var _text = "";

    if (is_struct(_entry))
    {
        if (variable_struct_exists(_entry, "speaker")) _speaker = string(_entry.speaker);
        if (variable_struct_exists(_entry, "text")) _text = string(_entry.text);
    }

    var _prefix = _speaker + ": ";
    var _text_x = margin_x + string_width(_prefix);
    var _wrap_w = max(80, (margin_x + chat_w) - _text_x);
    var _msg_h = max(line_sep, string_height_ext(_text, line_sep, _wrap_w));
    var _block_h = _msg_h + msg_gap;

    if (used_h + _block_h > chat_h)
    {
		start_i = (used_h <= 0) ? j : (j + 1);
        break;
    }

    used_h += _block_h;
    start_i = j;
}

if (start_i < 0) start_i = 0;
if (start_i > total_msgs) start_i = total_msgs;

var yy = chat_top_y;

for (var i = start_i; i < array_length(chat_history); i++) {
	var e = chat_history[i];

	var speaker = "";
	var text = "";
	if (is_struct(e)) {
		if (variable_struct_exists(e, "speaker")) speaker = string(e.speaker);
		if (variable_struct_exists(e, "text")) text = string(e.text);
	}

	var prefix = speaker + ": ";
	var text_x = margin_x + string_width(prefix);
	var wrap_w = max(80, (margin_x + chat_w) - text_x);
	var original_len = string_length(text);
	var msg_h = max(line_sep, string_height_ext(text, line_sep, wrap_w));
	var remaining_h = (chat_top_y + chat_h) - yy;

	if (remaining_h <= 0) break;

	if (msg_h > remaining_h)
	{
		var lo = 1;
		var hi = string_length(text);
		var fit = 0;

		while (lo <= hi)
		{
			var mid = (lo + hi) div 2;
			var probe = string_copy(text, 1, mid);
			if (string_height_ext(probe, line_sep, wrap_w) <= remaining_h)
			{
				fit = mid;
				lo = mid + 1;
			}
			else
			{
				hi = mid - 1;
			}
		}

		if (fit <= 0) break;

		text = string_copy(text, 1, fit);
		if (fit < original_len) text += "...";
		msg_h = max(line_sep, string_height_ext(text, line_sep, wrap_w));
	}

	draw_set_color(c_aqua);
	draw_text(margin_x, yy, prefix);

	draw_set_color(c_white);
	draw_text_ext(text_x, yy, text, line_sep, wrap_w);

	yy += msg_h + msg_gap;
}

// Input box
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