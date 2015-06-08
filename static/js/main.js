$(document).ready(function(){

    function starRating() {
        var bookRating = $("#book_rating").data("bookrating");

        if (bookRating != undefined) {
            var rating_int = Math.floor(bookRating);
            var rating_dec = bookRating % 1;
            var renderStar = Array(rating_int + 1).join('<i class="fa fa-star"></i>');

            if (rating_dec > 0.6666) {
                renderStar += ('<i class="fa fa-star"></i>');
            } else if (rating_dec > 0.3333) {
                renderStar += ('<i class="fa fa-star-half-o"></i>');
            }

            return renderStar;
        }

        return undefined;
    }

    $("#book_rating").append(starRating());

    // add logic about what happens if edit button is already clicked
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

});