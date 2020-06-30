$(document).ready(function () {
    document.getElementById("main_content").innerHTML = "";

    $.getJSON("/weather/scripts/showing_passes.json", function(result) {
        $.each(result, function (i, field) {
            ShowPass(field);
        })
    });

    //start the countdown timer until the next pass
    CountDownTimer(document.getElementById("countdown").getAttribute("next_pass"), 'countdown');
});

function ShowPass(path, pass_index) {
    $.getJSON(path, function(result) {
        var clone = document.getElementById("template").cloneNode(true);

        date = new Date(result.aos).toLocaleString("en-US", {timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone});
        date = new Date(date)

        document.getElementById("main_content").innerHTML = document.getElementById("main_content").innerHTML + clone.innerHTML;
        document.getElementsByClassName("main_image")[document.getElementsByClassName("main_image").length - 1].setAttribute("src", result.links.a);
        document.getElementsByClassName("pass_title")[document.getElementsByClassName("pass_title").length - 1].innerHTML = date;
        document.getElementsByClassName("sat")[document.getElementsByClassName("sat").length - 1].innerHTML = "Satellite: " + result.satellite;
        document.getElementsByClassName("max_elev")[document.getElementsByClassName("max_elev").length - 1].innerHTML = "Max elevation: " + result.max_elevation + "°";
        document.getElementsByClassName("a")[document.getElementsByClassName("a").length - 1].setAttribute("href", result.links.a);
        document.getElementsByClassName("b")[document.getElementsByClassName("b").length - 1].setAttribute("href", result.links.b);
        document.getElementsByClassName("msa")[document.getElementsByClassName("msa").length - 1].setAttribute("href", result.links.MSA);
        document.getElementsByClassName("msa_precip")[document.getElementsByClassName("msa_precip").length - 1].setAttribute("href", result.links['MSA-precip']);
        document.getElementsByClassName("raw")[document.getElementsByClassName("raw").length - 1].setAttribute("href", result.links.raw);
    });
}

function CountDownTimer(dt, id)
{
    var end = new Date(dt).toLocaleString("en-US", {timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone});
    end = new Date(end);

    var _second = 1000;
    var _minute = _second * 60;
    var _hour = _minute * 60;
    var _day = _hour * 24;
    var timer;

    function showRemaining() {
        var now = new Date();
        var distance = end - now;
        if (distance < 0) {

            clearInterval(timer);
            document.getElementById(id).innerHTML = 'Processing images...';

            return;
        }
        var days = Math.floor(distance / _day);
        var hours = Math.floor((distance % _day) / _hour);
        var minutes = Math.floor((distance % _hour) / _minute);
        var seconds = Math.floor((distance % _minute) / _second);

        document.getElementById(id).innerHTML = "Time until next image: about " + days + 'days ';
        document.getElementById(id).innerHTML += hours + 'hrs ';
        document.getElementById(id).innerHTML += minutes + 'mins ';
        document.getElementById(id).innerHTML += seconds + 'secs';
    }

    timer = setInterval(showRemaining, 1000);
}