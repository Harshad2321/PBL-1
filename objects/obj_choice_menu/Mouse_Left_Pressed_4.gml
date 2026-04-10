// Convert mouse position to GUI coordinates
var _mouse_gui_x = device_mouse_x_to_gui(0);
var _mouse_gui_y = device_mouse_y_to_gui(0);

// Check which button was clicked
var _chosen_number = -1;

for (var i = 0; i < 3; i++) {
    if (_mouse_gui_x >= btn_x && _mouse_gui_x <= btn_x + btn_w) {
        if (_mouse_gui_y >= btn_y[i] && _mouse_gui_y <= btn_y[i] + btn_h) {
            _chosen_number = i + 1;
            break;
        }
    }
}

// Send choice through obj_controller's unified function
if (_chosen_number != -1) {
    if (instance_exists(obj_controller)) {
        obj_controller.send_choice(_chosen_number);
    }
    visible = false;
}
