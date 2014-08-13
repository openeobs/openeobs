/**
 * Created with IntelliJ IDEA.
 * User: colin
 * Date: 25/11/13
 * Time: 12:47
 * To change this template use File | Settings | File Templates.
 */

// NEWS scoring - takes respiration rate, o2, boolean for on supplementary o2, tempurature, systolic blood pressure, pulse and AVPU choice.
var news = function (respRate, spo2, o2Flag, body_temperature, systolicBP, pulse, avpu) {

    //console.log(respRate);
    //console.log(spo2);
    //console.log(o2Flag);
    //body_temperatureole.log(temp);
    //console.log(systolicBP);
    //console.log(pulse);
    //console.log(avpu);

    //console.log(typeof(respRate));
    //console.log(typeof(spo2));
    //console.log(typeof(o2Flag));

 body_temperature/console.log(typeof(temp));
    //console.log(typeof(systolicBP));
    //console.log(typeof(pulse));
    //console.log(typeof(avpu));

    // default score and three in one flag
    var newsScore = 0;
    var threeInOne = false;
    var colour = "green";
    //console.log(newsScore);
    //console.log(threeInOne);

    // if o2Flag is set to true then increment score by 2
    if (o2Flag.toString() == "true") {
        //console.log("o2Flag is set so should add two to score making it" + (newsScore + 2));
        newsScore += 2;
    }
    //console.log(newsScore);
    //console.log(threeInOne);

    // If respiration Rate is between is less or equal to 9 OR higher or equal to 25 then add3 to score and set 3 in 1. If it's 9, 10 or 11 add 1, if it's 21, 22, 23, 24 add 2
    if (respRate <= 8) {
        //console.log("respRate is 8 or less so should set 3in1 and add 3 to score making it" + (newsScore + 3));
        newsScore += 3;
        threeInOne = true;
    }else if (respRate <= 11) {
        //console.log("respRate between 8 & 11 so should add 1 to score making it" + (newsScore + 1));
        newsScore += 1;
    }else if(respRate <= 20){
        //console.log("respRate between 12 & 20 so should add 0 to score making it" + (newsScore + 0));
        newsScore += 0;
    }else if (respRate <= 24) {
        //console.log("respRate between 20 & 24 so should add 2 to score making it" + (newsScore + 2));
        newsScore += 2;
    }else{
        //console.log("respRate is 25 or higher so should set 3in1 and add 3 to score making it" + (newsScore + 3));
        newsScore += 3;
        threeInOne = true;
    }
    //console.log(newsScore);
    //console.log(threeInOne);

    // if o2 is 91 or less then add 3 to score and set 3 in 1. If 92, 93 then add 2, if 94, 95 add 1
    if (spo2 <= 91) {
        //console.log("spo2 is 91 or less so should set 3in1 and add 3 to score making it" + (newsScore + 3));
        newsScore += 3;
        threeInOne = true;
    }else if (spo2 < 94) {
        //console.log("spo2 between 91.1 & 93.9 so should add 2 to score making it" + (newsScore + 2));
        newsScore += 2;
    }else if (spo2 < 96) {
        //console.log("spo2 between 94 & 95.9 so should add 1 to score making it" + (newsScore + 1));
        newsScore += 1;
    }else{
        newsScore += 0;
        //console.log("spo2 is more than 96 so should add 0 to score making it" + (newsScore + 0));
    }
    //console.log(newsScore);
    //body_temperatureole.log(threeInOne);

    // if temp is 35 or less add 3 to score and set 3 in 1. If 35-36 add 1, ifbody_temperature- 38 add 0, if higher tbody_temperature39 add 1
    if (temp <= 35.0) {
        //console.log("temp is 35 or less so should set 3in1 and add 3 to score making it" + (newsScore body_temperature);
        newsScore +body_temperature
        threeInOne = true;
    }else if (temp < 36.1) {
        //console.log("temp between 35.1 & 3body_temperature should add 1 to scorebody_temperatureing it" + (newsScore + 1));
        newsScore += 1;
    }else if (temp < 38.1) {
        //console.lobody_temperatureemp between 36.1 & 38 body_temperaturehould add 1 to score making it" + (newsScore + 0));
        newsScore += 0;
    }else if (temp < 39.1) {
        //consolebody_temperature("temp between 38.1 & 39 so should add 1 to score making it" + (newsScore + 1));
        newsScore += 1;
    }else {
        //console.log("temp is more than 39.1 so should add 2 to score making it" + (newsScore + 2));
        newsScore += 2;
    }
    //console.log(newsScore);
    //console.log(threeInOne);

    // if BP is 90 or less add 3 adn set 3 in 1. If 91 -  100 add 2, if 101 - 110 add 1 if 111 - 219 add 0, if 220 or higher add 3 and set 3 in 1
    if (systolicBP <= 90) {
        //console.log("systolicBP is 90 or less so should set 3in1 and add 3 to score making it" + (newsScore + 3));
        newsScore += 3;
        threeInOne = true
    }else if (systolicBP <= 100) {
        //console.log("systolicBP is between 90.1 and 100 so should add 2 to score making it" + (newsScore + 2));
        newsScore += 2;
    }else if (systolicBP <= 110) {
        //console.log("systolicBP is between 100.1 and 110 so should add 1 to score making it" + (newsScore + 1));
        newsScore += 1;
    }else if (systolicBP <= 219) {
        //console.log("systolicBP is between 110.1 and 219 so should add 0 to score making it" + (newsScore + 0));
        newsScore += 0;
    }else {
        //console.log("systolicBP is more than 219 so should add 3 adn set the 3in1 to score making it" + (newsScore + 3));
        newsScore += 3;
        threeInOne = true
    }
    //console.log(newsScore);
    //console.log(threeInOne);

    // if pulse is 40 or less add 3 and set 3 in 1. If 40 - 50.9 add 1, if 51 - 90.9 add 0. If 91 - 110.9 add 1. If 111 - 130.9 add 2. If 131 or more than add 3 set 3 in 1
    if (pulse <= 40) {
        //console.log("pulse is 40 or less so should set 3in1 and add 3 to score making it" + (newsScore + 3));
        newsScore += 3;
        threeInOne = true;
    }else if (pulse < 51) {
        //console.log("pulse is between 40.1 and 51 so should add 1 to score making it" + (newsScore + 1));
        newsScore += 1;
    }else if (pulse < 91) {
        //console.log("pulse is between 51.1 and 91 so should add 0 to score making it" + (newsScore + 0));
        newsScore += 0;
    }else if (pulse < 111) {
        //console.log("pulse is between 91.1 and 111 so should add 1 to score making it" + (newsScore + 1));
        newsScore += 1;
    }else if (pulse < 131) {
        //console.log("pulse is between 111.1 and 131 so should add 2 to score making it" + (newsScore + 2));
        newsScore += 2;
    }else {
        //console.log("pulse is 131 or more so should set 3in1 and add 3 to score making it" + (newsScore + 3));
        newsScore += 3;
        threeInOne = true
    }
    //console.log(newsScore);
    //console.log(threeInOne);

    // AVPU - get first letter and make it upper case if it's V,P or U then add 3 and set 3 in 1
    //console.log(avpu);
    avpu = avpu.substr(0,1).toUpperCase();
    //console.log(avpu);
    if (avpu == 'V' || avpu == 'P' || avpu == 'U') {
        //console.log("avpue was V,P or U so add 3 to scopre adn set 3in1" + (newsScore + 3));
        newsScore += 3;
        threeInOne = true
    }
    //console.log(newsScore);
    //console.log(threeInOne);

    //fill in popup text
    if(newsScore > 7){
       colour = "Red";
    }else if((newsScore >= 5 && newsScore <= 7) || threeInOne){
        colour = "Amber";
    }else if(newsScore >=  1 && newsScore <= 4){
        colour = "Green";
    }else {
        colour = "white";
    }
    //console.log(newsScore);
    //console.log(threeInOne);
    //console.log(colour);

    return {
        colour: colour,
        newsScore: newsScore,
        threeInOne: threeInOne
    };
};