
var _dx = 0;
var _dy = gui_h * 0.7;
var _boxw = gui_w;
var _boxh = gui_h - _dy;

var head_x;
var head_y = gui_h * 0.975;
var head_scale = 0.5;

// Decide position + scale
switch (messages[current_message].name)
{
	case "Dad":
		head_x = 80;
		head_scale = dad_scale;
		break;

	case "Mom":
		head_x = gui_w - 180;
		head_scale = mom_scale;
		break;

	case "Main":
		head_x = 80;
		head_scale = main_scale;
		break;
}

// Draw
if (current_head != -1)
{
	draw_sprite_ext(current_head, 0, head_x, head_y, head_scale, head_scale, 0, c_white, 1);
}

draw_surface_stretched(spr_box,_dx, _dy, _boxw, _boxh);

_dx += 16;
_dy += 16;

draw_set_font(Font1);

var _name = messages[current_message].name;
draw_set_colour(global.char_colors[$ _name]);
draw_text(_dx, _dy, _name);
draw_set_colour(c_white);

_dy += 40;

draw_text_ext(_dx, _dy, draw_message, -1, _boxw - _dx * 2);

