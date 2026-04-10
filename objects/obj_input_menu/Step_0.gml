// Handle menu input
if (menu_active && array_length(options) > 0) {
    // Arrow keys: select option
    if (keyboard_check_pressed(vk_up)) {
        selected_option = max(0, selected_option - 1);
    }
    if (keyboard_check_pressed(vk_down)) {
        selected_option = min(array_length(options) - 1, selected_option + 1);
    }
    
    // Enter: select current option and send to API
    if (keyboard_check_pressed(vk_space) || keyboard_check_pressed(vk_enter)) {
        var chosen_text = options[selected_option];
        send_to_api(chosen_text);
        menu_active = false;
        waiting_response = true;
    }
}
