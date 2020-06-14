header = `

<div id="menu">
    <ul>
        <li><a name="weather" href="/weather/index.html">Weather</a></li>
        <li><a name="projects" href="/projects/index.html">Projects</a></li>
        <li><a name="home" href="/index.html">Home</a></li>
    </ul>
</div>

<style>
    #menu {
        margin-top: 20px;
        margin-right: 20px;
        background-color: #2b2b2b;
    }
    
    #menu ul {
        list-style-type: none;
        overflow: hidden;
        margin: 0;
        padding: 0;
    }

    #menu ul li {
        float: right;
    }

    #menu ul li a {
        color: whitesmoke;
        text-decoration: none;
        display: block;
        text-align: center;
        padding: 10px;
    }

    #menu ul li a:hover {
        color: rgb(161, 161, 161);
    }
</style>

`

$(document).ready(function () {
    $('#header').prepend(header);
  });