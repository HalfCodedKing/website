//Made by Felix (Blobtoe)

$(document).ready(function () {
    document.getElementById("main_content").innerHTML = "";

    //only get the passed that need to be shown
    $.getJSON("/weather/scripts/showing_passes.json", function(result) {
        //add a template html block to the page for every pass
        $.each(result, function (i, field) {
            var clone = document.getElementById("template").cloneNode(true);
            document.getElementById("main_content").innerHTML = document.getElementById("main_content").innerHTML + clone.innerHTML;
        });
        //edit the html blocks to show individual passes
        //editing the blocks after they were created makes the order of the passes correctly consistent
        var i = 0;
        $.each(result, function (i, field) {
            ShowPass(field, i);
            i++;
        });
    });

    //read all the passes of the day
    $.getJSON("/weather/scripts/daily_passes.json", function(result) {
        $.each(result, function (i, field) {
            if (field.status == "INCOMING") {
                CountDownTimer(field.los, 'countdown')
            }
        })
        document.getElementById("countdown").innerHTML = "Time until next image: unavailable";
    })
});

function ShowPass(path, i) {
    //get info about the specific pass
    $.getJSON(path, function(result) {
        //change the UTC date to local time
        date = new Date(result.aos).toLocaleString("en-US", {timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone});
        date = new Date(date)

        //add info that is present on all passes
        document.getElementsByClassName("pass_title")[i].innerHTML = date;
        document.getElementsByClassName("sat")[i].innerHTML = "Satellite: " + result.satellite;
        document.getElementsByClassName("max_elev")[i].innerHTML = "Max elevation: " + result.max_elevation + "°";

        //if the pass if from a NOAA satellite
        if (result.satellite.substring(0, 4) == "NOAA") {
            //add the info to the html
            document.getElementsByClassName("main_image")[i].setAttribute("src", result.links.a);
            document.getElementsByClassName("a")[i].setAttribute("href", result.links.a);
            document.getElementsByClassName("b")[i].setAttribute("href", result.links.b);
            document.getElementsByClassName("msa")[i].setAttribute("href", result.links.msa);
            document.getElementsByClassName("msa_precip")[i].setAttribute("href", result.links['msa-precip']);
            document.getElementsByClassName("raw")[i].setAttribute("href", result.links.raw);
        }
        //if the pass is from METEOR-M 2
        else if (result.satellite == "METEOR-M 2") {
            //add the info to the html
            document.getElementsByClassName("main_image")[i].setAttribute("src", result.link);
        }
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