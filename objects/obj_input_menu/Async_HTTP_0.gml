// Function to send player choice to API and get parent response
function send_to_api(player_choice) {
    var url = "http://localhost:8000/message";
    var json_data = json_stringify({
        player_choice: player_choice
    });
    
    http_post_string(url, json_data);
}

// Handle API response
function handle_api_response(json_response) {
    try {
        var response = json_parse(json_response);
        api_response = response.parent_response;
        
        // Update dialogue box with parent response
        if (instance_exists(Dialog_box)) {
            Dialog_box.dialogue_text = api_response;
            Dialog_box.show_dialogue = true;
        }
        
        waiting_response = false;
        menu_active = true;
    } catch(e) {
        show_message("API Error: " + string(e));
    }
}
