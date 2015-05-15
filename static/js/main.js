$(document).ready(function(){
    // add logic about what happens if ehit button is already clicked
    var untrans_p_class;
    var paragraphId;

    function display_translated_text(untrans_text) {

    }

    function placeParagraph(translatedText, textId) {
        // PLaces the translated text in the #translated div if a user adds or
        // updates a translation. Doesn't make a db call.
        translated_list = $(".new_translated");

        console.log(translated_list);

        if (translated_list.length === 0) {
            $("#translated").append("<p class='new_translated' id='n"+textId+"'>"+translatedText+"</p>");
            console.log("fist");
        } else {
            console.log("hey")
        }

    }

    // hides and shows edit button
    $(".a_chapter_and_bttn").on("mouseenter", function () {
        $(this).find("button").show();
    });

    $(".a_chapter_and_bttn").on("mouseleave", function () {
        $(this).find("button").hide();
    });

    // when clicked, gets the paragraph id from the clicked paragraph and shows text area
    $(".edit_text").on("click", function () {
        $("#translate_textarea").show();
        untrans_p_class = $(this).parent().attr("class");
        untrans_p_class = untrans_p_class.split(" ");
        paragraphId = untrans_p_class[1];
    });

    $("#submit_bttn").on("click", function (evt) {
        evt.preventDefault();
        var translated_text = $("#text_form_ta").val();

        $.ajax({
            url: "/save_text",
            data: $('form').serialize() + "&p_id=" + paragraphId,
            type: "POST",
            success: function(response) {
                $("#translate_textarea").hide();
                placeParagraph(response.translated_text, response.order);
            },
            error: function(error) {
                console.log(error);
            }
        });

    });


    // when page loads
    function main() {
        // hide the edit text button
        var edit_text_bttn = $(".edit_text");
        edit_text_bttn.hide();

        $("#translate_textarea").hide();
    }

    main();
});