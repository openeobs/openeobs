/**
 * Created by colinwren on 28/08/15.
 */
function cleanUp(){
    var modals = document.getElementsByClassName('dialog');
    var full_modals = document.getElementsByClassName('full-modal');
    var covers = document.getElementsByClassName('cover');
    for(var i = 0; i < modals.length; i++){
        var modal = modals[i];
        modal.parentNode.removeChild(modal);
    }
    for(var i = 0; i < covers.length; i++){
        var cover = covers[i];
        cover.parentNode.removeChild(cover);
    }
    for(var i = 0; i < full_modals.length; i++){
        var full_modal = full_modals[i];
        full_modal.parentNode.removeChild(full_modal);
    }
    var test = document.getElementById('test');
    test.innerHTML = '';
}
