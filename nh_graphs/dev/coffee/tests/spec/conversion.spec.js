/**
 * Created by colinwren on 22/06/15.
 */
describe('Conversion', function() {

    var graphlib;

    beforeEach(function () {
        if(graphlib == null){
            graphlib = new NHGraphLib();
        }
    });

    afterEach(function () {
        if (graphlib != null) {
           graphlib = null;
        }
    });

    it('Has a function for String to Date Conversion', function(){
        expect(typeof(graphlib.date_from_string)).toBe('function');
    });

    it('Has a function for Date to String Conversion', function(){
        expect(typeof(graphlib.date_to_string)).toBe('function');
    });

    it('Has a function for single to double digit date element conversion', function(){
        expect(typeof(graphlib.leading_zero)).toBe('function');
    });

    describe('String to Date Conversion', function(){

        it('converts Odoo Format (YYYY-MM-DD HH:MM:SS) date string to date object', function(){
            var date_string = '1988-01-12 06:00:00';
            var date_for_string = graphlib.date_from_string(date_string);
            expect(typeof(date_for_string)).toBe('object');
            if(navigator.userAgent.indexOf('MSIE') < 0 && navigator.userAgent.indexOf('Trident') < 0) {
                expect(date_for_string.constructor.name).toBe('Date');
            }
            expect(date_for_string.getFullYear()).toBe(1988);
            expect(date_for_string.getMonth()).toBe(0);
            expect(date_for_string.getDate()).toBe(12);
            expect(date_for_string.getHours()).toBe(6);
            expect(date_for_string.getMinutes()).toBe(0);
            expect(date_for_string.getSeconds()).toBe(0);
        });

        it('converts Odoo Format (YYYY-MM-DD HH:MM:SS) date string to date object - EOBS 1366', function(){
            var date_string = '2017-07-02 16:05:48';
            var date_for_string = graphlib.date_from_string(date_string);
            expect(typeof(date_for_string)).toBe('object');
            if(navigator.userAgent.indexOf('MSIE') < 0 && navigator.userAgent.indexOf('Trident') < 0) {
                expect(date_for_string.constructor.name).toBe('Date');
            }
            expect(date_for_string.getFullYear()).toBe(2017);
            expect(date_for_string.getMonth()).toBe(6);
            expect(date_for_string.getDate()).toBe(2);
            expect(date_for_string.getHours()).toBe(16);
            expect(date_for_string.getMinutes()).toBe(5);
            expect(date_for_string.getSeconds()).toBe(48);
        });

        it('throws an error when unable to convert invalid date string to date object', function(){
           var date_string = 'The super awesome day when Colin was brought into the world - Colin Epoch';
            expect(function(){ graphlib.date_from_string(date_string)}).toThrowError('Invalid date format');
        });
    });

    describe('Date to String Conversion', function(){

        it('converts date object to Graph Format (day DD/MM/YY HH:MM) string', function(){
            var date = new Date('1988-01-12T06:00:00');
            var string_for_date = graphlib.date_to_string(date);
            expect(string_for_date).toBe('Tue 12/01/88 06:00');
        });

        it('throws error when converting Invalid Date to to Odoo Format (YYYY-MM-DD HH:MM:SS) string', function(){
            var date = new Date('k');
            expect(function(){ graphlib.date_to_string(date) }).toThrowError("Invalid date format");
        });
    });

    describe('Single to Double Digit date element Conversion', function(){

        it('converts single digit date element to double digit with leading zero', function(){
           var date = new Date('1988-01-12T06:00:00');
           var month = (date.getMonth() +1);
           expect(month.toString()).toBe('1');
           expect(graphlib.leading_zero(month)).toBe('01');
        });

        it('does not prepend a zero to double digit date elements', function(){
           var date = new Date('1988-12-12T06:00:00');
           var month = (date.getMonth() +1);
           expect(month.toString()).toBe('12');
           expect(graphlib.leading_zero(month)).not.toBe('012');
           expect(graphlib.leading_zero(month)).toBe('12');
       });
    });
});




