window.onload = function() {
    var locationRequest = new XMLHttpRequest();
    var weatherRequest = new XMLHttpRequest();
    var KEYweather = "16a2c3d698b77a6ac2b3837e67cdc357";
    var KEYloc = "2a59946795727a";

    locationRequest.open("GET", "https://ipinfo.io?token=" + KEYloc, true);
    locationRequest.onload = function() {
        if (this.readyState == 4 && this.status == 200) {
            var data = JSON.parse(this.response);
            var loc = data.loc.split(",");
            //console.log(data)

            weatherRequest.open("GET", "https://api.openweathermap.org/data/2.5/weather?lat=" + loc[0] + "&lon=" + loc[1] + "&APPID=" + KEYweather, true);
            weatherRequest.onload = function() {
                if (this.readyState == 4 && this.status == 200) {
                    var weather = JSON.parse(this.response);
                    console.log(weather)
                    var temp = Math.round((weather.main.temp - 273) * 10) / 10;
                    var icon = weather.weather["0"].icon;
                    document.getElementById("icon").src = "https://openweathermap.org/img/wn/" + icon + "@2x.png"
                    document.getElementById("icon").alt = weather.weather['0'].description;
                    document.getElementById("icon").title = weather.weather['0'].description;
                    document.getElementById("temp").innerHTML = temp + "°C";
                    document.getElementById("location").innerHTML = "in " + weather.name + ", " + weather.sys.country;
                }
            }
            weatherRequest.send();
        }
    }
    locationRequest.send();

    document.getElementById("search").addEventListener("submit", function() {
        weatherRequest.open("GET", "https://api.openweathermap.org/data/2.5/weather?q=" + document.getElementById("searchBox").value + "&APPID=" + KEYweather, true);
        weatherRequest.onload = function() {
            if (this.readyState == 4 && this.status == 200) {
                var weather = JSON.parse(this.response);
                var temp = Math.round((weather.main.temp - 273) * 10) / 10;
                var icon = weather.weather["0"].icon;
                document.getElementById("icon").src = "https://openweathermap.org/img/wn/" + icon + "@2x.png"
                document.getElementById("icon").alt = weather.weather['0'].description;
                document.getElementById("icon").title = weather.weather['0'].description;
                document.getElementById("temp").innerHTML = temp + "°C";
                document.getElementById("location").innerHTML = "in " + weather.name + ", " + weather.sys.country;
            } else if (this.status == 404) {
                alert("City not found");
            }
        }
        weatherRequest.send();
    });
}
