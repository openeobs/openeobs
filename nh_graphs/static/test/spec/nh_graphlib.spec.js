describe('NHGraphlib - Object', function() {
    var graphlib, request;
    beforeEach(function () {
        if(graphlib == null){
            graphlib = new NHGraphLib();
        }
    });

    afterEach(function () {
        if (graphlib != null) {
           graphlib = null;
        }
         var covers = document.getElementsByClassName('cover');
        var body = document.getElementsByTagName('body')[0];
         for(var i = 0; i < covers.length; i++){
	        var cover = covers[i];
	        body.removeChild(cover);
        }
    });

    it('creates a NHMobile object with version number', function () {
        expect(graphlib.version).toEqual('0.0.1')
    });
});
