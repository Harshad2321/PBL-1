/// ==========================
/// INTERACTION (NPC triggers chat)
/// ==========================
if (pending_interaction)
{
    pending_interaction = false;

    if (game_mode == "free_roam")
    {
        start_chat();
    }
}


/// ==========================
/// SCENARIO MODE (pick 1/2/3)
/// ==========================
if (game_mode == "scenario")
{
    if (keyboard_check_pressed(ord("1"))) send_choice(1);
    if (keyboard_check_pressed(ord("2"))) send_choice(2);
    if (keyboard_check_pressed(ord("3"))) send_choice(3);
    if (keyboard_check_pressed(vk_f5)) trigger_next_day();
}


/// ==========================
/// CHOICE FEEDBACK (after choosing)
/// ==========================
if (game_mode == "choice_feedback")
{
    feedback_timer--;

    if (feedback_timer <= 0)
    {
        game_mode = "free_roam";
        scenario_text = "Move around.\nPress T to talk.\nPress F5 for next day.";
    }

    // Skip feedback and go to next day immediately
    if (keyboard_check_pressed(vk_f5))
    {
        trigger_next_day();
    }
}


/// ==========================
/// DAY SUMMARY (before next day starts)
/// ==========================
if (game_mode == "day_summary")
{
    // Allow user to skip the display delay.
    if (!day_summary_waiting)
    {
        if (keyboard_check_pressed(vk_return) || keyboard_check_pressed(vk_space) || keyboard_check_pressed(vk_f5))
        {
            day_summary_timer = 0;
        }

        day_summary_timer--;
        if (day_summary_timer <= 0) {
            day_summary_ready = true;
        }
    }

    // Auto-request next day once summary display time completes.
    if (!day_summary_waiting && day_summary_ready)
    {
        if (instance_exists(obj_api_controller) && obj_api_controller.req_start == -1)
        {
            day_summary_waiting = true;
            scenario_text = "Loading next day...";

            // Clear old choices so UI refreshes cleanly once /start returns.
            choices = [];
            choice_ids = [];

            var _body = ds_map_create();
            if (day_summary_endpoint == "http://127.0.0.1:8000/start") {
                ds_map_add(_body, "player_role", "father");
            }

            obj_api_controller.req_start = scr_api_post(day_summary_endpoint, _body);
        }
    }
}


/// ==========================
/// CHAT MODE
/// ==========================
if (game_mode == "chat")
{
    // Send player message through obj_api_controller
    if (global.pending_message != "")
    {
        var msg_to_send = global.pending_message;
        global.pending_message = "";

        if (msg_to_send == "/done")
        {
            if (instance_exists(obj_api_controller))
            {
                obj_api_controller.req_end_conv = scr_api_post("http://127.0.0.1:8000/end_conversation", ds_map_create());
            }
            if (instance_exists(global.chat_input_id))
            {
                global.chat_input_id.visible = false;
            }
            game_mode = "loading";
            scenario_text = "Ending conversation...";
        }
        else
        {
            if (instance_exists(global.chat_input_id))
            {
                with (global.chat_input_id) {
                    array_push(chat_history, {speaker: "You", text: msg_to_send});
                }
            }

            // Route through obj_api_controller
            if (instance_exists(obj_api_controller))
            {
                var _body = ds_map_create();
                ds_map_add(_body, "message", msg_to_send);
                obj_api_controller.req_message = scr_api_post("http://127.0.0.1:8000/message", _body);
            }
        }
    }

    // Q = exit chat
    if (keyboard_check_pressed(ord("Q")))
    {
        game_mode = "free_roam";
        scenario_text = "Move around.\nPress T to talk.\nPress F5 for next day.";

        if (instance_exists(global.chat_input_id))
        {
            global.chat_input_id.visible = false;
        }
    }

    // F5 = NEXT DAY Event directly from chat mode
    if (keyboard_check_pressed(vk_f5))
    {
        trigger_next_day();
    }
}


/// ==========================
/// FREE ROAM — F5 = NEXT DAY
/// ==========================
if (game_mode == "free_roam")
{
    if (keyboard_check_pressed(vk_f5))
    {
        trigger_next_day();
    }
}