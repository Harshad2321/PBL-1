/// GameMaker HTTP Integration Example
/// Place this code in your GameMaker objects

// ==========================================
// CONFIGURATION
// ==========================================
global.api_url = "http://localhost:5000/api";
global.session_id = "player_" + string(random(10000));

// ==========================================
// 1. CREATE NEW GAME
// ==========================================
function create_new_game(role) {
    var url = global.api_url + "/game/new";
    var data = json_stringify({
        session_id: global.session_id,
        role: role  // "FATHER" or "MOTHER"
    });

    var headers = ds_map_create();
    ds_map_add(headers, "Content-Type", "application/json");

    var request_id = http_request(url, "POST", headers, data);

    ds_map_destroy(headers);
    return request_id;
}

// ==========================================
// 2. GET CURRENT SCENARIO
// ==========================================
function get_scenario() {
    var url = global.api_url + "/game/scenario?session_id=" + global.session_id;
    var request_id = http_get(url);
    return request_id;
}

// ==========================================
// 3. MAKE A CHOICE
// ==========================================
function make_choice(choice_num) {
    var url = global.api_url + "/game/choice";
    var data = json_stringify({
        session_id: global.session_id,
        choice_number: choice_num  // 1, 2, or 3
    });

    var headers = ds_map_create();
    ds_map_add(headers, "Content-Type", "application/json");

    var request_id = http_request(url, "POST", headers, data);

    ds_map_destroy(headers);
    return request_id;
}

// ==========================================
// 4. SEND MESSAGE TO AI PARTNER
// ==========================================
function send_message_to_ai(message_text) {
    var url = global.api_url + "/game/message";
    var data = json_stringify({
        session_id: global.session_id,
        message: message_text
    });

    var headers = ds_map_create();
    ds_map_add(headers, "Content-Type", "application/json");

    var request_id = http_request(url, "POST", headers, data);

    ds_map_destroy(headers);
    return request_id;
}

// ==========================================
// 5. GET GAME STATUS
// ==========================================
function get_game_status() {
    var url = global.api_url + "/game/status?session_id=" + global.session_id;
    var request_id = http_get(url);
    return request_id;
}

// ==========================================
// HTTP ASYNC EVENT HANDLER
// ==========================================
// Place this in the HTTP event of your controller object
/*
var response_id = async_load[? "id"];
var status = async_load[? "status"];
var result = async_load[? "result"];

if (status == 0) {  // Success
    var json_data = json_parse(result);

    // Check what type of response
    if (variable_struct_exists(json_data, "scenario")) {
        // Scenario response
        var scenario = json_data.scenario;
        show_debug_message("Act: " + string(scenario.act));
        show_debug_message("Day: " + string(scenario.day));
        show_debug_message("Title: " + scenario.title);
        show_debug_message("Description: " + scenario.description);

        // Display choices
        for (var i = 0; i < array_length(scenario.choices); i++) {
            var choice = scenario.choices[i];
            show_debug_message("Choice " + string(i+1) + ": " + choice.text);
        }
    }
    else if (variable_struct_exists(json_data, "response")) {
        // AI message response
        var ai_response = json_data.response;
        show_debug_message("AI says: " + ai_response);
    }
    else if (variable_struct_exists(json_data, "story_status")) {
        // Status response
        var story = json_data.story_status;
        var relationship = json_data.relationship_status;
        show_debug_message("Story Status: " + json_stringify(story));
        show_debug_message("Relationship: " + json_stringify(relationship));
    }
} else {
    show_debug_message("HTTP request failed: " + string(status));
}
*/

// ==========================================
// USAGE EXAMPLE IN CREATE EVENT
// ==========================================
/*
// In obj_game_controller Create event:
create_new_game("FATHER");

// Wait a moment, then get first scenario
alarm[0] = 30;  // 0.5 seconds

// In Alarm 0 event:
get_scenario();
*/

// ==========================================
// BUTTON CLICK EXAMPLE
// ==========================================
/*
// When player clicks choice button 1, 2, or 3:
if (mouse_check_button_pressed(mb_left)) {
    if (position_meeting(mouse_x, mouse_y, obj_choice_button1)) {
        make_choice(1);
    }
    else if (position_meeting(mouse_x, mouse_y, obj_choice_button2)) {
        make_choice(2);
    }
    else if (position_meeting(mouse_x, mouse_y, obj_choice_button3)) {
        make_choice(3);
    }
}
*/
