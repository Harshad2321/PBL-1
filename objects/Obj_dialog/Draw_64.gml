var _x = 40;
var _y = gui_h * 0.25;
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

    var _content_left = _panel_x + 26;
    var _content_right = _panel_x + _panel_w - 26;
    var _row_y = _panel_y + 98;
    var _row_gap = clamp(_panel_h * 0.11, 52, 64);

    var _gap = 12;
    var _label_col_w = clamp(_panel_w * 0.22, 120, 180);
    var _value_col_w = clamp(_panel_w * 0.14, 86, 118);
    var _delta_col_w = clamp(_panel_w * 0.18, 102, 150);

    var _label_right = _content_left + _label_col_w;
    var _delta_left = _content_right - _delta_col_w;
    var _value_left = _delta_left - _gap - _value_col_w;

    var _bar_x = _label_right + _gap;
    var _bar_right = _value_left - _gap;

    if (_bar_right < _bar_x + 140)
    {
        _label_right = max(_content_left + 90, _bar_right - 140 - _gap);
        _bar_x = _label_right + _gap;
    }

    var _bar_w = max(120, _bar_right - _bar_x);
    var _value_right = _value_left + _value_col_w - 2;
    var _delta_right = _content_right - 2;
    var _bar_h = 18;

    var _labels = ["Trust", "Resentment", "Closeness", "Stress"];
    var _values = [obj_controller.summary_trust, obj_controller.summary_resentment, obj_controller.summary_closeness, obj_controller.summary_stress];
    var _deltas = [obj_controller.summary_delta_trust, obj_controller.summary_delta_resentment, obj_controller.summary_delta_closeness, obj_controller.summary_delta_stress];
    var _higher_better = [true, false, true, false];

    for (var i = 0; i < 4; i++)
    {
        var _y0 = _row_y + (i * _row_gap);
        var _v = clamp(_values[i], 0, 1);
        var _d = _deltas[i];
        var _fill_w = _bar_w * _v;

        draw_set_colour(c_white);
        draw_set_halign(fa_right);
        draw_text(_label_right, _y0, _labels[i]);

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
        draw_set_halign(fa_right);
        draw_set_colour(make_colour_rgb(220, 228, 245));
        draw_text(_value_right, _y0, string_format(_v, 1, 2));

        var _good = ((_higher_better[i] && _d > 0.001) || (!_higher_better[i] && _d < -0.001));
        var _bad = ((_higher_better[i] && _d < -0.001) || (!_higher_better[i] && _d > 0.001));

        var _delta_col = make_colour_rgb(190, 190, 190);
        if (_good) _delta_col = c_lime;
        if (_bad) _delta_col = c_red;

        var _prefix = "";
        if (_d > 0.001) _prefix = "+";

        draw_set_colour(_delta_col);
        draw_text(_delta_right, _y0, "(" + _prefix + string_format(_d, 1, 2) + ")");
    }

    var _summary_hint = "";
    if (obj_controller.day_summary_waiting)
    {
        draw_set_colour(make_colour_rgb(180, 210, 255));
        _summary_hint = "Loading next day...";
    }
    else
    {
        draw_set_colour(c_yellow);
        _summary_hint = "Next day starts automatically (ENTER/SPACE/F5 to speed up)";
    }

    draw_set_halign(fa_left);
    draw_text_ext(_content_left, _panel_y + _panel_h - 88, _summary_hint, 30, _content_right - _content_left);

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
draw_set_halign(fa_left);
draw_set_valign(fa_top);

var _line_sep_text = 30;
var _line_sep_choice = 26;
var _choice_gap = 8;

var _full_text = string(obj_controller.scenario_text);
var _typed_text = _full_text;

if (scenario_type_source == _full_text)
{
    _typed_text = scenario_type_visible;
}

var _choices = [];
var _choice_block_h = 0;

if (obj_controller.game_mode == "scenario")
{
    _choices = obj_controller.choices;

    if (array_length(_choices) == 0)
    {
        _choice_block_h = string_height_ext("Loading choices...", _line_sep_choice, _width);
    }
    else
    {
        for (var i = 0; i < array_length(_choices); i++)
        {
            var _choice_label = string(i + 1) + ". " + string(_choices[i]);
            _choice_block_h += string_height_ext(_choice_label, _line_sep_choice, _width);

            if (i < array_length(_choices) - 1)
            {
                _choice_block_h += _choice_gap;
            }
        }
    }

    _choice_block_h += 12;
}

var _max_text_h = (gui_h - 30) - _y - _choice_block_h - 10;
if (_max_text_h < 80) _max_text_h = 80;

var _display_text = _typed_text;
var _text_truncated = false;

if (string_length(_display_text) > 0 && string_height_ext(_display_text, _line_sep_text, _width) > _max_text_h)
{
    var _lo = 1;
    var _hi = string_length(_display_text);
    var _fit = 1;

    while (_lo <= _hi)
    {
        var _mid = (_lo + _hi) div 2;
        var _probe = string_copy(_display_text, 1, _mid);

        if (string_height_ext(_probe, _line_sep_text, _width) <= _max_text_h)
        {
            _fit = _mid;
            _lo = _mid + 1;
        }
        else
        {
            _hi = _mid - 1;
        }
    }

    _display_text = string_copy(_display_text, 1, max(1, _fit));
    if (_fit < string_length(_typed_text))
    {
        _display_text += "...";
        _text_truncated = true;
    }
}

draw_text_ext(_x, _y, _display_text, _line_sep_text, _width);

var _text_height = 0;
if (_display_text != "")
{
    _text_height = string_height_ext(_display_text, _line_sep_text, _width);
}

var _choice_y = clamp(_y + _text_height + 16, _y + 44, gui_h - 24 - _choice_block_h);

// ==========================
// CHOICES / LOADING
// ==========================
if (obj_controller.game_mode == "scenario")
{
    if (array_length(_choices) == 0)
    {
        draw_set_colour(c_gray);
        draw_text_ext(_x, _choice_y, "Loading choices...", _line_sep_choice, _width);
    }
    else
    {
        var _draw_choice_y = _choice_y;

        for (var i = 0; i < array_length(_choices); i++)
        {
            var _choice_text = string(i + 1) + ". " + string(_choices[i]);

            draw_set_colour(c_yellow);
            draw_text_ext(_x, _draw_choice_y, _choice_text, _line_sep_choice, _width);

            _draw_choice_y += string_height_ext(_choice_text, _line_sep_choice, _width) + _choice_gap;
        }
    }
}

draw_set_colour(c_white);


