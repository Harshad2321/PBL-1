/// @description scr_api_parse(async_map)
/// @param async_map The async_load ds_map from Async HTTP event
/// @return A struct parsed from JSON, or undefined on error

function scr_api_parse(_async_map)
{
    // Check HTTP status
    var _status = _async_map[? "status"];
    if (_status != 0) {
        return undefined;
    }

    // Get result string
    var _result = _async_map[? "result"];
    if (is_undefined(_result) || _result == "") {
        return undefined;
    }

    // Parse JSON string to struct
    try {
        var _parsed = json_parse(_result);
        return _parsed;
    } catch(_error) {
        return undefined;
    }
}
