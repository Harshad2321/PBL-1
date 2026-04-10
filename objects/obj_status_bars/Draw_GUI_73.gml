// Get GUI dimensions
var _gui_width = display_get_gui_width();
var _gui_height = display_get_gui_height();

// ==========================
// DAY SUMMARY OVERLAY
// ==========================
if (instance_exists(obj_controller) && obj_controller.game_mode == "day_summary" && !instance_exists(Obj_dialog))
{
    var _panel_w = clamp(_gui_width * 0.66, 620, 900);
    var _panel_h = clamp(_gui_height * 0.70, 420, 620);
    var _panel_x = (_gui_width - _panel_w) * 0.5;
    var _panel_y = (_gui_height - _panel_h) * 0.5;
    var _header_h = 76;

    // Backdrop
    draw_set_alpha(0.55);
    draw_set_color(c_black);
    draw_rectangle(0, 0, _gui_width, _gui_height, false);
    draw_set_alpha(1);

    // Main card
    draw_set_color(make_colour_rgb(20, 26, 38));
    draw_rectangle(_panel_x, _panel_y, _panel_x + _panel_w, _panel_y + _panel_h, false);

    // Header strip
    draw_set_color(make_colour_rgb(38, 56, 92));
    draw_rectangle(_panel_x, _panel_y, _panel_x + _panel_w, _panel_y + _header_h, false);

    // Card outline
    draw_set_color(c_white);
    draw_rectangle(_panel_x, _panel_y, _panel_x + _panel_w, _panel_y + _panel_h, true);

    draw_set_font(-1);
    draw_set_halign(fa_left);
    draw_set_valign(fa_top);

    draw_set_color(c_white);
    draw_text(_panel_x + 24, _panel_y + 18, "Day " + string(obj_controller.summary_day) + " Complete");

    draw_set_color(make_colour_rgb(195, 210, 240));
    draw_text(_panel_x + 24, _panel_y + 42, "AI Relationship Status and Daily Change");

    var _bar_x = _panel_x + 170;
    var _bar_w = _panel_w - 330;
    var _bar_h = 20;
    var _row_gap = 62;
    var _start_y = _panel_y + _header_h + 42;

    var _rows = [
        {label: "Trust", value: obj_controller.summary_trust, delta: obj_controller.summary_delta_trust, color: c_lime, higher_is_better: true},
        {label: "Resentment", value: obj_controller.summary_resentment, delta: obj_controller.summary_delta_resentment, color: c_red, higher_is_better: false},
        {label: "Closeness", value: obj_controller.summary_closeness, delta: obj_controller.summary_delta_closeness, color: c_aqua, higher_is_better: true},
        {label: "Stress", value: obj_controller.summary_stress, delta: obj_controller.summary_delta_stress, color: make_colour_rgb(255, 140, 0), higher_is_better: false}
    ];

    for (var i = 0; i < array_length(_rows); i++)
    {
        var _r = _rows[i];
        var _y = _start_y + (i * _row_gap);
        var _fill = _bar_w * clamp(_r.value, 0, 1);
        var _delta = _r.delta;

        // Label
        draw_set_color(c_white);
        draw_set_halign(fa_right);
        draw_text(_bar_x - 16, _y + 1, _r.label);

        // Value bar
        draw_set_halign(fa_left);
        draw_set_color(make_colour_rgb(54, 63, 84));
        draw_rectangle(_bar_x, _y, _bar_x + _bar_w, _y + _bar_h, false);

        draw_set_color(_r.color);
        draw_rectangle(_bar_x, _y, _bar_x + _fill, _y + _bar_h, false);

        draw_set_color(c_white);
        draw_rectangle(_bar_x, _y, _bar_x + _bar_w, _y + _bar_h, true);

        // Numeric value
        draw_set_color(make_colour_rgb(220, 228, 245));
        draw_text(_bar_x + _bar_w + 14, _y + 1, string_format(_r.value, 1, 2));

        // Delta color indicates good/bad direction, not just +/- sign.
        var _delta_col = make_colour_rgb(200, 200, 200);
        var _is_good = ((_r.higher_is_better && _delta > 0.001) || (!_r.higher_is_better && _delta < -0.001));
        var _is_bad = ((_r.higher_is_better && _delta < -0.001) || (!_r.higher_is_better && _delta > 0.001));
        if (_is_good) _delta_col = c_lime;
        if (_is_bad) _delta_col = c_red;

        var _delta_prefix = "";
        if (_delta > 0.001) _delta_prefix = "+";

        draw_set_color(_delta_col);
        draw_text(_bar_x + _bar_w + 90, _y + 1, "(" + _delta_prefix + string_format(_delta, 1, 2) + ")");
    }

    draw_set_halign(fa_center);
    if (obj_controller.day_summary_waiting)
    {
        draw_set_color(make_colour_rgb(180, 210, 255));
        draw_text(_panel_x + _panel_w * 0.5, _panel_y + _panel_h - 54, "Loading next day...");
    }
    else if (obj_controller.day_summary_ready)
    {
        draw_set_color(c_yellow);
        draw_text(_panel_x + _panel_w * 0.5, _panel_y + _panel_h - 54, "Starting next day... (Press ENTER/SPACE/F5 to continue now)");
    }
    else
    {
        draw_set_color(make_colour_rgb(180, 180, 180));
        draw_text(_panel_x + _panel_w * 0.5, _panel_y + _panel_h - 54, "Preparing summary... (auto-continue in a moment)");
    }

    draw_set_halign(fa_left);
    draw_set_valign(fa_top);
    draw_set_color(c_white);
    exit;
}

// ==========================
// COMPACT HUD (normal gameplay)
// ==========================
var x_start = _gui_width - 220;
var y_start = 20;
var bar_width = 200;
var bar_height = 16;
var bar_spacing = 28;

var _bars = [
    {label: "Trust", value: global.trust, color: c_lime},
    {label: "Resentment", value: global.resentment, color: c_red},
    {label: "Closeness", value: global.closeness, color: c_aqua},
    {label: "Stress", value: global.stress, color: make_colour_rgb(255, 140, 0)}
];

draw_set_font(-1);
draw_set_halign(fa_left);
draw_set_valign(fa_middle);

for (var j = 0; j < array_length(_bars); j++) {
    var _bar = _bars[j];
    var _y_pos = y_start + (j * bar_spacing);
    var _fill_width = bar_width * clamp(_bar.value, 0, 1);

    draw_set_color(c_dkgray);
    draw_rectangle(x_start, _y_pos, x_start + bar_width, _y_pos + bar_height, false);

    draw_set_color(_bar.color);
    draw_rectangle(x_start, _y_pos, x_start + _fill_width, _y_pos + bar_height, false);

    draw_set_color(c_white);
    draw_rectangle(x_start, _y_pos, x_start + bar_width, _y_pos + bar_height, true);

    draw_set_color(c_white);
    draw_set_halign(fa_right);
    draw_text(x_start - 10, _y_pos + bar_height / 2, _bar.label + ":");

    draw_set_halign(fa_left);
    draw_text(x_start + bar_width + 10, _y_pos + bar_height / 2, string_format(_bar.value, 1, 2));
}

draw_set_halign(fa_left);
draw_set_valign(fa_top);
draw_set_color(c_white);
