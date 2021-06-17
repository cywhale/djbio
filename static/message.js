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

    socket.onclose = function () {
      console.log("Disconnected from websocket");
    }

    socket.onmessage = function message(event) {
      let data = JSON.parse(event.data);
      console.log("Data received: ", data);
      // NOTE: We escape JavaScript to prevent XSS attacks.
      if (data.error) {
        alert(data.error);
        return;
      }
      let username = encodeURI(data['username']);
      let user = $('li').filter(function () {
        return $(this).data('username') == username;
      });

      if (data['message']) {
        console.log(data['message']);
        let msg = $("#msgbox");
        let adminmsg = $("#adminmsgbox");
        let ele = $("<tr></tr>");

        ele.append($("<td></td>").text(data['message'])); //channels 1.1.8: use data['message'].message
        msg.append(ele);
        adminmsg.append(ele);
      }

      if (data['is_logged_in']) {
        user.html(username + ': Online');
      }
      else {
        user.html(username + ': Offline');
      }
    };
/* 20210616 modified: if only allow admin send message, comment it and user.html <!--tfoot> */
    $("#msgform").on("submit", function(event) {
        let msg = {
            message: $('#message').val(),
        }
        socket.send(JSON.stringify(msg));
        $("#message").val('').focus();
        return false;
    });
/* ---------------- admin control -------------------- */
    $("#adminmsgform").on("submit", function(event) {
      //let due = document.getElementById("due_datetime").value;
        let msg = {
            message: $('#adminmessage').val(),
            due: $('#due_datetime').val(),
        }
        socket.send(JSON.stringify(msg));
        $("#adminmessage").val('').focus();
        return false;
    });
});


