/// @description next_day()
/// Advance the game to the next day via obj_controller

function next_day() {
    if (instance_exists(obj_controller)) {
        obj_controller.trigger_next_day();
    }
}
