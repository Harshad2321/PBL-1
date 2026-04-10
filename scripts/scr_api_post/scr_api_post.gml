/// @description scr_api_post(url, body_map)
/// @param url The API endpoint URL
/// @param body_map A ds_map containing the request body
/// @return The HTTP request ID

function scr_api_post(_url, _body_map)
{
	// Build JSON string from ds_map
	var _json_body = json_encode(_body_map);

	// Create header map
	var _header_map = ds_map_create();
	ds_map_add(_header_map, "Content-Type", "application/json");

	// Make the HTTP request
	var _request_id = http_request(_url, "POST", _header_map, _json_body);

	// Clean up
	ds_map_destroy(_header_map);
	ds_map_destroy(_body_map);

	return _request_id;
}
