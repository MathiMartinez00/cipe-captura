// Based on
// https://www.geodatasource.com/developers/javascript
function distanceInK(lat1, lon1, lat2, lon2) {
  if (lat1 === lat2 && lon1 === lon2) {
    return 0;
  } else {
    const radlat1 = (Math.PI * lat1) / 180;
    const radlat2 = (Math.PI * lat2) / 180;
    const theta = lon1 - lon2;
    const radtheta = (Math.PI * theta) / 180;
    let dist =
      Math.sin(radlat1) * Math.sin(radlat2) +
      Math.cos(radlat1) * Math.cos(radlat2) * Math.cos(radtheta);
    if (dist > 1) {
      dist = 1;
    }
    dist = Math.acos(dist);
    dist = (dist * 180) / Math.PI;
    dist = dist * 60 * 1.1515;
    dist = dist * 1.609344;
    return dist;
  }
}

function voteComplaint(complaint, isYes) {
  // console.log(complaint, isYes);
  fetch("/api/complaint-votes/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      complaint: complaint.id,
    }),
  });
}

async function addMarkersComplaint(complaints, map, markerClusterer) {
  const { AdvancedMarkerElement, InfoWindow } =
    await google.maps.importLibrary("marker");

  const markers = complaints.map((complaint) => {
    const marker = new AdvancedMarkerElement({
      map: map,
      position: { lat: complaint.latitude, lng: complaint.longitude },
      title: "Test",
      gmpClickable: true,
    });

    marker.addListener("click", (e) => {
      map.setZoom(15);
      map.panTo(marker.position);
      const modalElement = document.getElementById("detailModal");
      const modalBootstrap = new bootstrap.Modal(modalElement);
      const photoElement = document.getElementById("complaint-photo");
      if (complaint.photo) {
        photoElement.src = complaint.photo;
        photoElement.style.visibility = "visible";
      } else {
        photoElement.style.visibility = "hidden";
      }
      const voteYesButton = document.getElementById("vote-complaint-yes");
      voteYesButton.addEventListener(
        "click",
        () => {
          voteComplaint(complaint, true);
        },
        { once: true },
      );

      const voteNoButton = document.getElementById("vote-complaint-no");
      voteNoButton.addEventListener(
        "click",
        () => {
          voteComplaint(complaint, false);
        },
        { once: true },
      );

      const cityElement = document.getElementById("complaint-city");
      cityElement.innerHTML = `Ciudad: ${complaint.city.name}`;

      const complaintTypeElement = document.getElementById(
        "complaint-complaint-type",
      );
      complaintTypeElement.innerHTML = `Tipo de denuncia: ${complaint.complaint_type.name}`;

      const descriptionElement = document.getElementById(
        "complaint-description",
      );
      descriptionElement.innerHTML = `Descripción: ${complaint.description}`;

      modalBootstrap.show();
    });

    const infowWindow = new google.maps.InfoWindow({
      content: "<div>Hi!<div>",
      ariaLabel: "Test",
    });

    marker.content.addEventListener("mouseenter", (e) => {
      infowWindow.open({
        anchor: marker,
        map,
      });
    });

    marker.content.addEventListener("mouseleave", (e) => {
      infowWindow.close();
    });
    markerClusterer.addMarker(marker);
    return marker;
  });
}

function addMarkers(scientists, isIndex, map, markers) {
  /***
    map: variable containing the map
    markers: variable containing the group of markers
    ***/

  // Create markers
  let inst_lat, inst_lng;
  let arr_pos = [];
  let new_lat, new_lng;

  for (i = 0; i < scientists.length; i++) {
    inst_lat = scientists[i].institution_latitude;
    inst_lng = scientists[i].institution_longitude;
    pos = { lat: inst_lat, lng: inst_lng };

    // check if a marker with the position pos (or close) was already included in the map, if so,
    // modify a bit the position
    for (j = 0; j < arr_pos.length; j++) {
      distance_km = distanceInK(
        arr_pos[j].lat,
        arr_pos[j].lng,
        pos.lat,
        pos.lng,
      );
      if (distance_km < 1) {
        new_lat = pos.lat + (Math.random() - 0.5) / 1500;
        new_lng = pos.lng + (Math.random() - 0.5) / 1500;
        pos = { lat: new_lat, lng: new_lng };
      }
    }

    let leafletMarker = L.marker([pos.lat, pos.lng]);
    if (!isIndex) {
      leafletMarker
        .bindPopup(generateInfoWindowContent(scientists[i]))
        .openPopup();
    }
    markers.addLayer(leafletMarker);
  }

  //leaflet cluster added to map
  map.addLayer(markers);
}

function removeMarkers(markerClusterer) {
  markerClusterer.clearMarkers();
  markerClusterer.render();
}

/**
 * @param {string} mapDivId - Div's id where the map will be rendered.
 */
async function initMap(mapDivId) {
  const position = { lat: -23.4425, lng: -58.4438 };
  const { Map } = await google.maps.importLibrary("maps");
  const map = new Map(document.getElementById(mapDivId), {
    zoom: 6,
    center: position,
    mapId: "DEMO_MAP_ID",
  });
  const markerCluster = new markerClusterer.MarkerClusterer({ map: map });
  return { map, markerClusterer: markerCluster };
}

function initAutocomplete() {
  var map = new google.maps.Map(document.getElementById("map-registration"), {
    center: { lat: 41.389633, lng: 40.116217 },
    zoom: 2,
    mapTypeId: "roadmap",
  });

  // Create the search box and link it to the UI element.
  var input = document.getElementById("pac-input");
  var searchBox = new google.maps.places.SearchBox(input);
  map.controls[google.maps.ControlPosition.TOP_LEFT].push(input);

  // Bias the SearchBox results towards current map's viewport.
  map.addListener("bounds_changed", function () {
    searchBox.setBounds(map.getBounds());
  });

  var markers = [];
  // Listen for the event fired when the user selects a prediction and retrieve
  // more details for that place.
  searchBox.addListener("places_changed", function () {
    var places = searchBox.getPlaces();

    if (places.length == 0) {
      return;
    }

    // Clear out the old markers.
    markers.forEach(function (marker) {
      marker.setMap(null);
    });

    markers = [];

    // For each place, get the icon, name and location.
    var bounds = new google.maps.LatLngBounds();
    places.forEach(function (place) {
      if (!place.geometry) {
        console.log("Returned place contains no geometry");
        return;
      }
      var icon = {
        url: place.icon,
        size: new google.maps.Size(71, 71),
        origin: new google.maps.Point(0, 0),
        anchor: new google.maps.Point(17, 34),
        scaledSize: new google.maps.Size(25, 25),
      };

      // Set the value of the hidden fields
      document.getElementById("id_location_name").value = place.name;
      document.getElementById("id_location_lat").value =
        place.geometry.location.lat();
      document.getElementById("id_location_lng").value =
        place.geometry.location.lng();

      // Create a marker for each place.
      markers.push(
        new google.maps.Marker({
          map: map,
          title: place.name,
          position: place.geometry.location,
        }),
      );

      if (place.geometry.viewport) {
        // Only geocodes have viewport.
        bounds.union(place.geometry.viewport);
      } else {
        bounds.extend(place.geometry.location);
      }
    });
    map.fitBounds(bounds);
  });
  return map;
}
