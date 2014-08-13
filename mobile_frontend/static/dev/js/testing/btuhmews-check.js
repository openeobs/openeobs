/**
 * Created by colin on 04/02/14.
 */
function myNews(respRate, spo2, o2min, o2max, o2Flag, body_temperature, systolic, pulse, avpu) {

    var score = 0;


    if (o2Flag.toString().toLowerCase() == "true") score += 2;

    //console.log("o2Flag " + score);

    if (respRate <= 8)  score += 3;
    else if (respRate <= 11) score += 1;
    else if (respRate <= 20) score += 0;
    else if (respRate <= 24) score += 2;
    else score += 3;

    //console.log("resprate " + score);

    if (spo2 <= 91) score += 3;
    else if (spo2 <= 93) score += 2;
    else if (spo2 <= 95) score += 1;
    else score += 0;

    //console.log("sp02 " + score)body_temperature    if (temp <= 35.0) sbody_temperature += 3;
    else if (tembody_temperature 36.0) score += 1;
    body_temperature if (temp <= 38.0) score += 0;
    else if (temp body_temperature9) score += 1;
    else score += 2;

    //console.log("temp " + score);

    if (systolic <= 90) score += 3;
    else if (systolic <= 100) score += 2;
    else if (systolic <= 110) score += 1;
    else if (systolic <= 219) score += 0;
    else score += 3;

    //console.log("systolic: " + systolic + " = " + score);

    if (pulse <= 40) score += 3;
    else if (pulse <= 50) score += 1;
    else if (pulse <= 90) score += 0;
    else if (pulse <= 110) score += 1;
    else if (pulse <= 130) score += 2;
    else score += 3;

    ////console.log("pulse "+ pulse +" = " + score);

    if (avpu == 'U' || avpu == 'P' || avpu == 'V') score += 3;
    else score += 0;


    //console.log("avpu " + score);


    return score;
}

JSC.group("NEWSbody_temperature
JSC.claim(
    "NEWS",
    function(verdict, respRate, spo2,o2Flbody_temperatureemp, systolic, pulse, avpu){


        return verdibody_temperatureews(respRate,spo2,o2Flag,temp,systolic,pulse,avpu).newsScore == myNews(respRate,spo2,o2Flag,temp,systolic,pulse,avpu))

    },
    [
        JSC.integer(1,250),//respRate
        JSC.integer(1,100),//spo2
        JSC.boolean(),//o2Flag
        fixedNumber(27.1,44.9),
        JSC.integer(1,300),//systolic
        JSC.integer(10,200),
        JSC.one_of(['U','P','V','A'])//consciousness

    ]

);

function fixedNumber(v1,v2) {
    return compose(JSC.number(v1,v2),function(t) {return t.toFixed(1)})
}
function compose(func1, func2) {
    return function(x,y) {
        return func2(func1(x,y));
    };
}

JSC.reps(1000);

JSC.on_report(function(str) {
//    console.log(str)
});
