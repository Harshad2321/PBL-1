if (instance_number(obj_controller) > 1) {
    instance_destroy();
    exit;
}

global.controller = id;
global.pending_message = "";

/// ==========================
/// INITIALIZE GAME STATE
/// ==========================

game_day = 1;
scenario_text = "Loading...";
choices = [];
choice_ids = [];

game_mode = "scenario";

feedback_timer = 0;
last_choice_index = 0;

pending_interaction = false;

var _init_day = variable_global_exists("current_day") ? global.current_day : 1;
var _init_trust = variable_global_exists("trust") ? global.trust : 0.5;
var _init_resentment = variable_global_exists("resentment") ? global.resentment : 0.0;
var _init_closeness = variable_global_exists("closeness") ? global.closeness : 0.5;
var _init_stress = variable_global_exists("stress") ? global.stress : 0.3;

// Day summary baseline (start-of-day) and display values.
day_start_day = _init_day;
day_start_trust = _init_trust;
day_start_resentment = _init_resentment;
day_start_closeness = _init_closeness;
day_start_stress = _init_stress;

summary_day = _init_day;
summary_trust = _init_trust;
summary_resentment = _init_resentment;
summary_closeness = _init_closeness;
summary_stress = _init_stress;
summary_delta_trust = 0;
summary_delta_resentment = 0;
summary_delta_closeness = 0;
summary_delta_stress = 0;

day_summary_timer = 0;
day_summary_ready = false;
day_summary_waiting = false;
day_summary_endpoint = "";

// NOTE: All HTTP requests go through obj_api_controller.
// obj_controller only manages game_mode and keyboard input.
// No direct HTTP calls from here — avoids dual-request conflicts.

/// ==========================
/// FUNCTION: SEND CHOICE (keyboard 1/2/3)
/// ==========================
function send_choice(index)
{
    if (!instance_exists(obj_api_controller)) exit;

    last_choice_index = index - 1;

    // Prime the chat history with the scenario + chosen option
    if (instance_exists(global.chat_input_id)) {
        with (global.chat_input_id) {
            chat_history = [];
            array_push(chat_history, {speaker: "Scenario", text: global.current_scenario});
            if (index >= 1 && index <= 3) {
                var _choices_arr = [global.choice0, global.choice1, global.choice2];
                array_push(chat_history, {speaker: "You", text: _choices_arr[index - 1]});
            }
            input_string = "";
            keyboard_string = "";
        }
    }

    var _body = ds_map_create();
    ds_map_add(_body, "day", game_day);
    ds_map_add(_body, "choice", index);
    obj_api_controller.req_choose = scr_api_post("http://127.0.0.1:8000/choose", _body);
}


/// ==========================
/// FUNCTION: START CHAT
/// ==========================
function start_chat()
{
    game_mode = "chat";

    if (!instance_exists(global.chat_input_id) && instance_exists(obj_chat_input)) {
        global.chat_input_id = instance_find(obj_chat_input, 0);
    }

    if (instance_exists(global.chat_input_id))
    {
        with (global.chat_input_id) {
            visible = true;
            input_string = "";
            keyboard_string = "";
        }
    }

    scenario_text = "Start chatting. Press ENTER to send. Press Q to exit.";
}


/// ==========================
/// FUNCTION: NEXT DAY
/// ==========================
function trigger_next_day()
{
    if (!instance_exists(obj_api_controller)) exit;

    if (game_mode == "day_summary") exit;

    var _from_mode = game_mode;

    show_debug_message("NEXT DAY TRIGGERED");

    // Force clean state
    feedback_timer = 0;
    pending_interaction = false;

    // Hide chat UI
    if (instance_exists(global.chat_input_id))
    {
        global.chat_input_id.visible = false;
    }

    // Hide choice menu while loading
    if (instance_exists(global.choice_menu_id))
    {
        global.choice_menu_id.visible = false;
    }

    // Safety: ensure status/summary renderer exists and is visible.
    if (instance_exists(obj_status_bars))
    {
        global.status_bars_id = instance_find(obj_status_bars, 0);
        if (instance_exists(global.status_bars_id)) {
            global.status_bars_id.visible = true;
        }
    }
    else
    {
        var _bars_obj = asset_get_index("obj_status_bars");
        if (_bars_obj != -1) {
            if (layer_exists("Instances")) {
                global.status_bars_id = instance_create_layer(0, 0, "Instances", _bars_obj);
            } else {
                global.status_bars_id = instance_create_depth(0, 0, 0, _bars_obj);
            }

            if (instance_exists(global.status_bars_id)) {
                global.status_bars_id.visible = true;
            }
        }
    }

    // Capture end-of-day snapshot and deltas from the day-start baseline.
    summary_day = global.current_day;
    summary_trust = global.trust;
    summary_resentment = global.resentment;
    summary_closeness = global.closeness;
    summary_stress = global.stress;
    summary_delta_trust = summary_trust - day_start_trust;
    summary_delta_resentment = summary_resentment - day_start_resentment;
    summary_delta_closeness = summary_closeness - day_start_closeness;
    summary_delta_stress = summary_stress - day_start_stress;

    day_summary_endpoint = "http://127.0.0.1:8000/start";
    if (_from_mode == "scenario") {
        day_summary_endpoint = "http://127.0.0.1:8000/skip_day";
    }

    day_summary_timer = max(1, room_speed * 3);
    day_summary_ready = false;
    day_summary_waiting = false;

    game_mode = "day_summary";
    scenario_text = "Day " + string(summary_day) + " summary";
}