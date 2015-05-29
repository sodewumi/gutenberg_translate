$(document).ready(function(){
    // add logic about what happens if edit button is already clicked
    var langId = $("#translated").data('language');
    var groupId = $("#translated").data('groupid');
    var bookId = $("#translated").data('bookid');
    var bookgroupId = $("#translate_textarea").data('bookgroupid');
    var counter = 0;

    var paragraphId;

    function placeParagraph(translatedText, pId) {
        // Places the translated text in the assigned paragraph div depending on
        // whether a user adds or updates a translation. Doesn't make a db call.
        // change name

        var paragraphId = $("#"+pId);

        paragraphId.empty();
        paragraphId.html("<p>"+translatedText+"</p>");
    }

    function hiddenInputs(newUsername) {

        var hiddenInput = $("<input type='hidden' name='usernames'>").val(newUsername);
        $("#add_book_form .form-group").last().after(hiddenInput);

    }

    function userExists (exists) {
        // Shows different messages depending on what the user enters into the 
        var already_found = false;

        if (exists !== null) {
            $(".collab_usernames").each(function () {
                this_username = $(this).html();
                this_username = this_username.toLowerCase();
                this_username = $.trim(this_username);

                if (this_username === exists) {
                    $("#error_message").html("You've already added this username");
                    already_found = true;
                    return already_found;
                }
            });

            if (already_found === false) {
                hiddenInputs(exists);
                $("#collab_list").append("<li class='collab_usernames'>"+exists+"</li>");
            }
        } else {
            $("#error_message").html("This username doesn't exist");
        }
    }


    // hides and shows edit button
    $(".a_chapter_and_bttn").on("mouseenter", function () {
        $(this).find("button").show();
    });

    $(".a_chapter_and_bttn").on("mouseleave", function () {
        $(this).find("button").hide();
    });

    //on keypress send an ajax rquest that checks if user exists
    $("#group_name_input").on("keypress", function (evt) {
        $("#error_message").empty();
        var key = evt.which;
        if (key === 13) {
            evt.preventDefault();

            $.ajax({
                url: "/check_user",
                data: "&collab_names=" + $("#group_name_input").val(),
                type: "POST",
                success: function(response) {
                    $("#translate_textarea").val("");
                    userExists(response.collab_username);
                },
                error: function(error) {
                    console.log(error);
                }
            });
            $("#group_name_input").val("");
        }
    });

    $("#new_group_names").on("keypress", function (evt) {
        var keystroke = evt.which;
        if (keystroke === 13) {
            evt.preventDefault();
        }
    });

    // clears out form when clicked
    $("#close_btn").on("click", function () {
        $("#group_name_input").val("");
        $("#new_group_names").val("");
        $("#collab_list li:not(:first)").remove();
    });

    $(".edit_text").click(function () {
        $("#translate_textarea").show();
        paragraphId = $(this).data('paragraphid');
    });

    $("#submit_bttn").on("click", function (evt) {
        evt.preventDefault();
        var translated_text = $("#text_form_ta").val();

        $.ajax({
            url: "/save_text",
            data: $('form').serialize() + "&p_id=" + paragraphId + "&bg_id=" + bookgroupId,
            type: "POST",
            success: function(response) {
                $("#translate_textarea").hide();
                placeParagraph(response.translated_text, response.paragraph_id);
            },
            error: function(error) {
                console.log(error);
            }
        });
    });


    function goodreads(){}
    // when page loads
    function main() {
        // hide the edit text button
        var edit_text_bttn = $(".edit_text");
        edit_text_bttn.hide();

        $("#translate_textarea").hide();
    }

    main();
});