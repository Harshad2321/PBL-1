// Convert mouse position to GUI coordinates
var _mouse_gui_x = device_mouse_x_to_gui(0);
var _mouse_gui_y = device_mouse_y_to_gui(0);

choice_hover = 0;

// Check each button
for (var i = 0; i < 3; i++) {
    if (_mouse_gui_x >= btn_x && _mouse_gui_x <= btn_x + btn_w) {
        if (_mouse_gui_y >= btn_y[i] && _mouse_gui_y <= btn_y[i] + btn_h) {
            choice_hover = i + 1;
            break;
        }
    }
}
