// Initialize global variables to noone (not undefined)
global.chat_input_id = noone;
global.api_controller_id = noone;
global.status_bars_id = noone;
global.choice_menu_id = noone;

// Launch Python backend
var _launcher = working_directory + "PBL-1\\launcher.bat";
if (!file_exists(_launcher)) {
    // Runner builds execute from a temp folder, so use local dev fallback path.
    var _fallback_launcher = "D:\\STUDY\\PBL\\NUTURE\\PBL-1\\launcher.bat";
    if (file_exists(_fallback_launcher)) {
        _launcher = _fallback_launcher;
    }
}

if (file_exists(_launcher)) {
    execute_shell("cmd.exe", "/c start /B \"\" \"" + _launcher + "\"", false);
} else {
    show_debug_message("launcher.bat not found at: " + _launcher);
}

function _spawn_or_get(_asset_name)
{
    var _asset_index = asset_get_index(_asset_name);
    if (_asset_index == -1) {
        show_debug_message("Missing object asset: " + _asset_name);
        return noone;
    }

    if (!instance_exists(_asset_index)) {
        return instance_create_layer(0, 0, "Instances", _asset_index);
    }

    return instance_find(_asset_index, 0);
}

// Spawn persistent objects using direct creation
global.api_controller_id = _spawn_or_get("obj_api_controller");
global.status_bars_id = _spawn_or_get("obj_status_bars");
global.choice_menu_id = _spawn_or_get("obj_choice_menu");
global.chat_input_id = _spawn_or_get("obj_chat_input");

// Initially hide chat input
if (instance_exists(global.chat_input_id)) {
    global.chat_input_id.visible = false;
}
