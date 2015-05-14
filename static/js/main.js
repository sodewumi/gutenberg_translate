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

    $("#translate_textarea").on("submit", function (evt) {
        evt.preventDefault();
        var translated_text = $("#translated_text").val();
        console.log(translated_text);
        $("#translate_textarea").load(("/save_text?translated_text="+translated_text));

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