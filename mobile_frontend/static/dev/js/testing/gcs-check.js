/**
 * Created by colin on 24/01/14.
 */
function myGCS(eyes, verbal, motor){
    var score = 0;
    if(eyes == "C"){
        score += 1;
    }else{
       switch(eyes){
           case 1:
              score += 1;
              break;
           case 2:
               score += 2;
               break;
           case 3:
               score += 3;
               break;
           case 4:
               score += 4;
               break;
           default:
               console.log("invalid input");
               break;
       }
    }
    if(verbal == "T"){
        score += 1;
    }else{
        switch(verbal){
            case 1:
                score += 1;
                break;
            case 2:
                score += 2;
                break;
            case 3:
                score += 3;
                break;
            case 4:
                score += 4;
                break;
            case 5:
                score += 5;
                break;
            default:
                console.log("invalid input");
                break;
        }
    }

    switch(motor){
        case 1:
            score += 1;
            break;
        case 2:
            score += 2;
            break;
        case 3:
            score += 3;
            break;
        case 4:
            score += 4;
            break;
        case 5:
            score += 5;
            break;
        case 6:
            score += 6;
            break;
        default:
            console.log("invalid input - m ");
            break;
    }

    return score;
}

JSC.group("GCS");

JSC.claim("GCS", function(verdict, eyes, verbal, motor){
        return verdict(gcs(eyes, verbal, motor).gcsScore == myGCS(eyes, verbal, motor))
    },
    [
        JSC.one_of([JSC.character('C'),JSC.integer(1,4)]), // eyes
        JSC.one_of([JSC.character('T'), JSC.integer(1,5)]), // verbal
        JSC.integer(1,6) // motor
    ]
);

JSC.reps(1000);

JSC.on_report(function(str) {
    document.getElementById("results").innerHTML += str;
    document.getElementById("results").innerHTML += "<br>";
});