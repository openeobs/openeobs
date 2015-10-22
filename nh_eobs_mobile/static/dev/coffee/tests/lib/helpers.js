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

// Utility for event handling tests
function default_action(event){
    var test_area = document.getElementById('test');
    if(test_area.classList.contains('default-happened')){
        test_area.classList.add('double-call');
    }else{
        test_area.classList.add('default-happened')
    }
}

// Utility for event handling tests
function non_default_action(event){
    var test_area = document.getElementById('test');
    test_area.classList.add('default-prevented')
}

// Utility for event handling tests
function arg_actions(event, position_one, position_two, position_three){
    var test_area = document.getElementById('test');
    test_area.classList.add('arg');
    test_area.classList.add('p1-' + position_one);
    test_area.classList.add('p2-' + position_two);
    test_area.classList.add('p3-' + position_three);
}

// Utility for event handling tests
function arg_action(event, position_one){
    var test_area = document.getElementById('test');
    test_area.classList.add('arg');
    test_area.classList.add('p1-' + position_one);
}