window.onload = function () {

    var file = document.getElementById("thefile");
    var audio = document.getElementById("audio");

    file.onchange = function () {
        var files = this.files;
        audio.src = URL.createObjectURL(files[0]);
        audio.load();
        audio.play();
        var context = new AudioContext();
        var src = context.createMediaElementSource(audio);
        var analyser = context.createAnalyser();

        var canvas = document.getElementById("canvas");
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        var ctx = canvas.getContext("2d");

        src.connect(analyser);
        analyser.connect(context.destination);

        analyser.fftSize = 256;

        var bufferLength = analyser.frequencyBinCount;
        console.log(bufferLength);

        var dataArray = new Uint8Array(bufferLength);

        var WIDTH = canvas.width;
        var HEIGHT = canvas.height;

        var barWidth = (WIDTH / bufferLength) * 2.5;
        var barHeight;

        function renderFrame() {
            requestAnimationFrame(renderFrame);


            analyser.getByteFrequencyData(dataArray);

            ctx.fillStyle = "#000";
            ctx.fillRect(0, 0, WIDTH, HEIGHT);

          // make points array
            var points = [];
            var X = 0;
            for (i = 0; i < dataArray.length; i++) {
                points.push({x:X, y:HEIGHT - (dataArray[i] * 3)});
                X += barWidth + 1;
            }

            // move to the first point
            ctx.moveTo(points[0].x, points[0].y);

            for (i = 1; i < points.length - 2; i++) {
                barHeight = dataArray[i] * 3;
                //var r = barHeight + (25 * (i / bufferLength));
                var r = points[i].y * 2;
                var g = 250 * (i / bufferLength);
                var b = points[i].x;
                ctx.strokeStyle = "rgb(" + r + "," + g + "," + b + ")";
                //ctx.strokeStyle="rgb(255,0,0)";

                var xc = (points[i].x + points[i + 1].x) / 2;
                var yc = (points[i].y + points[i + 1].y) / 2;
                ctx.quadraticCurveTo(points[i].x, points[i].y, xc, yc);
            }
            ctx.strokeStyle="#f49842";
            // curve through the last two points
            ctx.quadraticCurveTo(points[i].x, points[i].y, points[i + 1].x, points[i + 1].y);
            ctx.stroke();
            ctx.beginPath();
        }
        audio.play();
        renderFrame();
    };
};
