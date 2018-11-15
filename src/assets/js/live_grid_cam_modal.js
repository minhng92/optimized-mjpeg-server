/* GLOBAL VARIABLES */
var dragged_element = null;     // null or jquery object (camera_row)
var showing_cameras = {
    // cam_block_1: data-stream
    // cam_block_2: data-stream
    // cam_block_3: data-stream
    // cam_block_4: data-stream
}

function show_camera_modal(obj) {
    $('#modal').show();
    var stream_source = obj.attr("title");
    $('#modal #current_cam').attr("src", stream_source);
    $('#modal #modal_header').html(obj.html());
}

function cam_mouse_down(event) {
    if (event.which != 1) { // event.which == 1 --> left mouse click
        return;
    }

    if(!$('#cam_pick').length) {     // dynamically create a small icon at user pointer
        $($.parseHTML('<i id="cam_pick" class="fa fa-video-camera camera_color fa-lg" aria-hidden="true"></i>')).appendTo('#cam_container');
        $('#cam_pick').css("position", "absolute");
        $('#cam_pick').show();
    } else {
        $('#cam_pick').show();
    }

    $('#cam_container').off("mousemove");
    $('#cam_container').mousemove(function(e) {
        // update location
        cam_move(e);
    });
}

$('div .camera_row').mousedown(function (event) {
    dragged_element = $(this);
    cam_mouse_down(event); 
});

function cam_move(event) {
    $('#cam_pick').css("left", event.clientX);
    $('#cam_pick').css("top", event.clientY);
}

$('#cam_container').mouseup(function(e){
    $('#cam_container').off('mousemove');

    var is_drop_from_drag = false;
    if($('#cam_pick').is(":visible")) {
        is_drop_from_drag = true;
    }

    $('#cam_pick').hide();
    if(!is_drop_from_drag) {
        return;
    }

    var elem = document.elementFromPoint(e.clientX, e.clientY);
    var elements_at_drop = $(elem);

    var cam_block = null;
    elements_at_drop.each(function(i, obj) {
        if ($(obj).hasClass('cam_block')) {
            cam_block = $(obj);
            return;
        } else if($(obj).parent().hasClass('cam_block')) {
            cam_block = $(obj).parent();
            return;
        }
    });

    if (!cam_block) {
        elements_at_drop.each(function(i, obj) {
            if ($(obj).attr("src") == dragged_element.attr("title")) {
                show_camera_modal($(this));
                return;
            }
        });
        console.log('Drop at element which does not have "cam_block" class --> do nothing :D.')
        return;
    }

    stick_camera_to_showing_block(dragged_element, cam_block);
});

function stick_camera_to_showing_block(j_camera_row, j_cam_block) {
    // update image source
    j_cam_block.find('img').attr("src", j_camera_row.attr("title"));
    showing_cameras[j_cam_block.attr('id')] = j_camera_row.attr("title");

    j_cam_block.find('span').html(j_camera_row.html());

    // update UI
    var showing_streams = $.map(showing_cameras, function(value, key) { return value });
    $('.camera_row').each(function(i, obj) {
        var stream = $(obj).attr("src");
        if (showing_streams.indexOf(stream) != -1) {
            $(obj).find('i').removeClass("camera_color");
            $(obj).find('i').removeClass("camera_showing_color");
            $(obj).find('i').addClass("camera_showing_color");
        } else {
            $(obj).find('i').removeClass("camera_color");
            $(obj).find('i').removeClass("camera_showing_color");
            $(obj).find('i').addClass("camera_color");
        }
    });
}

$('#modal, .modal_close').click(function () {
    $('#modal').hide();
});

$('#modal .insertscreen').click(function(event) {
    event.stopImmediatePropagation();
});

function ClickFullScreenById(video_id) {
    $('#' + video_id).fullscreen();
}

function SwitchStreamOriginAndProcessed(video_id) {
    var current_source = $('#' + video_id).attr('src');
    if (current_source.endsWith("_origin")) {
        new_source = current_source.substring(0, current_source.length-7);
        $('#' + video_id).attr('src', new_source);
    } else {
        $('#' + video_id).attr('src', current_source + '_origin');
    }
}