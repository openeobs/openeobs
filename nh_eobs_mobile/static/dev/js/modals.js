/**
 * Created by colin on 30/12/13.
 */

// displays a modal with id, title in h2, content and menu options
// e.g. displayModal("obsPick", "Pick an observation", "<ul><li>meh</li><li>Meh</li></ul>", ["<a>cancel</a>", "<a>Accept</a>"]);
function displayModal(id, title, content, options, popupTime, el){
    popupTime = typeof popupTime !== 'undefined' ? popupTime : 0;
    el = typeof el !== 'undefined' ? el : ".content";
    console.log("id:" + id + " title:" + title + " content:" + content + " options:" + options + " popupTime:" + popupTime + " el:" + el);


    // add cover to the content (to show the user something has popped up)
    $(".content").prepend("<div class=\"cover\" id=\"obsCover\" style=\"height:"+$(".content").height()+"px\"></div>");

    // create the dialog element and give it the id selected
    var dialog = $("<div class=\"dialog\" id=\"" + id + "\"></div>");

    // append the title (as a h2)
    dialog.append("<h2>" + title + "</h2>") ;

    // append the content (this is written outside the function)
    var dialogInfo = $("<div class=\"dialogContent\"></div>");
    if(typeof(content) !== "object"){
        dialogInfo.append(content);
        dialog.append(dialogInfo);
    } // append the options (which is an array of DOM elements)
    var optLenStr;
    switch (options.length){
        case 1:
            optLenStr = "one";
            break;
        case 2:
            optLenStr = "two";
            break;
        case 3:
            optLenStr = "three";
            break;
        case 4:
            optLenStr = "four";
            break;
        default:
            optLenStr = "one";
            break;
    }
    var buttons = $("<ul class=\"options " + optLenStr + "-col\"></ul>");
    for(var i =0; i < options.length; i++){
        buttons.append("<li>" + options[i] + "</li>");
    }
    if(typeof(content) !== "object"){
        dialog.append(buttons);
    }

    // present the modal and lock the page (so can't scroll)
    dialog.css("display", "inline-block").fadeIn(popupTime);
    $(el).append(dialog);
    $("body").css("overflow", "hidden");

    // make sure the modal fits on the screen properly
    if(typeof(content) == "object"){
        console.log("content is object")
        content.onload = function(){
            dialogInfo.append(this);
            dialog.append(dialogInfo);
            dialog.append(buttons);
            calculateModalSize(dialog, dialogInfo);
        }
    }else{
        calculateModalSize(dialog, dialogInfo);
    }
}

function calculateModalSize(dialog, dialogInfo){
    var customMargin = 40;
    var pageHeaderHeight = $(".header").height(); // height of the page header
    var boxHeaderHeight = dialog.children("h2").height(); // height of the modal title
    var boxOptionsHeight = dialog.children(".options" ).children("li").first().height(); // height of the menu
    var patientNameHeight = $("#patientName").height();
    var availableSpace = (($(window).height()) - (($(".header").height() - patientNameHeight) - (customMargin *2))); // the total amount of space available after accounting for header and margin
    var maxContentHeight = ((availableSpace - (boxHeaderHeight + boxOptionsHeight) - customMargin*2));  // the total space available for the content to take up
    // log it for debugging
    if(console){
        console.log("available space is: " + $(window ).height() + " - " + ($(".header").height() - (customMargin *2)) + " so entire popup is " + availableSpace + ", options is " + boxOptionsHeight + " and header is " + boxHeaderHeight + " so menu can be" + maxContentHeight);
    }

    // based on the size of the modal apply some heights and stuff
    dialog.css("top", pageHeaderHeight + patientNameHeight + customMargin);
    dialog.css("max-height", availableSpace);
    dialogInfo.css("max-height", maxContentHeight);
}


// dismisses a modal, uses a mode to either hide or remove the modal
function dismissModal(id, mode){
    // if mode is delete then remove the element
    if(mode == "delete"){
        $("#"+id).remove();
        // if mode is hide then don't display it
    }else if(mode == "hide"){
        $("#"+id).css("display", "none");

    }else if(mode == "all"){
        $(".dialog").remove();
    }else{
        return false;
    }
    $(".cover").remove();
    $("body").css("overflow", "auto");
}

// click cancel on a modal should hide that modal
$(".content").on("click", ".dialog .cancel", function(e){
    e.preventDefault();
    dismissModal("","all");
});

// clicking the cover should hide modals
$(".content").on("click", ".cover", function(e){
    e.preventDefault();
    dismissModal("","all");
});