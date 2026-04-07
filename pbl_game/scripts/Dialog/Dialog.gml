function create_dialog(_messages){
	if (instance_exists(Obj_dialog)) return;
	
	var _inst = instance_create_depth(0, 0, 0, Obj_dialog);
	_inst.messages = _messages;
	_inst.current_message = 0;

	// ✅ NEW: set first speaker head
	var _name = _messages[0].name;

	switch (_name)
	{
		case "Dad":
			_inst.current_head = _inst.dad_head;
			break;

		case "Mom":
			_inst.current_head = _inst.mom_head;
			break;

		case "Main":
			_inst.current_head = _inst.main_head;
			break;

		default:
			_inst.current_head = -1;
	}
}

char_colors = {
	"Dad": c_yellow,
	"Main": c_aqua,
    "Mom": c_purple
}

welcome_dialog = [
{
	name: "Dad",
	msg: "Welcome!!."
},

{
	name: "Main",
	msg: "Thanks!"
},

{
	name: "Dad",
	msg: "A"
},

{
	name: "Main",
	msg: "B"
},

{
	name: "Dad",
	msg: "C"
}
]
welcome_dialog1 = [
{
	name: "Mom",
	msg: "Welcome!!."
},

{
	name: "Main",
	msg: "Thanks!"
},

{
	name: "Mom",
	msg: "A"
},

{
	name: "Main",
	msg: "B"
},

{
	name: "Mom",
	msg: "C"
}
]