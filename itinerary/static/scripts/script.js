var server_host = window.location.hostname;
var server_port = window.location.port;

//Get cookie information
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

//Adds an item to a trip day
// function addItem(day_id) {
//     //Take item name from input create JSON object
//     var new_item_name = $('input#new_item_day_' + day_id).val();
//     var new_item = {
//         'item_name': new_item_name,
//         'day': 'http://' + server_host + ':' + server_port + '/api/days/' + day_id + '/'
//     };

//     //Use API to update database, update the template if successful
//     $.ajax({
//         type: 'POST',
//         url: 'http://' + server_host + ':' + server_port + '/api/items/',
//         beforeSend: function (request) {
//             request.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));
//         },
//         data: new_item,
//         success: function(item) {
//             //Update page
//             console.log(item);
//             var item_insert = '<h4 id="item_' + item.id + '" class="movable item" onmousedown="pickUp(this)" onmouseup="drop(this)">' + item.item_name + '</h4>';
//             $(item_insert).insertBefore('div#add_area_day_' + day_id)
//             $('input#new_item_day_' + day_id).val('');
//         },
//     });
// }

var moving_item = null;
var items_list = null;
function pickUp(element) {
    var parent = element.parentElement;
    parent.style.position = "fixed";
    $("#empty_space").show();
    $("#empty_space").insertAfter(parent);
    parent.style.zIndex = "1";
    moving_item = parent;
    items_list = document.getElementsByClassName("movable");
    $("body").addClass("not_selectable");
}

function drop(element) {
    var parent = element.parentElement;
    $(parent).insertBefore("#empty_space");
    parent.style.position = "relative";
    parent.style.left = "";
    parent.style.top = "";
    parent.style.zIndex = "";
    $("#empty_space").hide();
    moving_item = null;
    $("body").removeClass("not_selectable");
    clearSelection();
    var new_day = parent.parentElement;
    updateItems(new_day);
}

function moveToInterested(element, item_id) {
    $.ajax({
        type: 'POST',
        url: 'http://' + server_host + ':' + server_port + '/moveToInterested/' + item_id,
        beforeSend: function (request) {
            request.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));
        },
        success: function(response) {
            document.getElementById('interested_list').appendChild(element.parentElement);
        },
    });
}

function clearSelection() {
    if (window.getSelection) {
        window.getSelection().removeAllRanges();
    } else if (document.selection) {
        document.selection.empty();
    }
}

function updateItems(day) {
    var items = day.getElementsByClassName('item');
    var day_id = day.id;
    if (day_id == 'interested_list') {
        day_id = null;
    } else {
        day_id = day_id.slice(4)
    }
    console.log(items);
    var data = {};
    data['items'] = [];
    for (var i = 0; i < items.length; i++) {
        var item = {'item_id': parseInt(items[i].id.slice(5)), 'day_id': day_id, 'position': i + 1};
        data['items'].push(JSON.stringify(item));
    }
    console.log(data);
    $.ajax({
        type: 'POST',
        url: 'http://' + server_host + ':' + server_port + '/updateItemPositions/',
        beforeSend: function (request) {
            request.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));
        },
        data: data,
        success: function(response) {
            console.log(response);
        },
    });
}

// function hasClass(element, cls) {
//     return (' ' + element.className + ' ').indexOf(' ' + cls + ' ') > -1;
// }

past_trips_loaded = false;
function loadPastTrips() {
    if (!past_trips_loaded) {
        $.ajax({
            type: 'POST',
            url: 'http://' + server_host + ':' + server_port + '/pastTrips/',
            beforeSend: function (request) {
                request.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));
            },
            success: function(response) {
                past_trips_loaded = true;
                if (response['message']) {
                    $('div#past_trips').append('<p>' + response['message'] + '</p>');
                    return;
                }
                console.log(response);
                data = response.trips.data;
                for (var i = 0; i < data.length; i++) {
                    $('div#past_trips').append('<p><a href="/trip/' + data[i].id + '">' + data[i].trip_name + '</a></p>');
                }
            },
        });
    }
}

var autocomplete_options = null;
var current_option = null;
var old_query = '';
var marker_image = document.createElement('img');
marker_image.src = '/static/images/map_marker.png';
var marker = null;

function searchAutocomplete(query, type, click_function) {
    $.get('https://api.mapbox.com/geocoding/v5/mapbox.places/'+ query + '.json?types=' + type + '&language=en&access_token=' + mapboxgl.accessToken, function(data, status){
        if (data) {
            $("#autocomplete_area").show();
            $("#autocomplete_area").empty();
            for (var i = 0; i < data.features.length; i++) {
                var name = data.features[i].place_name;
                if (data.features[i].matching_place_name) {
                    name = name + ", " + data.features[i].matching_place_name;
                }
                $("#autocomplete_area").append('<p class="autocomplete_options" onclick="' + click_function + '(' + i + ')">' + name + '</p>');
            }
            autocomplete_options = data.features;
            current_option = null;
        } else {
            $("#autocomplete_area").hide();
        }
    });
}

function navigateAutocomplete(event) {
    if ($("#autocomplete_area").is(":visible")) {
        if (event.keyCode == 40) {
            event.preventDefault();
            if (current_option == null) {
                current_option = -1;
            }
            current_option = (current_option + 1) % autocomplete_options.length;
        } else if (event.keyCode == 38) {
            event.preventDefault();
            if (current_option == null) {
                current_option = 0;
            }
            current_option = (current_option - 1) % autocomplete_options.length;
        }
        $(".autocomplete_options").eq(current_option).addClass("autocomplete_focus").siblings().removeClass("autocomplete_focus");
        if (event.keyCode == 13) {
            event.preventDefault();
            $(".autocomplete_options").eq(current_option).click();
        }
    }
}

function showAutocomplete(event) {
    if ($("#autocomplete_area").children().length > 0) {
        $("#autocomplete_area").show();
    }
}

$("#autocomplete_area").hover(function() {
    $(".autocomplete_options").removeClass("autocomplete_focus");
    current_option = null;
});

function goToLocation(index, map) {
    if (autocomplete_options[index].bbox) {
        map.fitBounds(autocomplete_options[index].bbox);
    } else {
        map.flyTo({center: autocomplete_options[index].center, zoom: 17});
    }
    if (marker == null) {
        marker = new mapboxgl.Marker(marker_image, {offset: [-9, -32]}).setLngLat(autocomplete_options[index].center).addTo(map)
    } else {
        marker.setLngLat(autocomplete_options[index].center);
    }
    var name = autocomplete_options[index].place_name;
    if (autocomplete_options[index].matching_place_name) {
        name = name + ", " + autocomplete_options[index].matching_place_name;
    }
    input_box.val(name);
    old_query = name;
}

// //For the Google Places API
// var map;
// var autocomplete

// function initMap() {
//     //Center the map on the US my default
//     //TODO: Create an array of different cities and randomly choose one of those
//     var us = {lat: 37.1, lng: -95.7};

//     map = new google.maps.Map(document.getElementById('map'), {
//         center: {lat: 37.1, lng: -95.7},
//         zoom: 3,
//         mapTypeControl: false,
//         panControl: false,
//         zoomControl: false,
//         streetViewControl: false
//     });

//     //Autocomplete is connected to 'id_location' input and only returns cities
//     //TODO: Allow it to autocomplete cities and addresses
//     autocomplete = new google.maps.places.Autocomplete(
//         /** @type {!HTMLInputElement} */ (
//             document.getElementById('id_location')), {
//             types: ['(cities)']
//         });

//     autocomplete.addListener('place_changed', onPlaceChanged);
// }

// //If an autocomplete option is selected, go to that place in the map
// function onPlaceChanged() {
//     var place = autocomplete.getPlace();
//     if (place.geometry) {
//         map.panTo(place.geometry.location);
//         map.setZoom(15);
//     } else {
//         document.getElementById('autocomplete').placeholder = 'Enter a city';
//     }
// }