messages = [];
current_message = -1;
current_char = 0;
draw_message = "";

char_speed = 0.5;
input_key = vk_space;

gui_w = display_get_gui_width();
gui_h = display_get_gui_height();

spr_box = create_dialog_box(600, 120);

dad_head = Spr_dad_head;
mom_head = Spr_mom_head;
main_head = Spr_head;

// current portrait
current_head = -1;
dad_scale  = 0.5;
mom_scale  = 0.5;
main_scale = 8.5;

if (array_length(messages) > 0)
{
	current_message = 0;

	var _name = messages[0].name;

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