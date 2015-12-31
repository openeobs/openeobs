/**
 * Created by colinwren on 15/06/15.
 */
describe('Utilities', function(){
    var mobile;
    beforeEach(function () {
        if(mobile == null){
            mobile = new NHMobile();
        }
    });

    afterEach(function () {
        if (mobile != null) {
           mobile = null;
        }
    });

    it('has a function to get the current timestamp in seconds', function(){
        expect(typeof(mobile.get_timestamp)).toBe('function');
    });

    describe('Timestamp', function(){
        it('returns the timestamp in seconds since unix epoch', function(){
            var timestamp = Math.round(new Date().getTime() / 1000);
            expect(mobile.get_timestamp()).toBe(timestamp);
        });

        it('does not return the timestamp in milliseconds since unix epoch like JS normally does', function(){
            var timestamp = new Date().getTime();
            expect(mobile.get_timestamp()).not.toBe(timestamp);
        });
    });
});