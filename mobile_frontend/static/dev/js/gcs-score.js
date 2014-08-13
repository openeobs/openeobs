/**
 * Created with IntelliJ IDEA.
 * User: colin
 * Date: 25/11/13
 * Time: 12:47
 * To change this template use File | Settings | File Templates.
 */

// GCS scoring function - takes E (eye), V (verbal) and M (motor) values as inputs and calculates a GCS score
function gcs(E, V, M) {
    var gcsScore = 0; // Default score
    var colour = "green";
    if (E == "C") {
        gcsScore += 1;
    }else if( E >= 1 && E <= 4 ){
        gcsScore += parseInt(E);
    }else{
        //invalid input
    }

    if (V == "T"){
        gcsScore += 1;
    }else if( V >= 1 && V <= 5 ){
        gcsScore += parseInt(V);
    }else{
        // invalid input
    }

    if (M >= 1 && M <= 6) {
        gcsScore += parseInt(M);
    }else{
        // invalid input
    }

    // Set the colour of the score based on the range
    if(gcsScore < 9){
        colour = "red";
    }else if (gcsScore >= 9 && gcsScore <= 12){
        colour = "amber";
    }else if (gcsScore >= 13){
        colour = "green";
    }

    // return the score
    return {
        colour: colour,
        gcsScore: gcsScore
    };
};



