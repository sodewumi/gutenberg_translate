$(document).ready(function(){
    // add logic about what happens if ehit button is already clicked
    var untrans_p_class;
    var paragraphId;

    function display_translated_text(untrans_text) {

    }

    function placeParagraph(translatedText, pId) {
        // PLaces the translated text in the #translated div if a user adds or
        // updates a translation. Doesn't make a db call.
        var paragraphId = $("#"+pId);

        paragraphId.empty();
        paragraphId.html("<p>"+translatedText+"</p>");


        // var translatedList = $(".finished_translations");
        // var translatedListLength = translatedList.length;
        // var paragraphTextId;
        // var insertionParagraphNumber = 0; //max
        // var textIdNum = +textId;


        // // checks if a translation has been added previously
        // if (translatedListLength === 0) {
        //     console.log("appending");
        //     $("#translated").append("<p class='finished_translations' id='t"+textId+
        //         "'>"+translatedText+"</p>");
        // } else {
        //     console.log('not empty');
        //     // finds the paragraph whose textId is before the newly translated
        //     // paragraph (including itself)
        //     translatedList.each(function () {
        //         paragraphTextId = $(this).attr("id");
        //         paragraphTextId = +paragraphTextId.substring(1);

        //         if ((insertionParagraphNumber <= paragraphTextId) &&
        //                 (insertionParagraphNumber < textIdNum)) {
        //             insertionParagraphNumber = paragraphTextId;
        //         }
        //     });

        //     // checks if you are updating or adding a new translation
        //     if (insertionParagraphNumber === textIdNum) {
        //         updated_paragraph = $("#t" +textId);
        //         $("#t" +textId).empty();
        //         $("#t" +textId).html(translatedText);
        //     } else {
        //         var beforeParagraph = $("#t" +
        //             insertionParagraphNumber.toString());
        //         beforeParagraph.after("<p class='finished_translations' id='t"+textId+"'>"+translatedText+"</p>");

        //     }
        // }

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


    // when page loads
    function main() {
        // hide the edit text button
        var edit_text_bttn = $(".edit_text");
        edit_text_bttn.hide();

        $("#translate_textarea").hide();
    }

    main();
});