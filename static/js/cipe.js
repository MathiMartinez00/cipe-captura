// Initialize and add the map
var InforObj = [];
var centerCords = {
    lat: 41.389633,
    lng: 2.116217
};
var twitter_icon = 'https://cdn4.iconfinder.com/data/icons/bettericons/354/twitter-circle-512.png';
var gscholar_icon = 'https://www.pngfind.com/pngs/m/507-5077250_icon-google-scholar-logo-hd-png-download.png';
var facebook_icon = 'https://cdn4.iconfinder.com/data/icons/social-media-icons-the-circle-set/48/facebook_circle-512.png';
var scopus_icon = 'https://manila.lpu.edu.ph/images/scopus.png';
var instws_icon = 'https://images.vexels.com/media/users/3/141505/isolated/preview/6900ccb692f7bbf429da34292e591604-world-round-icon-1-by-vexels.png';
var persws_icon = 'https://www.sccpre.cat/mypng/full/223-2234989_circle-icons-browser-web-page-icon-png.png';
var orcid_icon = 'http://www.batmacro.com/images/sampledata/avatar_nine/content/ORCID-icon.png';

//window.onload = function () {
//    initMap();
//};
function closeInfoWindow() {
    if (InforObj.length > 0) {
        /* detach the info-window from the marker */
        InforObj[0].set("marker", null);
        /* and close it */
        InforObj[0].close();
        /* blank the array */
        InforObj.length = 0;
    }
}

function generateInfoWindowContent(scientist_info) {
    var content = '';
    content = "<div class='text-body text-left'><b>" + scientist_info.name + "</b>";
    content = content + "<br>" + scientist_info.institution_name;
    content = content + "<br>" + scientist_info.institution_city + ", " + scientist_info.institution_country;
    content = content + "<br><br>" + scientist_info.position;
    content = content + "<br>Área: " + scientist_info.scientific_area;
    if (scientist_info.becal_fellow == true) {
        content = content + "<br>Becario Becal";
    }
    if (scientist_info.twitter_handler != null || scientist_info.gscholar_profile != null ||
        scientist_info.facebook_profile != null || scientist_info.scopus_profile != null ||
        scientist_info.institutional_website != null || scientist_info.personal_website != null ||
        scientist_info.orcid_profile)
    {
        content = content + "</br><br>";
        if (scientist_info.facebook_profile != null) {
            content = content + "<a href='" + scientist_info.facebook_profile +
                               "' target='_blank'><img src='" + facebook_icon +"' width='31' height='31' title='Perfil Facebook' alt='Facebook Logo'></a>";
        }
        if (scientist_info.twitter_handler != null) {
            content = content + "<a href='https://twitter.com/" + scientist_info.twitter_handler +
                                "' target='_blank'><img src='" + twitter_icon +"' width='32' height='32' title='Perfil Twitter' alt='Twitter Logo'></a>";
        }
        if (scientist_info.gscholar_profile != null) {
            content = content + "<a href='" + scientist_info.gscholar_profile +
                               "' target='_blank'><img src='" + gscholar_icon +"' width='32' height='32' title='Perfil Google Scholar' alt='Scholar Logo'></a>";
        }
        if (scientist_info.scopus_profile != null) {
            content = content + "<a href='" + scientist_info.scopus_profile +
                               "' target='_blank'><img src='" + scopus_icon +"' width='32' height='32' title='Perfil Scopus' alt='Scopus Logo'></a>";
        }
        if (scientist_info.orcid_profile != null) {
            content = content + "<a href='" + scientist_info.orcid_profile +
                               "' target='_blank'><img src='" + orcid_icon +"' width='32' height='32' title='Perfil ORCID' alt='ORCID Logo'></a>";
        }
        if (scientist_info.institutional_website != null) {
            content = content + "<a href='" + scientist_info.institutional_website +
                               "' target='_blank'><img src='" + instws_icon +"' width='32' height='32' title='Perfil Web Institucional' alt='Scopus Logo'></a>";
        }
        if (scientist_info.personal_website != null) {
            content = content + "<a href='" + scientist_info.personal_website +
                               "' target='_blank'><img src='" + persws_icon +"' width='32' height='32' title='Página Web Personal' alt='Scopus Logo'></a>";
        }
    }

    content = content + "</div>";
    return content
}

function addMarkers(scientists, isIndex) {
    // Create markers
    var inst_lat, inst_lng, str_info_window;
    for (i=0; i < scientists.length; i++) {
        inst_lat = scientists[i].institution_latitude;
        inst_lng = scientists[i].institution_longitude;
        const marker = new google.maps.Marker({position: {lat: inst_lat, lng: inst_lng}, map: map});
        if (!isIndex) {
            infoWindowContent = generateInfoWindowContent(scientists[i])
            const infowindow = new google.maps.InfoWindow({
                content: infoWindowContent
            });
            marker.addListener('click', function () {
                closeInfoWindow();
                infowindow.open(marker.get('map'), marker);
                InforObj[0] = infowindow;
            });
        }
    }
}

function initMap() {
    map = new google.maps.Map(document.getElementById('map'), {
        zoom: 2,
        center: centerCords
    });
}