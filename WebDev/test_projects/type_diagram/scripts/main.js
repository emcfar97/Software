const perceiver = {"EP":null, "IP":null};
const judger = {"IJ":null, "EJ":null};
const disable = {"XX": null, "XP": null, "XJ": null, "EX": null, "IX": null,}

// type elements
var E_I = document.getElementById("E-I");
var S_N = document.getElementById("S-N");
var T_F = document.getElementById("T-F");
var P_J = document.getElementById("P-J");

// stack elements
var stack = document.getElementById("stack");
var e_perception = document.getElementById("e_perception");
var i_perception = document.getElementById("i_perception");
var e_judgement = document.getElementById("e_judgement");
var i_judgement = document.getElementById("i_judgement");

// content elements
var attitude = document.getElementById("attitude")
var perception = document.getElementById("perception");
var judgement = document.getElementById("judgement");
var unnamed = document.getElementById("unnamed");

var sensation = perception.previousSibling.previousSibling;
var intuition = perception.nextSibling.nextSibling;
var thinking = judgement.previousSibling.previousSibling;
var feeling = judgement.nextSibling.nextSibling;

attitude.oninput = attitude_slider;
perception.oninput = perception_slider;
judgement.oninput = judgement_slider;
unnamed.oninput = unnamed_slider;

// compass elements
var compass = document.getElementById("compass");
var compass_rose = document.getElementById("compass-rose");
var perception_0 = document.getElementById("perception_0");
var judgement_1 = document.getElementById("judgement_1");
var judgement_0 = document.getElementById("judgement_0");
var perception_1 = document.getElementById("perception_1");

function attitude_slider() {

    var value = parseInt(attitude.value);
    var temperament = E_I.textContent + P_J.textContent;
    if (0 < value && value <= 50) {
        E_I.textContent = "E";
    }
    else if (50 < value && value <= 100) {
        E_I.textContent = "I";
    }
    if (!(temperament in disable)) {
        perception.disabled = false;
        judgement.disabled = false;
        rotate_compass(value);
        get_stack();
        perception_slider();
        judgement_slider();
    }
}
function perception_slider() {

    var value = parseInt(perception.value);
    var temperament = E_I.textContent + P_J.textContent;

    if (0 < value && value <= 33) {

        i_perception.textContent = "Ni";
        e_perception.textContent = "Se";
        perception_1.textContent = "Ni";
        perception_0.textContent = "Se";

        if (temperament in judger) {
            S_N.textContent = "N";
        }
        else if (temperament in perceiver) {
            S_N.textContent = "S";
        }
    } 
    else if (33 < value && value <= 66) {

        i_perception.textContent = "Pi";
        e_perception.textContent = "Pe";
        perception_1.textContent = "Pi";
        perception_0.textContent = "Pe";

        S_N.textContent = "X";
    } 
    else if (66 < value && value <= 100) {

        i_perception.textContent = "Si";
        e_perception.textContent = "Ne";
        perception_1.textContent = "Si";
        perception_0.textContent = "Ne";

        if (temperament in judger) {
            S_N.textContent = "S";
        }
        else if (temperament in perceiver) {
            S_N.textContent = "N";
        }
    }
    if (temperament == "IJ") {
        sensation.textContent = 'N';
        intuition.textContent = 'S';
    }
    else {
        sensation.textContent = 'S';
        intuition.textContent = 'N';
    }
}
function judgement_slider() {

    var value = parseInt(judgement.value);
    var temperament = E_I.textContent + P_J.textContent;

    if (0 < value && value <= 33) {

        e_judgement.textContent = "Te";
        i_judgement.textContent = "Fi";
        judgement_0.textContent = "Te";
        judgement_1.textContent = "Fi";

        if (temperament in judger) {
            T_F.textContent = "T";
        }
        else if (temperament in perceiver) {
            T_F.textContent = "F";
        }
    } 
    else if (33 < value && value <= 66) {

        e_judgement.textContent = "Je";
        i_judgement.textContent = "Ji";
        judgement_0.textContent = "Je";
        judgement_1.textContent = "Ji";

        T_F.textContent = "X";
    } 
    else if (66 < value && value <= 100) {

        e_judgement.textContent = "Fe";
        i_judgement.textContent = "Ti";
        judgement_0.textContent = "Fe";
        judgement_1.textContent = "Ti";


        if (temperament in judger) {
            T_F.textContent = "F";
        }
        else if (temperament in perceiver) {
            T_F.textContent = "T";
        }
    }
    if (temperament == "IJ") {
        thinking.textContent = 'T';
        feeling.textContent = 'F';
    }
    else {
        thinking.textContent = 'F';
        feeling.textContent = 'T';
    }
}
function unnamed_slider() {

    var value = parseInt(unnamed.value);
    var temperament = E_I.textContent + P_J.textContent;
    if (0 < value && value <= 50) {
        P_J.textContent = "P";
    }
    else if (50 < value && value <= 100) {
        P_J.textContent = "J";
    }
    if (!(temperament in disable)) {
        perception.disabled = false;
        judgement.disabled = false;
        rotate_compass(value);
        get_stack();
        perception_slider();
        judgement_slider();
    }
}
function get_stack() {
    
    var temperament = E_I.textContent + P_J.textContent;

    switch (temperament) {
        case "EP":
            stack.replaceChildren(
                e_perception, ' - ',
                i_judgement, ' - ',
                e_judgement, ' - ',
                i_perception
            );
            compass.replaceChildren(
                perception_0,
                judgement_1,
                judgement_0,
                perception_1,
                compass_rose
            );
            perception_0.style.gridArea = "1 / 2";
            judgement_1.style.gridArea = "2 / 1";
            judgement_0.style.gridArea = "2 / 3";
            perception_1.style.gridArea = "3 / 2";
            break;
        case "IJ":
            stack.replaceChildren(
                i_perception, ' - ',
                e_judgement, ' - ',
                i_judgement, ' - ',
                e_perception
            );
            compass.replaceChildren(
                perception_1,
                judgement_0,
                judgement_1,
                perception_0,
                compass_rose
            );
            perception_1.style.gridArea = "1 / 2";
            judgement_0.style.gridArea = "2 / 1";
            judgement_1.style.gridArea = "2 / 3";
            perception_0.style.gridArea = "3 / 2";
            break;
        case "EJ":
            stack.replaceChildren(
                e_judgement, ' - ',
                i_perception, ' - ',
                e_perception, ' - ',
                i_judgement
            );
            compass.replaceChildren(
                judgement_0,
                perception_1,
                perception_0,
                judgement_1,
                compass_rose
            );
            judgement_0.style.gridArea = "1 / 2";
            perception_1.style.gridArea = "2 / 1";
            perception_0.style.gridArea = "2 / 3";
            judgement_1.style.gridArea = "3 / 2";
            break;
        case "IP":
            stack.replaceChildren(
                i_judgement, ' - ',
                e_perception, ' - ',
                i_perception, ' - ',
                e_judgement
            );
            compass.replaceChildren(
                judgement_1,
                perception_0,
                perception_1,
                judgement_0,
                compass_rose
            );
            judgement_1.style.gridArea = "1 / 2";
            perception_0.style.gridArea = "2 / 1";
            perception_1.style.gridArea = "2 / 3";
            judgement_0.style.gridArea = "3 / 2";
            break;
    }
}
function rotate_compass(value) {
    
    var degree = (value - 50) * 1.8;
    value = 'rotate(' + degree + 'deg)'

    compass_rose.style.transform = value;
}