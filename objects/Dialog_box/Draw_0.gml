/// Draw Dialogue UI
if (show_dialogue) {
    // Semi-transparent black background
    draw_set_alpha(0.7);
    draw_rectangle_color(50, 360, 1230, 580, c_black, c_black, c_black, c_black, false);
    draw_set_alpha(1);
    
    // Draw dialogue box sprite
    if (sprite_exists(spr_dialogue_box)) {
        draw_sprite(spr_dialogue_box, -1, dial_x, dial_y);
    }
    
    // Draw speaker portrait
    if (current_speaker == "father") {
        if (sprite_exists(spr_father_portrait)) {
            draw_sprite(spr_father_portrait, -1, 120, 430);
        }
    } else {
        if (sprite_exists(spr_player_portrait)) {
            draw_sprite(spr_player_portrait, -1, 120, 430);
        }
    }
    
    // Draw speaker name
    draw_set_color(c_yellow);
    draw_set_font(-1);
    draw_text(300, 400, string_upper(current_speaker));
    
    // Draw dialogue text
    draw_set_color(c_white);
    draw_text_ext(300, 420, dialogue_text, 20, 300);
    
    // Draw choice buttons
    if (show_choices) {
        for (var i = 0; i < array_length(choice_options); i++) {
            var btn_x = 850;
            var btn_y = 410 + (i * 50);
            
            // Draw button sprite
            if (sprite_exists(spr_choice_button)) {
                draw_sprite(spr_choice_button, -1, btn_x, btn_y);
            }
            
            // Highlight selected
            if (i == choice_index) {
                draw_set_color(c_yellow);
            } else {
                draw_set_color(c_white);
            }
            
            // Draw choice label
            draw_text(btn_x - 35, btn_y - 12, chr(65 + i) + ": " + choice_options[i]);
        }
    }
    
    draw_set_color(c_white);
}