if (retry_start_request && req_start == -1) {
    startup_retry_timer--;

    if (startup_retry_timer <= 0) {
        var _body = ds_map_create();
        ds_map_add(_body, "player_role", "father");
        req_start = scr_api_post("http://127.0.0.1:8000/start", _body);

        retry_start_request = false;
        startup_retry_timer = startup_retry_delay;
    }
}

global.status_timer++;
if (global.status_timer >= 180) {
    if (req_status == -1) {
        req_status = scr_api_get("http://127.0.0.1:8000/status");
        global.status_timer = 0;
    }
}
