$(document).ready(function(){
    // add logic about what happens if ehit button is already clicked
    var untrans_p_class;

    function display_translated_text(untrans_text) {
        alert('hey');
    }

    // hides and shows edit button
    $(".a_chapter_and_bttn").on("mouseenter", function () {
        $(this).find("button").show();
    });

    $(".a_chapter_and_bttn").on("mouseleave", function () {
        $(this).find("button").hide();
    });

    $(".edit_text").on("click", function () {
        $("#translate_textarea").show();
        untrans_p_class = $(this).parent().attr("class");
    });

    $("#submit_bttn").on("click", function (evt) {
        evt.preventDefault();
        var translated_text = $("#text_form_ta").val();
        console.log(translated_text);

        $.ajax({
            url: "/save_text",
            data: $('form').serialize(),
            type: "POST",
            success: function(response) {
                $("#translate_textarea").hide();
                $("#translated").append(response.translated_text);
                console.log(response.translated_text);
            },
            error: function(error) {
                console.log(error);
            }
        });
        // $("#translate_textarea").load(("/save_text?translated_text="+translated_text));

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