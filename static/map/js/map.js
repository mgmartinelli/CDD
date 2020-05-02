
var geojson;
var newWindow;
var statesData = {};


L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token=' + mapboxAccessToken, {
    id: 'mapbox/light-v9',
    attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
    tileSize: 512,
    zoomOffset: -1
}).addTo(map);




function getColor(d) {
    var items = ['#E35F5F', '#ffa500', '#ffff00', '#008000', '#0000ff', '#ee82ee', '#4b0082']

    var item = items[Math.floor(Math.random() * items.length)];
    return item;
}

function style(feature) {
    return {
        fillColor: feature.properties.color,
        weight: 2,
        opacity: 1,
        color: 'white',
        dashArray: '3',
        fillOpacity: 0.7
    };
}

function highlightFeature(e) {
    var layer = e.target;

    layer.setStyle({
        weight: 5,
        color: '#666',
        dashArray: '',
        fillOpacity: 0.7
    });

    if (!L.Browser.ie && !L.Browser.opera && !L.Browser.edge) {
        layer.bringToFront();
    }
    info.update(layer.feature.properties);
}

function resetHighlight(e) {
    geojson.resetStyle(e.target);
    info.update();
}

function onEachFeature(feature, layer) {
    layer.on({
        mouseover: highlightFeature,
        mouseout: resetHighlight,
        click: zoomToFeature
    });
}

function zoomToFeature(e) {
    //newWindow = window.open("index.html?coords=" + encodeURI(e), "_blank");
    //zoomInOnOtherWindow(newWindow, e);
    //test = e.target.getBounds();
    map.fitBounds(e.target.getBounds());
}

function zoomInOnOtherWindow(newWindow, e){
    if (typeof newWindow.window.map === 'undefined'){
        setTimeout((newWindow, e) => zoomInOnOtherWindow(newWindow, e), 50);
    }
    else{
        newWindow.window.map.fitBounds(e.target.getBounds());
    }

}

var info = L.control();

info.onAdd = function (map) {
    this._div = L.DomUtil.create('div', 'info'); // create a div with a class "info"
    this.update();
    return this._div;
};

// method that we will use to update the control based on feature properties passed
info.update = function (props) {
    this._div.innerHTML = '<h4>' + US_state + ' Districts</h4>' +  (props ?
        '<b> District: </b>' + props.name.substring(props.name.length-2, props.name.length) + '<br />' + '<b> Population: </b>' + props.population + '</br><b> Voting Booths: </b>' + props.num_voting_booths
        : 'Hover over a state');
};

info.addTo(map);

var legend = L.control({position: 'bottomright'});

legend.onAdd = function (map) {

    var div = L.DomUtil.create('div', 'info legend'),
        grades = [0, 100000, 200000, 500000, 1000000, 2000000, 5000000, 10000000],
        labels = [];

    // loop through our density intervals and generate a label with a colored square for each interval
    for (var i = 0; i < grades.length; i++) {
        div.innerHTML +=
            '<i style="background:' + getColor() + '"></i> ' +
            grades[i] + (grades[i + 1] ? '&ndash;' + grades[i + 1] + '<br>' : '+');
    }

    return div;
};


function loadJSON(callback, state) {   
    var xobj = new XMLHttpRequest();
    var link = /api/ + state + /data/
    xobj.overrideMimeType("application/json");
    xobj.open('GET', link, true);
    xobj.onreadystatechange = function () {
      if (xobj.readyState == 4 && xobj.status == "200") {
        callback(JSON.parse(xobj.responseText));
      }
    };
    xobj.send(null);  
}


function waitThenRun(callback) {
    let intervalId = setInterval(function() {
      if (statesData.features !== undefined) {
        callback();
        clearInterval(intervalId);
      }
    }, 10);
  }

function drawStateData() {  
    for(let i = 0; i < statesData["features"].length; i++){
        statesData["features"][i]["properties"]["color"] = getColor();
    }
    geojson = L.geoJson(statesData, {
        style: style,
        onEachFeature: onEachFeature
    }).addTo(map);
}

