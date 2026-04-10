input_string    = "";
display_reply   = "";
cursor_visible  = true;
cursor_timer    = 0;
max_input_chars = 120;
chat_history    = array_create(0);  // Start with empty array
array_push(chat_history, {speaker: "Mother", text: "Hello! What would you like to talk about?"});
keyboard_string = "";
visible         = false;
