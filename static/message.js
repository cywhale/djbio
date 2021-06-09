// ref: https://www.itread01.com/content/1544328034.html
$(function() {
    var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
    //var socket = new WebSocket('ws://' + window.location.host + '/users/');
    var socket = new ReconnectingWebSocket(ws_scheme + '://' + window.location.host + '/users/'); // '/users'+ window.location.pathname);
    socket.onopen = function open() {
      console.log('WebSockets connection created.');
    };

    if (socket.readyState == WebSocket.OPEN) {
      socket.onopen();
    }

    socket.onmessage = function message(event) {
      let data = JSON.parse(event.data);
      // NOTE: We escape JavaScript to prevent XSS attacks.

      let username = encodeURI(data['username']);
      let user = $('li').filter(function () {
        return $(this).data('username') == username;
      });

      if (data['message']) {
        console.log(data['message']);
        let msg = $("#msgbox");
        let ele = $("<tr></tr>");

        ele.append($("<td></td>").text(data['message'].message));
        msg.append(ele);
      }

      if (data['is_logged_in']) {
        user.html(username + ': Online');
      }
      else {
        user.html(username + ': Offline');
      }
    };

    $("#msgform").on("submit", function(event) {
        let msg = {
            message: $('#message').val(),
        }
        socket.send(JSON.stringify(msg));
        $("#message").val('').focus();
        return false;
    });
});
