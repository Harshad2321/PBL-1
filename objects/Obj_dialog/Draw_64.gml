var _x = 40;
var _y = gui_h * 0.35;
var _width = gui_w - 80;

if (!instance_exists(obj_controller)) exit;

if (obj_controller.game_mode != "scenario" && obj_controller.game_mode != "choice_feedback" && obj_controller.game_mode != "day_summary") {
    exit;
}

if (obj_controller.game_mode == "day_summary")
{
    var _sw = display_get_gui_width();
    var _sh = display_get_gui_height();
    var _panel_x = _sw * 0.15;
    var _panel_y = _sh * 0.12;
    var _panel_w = _sw * 0.70;
    var _panel_h = _sh * 0.76;

    draw_set_alpha(0.62);
    draw_set_colour(c_black);
    draw_rectangle(0, 0, _sw, _sh, false);
    draw_set_alpha(1);

    draw_set_colour(make_colour_rgb(20, 26, 38));
    draw_rectangle(_panel_x, _panel_y, _panel_x + _panel_w, _panel_y + _panel_h, false);
    draw_set_colour(c_white);
    draw_rectangle(_panel_x, _panel_y, _panel_x + _panel_w, _panel_y + _panel_h, true);

    draw_set_font(Font1);
    draw_set_halign(fa_left);
    draw_set_valign(fa_top);

    draw_set_colour(c_white);
    draw_text(_panel_x + 28, _panel_y + 24, "Day " + string(obj_controller.summary_day) + " Summary");

    var _row_y = _panel_y + 95;
    var _row_gap = 64;

    var _labels = ["Trust", "Resentment", "Closeness", "Stress"];
    var _values = [obj_controller.summary_trust, obj_controller.summary_resentment, obj_controller.summary_closeness, obj_controller.summary_stress];
    var _deltas = [obj_controller.summary_delta_trust, obj_controller.summary_delta_resentment, obj_controller.summary_delta_closeness, obj_controller.summary_delta_stress];
    var _higher_better = [true, false, true, false];

    for (var i = 0; i < 4; i++)
    {
        var _y0 = _row_y + (i * _row_gap);
        var _v = clamp(_values[i], 0, 1);
        var _d = _deltas[i];
        var _bar_x = _panel_x + 210;
        var _bar_w = _panel_w - 370;
        var _bar_h = 18;
        var _fill_w = _bar_w * _v;

        draw_set_colour(c_white);
        draw_set_halign(fa_right);
        draw_text(_bar_x - 16, _y0, _labels[i]);

        draw_set_halign(fa_left);
        draw_set_colour(make_colour_rgb(56, 66, 86));
        draw_rectangle(_bar_x, _y0 + 2, _bar_x + _bar_w, _y0 + 2 + _bar_h, false);

        var _bar_col = c_aqua;
        if (i == 0) _bar_col = c_lime;
        if (i == 1) _bar_col = c_red;
        if (i == 3) _bar_col = make_colour_rgb(255, 140, 0);

        draw_set_colour(_bar_col);
        draw_rectangle(_bar_x, _y0 + 2, _bar_x + _fill_w, _y0 + 2 + _bar_h, false);

        draw_set_colour(c_white);
        draw_rectangle(_bar_x, _y0 + 2, _bar_x + _bar_w, _y0 + 2 + _bar_h, true);
        draw_text(_bar_x + _bar_w + 12, _y0, string_format(_v, 1, 2));

        var _good = ((_higher_better[i] && _d > 0.001) || (!_higher_better[i] && _d < -0.001));
        var _bad = ((_higher_better[i] && _d < -0.001) || (!_higher_better[i] && _d > 0.001));

        var _delta_col = make_colour_rgb(190, 190, 190);
        if (_good) _delta_col = c_lime;
        if (_bad) _delta_col = c_red;

        var _prefix = "";
        if (_d > 0.001) _prefix = "+";

        draw_set_colour(_delta_col);
        draw_text(_bar_x + _bar_w + 95, _y0, "(" + _prefix + string_format(_d, 1, 2) + ")");
    }

    draw_set_halign(fa_center);
    if (obj_controller.day_summary_waiting)
    {
        draw_set_colour(make_colour_rgb(180, 210, 255));
        draw_text(_panel_x + _panel_w * 0.5, _panel_y + _panel_h - 48, "Loading next day...");
    }
    else
    {
        draw_set_colour(c_yellow);
        draw_text(_panel_x + _panel_w * 0.5, _panel_y + _panel_h - 48, "Next day starts automatically (ENTER/SPACE/F5 to speed up)");
    }

    draw_set_halign(fa_left);
    draw_set_valign(fa_top);
    draw_set_colour(c_white);
    exit;
}

// ==========================
// BACKGROUND
// ==========================
draw_set_alpha(0.7);
draw_set_colour(c_black);
draw_rectangle(_x - 20, _y - 20, _x + _width + 20, gui_h - 20, false);
draw_set_alpha(1);

// ==========================
// TEXT
// ==========================
draw_set_colour(c_white);
draw_set_font(Font1);

var full_text = obj_controller.scenario_text;
var text_height = string_height_ext(full_text, -1, _width);

draw_text_ext(_x, _y, full_text, -1, _width);

// ==========================
// CHOICES / LOADING
// ==========================
var choice_y = _y + text_height + 20;

if (obj_controller.game_mode == "scenario")
{
    var c = obj_controller.choices;

    // 🔥 LOADING STATE (IMPORTANT)
    if (array_length(c) == 0)
    {
        draw_set_colour(c_gray);
        draw_text(_x, choice_y, "Loading choices...");
    }
    else
    {
        for (var i = 0; i < array_length(c); i++)
        {
            draw_set_colour(c_yellow);
            draw_text(_x, choice_y + i * 40, string(i+1) + ". " + c[i]);
        }
    }
}


