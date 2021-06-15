#from channels.routing import route #channels 1.1.8
## channels 3.0
from django.urls import path
from channels.http import AsgiHandler
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
##
from api.consumers import MsgConsumer #--> channels 1.1.8 #*

## channels 1.1.8
#channel_routing = [
#    route('websocket.connect', ws_connect),
#    route('websocket.receive', ws_receive),
#    route('websocket.disconnect', ws_disconnect),
#]
##
## channels 3.0
application = ProtocolTypeRouter({
    # https://github.com/andrewgodwin/channels-examples/blob/master/multichat/multichat/routing.py
    "websocket": AuthMiddlewareStack(
        URLRouter([
            path('users/', MsgConsumer.as_asgi()),
        ]),
    ),
})
