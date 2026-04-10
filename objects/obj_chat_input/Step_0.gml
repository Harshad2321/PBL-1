// ONLY RUN IN CHAT MODE
if (obj_controller.game_mode != "chat") exit;


// ==========================
// CURSOR BLINK
// ==========================
cursor_timer++;
if (cursor_timer >= 30) {
    cursor_visible = !cursor_visible;
    cursor_timer = 0;
}


// ==========================
// INPUT CAPTURE
// ==========================
input_string += keyboard_string;
keyboard_string = "";


// ==========================
// LIMIT INPUT LENGTH
// ==========================
if (string_length(input_string) > max_input_chars) {
    input_string = string_copy(input_string, 1, max_input_chars);
}


// ==========================
// BACKSPACE
// ==========================
if (keyboard_check_pressed(vk_backspace)) {
    if (string_length(input_string) > 0) {
        input_string = string_copy(input_string, 1, string_length(input_string) - 1);
    }
}


// ==========================
// ENTER → SEND MESSAGE
// ==========================
if (keyboard_check_pressed(vk_return)) 
{
    if (input_string != "") 
    {
        global.pending_message = input_string;

        show_debug_message("MESSAGE STORED: " + global.pending_message);

        input_string = "";
    }
}