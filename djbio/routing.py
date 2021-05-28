from channels.routing import route
#from django.urls import path
#from channels.http import AsgiHandler
#from channels.routing import ProtocolTypeRouter, URLRouter
#from channels.auth import AuthMiddlewareStack

from api.consumers import ws_connect, ws_disconnect

channel_routing = [
    route('websocket.connect', ws_connect),
    route('websocket.disconnect', ws_disconnect),
]
#application = ProtocolTypeRouter({
#    # https://github.com/andrewgodwin/channels-examples/blob/master/multichat/multichat/routing.py
#    "websocket": AuthMiddlewareStack(
#        URLRouter([
#            path('websocket.connect', ws_connect),
#            path('websocket.disconnect', ws_disconnect),
#        ]),
#    ),
#})
