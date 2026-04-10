// Request ID trackers
req_start    = -1;
req_choose   = -1;
req_message  = -1;
req_status   = -1;
req_end_conv = -1;

// Global state
global.ai_reply          = "";
global.last_ai_reply     = "";
global.current_scenario  = "";
global.choice0           = "";
global.choice1           = "";
global.choice2           = "";
global.trust             = 0.5;
global.resentment        = 0.0;
global.closeness         = 0.5;
global.stress            = 0.3;
global.current_day       = 1;
global.game_over         = false;
global.day_summary       = "";
global.status_timer      = 0;
startup_retry_delay      = room_speed;
startup_retry_timer      = 1;
retry_start_request      = true;

// Start request is sent from Step with retry handling.
