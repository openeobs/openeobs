/**
 * Created by colin on 10/01/14.
 */

function mews(pulse, respRate, temp, urine, systolic, consciousness){


    var mewsScore = 0;
    var colour = "green";

    if(pulse <= 40){
        mewsScore += 2;
    }else if(pulse <= 50){
        mewsScore += 1;
    }else if(pulse <= 100){
        mewsScore += 0;
    }else if(pulse <= 110){
        mewsScore += 1;
    }else if(pulse <= 130){
        mewsScore += 2;
    }else{
        mewsScore += 3;
    }


    if(respRate <= 7){
        mewsScore += 3;
    }else if(respRate <= 10){
        mewsScore += 2;
    }else if(respRate <= 14){
        mewsScore += 0;
    }else if(respRate <= 20){
        mewsScore += 1;
    }else if(respRate <= 29){
        mewsScore += 2;
    }else{
        mewsScore += 3;
    }


    if(temp <= 35){
        mewsScore += 2;
    }else if(temp <= 36){
        mewsScore += 1;
    }else if(temp <= 38){
        mewsScore += 0;
    }else if(temp <= 38.5){
        mewsScore += 1;
    }else{
        mewsScore += 2;
    }


    if(urine == 1){
        mewsScore += 3;
    }else if(urine == 2){
        mewsScore += 2;
    }else{
        mewsScore += 0;
    }


    if(systolic <= 70){
        mewsScore += 3;
    }else if(systolic <= 80){
        mewsScore += 2;
    }else if(systolic <= 100){
        mewsScore += 1;
    }else if(systolic >= 200){
        mewsScore += 2;
    }


    if(typeof(consciousness) == "string"){
        if(consciousness == 'U'){
            mewsScore += 3;
        }else if(consciousness == 'P'){
            mewsScore += 2;
        }else if(consciousness == 'V' || consciousness == 'C'){
            mewsScore += 1;
        }
    }else{
        if(consciousness <= 8){
            mewsScore += 3;
        }else if(consciousness <= 13){
            mewsScore += 2;
        }else if(consciousness == 14){
            mewsScore  += 1;
        }
    }


    if(mewsScore > 5){
        colour = "Red";
    }else if(3 < mewsScore < 6){
        colour = "Amber";
    }else if(0 < mewsScore < 4){
        colour = "Green";
    }else{
        colour = "White";
    }


    // return the score
    return {
        colour: colour,
        mewsScore: mewsScore
    };
}