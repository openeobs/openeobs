var phantomJSPadding = '';
describe('NHModal', function(){

	beforeEach(function(){
		var test = document.getElementById('test');
		if(test != null){
			test.parentNode.removeChild(test);
		}
        var test_area = document.createElement('div');
        test_area.setAttribute('id', 'test');
        test_area.style.height = '500px';
        document.getElementsByTagName('body')[0].appendChild(test_area);
        if (navigator.userAgent.indexOf("PhantomJS") > 0 || (navigator.userAgent.indexOf('iPhone') > 0 && navigator.userAgent.indexOf('6_0') > 0) || navigator.userAgent.indexOf('Android') > 0){
           phantomJSPadding = ' ';
        }
	});

    afterEach(function(){
        var test = document.getElementById('test');
        var covers = document.getElementsByClassName('cover');
        var body = document.getElementsByTagName('body')[0];
        if(test != null){
            test.parentNode.removeChild(test);
        }
        
        for(var i = 0; i < covers.length; i++){
	        var cover = covers[i];
	        body.removeChild(cover);
        }
    });

//    it('tells me what the useragent string is', function(){
////        expect(navigator.userAgent.indexOf('iPhone') > 0).toBe(true);
////        expect(navigator.userAgent.indexOf('7_0_') < 0).toBe(true);
//        expect(navigator.userAgent).toBe('meh');
////        Mozilla/5.0 (iPhone; CPU iPhone OS 7_0_3 like Mac OS X) Apple/WebKit/547.51.1 (KHTML, like Gecko) Version/7.0 Mobile/11B508 Safari/9537.53
//    }) ;
	
	it('creates a dialog object', function(){
		var modal = new window.NHModal('id', 'title', 'content', ['<a href="#" data-action="close" data-target="id">Option</a>'], 0, document.getElementById('test'))
		var test_modal = document.getElementById('id');
		var test_modal_content = test_modal.getElementsByClassName('dialogContent')[0]
        if(navigator.userAgent.indexOf('Firefox') > 0){
            expect(test_modal.innerHTML).toEqual('<h2>title</h2><div style="max-height: '+test_modal_content.style.maxHeight+';'+phantomJSPadding+'" class="dialogContent">content</div><ul class="options one-col"><li><a href="#" data-action="close" data-target="id">Option</a></li></ul>');
        }else if(navigator.userAgent.indexOf('MSIE') > 0 || navigator.userAgent.indexOf('Trident') > 0){
            if(navigator.userAgent.indexOf('MSIE 9.0') > 0){
                expect(test_modal.innerHTML).toEqual('<h2>title</h2><div style="max-height: '+test_modal_content.style.maxHeight+';'+phantomJSPadding+'" class="dialogContent">content</div><ul class="options one-col"><li><a href="#" data-target="id" data-action="close">Option</a></li></ul>');
            }else{
                expect(test_modal.innerHTML).toEqual('<h2>title</h2><div class="dialogContent" style="max-height: '+test_modal_content.style.maxHeight+';'+phantomJSPadding+'">content</div><ul class="options one-col"><li><a href="#" data-target="id" data-action="close">Option</a></li></ul>');
            }
        }else{
            expect(test_modal.innerHTML).toEqual('<h2>title</h2><div class="dialogContent" style="max-height: '+test_modal_content.style.maxHeight+';'+phantomJSPadding+'">content</div><ul class="options one-col"><li><a href="#" data-action="close" data-target="id">Option</a></li></ul>');
        }
	});
	
	it('places the dialog under the defined element', function(){
		var modal = new window.NHModal('id', 'title', 'content', ['<a href="#" data-action="close" data-target="id">Option</a>'], 0, document.getElementById('test'))
		var test_modal = document.getElementById('id');
		expect(test_modal.parentNode.id).toEqual('test');
		expect(test_modal.parentNode.localName).toEqual('div');
	});
	
	it('creates a cover object and the dialog object is above it', function(){
		var modal = new window.NHModal('id', 'title', 'content', ['<a href="#" data-action="close" data-target="id">Option</a>'], 0, document.getElementById('test'))
		var test_modal = document.getElementById('id');
		var test_cover = document.getElementsByClassName('cover')[0];
		//var test_modal_zindex = test_modal.style.zIndex;
		var test_modal_zindex = document.defaultView.getComputedStyle(test_modal.parentNode).getPropertyValue('z-index'); 
		//var test_cover_zindex = test_cover.style.zIndex;
		var test_cover_zindex = document.defaultView.getComputedStyle(test_cover).getPropertyValue('z-index');
		expect(parseInt(test_cover_zindex) > parseInt(test_modal_zindex)).toBe(false);
		expect(test_cover.parentNode.localName).toEqual('body');
	});
	
	it('creates a dialog object with two options', function(){
		var modal = new window.NHModal('id', 'title', 'content', ['<a href="#" data-action="close" data-target="id">Option 1</a>','<a href="#" data-action="confirm" data-target="id">Option 2</a>'], 0, document.getElementById('test'))
		var test_modal = document.getElementById('id');
		var test_modal_content = test_modal.getElementsByClassName('dialogContent')[0]
        if(navigator.userAgent.indexOf('Firefox') > 0) {
            expect(test_modal.innerHTML).toEqual('<h2>title</h2><div style="max-height: ' + test_modal_content.style.maxHeight + ';' + phantomJSPadding + '" class="dialogContent">content</div><ul class="options two-col"><li><a href="#" data-action="close" data-target="id">Option 1</a></li><li><a href="#" data-action="confirm" data-target="id">Option 2</a></li></ul>');
        }else if(navigator.userAgent.indexOf('MSIE') > 0 || navigator.userAgent.indexOf('Trident') > 0){
            if(navigator.userAgent.indexOf('MSIE 9.0') > 0){
                expect(test_modal.innerHTML).toEqual('<h2>title</h2><div style="max-height: ' + test_modal_content.style.maxHeight + ';' + phantomJSPadding + '" class="dialogContent">content</div><ul class="options two-col"><li><a href="#" data-target="id" data-action="close">Option 1</a></li><li><a href="#" data-target="id" data-action="confirm">Option 2</a></li></ul>');
            }else {
                expect(test_modal.innerHTML).toEqual('<h2>title</h2><div class="dialogContent" style="max-height: ' + test_modal_content.style.maxHeight + ';' + phantomJSPadding + '">content</div><ul class="options two-col"><li><a href="#" data-target="id" data-action="close">Option 1</a></li><li><a href="#" data-target="id" data-action="confirm">Option 2</a></li></ul>');
            }
        }else{
            expect(test_modal.innerHTML).toEqual('<h2>title</h2><div class="dialogContent" style="max-height: ' + test_modal_content.style.maxHeight + ';' + phantomJSPadding + '">content</div><ul class="options two-col"><li><a href="#" data-action="close" data-target="id">Option 1</a></li><li><a href="#" data-action="confirm" data-target="id">Option 2</a></li></ul>');
        }
    });
	
	it('creates a dialog object with three options', function(){
		var modal = new window.NHModal('id', 'title', 'content', ['<a href="#" data-action="close" data-target="id">Option 1</a>','<a href="#" data-action="confirm" data-target="id">Option 2</a>','<a href="#" data-action="confirm" data-target="id">Option 3</a>'], 0, document.getElementById('test'))
		var test_modal = document.getElementById('id');
		var test_modal_content = test_modal.getElementsByClassName('dialogContent')[0]
        if(navigator.userAgent.indexOf('Firefox') > 0) {
            expect(test_modal.innerHTML).toEqual('<h2>title</h2><div style="max-height: ' + test_modal_content.style.maxHeight + ';' + phantomJSPadding + '" class="dialogContent">content</div><ul class="options three-col"><li><a href="#" data-action="close" data-target="id">Option 1</a></li><li><a href="#" data-action="confirm" data-target="id">Option 2</a></li><li><a href="#" data-action="confirm" data-target="id">Option 3</a></li></ul>');
        }else if(navigator.userAgent.indexOf('MSIE') > 0 || navigator.userAgent.indexOf('Trident') > 0){
            if(navigator.userAgent.indexOf('MSIE 9.0') > 0){
                expect(test_modal.innerHTML).toEqual('<h2>title</h2><div style="max-height: ' + test_modal_content.style.maxHeight + ';' + phantomJSPadding + '" class="dialogContent">content</div><ul class="options three-col"><li><a href="#" data-target="id" data-action="close">Option 1</a></li><li><a href="#" data-target="id" data-action="confirm">Option 2</a></li><li><a href="#" data-target="id" data-action="confirm">Option 3</a></li></ul>');
            }else {
                expect(test_modal.innerHTML).toEqual('<h2>title</h2><div class="dialogContent" style="max-height: ' + test_modal_content.style.maxHeight + ';' + phantomJSPadding + '">content</div><ul class="options three-col"><li><a href="#" data-target="id" data-action="close">Option 1</a></li><li><a href="#" data-target="id" data-action="confirm">Option 2</a></li><li><a href="#" data-target="id" data-action="confirm">Option 3</a></li></ul>');
            }
        }else{
            expect(test_modal.innerHTML).toEqual('<h2>title</h2><div class="dialogContent" style="max-height: ' + test_modal_content.style.maxHeight + ';' + phantomJSPadding + '">content</div><ul class="options three-col"><li><a href="#" data-action="close" data-target="id">Option 1</a></li><li><a href="#" data-action="confirm" data-target="id">Option 2</a></li><li><a href="#" data-action="confirm" data-target="id">Option 3</a></li></ul>');
        }
    });
	
	it('creates a dialog object with four options', function(){
		var modal = new window.NHModal('id', 'title', 'content', ['<a href="#" data-action="close" data-target="id">Option 1</a>','<a href="#" data-action="confirm" data-target="id">Option 2</a>','<a href="#" data-action="confirm" data-target="id">Option 3</a>', '<a href="#" data-action="confirm" data-target="id">Option 4</a>'], 0, document.getElementById('test'))
		var test_modal = document.getElementById('id');
		var test_modal_content = test_modal.getElementsByClassName('dialogContent')[0]
        if(navigator.userAgent.indexOf('Firefox') > 0) {
            expect(test_modal.innerHTML).toEqual('<h2>title</h2><div style="max-height: ' + test_modal_content.style.maxHeight + ';' + phantomJSPadding + '" class="dialogContent">content</div><ul class="options four-col"><li><a href="#" data-action="close" data-target="id">Option 1</a></li><li><a href="#" data-action="confirm" data-target="id">Option 2</a></li><li><a href="#" data-action="confirm" data-target="id">Option 3</a></li><li><a href="#" data-action="confirm" data-target="id">Option 4</a></li></ul>');
        }else if(navigator.userAgent.indexOf('MSIE') > 0 || navigator.userAgent.indexOf('Trident') > 0){
            if(navigator.userAgent.indexOf('MSIE 9.0') > 0){
                expect(test_modal.innerHTML).toEqual('<h2>title</h2><div style="max-height: ' + test_modal_content.style.maxHeight + ';' + phantomJSPadding + '" class="dialogContent">content</div><ul class="options four-col"><li><a href="#" data-target="id" data-action="close">Option 1</a></li><li><a href="#" data-target="id" data-action="confirm">Option 2</a></li><li><a href="#" data-target="id" data-action="confirm">Option 3</a></li><li><a href="#" data-target="id" data-action="confirm">Option 4</a></li></ul>');
            }else {
                expect(test_modal.innerHTML).toEqual('<h2>title</h2><div class="dialogContent" style="max-height: ' + test_modal_content.style.maxHeight + ';' + phantomJSPadding + '">content</div><ul class="options four-col"><li><a href="#" data-target="id" data-action="close">Option 1</a></li><li><a href="#" data-target="id" data-action="confirm">Option 2</a></li><li><a href="#" data-target="id" data-action="confirm">Option 3</a></li><li><a href="#" data-target="id" data-action="confirm">Option 4</a></li></ul>');
            }
        }else{
            expect(test_modal.innerHTML).toEqual('<h2>title</h2><div class="dialogContent" style="max-height: ' + test_modal_content.style.maxHeight + ';' + phantomJSPadding + '">content</div><ul class="options four-col"><li><a href="#" data-action="close" data-target="id">Option 1</a></li><li><a href="#" data-action="confirm" data-target="id">Option 2</a></li><li><a href="#" data-action="confirm" data-target="id">Option 3</a></li><li><a href="#" data-action="confirm" data-target="id">Option 4</a></li></ul>');
        }
    });

    //it('dialogContent is resized correctly when it exceeds the window height', function(){
    //    var test_area = document.getElementById('test');
    //    test_area.style.maxHeight = '300px';
    //    var modal = new window.NHModal('id', 'title', 'content', ['<a href="#" data-action="close" data-target="id">Option</a>'], 0, document.getElementById('test'))
    //    var test_modal = document.getElementById('id');
    //    var test_modal_content = test_modal.getElementsByClassName('dialogContent')[0]
    //    if(navigator.userAgent.indexOf('Firefox') > 0) {
    //        expect(test_modal.innerHTML).toEqual('<h2>title</h2><div style="max-height: ' + test_modal_content.style.maxHeight + ';' + phantomJSPadding + '" class="dialogContent">content</div><ul class="options one-col"><li><a href="#" data-action="close" data-target="id">Option</a></li></ul>');
    //    }else if(navigator.userAgent.indexOf('MSIE') > 0 || navigator.userAgent.indexOf('Trident') > 0){
    //        if(navigator.userAgent.indexOf('MSIE 9.0') > 0){
    //            expect(test_modal.innerHTML).toEqual('<h2>title</h2><div style="max-height: ' + test_modal_content.style.maxHeight + ';' + phantomJSPadding + '" class="dialogContent">content</div><ul class="options one-col"><li><a href="#" data-target="id" data-action="close">Option</a></li></ul>');
    //        }else {
    //            expect(test_modal.innerHTML).toEqual('<h2>title</h2><div class="dialogContent" style="max-height: ' + test_modal_content.style.maxHeight + ';' + phantomJSPadding + '">content</div><ul class="options one-col"><li><a href="#" data-target="id" data-action="close">Option</a></li></ul>');
    //        }
    //    }else{
    //        expect(test_modal.innerHTML).toEqual('<h2>title</h2><div class="dialogContent" style="max-height: ' + test_modal_content.style.maxHeight + ';' + phantomJSPadding + '">content</div><ul class="options one-col"><li><a href="#" data-action="close" data-target="id">Option</a></li></ul>');
    //    }
    //});

    it('event listener setup correctly', function(){
        spyOn(window.NHModal.prototype, "handle_button_events");
        var modal = new window.NHModal('id', 'title', 'content', ['<a href="#" data-action="close" data-target="id">Option</a>'], 0, document.getElementById('test'))
        var test_modal = document.getElementById('id');
        var button = test_modal.getElementsByTagName('li')[0].getElementsByTagName('a')[0];
        var change_event = document.createEvent('CustomEvent');
	    change_event.initCustomEvent('click', false, false, false);	
	    button.dispatchEvent(change_event)
        //button.click();
        expect(window.NHModal.prototype.handle_button_events).toHaveBeenCalled();
    });
});