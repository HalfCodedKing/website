//Made by Felix (Blobtoe)

//everything is 'display: none' until everything is loaded
$(document).ready(function () {
    var pass_count = 0;
    var passes;

    //get all the passes
    $.ajaxSetup({
        async: false
    });
    $.getJSON("/weather/images/passes.json", function(result) {
        passes = result
    });
    $.ajaxSetup({
        async: true
    });

    //show the first 5 passes
    for (var i = 0; i < 5; i++) {
        ShowPass(passes[passes.length-pass_count-1]);
        pass_count++;
    }

    //show the next pass when the user scrolls down enough
    $(document).on('scroll', function() {
        if ($(this).scrollTop() >= $('.pass').eq(-3).position().top) {
          ShowPass(passes[passes.length-pass_count-1])
          pass_count++;
        }

        //show the back to top button when use scrolls down 2000 pixels
        if ($(this).scrollTop() >= 2000) {
            document.getElementById("top_button").style.display = "block";
        } else {
            document.getElementById("top_button").style.display = "none"
        }
    })



    //next pass info
    //read all the passes of the day
    $.getJSON("/weather/scripts/daily_passes.json", function(result) {
        $.each(result, function (i, field) {
            //get the first pass with status INCOMING
            if (field.status == "INCOMING") {
                //start the countdown to the start of the next pass
                var date = field.aos.split(/[\s- :.]+/)
                date = Date.UTC(date[0], date[1]-1, date[2], date[3], date[4], date[5])

                CountDownTimer(date, 'countdown')
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

//add and show a pass to the website from its json file path
function ShowPass(path) {
    $.ajaxSetup({
        async: false
    });

    //create clone of template
    var clone = document.getElementById("template").cloneNode(true);
    document.getElementById("main_content").innerHTML = document.getElementById("main_content").innerHTML + clone.innerHTML; 

    //get the clone in the document html (last div with id=pass)
    var pass = document.getElementsByClassName("pass")[document.getElementsByClassName("pass").length - 1]

    $.getJSON(path, function(result) {
        //seperate the date into its components
        var date = result.aos.split(/[\s- :.]+/)
        //make a new date object from the components
        date = Date.UTC(date[0], date[1]-1, date[2], date[3], date[4], date[5])

        //reformat the date into a nice string
        const dateTimeFormat = new Intl.DateTimeFormat('en', { year: 'numeric', month: 'long', day: '2-digit', hour: "numeric", minute: "2-digit", second: "2-digit", timeZoneName: "short"}) 
        const [{ value: month },,{ value: day },,{ value: year },,{value: hour},,{value: minute},,{value: second},,{value: dayPeriod},,{value: timeZoneName}] = dateTimeFormat.formatToParts(date)
        dateString = `${month} ${day}, ${year} at ${hour}:${minute}:${second} ${dayPeriod} ${timeZoneName}`

        //get date difference between now and the time of the pass
        var delta_time = Math.round(Date.now()/1000 - new Date(date).getTime()/1000);
        var delta_days = Math.floor(delta_time/86400)
        var delta_hours = Math.floor((delta_time-delta_days*86400)/3600)
        var delta_mins = Math.floor(((delta_time-delta_days*86400)-delta_hours*3600)/60)

        //show the delta in a nice string
        if (delta_days != 0) {
            pass.getElementsByClassName("delta_time")[0].innerHTML += delta_days + " day" + (delta_days === 1 ? "" : "s")
            if (delta_hours != 0) {
                pass.getElementsByClassName("delta_time")[0].innerHTML += ", "
            }
        }
        if (delta_hours != 0) {
            pass.getElementsByClassName("delta_time")[0].innerHTML += delta_hours + " hour" + (delta_hours === 1 ? "" : "s")
            if (delta_mins != 0) {
                pass.getElementsByClassName("delta_time")[0].innerHTML += " and "
            }
        }
        if (delta_mins != 0) {
            pass.getElementsByClassName("delta_time")[0].innerHTML += delta_mins + " minute" + (delta_mins === 1 ? "" : "s")
        }
        pass.getElementsByClassName("delta_time")[0].innerHTML += " ago."

        //add the name the title of the pass
        pass.getElementsByClassName("pass_title")[0].innerHTML = dateString;
        pass.getElementsByClassName("main_image")[0].setAttribute("src", result.main_image);

        //loop only show the div that matched the satellite's type
        var pass_info = pass.getElementsByClassName("pass_info")[0]
        for (var j = 0; j < pass_info.children.length; j++) {
            if (pass_info.children[j].getAttribute("class") == result.type) {
                //add general information
                pass_info.children[j].getElementsByClassName("sat")[0].innerHTML = "Satellite: " + result.satellite;
                pass_info.children[j].getElementsByClassName("max_elev")[0].innerHTML = "Max elevation: " + result.max_elevation + "°";
                pass_info.children[j].getElementsByClassName("frequency")[0].innerHTML = "Frequency: " + result.frequency + " Hz";
                pass_info.children[j].getElementsByClassName("sun_elev")[0].innerHTML = "Sun Elevation: " + result["sun_elev"] + "°"; 
            
                //add all the links
                for (var key in result.links) {
                    pass.getElementsByClassName(key)[0].setAttribute("href", result.links[key])
                }
            } else {
                //hide divs of different types
                pass_info.children[j].style.display = "none";
            }
            
        }
    });

    $.ajaxSetup({
        async: true
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

function ScrollToTop() {
    document.body.scrollTop = 0;
    document.documentElement.scrollTop = 0;
}