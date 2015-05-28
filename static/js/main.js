$(document).ready(function(){
    // add logic about what happens if edit button is already clicked
    var langId = $("#translated").data('language');
    var groupId = $("#translated").data('groupid');
    var bookId = $("#translated").data('bookid');
    var bookgroupId = $("#translated").data('bookgroupid');

    var paragraphId;

    function placeParagraph(translatedText, pId) {
        // Places the translated text in the assigned paragraph div depending on
        // whether a user adds or updates a translation. Doesn't make a db call.
        // change name
        var paragraphId = $("#"+pId);

        paragraphId.empty();
        paragraphId.html("<p>"+translatedText+"</p>");
    }



    // hides and shows edit button
    $(".a_chapter_and_bttn").on("mouseenter", function () {
        $(this).find("button").show();
    });

    $(".a_chapter_and_bttn").on("mouseleave", function () {
        $(this).find("button").hide();
    });

    //on keypress send an ajax rquest that checks if user exists
    $("#collab_names").on("keypress", function (evt) {

        var key = evt.which;
        if (key === 13) {
            evt.preventDefault();
            $.ajax({
                url: "/check_user",
                data: "&collab_names=" + $("#collab_names").val(),
                type: "POST",
                success: function(response) {
                    $("#translate_textarea").val("");
                    userExists(response.collab_username);
                },
                error: function(error) {
                    console.log(error);
                }
            });
            $("#collab_names").val("");
        }
    });

    function userExists (exists) {
        var already_found = false;
        collab_list = $("#collab_list");
        if (exists !== null) {
            $(".collab_usernames").each(function () {
                if ($(this).html() === exists) {
                    $("#error_message").html("You've already added this username");
                    already_found = true;
                    return already_found;
                }
            });

            if (already_found === false) {
                collab_list.append("<li class='collab_usernames'>"+exists+"</li>");
            }

        } else {
            $("#error_message").html("This username doesn't exist");
        }

    }


    // when clicked, gets the paragraph id from the clicked paragraph and shows text area
    // $(".edit_text").on("click", function () {
    //     $("#translate_textarea").show();
    //     // var groupid = $("#user_controls").data('groupid');
    //     untrans_p_class = $(this).parent().attr("class");
    //     untrans_p_class = untrans_p_class.split(" ");
    //     paragraphId = untrans_p_class[1];
    // });


    $(".edit_text").click(function () {
        $("#translate_textarea").show();
        paragraphId = $(this).data('paragraphid');
    });

    // $("#chosen_chap_submit").on("click", function (evt) {
    //     $.ajax({
    //         url: "/translate",
    //         data: $('form').serialize() + "&p_id=" + paragraphId + "&g_id=" + groupId + "&l_id=" + langId,
    //         type: "POST",
    //         success: function(response) {
    //             $("#translate_textarea").hide();
    //             placeParagraph(response.translated_text, response.paragraph_id);
    //         },
    //         error: function(error) {
    //             console.log(error);
    //         }
    //     });
    // });

    $("#submit_bttn").on("click", function (evt) {
        evt.preventDefault();
        var translated_text = $("#text_form_ta").val();

        $.ajax({
            url: "/save_text",
            data: $('form').serialize() + "&p_id=" + paragraphId + "&g_id=" + groupId + "&l_id=" + langId + "&b_id=" + bookId + "&bg_id=" + bookgroupId,
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