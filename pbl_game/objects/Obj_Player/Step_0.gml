if (instance_exists(Obj_dialog)) exit;

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
        sprite_index = spr_walk_down;
        image_speed = 0.5;
        image_xscale = 0.0625;
    }
    else if (_ver < 0) {
        sprite_index = Spr_walk_back;
        image_speed = 0.5;
        image_xscale = 0.0625;
    }
    else if (_hor > 0) {
        sprite_index = spr_walk_right;
        image_speed = 0.5;
        image_xscale = 0.0625;
    }
    else if (_hor < 0) {
        sprite_index = spr_walk_right;
        image_speed = 0.5;
        image_xscale = -0.0625; // flip
    }

} else {
    // Idle
    image_speed = 0;
    image_index = 0;
}