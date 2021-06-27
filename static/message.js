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

      let cnt = parseInt($('#msg_cnt').text()) //'{{msg_count}}'===''? 0 : parseInt('{{msg_count}}');
      cnt = cnt===null || isNaN(cnt)? 0 :  cnt;
      if (data['lastchecked']) {
        console.log("receive data lastchecked", data['lastchecked']);
        return
      }

      if (data['message']) {
        let res = $.grep($("span.msg-item"), function(el, index) {
          return el.textContent === data['message']
        });
        //console.log(data['message'], "in: ", res);
        if (res.length==0) { //avoid the same message item duplicated on msg box
          let msg = $("#msgbox");
          let adminmsg = $("#adminmsgbox");
          // a good notification css: https://codepen.io/badhe/pen/OREomL
          let ele0 = $("<li role='msg_li'></li>"); //.append("<button type='button' class='close' data-dismiss='msg_li' aria-label='Remove'>&times;</button>");
          let ele = $("<a href='#' class='top-text-block'></a>"); //$("<tr></tr>");
          if (data['message'].includes('IMPORTANT')) {
            ele.wrapInner($("<span class='top-text-light alert-danger msg-item'></span>").text(data['message'])) //.append($("<td></td>").text //channels 1.1.8: use data['message'].message
          } else {
            ele.wrapInner($("<span class='top-text-light alert-light msg-item'></span>").text(data['message'])) //.append($("<td></td>").text //channels 1.1.8: use data['message'].message
          }
          ele0.append(ele);
          msg.append(ele0);
          adminmsg.append(ele0);
          cnt += 1;
          $('#msg_cnt').text(cnt.toString());
          $('#msg_cnt').css('color', 'red');
        }
      }

      if (data['is_logged_in']) {
        user.html(username + ': Online');
      }
      else {
        user.html(username + ': Offline');
      }
    };


//  $('#msgbox').on('click', 'li a', function(e) {
    $(document).on("click", ".msg_list", function(event) {
      $('#msg_cnt').css('color', 'grey');
      socket.send(JSON.stringify({lastchecked: true}));
    });

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
        let localTime = '';
        let tzone = Intl.DateTimeFormat().resolvedOptions().timeZone; //moment.tz.guess(); //not work
        if ($('#due_datetime').val()) {
          let duett = new Date($('#due_datetime').val());
          let tzoffset = (new Date()).getTimezoneOffset() * 60000; //offset in milliseconds
          localTime = (new Date(duett - tzoffset)).toISOString().slice(0, -1);
          //console.log("calandar vs localtime: ", duett, localTime, tzone);
        }

        let msg = {
            message: $('#adminmessage').val(),
            level: $('#adminmsglevel').val(),
            due: localTime,
            tzone: tzone
        }
        socket.send(JSON.stringify(msg));
        $("#adminmessage").val('').focus();
        return false;
    });
});


