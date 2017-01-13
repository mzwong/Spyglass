function initMap() {
    var start = {lat: locations[0][0], lng: locations[0][1]};
    var map = new google.maps.Map(document.getElementById('map'), {
        zoom: 14,
        center: start
    });

    var label = 'A'.charCodeAt(0);
    for (var i = 0; i < locations.length; i++) {
        var currLocation = locations[i];
        var marker = new google.maps.Marker({
            position: {lat: currLocation[0], lng: currLocation[1]},
            label: String.fromCharCode(label),
            map: map
        });
        label++;
    }
}
