draw_self();

if (can_talk && instance_exists(obj_controller) && obj_controller.game_mode == "free_roam") 
{
	/*draw_set_color(c_white);
	draw_text(x - 5, y - 20, "...");*/
    draw_sprite(Sprite5, 0, x -15 ,y - 45);
}