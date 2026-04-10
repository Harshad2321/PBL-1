if (instance_exists(obj_controller) && obj_controller.game_mode != "free_roam") exit;

/*if (keyboard_check_pressed(vk_space))
{
	create_dialog([
	{
		name: "Test dialog!",
		msg: "It works!"
	}
	])
}*/

/*var _hor = keyboard_check(ord("D")) - keyboard_check(ord("A"));
var _ver = keyboard_check(ord("S")) - keyboard_check(ord("W"));

var dx = _hor * move_speed;
var dy = _ver * move_speed;


move_and_collide(dx, dy, tilemap);

// Move Right
if (keyboard_check(ord("D"))) {
    x += move_speed;

    sprite_index = spr_walk_right;
    image_speed = 0.5;

    image_xscale = 0.0625;   // normal
}

// Move Left
else if (keyboard_check(ord("A"))) {
    x -= move_speed;

    sprite_index = spr_walk_right;
    image_speed = 0.5;

    image_xscale = -0.0625;  // flip horizontally
}

// Idle
else {
    image_speed = 0;
    image_index = 0;
} */
// Input
var _hor = keyboard_check(ord("D")) - keyboard_check(ord("A"));
var _ver = keyboard_check(ord("S")) - keyboard_check(ord("W"));

// Movement
x += _hor * move_speed;
y += _ver * move_speed;

// Animation
if (_hor != 0 || _ver != 0) {

    // Vertical priority
    if (_ver > 0) {
        sprite_index = spr_father_walk_south;
        image_speed = 0.15;
        image_xscale = 4.352941;
        image_yscale = 3.2941177;
    }
    else if (_ver < 0) {
        sprite_index = spr_father_walk_north;
        image_speed = 0.15;
        image_xscale = 4.352941;
        image_yscale = 3.2941177;
    }
    else if (_hor > 0) {
        sprite_index = spr_father_walk_east;
        image_speed = 0.15;
        image_xscale = 4.352941;
        image_yscale = 3.2941177;
    }
    else if (_hor < 0) {
        sprite_index = spr_father_walk_west;
        image_speed = 0.15;
        image_xscale = 4.352941;
        image_yscale = 3.2941177;
    }

} else {
    // Idle - show static pose
    if (current_direction == "south") {
        sprite_index = spr_father_south;
    } else if (current_direction == "north") {
        sprite_index = spr_father_north;
    } else if (current_direction == "east") {
        sprite_index = spr_father_east;
    } else if (current_direction == "west") {
        sprite_index = spr_father_west;
    }
    image_speed = 0;
    image_index = 0;
    image_xscale = 4.352941;
    image_yscale = 3.2941177;
}