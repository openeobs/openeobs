/**
 * Created by colinwren on 15/06/15.
 */

describe('Unit Conversion', function(){
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

    it('Has a function for String to Date Conversion', function(){
        expect(typeof(mobile.date_from_string)).toBe('function');
    });

    it('Has a function for Date to String Conversion', function(){
        expect(typeof(mobile.date_to_string)).toBe('function');
    });

    it('Has a function for Date to DOB (YYYY-MM-DD) String Conversion', function(){
        expect(typeof(mobile.date_to_dob_string)).toBe('function');
    });

    it('Has a function for single to double digit date element conversion', function(){
        expect(typeof(mobile.leading_zero)).toBe('function');
    });

    describe('String to Date Conversion', function(){
        it('converts Odoo Format (YYYY-MM-DD HH:MM:SS) date string to date object', function(){
            var date_string = '1988-01-12 06:00:00';
            var date_for_string = mobile.date_from_string(date_string);
            expect(typeof(date_for_string)).toBe('object');
            if(navigator.userAgent.indexOf('MSIE') < 0 && navigator.userAgent.indexOf('Trident') < 0) {
                expect(date_for_string.constructor.name).toBe('Date');
            }
        });

        it('throws an error when unable to convert invalid date string to date object', function(){
           var date_string = 'The super awesome day when Colin was brought into the world - Colin Epoch';
            expect(function(){ mobile.date_from_string(date_string)}).toThrowError('Invalid date format');
        });
    });

    describe('Date to String Conversion', function(){
        it('converts date object to Odoo Format (YYYY-MM-DD HH:MM:SS) string', function(){
            var date = new Date('1988-01-12T06:00:00');
            var string_for_date = mobile.date_to_string(date);
            expect(string_for_date).toBe('1988-01-12 06:00:00');
        });

        it('converts date to dob string', function(){
            var date = new Date('1988-01-12T06:00:00');
            var string_for_date = mobile.date_to_dob_string(date);
            expect(string_for_date).toBe('1988-01-12');
        });

        it('throws error when converting Invalid Date to to Odoo Format (YYYY-MM-DD HH:MM:SS) string', function(){
            var date = new Date('k');
            expect(function(){ mobile.date_to_string(date) }).toThrowError("Invalid date format");
        });

        it('throws error when converting Invalid Date to to DOB (YYYY-MM-DD) string', function(){
            var date = new Date('k');
            expect(function(){ mobile.date_to_dob_string(date) }).toThrowError("Invalid date format");
        });
    });

    describe('Single to Double Digit date element Conversion', function(){
        it('converts single digit date element to double digit with leading zero', function(){
           var date = new Date('1988-01-12T06:00:00');
           var month = (date.getMonth() +1);
           expect(month.toString()).toBe('1');
           expect(mobile.leading_zero(month)).toBe('01');
        });

        it('does not prepend a zero to double digit date elements', function(){
           var date = new Date('1988-12-12T06:00:00');
           var month = (date.getMonth() +1);
           expect(month.toString()).toBe('12');
           expect(mobile.leading_zero(month)).not.toBe('012');
           expect(mobile.leading_zero(month)).toBe('12');
       });
    });
});