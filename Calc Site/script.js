var expression = "";
var canEdit = true;

window.onload = function() {

}

function clicked() {
    var key;
    if (event.target.children.length > 0) {
        key = event.target.children[0].innerHTML;
    } 
    else {
        key = event.target.innerHTML;
    }

    if (canEdit) {
        if (key == "+" || key == "-" || key == "*" || key == "/") {
            opertaor(key);
        } 
        else  if (key == "=") {
            expression += document.getElementById("screen").innerHTML.slice(0, -1);
            equals();
        }
        else {
            document.getElementById("screen").innerHTML += key;
        }
    }
    if (key == "CA") {
        clear();
    }
}

document.addEventListener('keydown', function(event) {
    const key = event.key;
    //console.log(key)
    if (canEdit) {
        if (parseInt(key) || key == "0" || key == "." || key == "(" || key == ")" || key == "^") {
            document.getElementById("screen").innerHTML += key;
        } 
        else if (key == 'Backspace') {
            document.getElementById("screen").innerHTML = document.getElementById("screen").innerHTML.slice(0, -1);
        }
        else if (key == "+" || key == "-" || key == "*" || key == "/") {
            opertaor(key);
        } 
        else if (key == "Enter") {
            expression += document.getElementById("screen").innerHTML;
            equals();
        }
    }
    if (key == "Escape") {
        clear();
    }
});

function equals() {
    //console.log(expression)
    var answer;
    try {
        answer = String(eval(expression.replace("^", "**")));
        document.getElementById("screen").innerHTML = answer;
        document.getElementById("expression").innerHTML = expression + "=" + answer;
    } catch (error) {
        document.getElementById("screen").innerHTML = "Error";
        document.getElementById("expression").innerHTML = "";
        canEdit = false;
    }
    
    expression = "";
}

function opertaor(key) {
    document.getElementById("screen").innerHTML += key
    expression += document.getElementById("screen").innerHTML;
    document.getElementById("screen").innerHTML = "";
    document.getElementById("expression").innerHTML = expression
}

function clear() {
    expression = "";
    document.getElementById("screen").innerHTML = "";
    document.getElementById("expression").innerHTML = expression
    canEdit = true;
}