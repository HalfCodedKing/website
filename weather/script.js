$(document).ready(function () {
    document.getElementById("main_content").innerHTML = "";

    $.getJSON("/weather/scripts/showing_passes.json", function(result) {
        $.each(result, function (i, field) {
            ShowPass("/weather/images/2020-06-29/2020-06-29_11.59.23/2020-06-29_11.59.23.json");
        })
    });

    //start the countdown timer until the next pass
    CountDownTimer(document.getElementById("countdown").getAttribute("next_pass"), 'countdown');
});

function ShowPass(path) {
    $.getJSON(path, function(result) {
        var clone = $("#template").clone(true).html();
        //clone.find("#main_image_id").attr("src", result.links.a);
        $(".pass_title").text(result.aos);
        $(".sat").text("Satellite: " + result.satellite);
        $(".max_elev").text("Max Elevation: " + result.max_elevation + "°");
        $(".a").attr("href", result.links.a);
        $(".b").attr("href", result.links.b);
        $(".msa").attr("href", result.links.MSA);
        $(".msa_precip").attr("href", result.links["MSA-precip"]);
        $(".raw").attr("href", result.links.raw);
        $("#main_content").append(clone);
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