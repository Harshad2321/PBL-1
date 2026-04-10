/// @description scr_send_choice(choice_index)
/// Send player's choice to the API
/// @param choice_index The choice number (1, 2, or 3)

function scr_send_choice(_choice_index)
{
    if (instance_exists(obj_controller))
    {
        obj_controller.request_type = "choose";
        
        // Send the choice via API
        var _data = json_stringify({
            day: obj_controller.day,
            choice: _choice_index
        });
        
        var _headers = ds_map_create();
        ds_map_add(_headers, "Content-Type", "application/json");
        http_request("http://127.0.0.1:8000/choose", "POST", _headers, _data);
    }
}
