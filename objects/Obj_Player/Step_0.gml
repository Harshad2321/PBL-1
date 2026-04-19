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

function _is_blocked(_foot_x, _foot_y)
{
    var _foot_half_w = 16;
    var _foot_half_h = 7;
    var _x1 = _foot_x - _foot_half_w;
    var _x2 = _foot_x + _foot_half_w;
    var _y1 = _foot_y - _foot_half_h;
    var _y2 = _foot_y + _foot_half_h;

    // Character body bounds (broader than feet) for player-vs-character overlap checks.
    var _body_x1 = _foot_x - 17;
    var _body_x2 = _foot_x + 17;
    var _body_y1 = _foot_y - 44;
    var _body_y2 = _foot_y + 8;

    function _overlaps(_ax1, _ay1, _ax2, _ay2, _bx1, _by1, _bx2, _by2)
    {
        return !(_ax2 < _bx1 || _ax1 > _bx2 || _ay2 < _by1 || _ay1 > _by2);
    }

    function _overlaps_character(_inst, _px1, _py1, _px2, _py2)
    {
        if (!instance_exists(_inst)) return false;

        var _nx1 = _inst.bbox_left + 8;
        var _nx2 = _inst.bbox_right - 8;
        var _ny1 = _inst.bbox_top + 6;
        var _ny2 = _inst.bbox_bottom - 2;

        // Fallback for thin masks/scales.
        if (_nx2 <= _nx1) {
            var _cx = (_inst.x);
            _nx1 = _cx - 12;
            _nx2 = _cx + 12;
        }
        if (_ny2 <= _ny1) {
            var _cy = (_inst.y);
            _ny1 = _cy - 24;
            _ny2 = _cy + 10;
        }

        return _overlaps(_px1, _py1, _px2, _py2, _nx1, _ny1, _nx2, _ny2);
    }

    // Keep player in room bounds.
    if (_x1 < 45 || _x2 > room_width - 45) return true;
    if (_y1 < 265 || _y2 > room_height - 20) return true;

    // Room_Hall uses a painted background, so collisions must be explicit.
    if (room == Room_Hall)
    {
        // Sofa (left)
        if (_overlaps(_x1, _y1, _x2, _y2, 70, 295, 320, 706)) return true;

        // TV stand (center top)
        if (_overlaps(_x1, _y1, _x2, _y2, 425, 300, 690, 452)) return true;

        // Table (center) - tuned to avoid blocking free space on right side.
        if (_overlaps(_x1, _y1, _x2, _y2, 598, 452, 748, 706)) return true;

        // Left side-table + cabinet cluster
        if (_overlaps(_x1, _y1, _x2, _y2, 20, 545, 235, 710)) return true;

        // Right plant + pot
        if (_overlaps(_x1, _y1, _x2, _y2, 905, 300, 1038, 710)) return true;

    }

    // Dynamic blockers: partner/NPC bodies.
    var _npc_obj = asset_get_index("obj_npc_parent");
    if (_npc_obj != -1)
    {
        var _npc_count = instance_number(_npc_obj);
        for (var _i = 0; _i < _npc_count; _i++)
        {
            var _npc = instance_find(_npc_obj, _i);
            if (_overlaps_character(_npc, _body_x1, _body_y1, _body_x2, _body_y2)) return true;
        }
    }

    // Dynamic blockers: child body.
    var _child_obj = asset_get_index("Obj_Child");
    if (_child_obj == -1) _child_obj = asset_get_index("obj_child");
    if (_child_obj != -1)
    {
        var _child_count = instance_number(_child_obj);
        for (var _j = 0; _j < _child_count; _j++)
        {
            var _child = instance_find(_child_obj, _j);
            if (_overlaps_character(_child, _body_x1, _body_y1, _body_x2, _body_y2)) return true;
        }
    }

    return false;
}

// Movement with axis-separated collision checks.
var _foot_offset = 18;

var _next_x = x + (_hor * move_speed);
if (!_is_blocked(_next_x, y + _foot_offset)) {
    x = _next_x;
}

var _next_y = y + (_ver * move_speed);
if (!_is_blocked(x, _next_y + _foot_offset)) {
    y = _next_y;
}

// Animation
if (_hor != 0 || _ver != 0) {

    // Vertical priority
    if (_ver > 0) {
        current_direction = "south";
        sprite_index = spr_father_walk_south;
        image_speed = 0.15;
        image_xscale = 4.352941;
        image_yscale = 3.2941177;
    }
    else if (_ver < 0) {
        current_direction = "north";
        sprite_index = spr_father_walk_north;
        image_speed = 0.15;
        image_xscale = 4.352941;
        image_yscale = 3.2941177;
    }
    else if (_hor > 0) {
        current_direction = "east";
        sprite_index = spr_father_walk_east;
        image_speed = 0.15;
        image_xscale = 4.352941;
        image_yscale = 3.2941177;
    }
    else if (_hor < 0) {
        current_direction = "west";
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