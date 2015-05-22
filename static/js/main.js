$(document).ready(function(){
    // add logic about what happens if ehit button is already clicked
    var untrans_p_class;
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