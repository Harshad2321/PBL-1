// ==========================
// AUTO CLOSE DIALOG (FIX)
// ==========================
if (obj_controller.game_mode != "scenario" && obj_controller.game_mode != "choice_feedback" && obj_controller.game_mode != "chat")
{
	current_message = -1;
	draw_message = "";
    exit;
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