$(document).ready(function(){

    var edit_text_bttn = $(".edit_text");

    edit_text_bttn.hide();

    $(".a_chapter_and_bttn").on("mouseenter", function() {
        $(this).find("button").show();
    });


    $(".a_chapter_and_bttn").on("mouseleave", function() {
        $(this).find("button").hide();
    });

});