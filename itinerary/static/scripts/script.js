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

var friends_list = [];
var already_found = false;
function showShareModal() {
    $('#modal').show();
    if (!already_found) {
        $.ajax({
            type: 'POST',
            url: 'http://' + server_host + ':' + server_port + '/getFriends/',
            beforeSend: function (request) {
                request.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));
            },
            success: function(friends) {
                console.log(friends);
                already_found = true;
                for (var i = 0; i < friends['unshared'].length; i++) {
                    friend = friends['unshared'][i];
                    $('div#friends_box').append('<span id="friend_' + friends_list.length + '" onclick="switchFriend(this)" class="share_friends">' + friend.name + '</span>');
                    friend.shared = false;
                    friends_list.push(friend);
                }

                for (var i = 0; i < friends['shared'].length; i++) {
                    friend = friends['shared'][i];
                    $('div#shared_box').append('<span id="friend_' + friends_list.length + '" onclick="switchFriend(this)" class="share_friends">' + friend.name + '</span>');
                    friend.shared = true;
                    friends_list.push(friend);
                }
            },
        });
    }
}

function switchFriend(element) {
    console.log(element.parentElement.id);
    var parent = element.parentElement.id;
    var index = parseInt(element.id.slice(7));
    if (parent == 'friends_box') {
        $('div#shared_box').append(element);
        friends_list[index].shared = true;
    } else if (parent == 'shared_box') {
        $('div#friends_box').append(element);
        friends_list[index].shared = false;
    }
    console.log(friends_list[index]);
}

function hideModal() {
    $('#modal').hide();
}

function shareWithFriends() {
    var share_ids = [];
    for (var i = 0; i < friends_list.length; i++) {
        if (friends_list[i].shared) {
            share_ids.push(friends_list[i].id);
        }
    }

    console.log(share_ids);

    $.ajax({
        type: 'POST',
        url: 'http://' + server_host + ':' + server_port + '/shareWithFriends/',
        beforeSend: function (request) {
            request.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));
        },
        data: {'id_list': share_ids},
        success: function(response) {
            hideModal();
        },
    });
}

var moving_item = null;
var items_list = null;
function pickUp(element) {
    element.style.position = "fixed";
    $("#empty_space").show();
    $("#empty_space").insertAfter(element);
    element.style.zIndex = "1";
    moving_item = element;
    items_list = document.getElementsByClassName("movable");
    $("body").addClass("not_selectable");
}

function drop(element) {
    $(element).insertBefore("#empty_space");
    element.style.position = "relative";
    element.style.left = "";
    element.style.top = "";
    element.style.zIndex = "";
    $("#empty_space").hide();
    moving_item = null;
    $("body").removeClass("not_selectable");
    clearSelection();
    updateItems();
}

function clearSelection() {
    if (window.getSelection) {
        window.getSelection().removeAllRanges();
    } else if (document.selection) {
        document.selection.empty();
    }
}

function updateItems() {
    var items = document.getElementsByClassName('item');
    var data = {};
    data['items'] = [];
    for (var i = 0; i < items.length; i++) {
        var day_id = parseInt(items[i].parentElement.id.slice(4));
        var position = $("#" + items[i].parentElement.id + " .item").index(items[i]) + 1;
        var item = {'item_id': parseInt(items[i].id.slice(5)), 'day_id': day_id, 'position': position};
        data['items'].push(JSON.stringify(item));
    }
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

//Exit modal if user clicks outside the box
window.onclick = function(event) {
    var modal = document.getElementById('modal');
    if (event.target == modal) {
        hideModal();
    }
}

window.onmousemove = function(event) {
    if (moving_item) {
        moving_item.style.left = event.clientX - 60 + "px";
        moving_item.style.top = event.clientY - 20 + "px";
        for (var i = 0; i < items_list.length; i++) {
            if (event.clientY < items_list[i].getBoundingClientRect().top) {
                $("#empty_space").insertBefore(items_list[i]);
                break;
            }
        }
    }
}

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

//For the Google Places API
var map;
var autocomplete

function initMap() {
    //Center the map on the US my default
    //TODO: Create an array of different cities and randomly choose one of those
    var us = {lat: 37.1, lng: -95.7};

    map = new google.maps.Map(document.getElementById('map'), {
        center: {lat: 37.1, lng: -95.7},
        zoom: 3,
        mapTypeControl: false,
        panControl: false,
        zoomControl: false,
        streetViewControl: false
    });

    //Autocomplete is connected to 'id_location' input and only returns cities
    //TODO: Allow it to autocomplete cities and addresses
    autocomplete = new google.maps.places.Autocomplete(
        /** @type {!HTMLInputElement} */ (
            document.getElementById('id_location')), {
            types: ['(cities)']
        });

    autocomplete.addListener('place_changed', onPlaceChanged);
}

//If an autocomplete option is selected, go to that place in the map
function onPlaceChanged() {
    var place = autocomplete.getPlace();
    if (place.geometry) {
        map.panTo(place.geometry.location);
        map.setZoom(15);
    } else {
        document.getElementById('autocomplete').placeholder = 'Enter a city';
    }
}