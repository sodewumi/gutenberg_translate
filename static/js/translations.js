$(document).ready(function(){

    var paragraphId;
    var chapterNumber;
    var groupId = $("#translated").data('groupid');
    var bookgroupId = $("#translate_textarea").data('bookgroupid');
    var username = $("#user_controls_row").data("username");
    var colors = ["49, 200, 203", "55,229,55", "221,129,118", "165,30,45"];
    var counter = 0;

/*------------------------------------------------------------------------------
        SocketIO Functions
-------------------------------------------------------------------------------*/

    var socket = io.connect('http://' + document.domain + ':' + location.port + '/rendertranslations');
    
    $(window).on('beforeunload', function (evt){
        socket.emit("disconnect");
    });

    socket.on('established connection', function (msg) {
        // Server confirms page is connected to socketio
        console.log(msg.connection_status);
    });

    socket.on('connect', function () {
        // Allows user to join a Room. Information about room name is taken from
        // bookgroupId and chapterNumber and sent to the joined socket route
        chapterNumber = $("select[name=chapter_selection] option:selected").val();
        socket.emit("joined", {"bookgroup_id": bookgroupId, "chapter_number": chapterNumber});
    });

    socket.on('joined_status', function (data) {
        // Transmits a message from the server that the user succesfully joined
        // a room. Sent from joined socket route
        console.log(data.msg);
    });

    socket.on('leave_status', function (data) {
        // Transmits a message from the server that the user succesfully joined
        // a room. Sent from joined socket route
        console.log(data.msg);
    });

    socket.on('update text', function (msg) {
        // The currently updated text is taken from the update text socket route
        //  and rendered on the appropriate paragraph.
        var UserColor = userTranslatingColor(msg.username);
        $('.' + msg.paragraphId +" p").css("background-color", UserColor);
        $('#' + msg.paragraphId +" p").text(msg.change_text);
    });

    socket.on('render reverted text', function (msg) {
        // If user cancels, rerenders the last translation within the database
        if (msg.last_text !== null){
            $('#' + msg.paragraphIdAjax +" p").text(msg.last_text);
        } else {
            $('#' + msg.paragraphIdAjax +" p").empty();
        }
        $('.' + msg.paragraphIdAjax +" p").css("background-color", "rgb(255,255,255)");
        $('.' + msg.paragraphIdAjax +" p").attr('data-toggle', "modal");
        //reattach click color event
    });

    socket.on('render submitted text', function (msg) {
        // renders saved text when user hits submit
        $('.' + msg.paragraphId +" p").css("background-color", "rgb(255,255,255)");
        $('#' + msg.paragraphId +" p").text(msg.changed_text);
        $('.' + msg.paragraphId +" p").attr('data-toggle', "modal");
        //reattach click color even
    });

    socket.on('hide button', function (msg) {
        $('.' + msg.paragraph_id +" p").attr('data-toggle', null);
    });


/*------------------------------------------------------------------------------
        Helper Functions
-------------------------------------------------------------------------------*/

    function translationInProgress (inProgress, paragraphId, translated_para_text) {
        // if the user is translating a paragraph, it stops another user from translating the 
        // same paragraph. Triggers triggers the socket.emit on the input
        // event handler for #text_form_ta
        if (inProgress === false) {
            $("#error_translation_in_progress").hide();
            $("#confirm").hide();
            $("#cancel_translation_btn").show();
            $("#translation_form").show();

            var untranslated_para_text = $("." + paragraphId + " p").text();

            $("#current_untans_text p").text(untranslated_para_text);
            $("#text_form_ta").val(translated_para_text);
            socket.emit('remove button', {"paragraph_id": paragraphId, "bookgroup_id": bookgroupId, "chapter_number": chapterNumber});
            $("#text_form_ta").trigger("input");
        } else {
            $("#cancel_translation_btn").hide();
            $("#translation_form").hide();
            $("#error_translation_in_progress").show();
            $("#confirm").show();
        }
    }

    function isEmpty( el ){
        return !$.trim(el.html());
    }

    /*--Sends an AJAX response to check if the current translation
    matches the one in the database--*/
    function translationProgressCheck () {
        paragraphId = $(this).data('paragraphid');
        if ($('.' + paragraphId +" p").data().toggle != null) {
            var translated_para_text =  $("#" + paragraphId + " p").text();

            $.ajax({
                url: "/in_translation",
                data: "&p_id=" + paragraphId + "&bg_id=" + bookgroupId + "&current_trans_text=" + translated_para_text,
                type: "POST",
                success: function(response) {
                  translationInProgress(response.inProgress, paragraphId, translated_para_text);
                },
                error: function(error) {
                    console.log(error);
                }
            });
        }   
    }
    
    function userTranslatingColor (usernameFromServer) {
        var userColor;
        $(".a-collab").each(function () {
            if ($(this).text() === usernameFromServer) {
                console.log(usernameFromServer);
                userColor = $(this).css('color').replace(')', ', 0.5)').replace('rgb', 'rgba');
            }
        });
        return userColor;
    }
/*------------------------------------------------------------------------------
        Event Handlers
-------------------------------------------------------------------------------*/

    $(".a-collab").each(function () {
        if (counter <= colors.length) {
            $(this).first("li").css("color", "rgb("+colors[counter]+")");
            counter += 1;
        } else {
            counter = 0;
        }
    });

    $(".untranslated p").on("click", translationProgressCheck);

    $("#text_form_ta").on("input", function (evt) {
        // Socket logs all changes made to the textarea and sends the info to
        // the value changed socket route
        socket.emit('value changed', {"paragraphId" : paragraphId,
                "change_text": $(this).val(), "bookgroup_id": bookgroupId,
                "chapter_number": chapterNumber, "username": username});     

    });

    $("#add_translation_section").on("hidden.bs.modal", function (evt) {
        $.ajax({
            url: "/cancel_translation",
            data: "&p_id=" + paragraphId + "&bg_id=" + bookgroupId + "&un=" + username,
            type: "POST",
            success: function(response) {
               socket.emit("canceled translation", {
                "last_text" : response.last_saved_trans,
                "paragraphIdAjax" : response.paragraph_id,
                "bookgroup_id": bookgroupId, "chapter_number": chapterNumber});
            },
            error: function(error) {
                console.log(error);
            }
        });
    });

    $("#submit_bttn").on("click", function (evt) {
        // submits translated text to the db.
        evt.preventDefault();
        var translated_text = $("#text_form_ta").val();

        $.ajax({
            url: "/save_text",
            data: $('form').serialize() + "&p_id=" + paragraphId + "&bg_id=" + bookgroupId + "&un=" + username,
            type: "POST",
            success: function(response) {
                socket.emit("submit text", {"changed_text" : response.translated_text, "paragraphId": response.paragraph_id, "bookgroup_id": bookgroupId, "chapter_number": chapterNumber});
            },
            error: function(error) {
                console.log(error);
            }
        });
        $(".trans_para").show();
    });



    $(function() {
        $('#chap_sel').change(function() {
            socket.emit("leave", {"bookgroup_id": bookgroupId, "chapter_number": chapterNumber});
            chapterNumber = $("select[name=chapter_selection] option:selected").val();
            this.form.submit();
        });
    });

    $(".trans_para").each(function () {
        if (isEmpty($(this))) {
            $(this).html("<p></p>");
        }
    });

    function main() {
        $("#confirm").hide();
    }

    main();
});


