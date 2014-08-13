function myMews(pulse, respRate,temp,urine,systolic,consciousness){

 var score = 0;

        if(pulse <= 40) score += 2;
        else if(pulse >= 41 && pulse <= 50) score += 1;
        else if(pulse >= 51 && pulse <= 100) score += 0;
        else if(pulse >= 101 && pulse <=110) score += 1;
        else if(pulse >= 111 && pulse <= 130) score += 2;
        else score += 3;

        if(respRate <= 7)  score += 3;
        else if(respRate >= 8 && respRate <=10) score += 2;
        else if(respRate >= 11 && respRate <= 14) score += 0;
        else if(respRate >= 15 && respRate <= 20) score += 1;
        else if(respRate >= 21 && respRate <= 29) score += 2;
        else score += 3;


        if(temp <= 35.0) score += 2;
        else if(temp > 35.0 && temp <= 36.0) score += 1;
        else if(temp > 36.0 && temp <= 38.0) score += 0;
        else if(temp > 38 && temp <= 38.5) score += 1;
        else score += 2;

        if(urine == 1) score += 3;
        else if(urine == 2) score += 2;
        else score += 0;


        if(systolic <= 70) score += 3;
        else if(systolic >= 71 && systolic <= 80) score += 2;
        else if(systolic >= 80 && systolic <= 100) score += 1;
        else if(systolic >= 101 && systolic <= 199) score += 0;
        else score += 2;



        if (typeof(consciousness) == "string") {
            if (consciousness == 'U')  score += 3;
            else if (consciousness == 'P')  score += 2;
            else if (consciousness == 'V' || consciousness == 'C') score += 1;
            else score += 0;
        } else {
            if (consciousness <= 8) score += 3;
            else if (consciousness <= 13)  score += 2;
            else if (consciousness <= 14)  score += 1;
            else score += 0
        }



    return score;
}

JSC.group("MEWS");

JSC.claim(
    "MEWS",
    function(verdict, pulse, respRate, temp, urine, systolic, consciousness){

        return verdict(mews(pulse,respRate,temp,urine,systolic,consciousness).mewsScore == myMews(pulse,respRate,temp,urine,systolic,consciousness))

    },
    [
       JSC.integer(1,250),//pulse
       JSC.integer(1,59),//respRate
       JSC.number(27.1,44.9),//temp
       JSC.integer(1,3),//urine
       JSC.integer(1,300),//systolic
       JSC.one_of([JSC.one_of(['U','P','V','C']),JSC.integer(1,15)])//consciousness

    ]

);

JSC.reps(1000);

JSC.on_report(function(str) {
    document.getElementById("results").innerHTML += str;
    document.getElementById("results").innerHTML += "<br>";
});