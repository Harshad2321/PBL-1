// ==========================
// AUTO CLOSE DIALOG (FIX)
// ==========================
if (obj_controller.game_mode != "scenario" && obj_controller.game_mode != "choice_feedback" && obj_controller.game_mode != "chat")
{
	current_message = -1;
	draw_message = "";
	scenario_type_source = "";
	scenario_type_visible = "";
	scenario_type_chars = 0;
    exit;
}

if (obj_controller.game_mode == "scenario" || obj_controller.game_mode == "choice_feedback")
{
	var _scenario_full_text = string(obj_controller.scenario_text);

	if (scenario_type_source != _scenario_full_text)
	{
		scenario_type_source = _scenario_full_text;
		scenario_type_visible = "";
		scenario_type_chars = 0;
	}

	var _scenario_len = string_length(scenario_type_source);

	if (_scenario_len <= 0)
	{
		scenario_type_visible = "";
		scenario_type_chars = 0;
	}
	else
	{
		if ((keyboard_check_pressed(vk_space) || keyboard_check_pressed(vk_return)) && scenario_type_chars < _scenario_len)
		{
			scenario_type_chars = _scenario_len;
		}
		else if (scenario_type_chars < _scenario_len)
		{
			scenario_type_chars = min(_scenario_len, scenario_type_chars + scenario_type_speed);
		}

		scenario_type_visible = string_copy(scenario_type_source, 1, floor(scenario_type_chars));
	}
}
else
{
	scenario_type_source = "";
	scenario_type_visible = "";
	scenario_type_chars = 0;
}

// ==========================
// ORIGINAL CODE
// ==========================
if (current_message < 0) exit;

var _str = messages[current_message].msg;

if (current_char < string_length(_str)) 
{
	current_char += char_speed * (1 + real(keyboard_check(input_key)));
	draw_message = string_copy(_str, 0, current_char);
}
else if (keyboard_check_pressed(input_key))
{
	current_message++;
	if (current_message >= array_length(messages))
	{
		instance_destroy();
	}
    else
    {
	   current_char = 0;

	   var _name = messages[current_message].name;

	   switch (_name)
	   {
		  case "Dad":
			 current_head = dad_head;
			 break;

		  case "Mom":
			 current_head = mom_head;
			 break; 
        
          case "Main":
			 current_head = main_head;
			 break;

		  default:
			 current_head = -1;
	   }
    }
}