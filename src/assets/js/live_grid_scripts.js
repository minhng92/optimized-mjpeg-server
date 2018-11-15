
$( document ).ready(function() {
    // loop by cam blocks
    var cam_rows = $('.camera_row');
    var cam_blocks = $('.cam_block');

    cam_blocks.each(function(i, obj) {
        if (i >= cam_rows.length || i >= cam_blocks.length) {
            return;
        }
        stick_camera_to_showing_block($(cam_rows[i]), $(obj));
    });
});
