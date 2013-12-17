
from django.conf.urls.defaults import patterns, include, url
import modules.socketio.sdjango

modules.socketio.sdjango.autodiscover()

urlpatterns = patterns("chat.views",
    url("^socket\.io", include(modules.socketio.sdjango.urls)),
    url("^$", "rooms", name="rooms"),
    url("^create/$", "create", name="create"),
    url("^(?P<slug>.*)$", "room", name="room"),
)
