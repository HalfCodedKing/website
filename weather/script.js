//Made by Felix (Blobtoe)

//everything is 'display: none' until everything is loaded
$(document).ready(function () {
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
            //get the first pass with status INCOMING
            if (field.status == "INCOMING") {
                //start the countdown to the start of the next pass
                CountDownTimer(field.aos, 'countdown')
                //fill in info about the next pass
                document.getElementById("next_pass_sat").innerHTML = "Satellite: " + field.satellite;
                document.getElementById("next_pass_max_elev").innerHTML = "Max Elevation: " + field.max_elevation + "°";
                document.getElementById("next_pass_frequency").innerHTML = "Frequency: " + field.frequency + " Hz";
                document.getElementById("next_pass_aos").innerHTML = "AOS: " + field.aos;
                document.getElementById("next_pass_los").innerHTML = "LOS: " + field.los;
                return false;
            }
        })
        //if no passes are incoming (last pass of the day)
        document.getElementById("countdown").innerHTML += "Next pass unavailable";
    })

    //hande clicks on the next pass more info button
    document.getElementById("next_pass_more_info_button").addEventListener("click", ShowNextPassInfo);

    //show everything once everything is loaded
    document.getElementById("loading").style.display = "none";
    document.getElementById("next_pass").style.display = "block";
    document.getElementsByClassName("seperator")[0].style.display = "block";
    document.getElementById("main_content").style.display = "block";
    document.getElementById("footer_div").style.display = "block";
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
        document.getElementsByClassName("frequency")[i].innerHTML = "Frequency: " + result.frequency + " Hz";

        //if the pass if from a NOAA satellite
        if (result.satellite.substring(0, 4) == "NOAA") {
            //add the info to the html
            document.getElementsByClassName("main_image")[i].setAttribute("src", result.links.a);
            document.getElementsByClassName("a")[i].setAttribute("href", result.links.a);
            document.getElementsByClassName("b")[i].setAttribute("href", result.links.b);
            document.getElementsByClassName("hvct")[i].setAttribute("href", result.links.hvct)
            document.getElementsByClassName("msa")[i].setAttribute("href", result.links.msa);
            document.getElementsByClassName("msa_precip")[i].setAttribute("href", result.links['msa-precip']);
            document.getElementsByClassName("raw")[i].setAttribute("href", result.links.raw);
        }
        //if the pass is from METEOR-M 2
        else if (result.satellite == "METEOR-M 2") {
            //add the info to the html
            document.getElementsByClassName("main_image")[i].setAttribute("src", result.link);
            document.getElementsByClassName("a")[i].style.display = "none";
            document.getElementsByClassName("b")[i].style.display = "none";
            document.getElementsByClassName("hvct")[i].style.display = "none"
            document.getElementsByClassName("msa")[i].style.display = "none";
            document.getElementsByClassName("msa_precip")[i].style.display = "none";
            document.getElementsByClassName("raw")[i].style.display = "none";
        }
    });
}


//copied from stack overflow or something lol
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
            document.getElementById(id).innerHTML = 'Recording Pass...';
            return;
        }
        var days = Math.floor(distance / _day);
        var hours = Math.floor((distance % _day) / _hour);
        var minutes = Math.floor((distance % _hour) / _minute);
        var seconds = Math.floor((distance % _minute) / _second);

        document.getElementById(id).innerHTML = " Next pass in about " + days + 'days ';
        document.getElementById(id).innerHTML += hours + 'hrs ';
        document.getElementById(id).innerHTML += minutes + 'mins ';
        document.getElementById(id).innerHTML += seconds + 'secs';
    }

    timer = setInterval(showRemaining, 1000);
}

//toggle the visibility of the next pass info
function ShowNextPassInfo () {
    var button = document.getElementById("next_pass_more_info_button");
    var info = document.getElementById("next_pass_info");
    if (button.value == "More Info") {
        button.value = "Less Info";
        info.style.display = "block"
    } else {
        button.value = "More Info";
        info.style.display = "none"
    }
}