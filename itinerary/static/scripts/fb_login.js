
window.fbAsyncInit = function() {
    FB.init({
        appId      : '1998261143737245',
        cookie     : true,
        xfbml      : true,
        version    : 'v2.8'
    });
    FB.AppEvents.logPageView();

    checkLoginState();
};

(function(d, s, id){
    var js, fjs = d.getElementsByTagName(s)[0];
    if (d.getElementById(id)) {return;}
    js = d.createElement(s); js.id = id;
    js.src = "//connect.facebook.net/en_US/sdk.js";
    fjs.parentNode.insertBefore(js, fjs);
}(document, 'script', 'facebook-jssdk'));

function checkLoginState() {
    FB.getLoginStatus(function(response) {
        if (response.status == "connected") {
            access_token = response.authResponse.accessToken;

            FB.api('/me', {fields: "id,first_name,last_name,picture,email"}, function(response) {
                $('span#full_name').append(response.first_name + ' ' + response.last_name);
                $('span#fb_picture').append('<img src="' + response.picture.data.url + '" height="25" width="25">');
                $('#fb_login_button').remove();

                var user = {
                    'fb_id': response.id,
                    'email': response.email,
                    'first_name': response.first_name,
                    'last_name': response.last_name,
                    'access_token': access_token
                };

                $.ajax({
                    type: 'POST',
                    url: 'http://' + server_host + ':' + server_port + '/login/',
                    beforeSend: function (request) {
                        request.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));
                    },
                    data: user,
                    success: function(user) {
                        console.log('Logged in');
                    },
                });
            });
        }
    });
}
