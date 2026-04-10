var _request_id = async_load[? "id"];
var _data = scr_api_parse(async_load);

if (is_undefined(_data)) {
    show_debug_message("API request failed or returned invalid JSON");

    if (_request_id == req_start) {
        req_start = -1;
        retry_start_request = true;
        startup_retry_timer = startup_retry_delay;

        if (instance_exists(obj_controller)) {
            obj_controller.scenario_text = "Connecting to backend...";
        }
    }
    else if (_request_id == req_choose) {
        req_choose = -1;
    }
    else if (_request_id == req_message) {
        req_message = -1;
    }
    else if (_request_id == req_status) {
        req_status = -1;
    }
    else if (_request_id == req_end_conv) {
        req_end_conv = -1;
    }

    exit;
}

// ===========================
// Handle /start response
// ===========================
if (_request_id == req_start) {
    show_debug_message("START RESPONSE RECEIVED");

    // Update globals
    global.current_scenario = _data.scenario;
    global.current_day = _data.day;

    if (variable_struct_exists(_data, "status")) {
        var _st = _data.status;
        if (variable_struct_exists(_st, "trust")) global.trust = _st.trust;
        if (variable_struct_exists(_st, "resentment")) global.resentment = _st.resentment;
        if (variable_struct_exists(_st, "closeness")) global.closeness = _st.closeness;
        if (variable_struct_exists(_st, "stress")) global.stress = _st.stress;
        if (variable_struct_exists(_st, "day")) global.current_day = _st.day;
        if (variable_struct_exists(_st, "game_over")) global.game_over = _st.game_over;
    }

    retry_start_request = false;

    // Parse choices safely
    if (variable_struct_exists(_data, "choices")) {
        var _choices = _data.choices;
        if (array_length(_choices) >= 3) {
            // Choices can be structs or strings
            if (is_struct(_choices[0])) {
                global.choice0 = variable_struct_exists(_choices[0], "text") ? string(_choices[0].text) : string(_choices[0]);
                global.choice1 = variable_struct_exists(_choices[1], "text") ? string(_choices[1].text) : string(_choices[1]);
                global.choice2 = variable_struct_exists(_choices[2], "text") ? string(_choices[2].text) : string(_choices[2]);
            } else {
                global.choice0 = string(_choices[0]);
                global.choice1 = string(_choices[1]);
                global.choice2 = string(_choices[2]);
            }
        }
    }

    // Show choice menu
    if (instance_exists(global.choice_menu_id)) {
        global.choice_menu_id.visible = true;
    }

    // Hide chat panel
    if (instance_exists(global.chat_input_id)) {
        global.chat_input_id.visible = false;
    }

    // SYNC obj_controller game state
    if (instance_exists(obj_controller)) {
        obj_controller.day_summary_waiting = false;
        obj_controller.day_summary_ready = false;
        obj_controller.game_mode = "scenario";
        obj_controller.scenario_text = global.current_scenario;
        obj_controller.game_day = global.current_day;
        obj_controller.choices = [global.choice0, global.choice1, global.choice2];
        obj_controller.choice_ids = [1, 2, 3];

        // Refresh day-start baseline for the next day-summary delta calculation.
        obj_controller.day_start_day = global.current_day;
        obj_controller.day_start_trust = global.trust;
        obj_controller.day_start_resentment = global.resentment;
        obj_controller.day_start_closeness = global.closeness;
        obj_controller.day_start_stress = global.stress;
    }

    req_start = -1;
}

// ===========================
// Handle /choose response
// ===========================
else if (_request_id == req_choose) {
    show_debug_message("CHOOSE RESPONSE RECEIVED");

    global.ai_reply = _data.ai_reaction;

    if (variable_struct_exists(_data, "status")) {
        var _s = _data.status;
        if (variable_struct_exists(_s, "trust")) global.trust = _s.trust;
        if (variable_struct_exists(_s, "resentment")) global.resentment = _s.resentment;
        if (variable_struct_exists(_s, "closeness")) global.closeness = _s.closeness;
        if (variable_struct_exists(_s, "stress")) global.stress = _s.stress;
        if (variable_struct_exists(_s, "day")) global.current_day = _s.day;
    }

    // Hide choice menu
    if (instance_exists(global.choice_menu_id)) {
        global.choice_menu_id.visible = false;
    }

    // Keep chat hidden until player presses T near an NPC in free roam.
    if (instance_exists(global.chat_input_id)) {
        with (global.chat_input_id) {
            visible = false;
            array_push(chat_history, {speaker: "Mother", text: global.ai_reply});
        }
        global.last_ai_reply = global.ai_reply;
    }

    // Show selected option for 2 seconds, then obj_controller Step switches to free_roam.
    if (instance_exists(obj_controller)) {
        var _selected_text = "";
        var _idx = obj_controller.last_choice_index;
        var _choices_arr = [global.choice0, global.choice1, global.choice2];

        if (_idx >= 0 && _idx < array_length(_choices_arr)) {
            _selected_text = _choices_arr[_idx];
        }

        if (_selected_text == "") {
            _selected_text = "Choice confirmed.";
        }

        obj_controller.game_mode = "choice_feedback";
        obj_controller.feedback_timer = max(1, room_speed * 2);
        obj_controller.scenario_text = "You selected: " + _selected_text + "\n\n" + global.ai_reply;
    }

    req_choose = -1;
}

// ===========================
// Handle /message response
// ===========================
else if (_request_id == req_message) {
    show_debug_message("MESSAGE RESPONSE RECEIVED");

    if (variable_struct_exists(_data, "reply")) {
        global.ai_reply = _data.reply;

        if (instance_exists(global.chat_input_id)) {
            with (global.chat_input_id) {
                visible = true;
                array_push(chat_history, {speaker: "Mother", text: global.ai_reply});
            }
            global.last_ai_reply = global.ai_reply;
        }

        // Keep obj_controller in chat mode
        if (instance_exists(obj_controller)) {
            obj_controller.scenario_text = "Partner: " + global.ai_reply;
        }
    }

    if (variable_struct_exists(_data, "status")) {
        var _s2 = _data.status;
        if (variable_struct_exists(_s2, "trust")) global.trust = _s2.trust;
        if (variable_struct_exists(_s2, "resentment")) global.resentment = _s2.resentment;
        if (variable_struct_exists(_s2, "closeness")) global.closeness = _s2.closeness;
        if (variable_struct_exists(_s2, "stress")) global.stress = _s2.stress;
        if (variable_struct_exists(_s2, "day")) global.current_day = _s2.day;
    }

    req_message = -1;
}

// ===========================
// Handle /status response
// ===========================
else if (_request_id == req_status) {
    global.trust = _data.trust;
    global.resentment = _data.resentment;
    global.closeness = _data.closeness;
    global.stress = _data.stress;
    global.current_day = _data.day;
    global.game_over = _data.game_over;

    req_status = -1;
}

// ===========================
// Handle /end_conversation response
// ===========================
else if (_request_id == req_end_conv) {
    global.day_summary = _data.day_summary;

    // Auto-start next day
    if (instance_exists(obj_controller)) {
        obj_controller.trigger_next_day();
    }

    req_end_conv = -1;
}
