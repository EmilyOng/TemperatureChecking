function showMap (pos) {
  latitude = pos.coords.latitude;
  longitude = pos.coords.longitude;
  var streetMap = L.map("streetMap").setView([latitude, longitude], 13);
  L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}', {
    attribution: "Map data &copy; <a href='https://www.openstreetmap.org/'>OpenStreetMap</a> contributors, <a href='https://creativecommons.org/licenses/by-sa/2.0/'>CC-BY-SA</a>, Imagery © <a href='https://www.mapbox.com/'>Mapbox</a>",
    maxZoom: 13,
    id: "mapbox/streets-v11",
    accessToken: "pk.eyJ1IjoiZW9ocSIsImEiOiJjazViM2NuNnIxNnFuM2ZvM2ZlMGlkNTRrIn0.rwD8ADA7qb2rckvNqlyw5w"
  }).addTo(streetMap);
  var marker = L.marker([latitude, longitude]).addTo(streetMap);
}

function plotter (data=null) {
  if (data) {
    kelvin = data[0];
    celcius = data[1];
    var traceK = {y: kelvin, mode: "markers", type: "scatter", name: "Kelvin"};
    var traceC = {y: celcius, mode: "markers", type: "scatter", name: "Celcius"};
    var traces = [traceK, traceC];
    var layout = {title: "Temperature readings"};
    Plotly.newPlot("plotterPanel", traces, layout);
  }
}

plotter({{result|safe}});
navigator.geolocation.getCurrentPosition(showMap);
