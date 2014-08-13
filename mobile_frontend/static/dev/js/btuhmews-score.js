/**
 * Created by colin on 04/02/14.
 */

// NEWS scoring - takes respiration rate, o2, boolean for on supplementary o2, tempurature, systolic blood pressure, pulse and AVPU choice.
var btuhmews = function (respRate, spo2, o2min, o2max, o2Flag, temp, systolicBP, pulse, avpu) {

    // default score and three in one flag
    var btuhmewsScore = 0;
    var threeInOne = false;
    var colour = "green";
//console.log(btuhmewsScore);
    //console.log(threeInOne);

    // if o2Flag is set to true then increment score by 2
    if (o2Flag.toString() == "true") {
        //console.log("o2Flag is set so should add two to score making it" + (btuhmewsScore + 2));
        btuhmewsScore += 2;
    }
    //console.log(btuhmewsScore);
    //console.log(threeInOne);

    // If respiration Rate is between is less or equal to 9 OR higher or equal to 25 then add3 to score and set 3 in 1. If it's 9, 10 or 11 add 1, if it's 21, 22, 23, 24 add 2
    if (respRate <= 8) {
        //console.log("respRate is 8 or less so should set 3in1 and add 3 to score making it" + (btuhmewsScore + 3));
        btuhmewsScore += 3;
        threeInOne = true;
    }else if (respRate <= 11) {
        //console.log("respRate between 8 & 11 so should add 1 to score making it" + (btuhmewsScore + 1));
        btuhmewsScore += 1;
    }else if(respRate <= 20){
        //console.log("respRate between 12 & 20 so should add 0 to score making it" + (btuhmewsScore + 0));
        btuhmewsScore += 0;
    }else if (respRate <= 24) {
        //console.log("respRate between 20 & 24 so should add 2 to score making it" + (btuhmewsScore + 2));
        btuhmewsScore += 2;
    }else{
        //console.log("respRate is 25 or higher so should set 3in1 and add 3 to score making it" + (btuhmewsScore + 3));
        btuhmewsScore += 3;
        threeInOne = true;
    }
    //console.log(btuhmewsScore);
    //console.log(threeInOne);

    console.log("o2min:" + o2min + " o2max:" + o2max);
    // if o2 is within target range
    if(spo2 >= o2min && spo2 <= o2max){
        btuhmewsScore += 0;
        console.log("was between range");
    } else if (spo2 <= 91) {
        // if o2 is 91 or less then add 3 to score and set 3 in 1. If 92, 93 then add 2, if 94, 95 add 1
        btuhmewsScore += 3;
        threeInOne = true;
        console.log("was less than 91");
    }else if (spo2 <= 93) {
        //console.log("spo2 between 91.1 & 93.9 so should add 2 to score making it" + (btuhmewsScore + 2));
        btuhmewsScore += 2;
        console.log("was less than 93");
    }

    // if temp is 35 or less add 3 to score and set 3 in 1. If 35-36 add 1, if 36 - 38 add 0, if higher than 39 add 1
    if (temp <= 35.0) {
        //console.log("temp is 35 or less so should set 3in1 and add 3 to score making it" + (btuhmewsScore + 3));
        btuhmewsScore += 3;
        threeInOne = true;
    }else if (temp < 36.1) {
        //console.log("temp between 35.1 & 36 so should add 1 to score making it" + (btuhmewsScore + 1));
        btuhmewsScore += 1;
    }else if (temp < 38.1) {
        //console.log("temp between 36.1 & 38 so should add 1 to score making it" + (btuhmewsScore + 0));
        btuhmewsScore += 0;
    }else if (temp < 39.0) {
        //console.log("temp between 38.1 & 39 so should add 1 to score making it" + (btuhmewsScorbody_temperature1));
        btuhmewsScore += 1;
    }else {
        //console.log("temp is more than 39.1 so should add 2 to score making it" + (btuhmewsScore + 2));
        btuhmewsScore += 2;
    }
    //console.log(btuhmewsScore);
    //console.log(threeInOne);

    // if BP is 90 or less add 3 adn set 3 in 1. If 91 -  100 add 2, if 101 - 110 add 1 if 111 - 219 add 0, if 220 or higher add 3 and set 3 in 1
    if (systolicBP < 80) {
        //console.log("systolicBP is 90 or less so should set 3in1 and add 3 to score making it" + (btuhmewsScore + 3));
        btuhmewsScore += 3;
        threeInOne = true
    }else if (systolicBP < 90) {
        //console.log("systolicBP is between 90.1 and 100 so should add 2 to score making it" + (btuhmewsScore + 2));
        btuhmewsScore += 2;
    }else if (systolicBP < 110) {
        //console.log("systolicBP is between 100.1 and 110 so should add 1 to score making it" + (btuhmewsScore + 1));
        btuhmewsScore += 1;
    }else if (systolicBP < 220) {
        //console.log("systolicBP is between 110.1 and 219 so should add 0 to score making it" + (btuhmewsScore + 0));
        btuhmewsScore += 0;
    }else {
        //console.log("systolicBP is more than 219 so should add 3 adn set the 3in1 to score making it" + (btuhmewsScore + 3));
        btuhmewsScore += 3;
        threeInOne = true
    }
    //console.log(btuhmewsScore);
    //console.log(threeInOne);

    // if pulse is 40 or less add 3 and set 3 in 1. If 40 - 50.9 add 1, if 51 - 90.9 add 0. If 91 - 110.9 add 1. If 111 - 130.9 add 2. If 131 or more than add 3 set 3 in 1
    if (pulse <= 49) {
        //console.log("pulse is 40 or less so should set 3in1 and add 3 to score making it" + (btuhmewsScore + 3));
        btuhmewsScore += 3;
        threeInOne = true;
    }else if (pulse <= 99) {
        //console.log("pulse is between 51.1 and 91 so should add 0 to score making it" + (btuhmewsScore + 0));
        btuhmewsScore += 0;
    }else if (pulse <= 119) {
        //console.log("pulse is between 91.1 and 111 so should add 1 to score making it" + (btuhmewsScore + 1));
        btuhmewsScore += 1;
    }else if (pulse < 140) {
        //console.log("pulse is between 111.1 and 131 so should add 2 to score making it" + (btuhmewsScore + 2));
        btuhmewsScore += 2;
    }else {
        //console.log("pulse is 131 or more so should set 3in1 and add 3 to score making it" + (btuhmewsScore + 3));
        btuhmewsScore += 3;
        threeInOne = true
    }
    //console.log(btuhmewsScore);
    //console.log(threeInOne);

    // AVPU - get first letter and make it upper case if it's V,P or U then add 3 and set 3 in 1
    //console.log(avpu);
    avpu = avpu.substr(0,1).toUpperCase();
    //console.log(avpu);
    if (avpu == 'V' || avpu == 'P' || avpu == 'U') {
        //console.log("avpue was V,P or U so add 3 to scopre adn set 3in1" + (btuhmewsScore + 3));
        btuhmewsScore += 3;
        threeInOne = true
    }
    //console.log(btuhmewsScore);
    //console.log(threeInOne);

    //fill in popup text
    if(btuhmewsScore > 7){
        colour = "Red";
    }else if((btuhmewsScore >= 5 && btuhmewsScore <= 7) || threeInOne){
        colour = "Amber";
    }else if(btuhmewsScore >=  1 && btuhmewsScore <= 4){
        colour = "Green";
    }else {
        colour = "white";
    }

    return {
        colour: colour,
        btuhmewsScore: btuhmewsScore,
        threeInOne: threeInOne
    };
};