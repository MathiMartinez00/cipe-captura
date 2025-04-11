// Based on
// https://www.geodatasource.com/developers/javascript

const parser = new DOMParser();

const trashSvgString = `<svg width="800px" height="80px" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M3 6.38597C3 5.90152 3.34538 5.50879 3.77143 5.50879L6.43567 5.50832C6.96502 5.49306 7.43202 5.11033 7.61214 4.54412C7.61688 4.52923 7.62232 4.51087 7.64185 4.44424L7.75665 4.05256C7.8269 3.81241 7.8881 3.60318 7.97375 3.41617C8.31209 2.67736 8.93808 2.16432 9.66147 2.03297C9.84457 1.99972 10.0385 1.99986 10.2611 2.00002H13.7391C13.9617 1.99986 14.1556 1.99972 14.3387 2.03297C15.0621 2.16432 15.6881 2.67736 16.0264 3.41617C16.1121 3.60318 16.1733 3.81241 16.2435 4.05256L16.3583 4.44424C16.3778 4.51087 16.3833 4.52923 16.388 4.54412C16.5682 5.11033 17.1278 5.49353 17.6571 5.50879H20.2286C20.6546 5.50879 21 5.90152 21 6.38597C21 6.87043 20.6546 7.26316 20.2286 7.26316H3.77143C3.34538 7.26316 3 6.87043 3 6.38597Z" fill="#1C274C"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M9.42543 11.4815C9.83759 11.4381 10.2051 11.7547 10.2463 12.1885L10.7463 17.4517C10.7875 17.8855 10.4868 18.2724 10.0747 18.3158C9.66253 18.3592 9.29499 18.0426 9.25378 17.6088L8.75378 12.3456C8.71256 11.9118 9.01327 11.5249 9.42543 11.4815Z" fill="#1C274C"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M14.5747 11.4815C14.9868 11.5249 15.2875 11.9118 15.2463 12.3456L14.7463 17.6088C14.7051 18.0426 14.3376 18.3592 13.9254 18.3158C13.5133 18.2724 13.2126 17.8855 13.2538 17.4517L13.7538 12.1885C13.795 11.7547 14.1625 11.4381 14.5747 11.4815Z" fill="#1C274C"/>
<path opacity="0.5" d="M11.5956 22.0001H12.4044C15.1871 22.0001 16.5785 22.0001 17.4831 21.1142C18.3878 20.2283 18.4803 18.7751 18.6654 15.8686L18.9321 11.6807C19.0326 10.1037 19.0828 9.31524 18.6289 8.81558C18.1751 8.31592 17.4087 8.31592 15.876 8.31592H8.12405C6.59127 8.31592 5.82488 8.31592 5.37105 8.81558C4.91722 9.31524 4.96744 10.1037 5.06788 11.6807L5.33459 15.8686C5.5197 18.7751 5.61225 20.2283 6.51689 21.1142C7.42153 22.0001 8.81289 22.0001 11.5956 22.0001Z" fill="#1C274C"/>
</svg>`;
const trashSvg = parser.parseFromString(trashSvgString, 'image/svg+xml').documentElement;

const potholeSvgString = `<svg version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" x="0px" y="0px" viewBox="0 0 100 81.64" enable-background="new 0 0 100 81.64" xml:space="preserve"><path d="M25.361,38.376"/><path d="M79.785,45.104"/><polygon points="0,81.64 100,81.64 100,70.546 90.771,70.546 88.89,76.085 72.223,78.862 65.277,70.528 0,70.546 "/><circle cx="63.875" cy="17.589" r="5.154"/><path d="M87.722,31.349l-4.789-19.031c-0.886-3.64-3.394-6.953-8.831-7.651l-9.915-1.226L47.233,1.345L37.142,0.099  c-5.421-0.646-8.659,1.958-10.429,5.27l-9.278,17.293c-2.84,0.015-8.188,2.684-8.947,8.904L5.629,54.69l6.863,0.848l-0.912,7.381  c-1.143,9.1,11.749,10.584,12.858,1.589l0.911-7.38l23.18,2.864l23.123,2.859l-0.911,7.38c-1.088,8.998,11.781,10.697,12.912,1.598  l0.913-7.381l6.864,0.848l2.859-23.124C95.036,35.951,90.495,32.058,87.722,31.349z M27.542,37.027  c-0.413,3.375-3.417,5.79-6.695,5.375c-3.29-0.398-5.612-3.47-5.184-6.844c0.409-3.4,3.41-5.817,6.695-5.382  C25.642,30.555,27.965,33.63,27.542,37.027z M74.188,29.503c-0.442-2.486-2.078-4.619-5.08-4.989l-11.465-1.422  c-2.812-0.348-5.023,1.188-6.089,3.613l-26.779-3.309l7.073-13.647c0.891-1.951,2.065-3.28,4.414-3.026l18.511,2.291l0.055,0.006  l18.57,2.295c2.307,0.321,3.123,1.895,3.542,4.008l3.536,14.958L74.188,29.503z M86.358,44.299  c-0.438,3.372-3.441,5.783-6.695,5.373c-3.314-0.399-5.641-3.474-5.241-6.85c0.438-3.396,3.442-5.813,6.753-5.375  C84.434,37.822,86.757,40.896,86.358,44.299z"/></svg>`
const potholeSvg = parser.parseFromString(potholeSvgString, 'image/svg+xml').documentElement;

const pinSvgString = '<svg xmlns="http://www.w3.org/2000/svg" width="56" height="56" viewBox="0 0 56 56" fill="none"><rect width="56" height="56" rx="28" fill="#7837FF"></rect><path d="M46.0675 22.1319L44.0601 22.7843" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"></path><path d="M11.9402 33.2201L9.93262 33.8723" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"></path><path d="M27.9999 47.0046V44.8933" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"></path><path d="M27.9999 9V11.1113" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"></path><path d="M39.1583 43.3597L37.9186 41.6532" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"></path><path d="M16.8419 12.6442L18.0816 14.3506" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"></path><path d="M9.93262 22.1319L11.9402 22.7843" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"></path><path d="M46.0676 33.8724L44.0601 33.2201" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"></path><path d="M39.1583 12.6442L37.9186 14.3506" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"></path><path d="M16.8419 43.3597L18.0816 41.6532" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"></path><path d="M28 39L26.8725 37.9904C24.9292 36.226 23.325 34.7026 22.06 33.4202C20.795 32.1378 19.7867 30.9918 19.035 29.9823C18.2833 28.9727 17.7562 28.0587 17.4537 27.2401C17.1512 26.4216 17 25.5939 17 24.7572C17 23.1201 17.5546 21.7513 18.6638 20.6508C19.7729 19.5502 21.1433 19 22.775 19C23.82 19 24.7871 19.2456 25.6762 19.7367C26.5654 20.2278 27.34 20.9372 28 21.8649C28.77 20.8827 29.5858 20.1596 30.4475 19.6958C31.3092 19.2319 32.235 19 33.225 19C34.8567 19 36.2271 19.5502 37.3362 20.6508C38.4454 21.7513 39 23.1201 39 24.7572C39 25.5939 38.8488 26.4216 38.5463 27.2401C38.2438 28.0587 37.7167 28.9727 36.965 29.9823C36.2133 30.9918 35.205 32.1378 33.94 33.4202C32.675 34.7026 31.0708 36.226 29.1275 37.9904L28 39Z" fill="#FF7878"></path></svg>';
const pinSvg = parser.parseFromString(pinSvgString, 'image/svg+xml').documentElement;

/**
 * 
 * @param {number} lat1 
 * @param {number} lon1 
 * @param {number} lat2 
 * @param {number} lon2 
 * @returns 
 */
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

function voteComplaint(complaint, vote_type) {
  fetch("/api/complaint-votes/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      complaint: complaint.id,
      vote_type: vote_type,
    }),
  });
}

async function resetMap(map) {
  const position = { lat: -23.4425, lng: -58.4438 };
  map.setCenter(position);
  map.setZoom(6);
}

async function addComplaintMarkers(complaints, map, markerClusterer) {
  const { AdvancedMarkerElement, InfoWindow, PinElement } =
    await google.maps.importLibrary("marker");

  const markers = complaints.map((complaint) => {
    const glyphPotholeSvgPinElement = new PinElement({
      glyph: 'B',
      glyphColor: 'white',
    });
    const marker = new AdvancedMarkerElement({
      map,
      position: { lat: complaint.latitude, lng: complaint.longitude },
      gmpClickable: true,
      content: glyphPotholeSvgPinElement.element,
    });

    marker.addListener("click", (e) => {
      console.log("Marker clicked!");
      const modalElement = document.getElementById("detailModal");
      const modalBootstrap = new bootstrap.Modal(modalElement, {
        backdrop: 'static',
      });
      const photoDivElement = document.getElementById("complaint-photo-div");
      const photoElement = document.getElementById("complaint-photo");

      if (complaint.photo) {
        photoElement.src = complaint.photo;
        photoDivElement.style.display = "block";
      } else {
        photoElement.src = "/";
        photoDivElement.style.display = "none";
      }
      const voteForm = document.getElementById("vote-complaint-form");
      voteForm.addEventListener(
        "submit",
        (e) => {
          e.preventDefault();
          const formData = new FormData(e.target);
          if (formData.get("vote-complaint")) {
            voteComplaint(complaint, formData.get("vote-complaint"));
          }
        },
        {
          once: true,
        },
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

      const datetimeElement = document.getElementById("complaint-datetime");
      datetimeElement.innerHTML = `Fecha de creación: ${new Date(complaint.created_at).toLocaleString()}`

      modalElement.addEventListener('hidePrevented.bs.modal', () => console.log("hidePrevented called"));
      modalBootstrap.show();
    });

    const infowWindow = new google.maps.InfoWindow({
      content: `<div>${complaint.complaint_type.name}<div>`,
      ariaLabel: "Denuncia",
      headerDisabled: true,
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
  const markerCluster = new markerClusterer.MarkerClusterer({ map });
  return { map, markerClusterer: markerCluster };
}
