var markersProbes = [],
    markersGT = [],
    gt = null,
    hit = null,
    miss = null,
    probes = null,
    circles = null,
    map, 
    pointarray, 
    heatmap;

function manageToggle(toggleType) {

    gt = document.getElementById('GTToggle');
    hit = document.getElementById('hitToggle');
    miss = document.getElementById('missToggle');
    fp = document.getElementById('fpToggle');
    probes = document.getElementById('probesToogle');
    circles = document.getElementById('circlesToggle');
    cluster = document.getElementById('cluster');
    heat = document.getElementById('heatmap');
    toggleSection=document.getElementById('toggleSection')
/*
    if (String(toggleType) === "reset") {
        uncheckToggle('GTToggle', markersGT)
        uncheckToggle('probesToogle', markersProbes)
        hit.checked = true;
        miss.checked = false;
        fp.checked = false;
        if (circles.checked) {
            circles.click()
        }
        if (!cluster.checked) {
            cluster.click()
        }
    } else 
*/
   if (String(toggleType) === "initialize") {

        reloadToogle('GTToggle', markersGT)
        reloadToogle('probesToogle', markersProbes)
        reloadCircle()
        cleanHeatmap()
        heat.checked = false;
        hit.checked = true;
        cluster.checked = true;
        miss.checked = false;
        fp.checked = false;
//manage circle!

    } else if (String(toggleType) === "basic") {
        toggleSection.style.display = 'none';
        checkToggle('GTToggle');
        checkToggle('hitToggle');
        uncheckToggle('probesToogle', markersProbes)
        miss.checked = false;
        fp.checked = false;
        if (circles.checked) {
            circles.click();
        }
    } else if (String(toggleType) === "extended") {
        toggleSection.style.display = 'none';
        checkToggle('GTToggle');
        checkToggle('hitToggle');
        checkToggle('missToggle');
        checkToggle('fpToggle');
        uncheckToggle('probesToogle', markersProbes)
        if (circles.checked) {
            circles.click();
        }
    } else if (String(toggleType) === "everything") {
        toggleSection.style.display = 'none';
        checkToggle('GTToggle');
        checkToggle('hitToggle');
        checkToggle('missToggle');
        checkToggle('fpToggle');
        checkToggle('probesToogle');
        checkToggle('circlesToggle');

    } else if (String(toggleType) === "custom") {
        toggleSection.style.display = 'block';
    }
}

function checkToggle(toggle) {
    if (!document.getElementById(toggle).checked) {
        document.getElementById(toggle).click();
    }
}

function uncheckToggle(toggle, markersDisable) {
    if (document.getElementById(toggle).checked) {
        document.getElementById(toggle).checked = false;
        clearMapsFromMarkers(markersDisable)
    }
}

function reloadToogle(toggle,markersDisable){
    var checked=document.getElementById(toggle).checked
    uncheckToggle(toggle, markersDisable)
    if(checked){
        checkToggle(toggle);
   }
}
function reloadCircle(){
    var checked=circles.checked
    if(checked){
        showCircles();
   }
}

function cleanHeatmap(){
    heat.checked=false;
    if(heatmap!=null)
    {enableDisableHeatmap()}
}

//try to see how much effort for insert the gadget
function showMarkersProbes() {
    if (probes.checked) {
        for (var i = 0; i < data.count; i++) {
            var markerData = data.instances[i].circle;
            var latLng = new google.maps.LatLng(markerData.latitude,
                markerData.longitude);
            var marker = new google.maps.Marker({
                position: latLng,
                title: markerData.id,
                icon: "data/dot2.png",
                map: map
            });
            google.maps.event.addListener(marker, 'click', function() {
                var infowindow = new google.maps.InfoWindow({
                    content: "<p>" + "Probe: " + this.getTitle() + "<br />Latitude: " + this.getPosition().lat().toFixed(5) + "<br />Longitude: " + this.getPosition().lng().toFixed(5)+"<p>" + "<a href=\"https://atlas.ripe.net/probes/"+this.getTitle()+"\" target=\"_blank\">RipeLinkProbes</a>" 
                });
                infowindow.open(map, this);
            });
            markersProbes.push(marker);
        }
    } else {
        probes.checked = true;
        uncheckToggle('probesToogle', markersProbes)

    }


}

function showMarkersHit() {
    if (hit.checked) {
        // default enable marker and cluster 
         markerCluster.addMarkers(markers)
        cluster.checked = true
    } else {
       // hide the marker and the cluster 
        for (var i = 0; i < markers.length; i++) {
            markers[i].setOptions({
                map: null,
                visible: true
            });
        }
        markerCluster.clearMarkers();
        cluster.checked = false
    }

}

function showMarkersGT() {
    if (gt.checked) {
        //Read the new markers
        document.getElementById('numberInstanceGT').innerHTML = "Number of GT: " + data.countGT;
        for (var i = 0; i < data.countGT; i++) {

            var markerData = data.markerGT[i];
            var latLng = new google.maps.LatLng(markerData.latitude,
                markerData.longitude);
            var marker = new google.maps.Marker({
                position: latLng,
                title: markerData.id,
                icon: "http://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=G|8B52CC|000000",
                map: map
            });

            google.maps.event.addListener(marker, 'click', function() {
                var infowindow = new google.maps.InfoWindow({
                    content: "<p>" + "Iata: " + this.getTitle() + "<br />Latitude: " + this.getPosition().lat().toFixed(5) + "<br />Longitude: " + this.getPosition().lng().toFixed(5)
                });
                infowindow.open(map, this);
            });
            markersGT.push(marker);
        }
    } else {
        document.getElementById('numberInstanceGT').innerHTML = "";
        gt.checked = true;
        uncheckToggle('GTToggle', markersGT)
    }
}


function clearMapsFromMarkers(markersArray) {
    for (var i = 0; i < markersArray.length; i++) {
        markersArray[i].setMap(null);
    }
    markersArray.length = 0;
}

function enableDisableHeatmap() {  
//DR: inspired from https://developers.google.com/maps/documentation/javascript/examples/layer-heatmap
    if (heat.checked) {
        if(cluster.checked){
            hit.click();
        }
        var pointArray = new google.maps.MVCArray(heatData);
        heatmap = new google.maps.visualization.HeatmapLayer({ 
            data: pointArray, 
            radius: 45,
            map: map 
            });
    } else {
        heatmap.setMap(null);
    }
}

function enableDisableCluster() {
    if (cluster.checked) {
        hit.checked = true;
        markerCluster = new MarkerClusterer(map, markers, {
            minimumClusterSize: '3'
        });
    } else {
        markerCluster.clearMarkers();
        for (var i = 0; i < markers.length; i++) {
            markers[i].setOptions({
                map: map,
                visible: true
            });
        }
    }
}

function showCircles() {
    if (circleShowed == false) {
        for (var i = 0; i < circlesMarker.length; i++) {
            circlesMarker[i].setMap(map);
            circlesMarker[i].setVisible(true)
        }
        circleShowed = true
    } else {
        circleShowed = false
        for (var i = 0; i < circlesMarker.length; i++) {
            circlesMarker[i].setVisible(false)
        }
    }
}
