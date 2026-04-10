if (instance_exists(Obj_Player) && point_distance(x, y, Obj_Player.x, Obj_Player.y) <= talk_radius)
{
	can_talk = true;
	if (keyboard_check_pressed(input_key))
	{
		// Only allow chat in free_roam mode
		if (instance_exists(obj_controller) && obj_controller.game_mode == "free_roam")
		{
			obj_controller.start_chat();
		}
	}
}
else 
{
	can_talk = false;
}