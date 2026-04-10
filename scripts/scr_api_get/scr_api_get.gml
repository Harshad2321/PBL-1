/// @description scr_api_get(url)
/// @param url The API endpoint URL
/// @return The HTTP request ID

function scr_api_get(_url)
{
	// Make the HTTP GET request
	var _request_id = http_get(_url);

	return _request_id;
}
