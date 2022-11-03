var markerCluster;
var markers = [];
var circlesMarker = [];
var map;
var circleShowed = false;
var center =  new google.maps.LatLng(48.6908333333, 9.14055555556);
var markerInTheCluster;
var data;

//trick for wait until the data are downloaded
function waitForLoadingData() {
    if (typeof data === "undefined") {
        setTimeout(waitForLoadingData, 100);
    } else {
        reloadMarkers()
    }
}

function initialize() {
    map = new google.maps.Map(document.getElementById('map'), {
    zoom: 2,
    
    minZoom: 2,
    center: center,
    mapTypeId: google.maps.MapTypeId.ROADMAP,
    zoomControlOptions: {
      style: google.maps.ZoomControlStyle.SMALL
    }
    });

    markerCluster = new MarkerClusterer(map, [], {
        minimumClusterSize: '3'
    });
    manageToggle();
}

function loadLocation() {
    //reset variable
    document.getElementById('chooseSelector').style.display = 'block';
    document.getElementById('reset10Ranking').selected = true;
    document.getElementById('reset10Size').selected = true;
    document.getElementById('resetPublicInfo').selected = true;
    document.getElementById('resetGroundTruth').selected = true;
    document.getElementById('numberInstanceGT').innerHTML = "";
    //document.getElementById('resetSelector').selected = true;
    data = undefined

/*reset the map
    map.setCenter(center);
    map.setZoom(2);
end reset the map */

//TODO: try to clean
    circleShowed = true
    showCircles();
//-------------------------------

    circlesMarker = []
//it wait 500ms, for read the right input(otherwise it will be empty the input)
    setTimeout(function() {
        var s = document.createElement('script');
          s.setAttribute('src', "data/anycastJson/output.json");
//        s.setAttribute('src', "data/anycastJson/" + document.getElementById("suggestBox").value.split("\t")[0]);
        document.body.appendChild(s);
    }, 500);
    waitForLoadingData()
}

function reloadMarkers() {
    document.getElementById('numberInstance').innerHTML = "Number of instances: " + data.count
    document.getElementById('hitToggle').checked=false;
    showMarkersHit()

    // Reset the markers array
    markers = [];

    heatData=[];
    //Read the new markers
    for (var i = 0; i < data.count; i++) {
        var markerData = data.instances[i].marker;
//------------HEATMAPTOFIX---------------
        var lat=parseFloat(markerData.latitude+(Math.random() * (0.0120 - 0.00200) + 0.00200).toFixed(5));
        var lng=parseFloat(markerData.longitude+(Math.random() * (0.0120 - 0.00200) + 0.00200).toFixed(5)); //TODO: change
        heatData[i] = new google.maps.LatLng(lat,lng);
//------------HEATMAPTOFIX---------------

        var latLng = new google.maps.LatLng(markerData.latitude, markerData.longitude);
        var marker = new google.maps.Marker({
            position: latLng,
            title: markerData.id,
            icon: "http://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=H|00FF00|000000"
        });

        var circleData = data.instances[i].circle;
        var drawCircle = new google.maps.Circle({
            center: new google.maps.LatLng(circleData.latitude, circleData.longitude),
            radius: circleData.radius * 1000, // metres
            strokeColor: '#FF0000',
            strokeOpacity: 0.8,
            strokeWeight: 2,
            fillColor: '#FF0000',
            fillOpacity: 0.35,
        });

        google.maps.event.addListener(marker, 'click', function() {
            var infowindow = new google.maps.InfoWindow({
        content: "<p>" + "Iata: " + this.getTitle() + "<br />Latitude: " + this.getPosition().lat().toFixed(5) + "<br />Longitude: " + this.getPosition().lng().toFixed(5)
            });
            infowindow.open(map, this);
        });
        <!-- end draw circle-->
        markers.push(marker);
        circlesMarker.push(drawCircle)
        }
    manageToggle('initialize')

    //Add the new marker to the cluster
    if(document.getElementById('cluster').checked)
        {markerCluster.addMarkers(markers) }//it should check before}

}
google.maps.event.addDomListener(window, 'load', initialize);
