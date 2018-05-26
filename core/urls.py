from django.conf.urls import url
from .views import (
    login_view,
    logout_view,
    polls_view,
    poll_vote_view,
    poll_results_view,
)


urlpatterns = [
    url(r'^$', login_view, name='login'),
    url(r'^logout$', logout_view, name='logout'),
    url(r'^polls/$', polls_view, name='public_polls'),
    url(r'^polls/(?P<poll_id>[0-9]+)$', polls_view, name='poll'),
    url(r'^polls/(?P<poll_id>[0-9]+)/vote$', poll_vote_view, name='poll_vote'),
    url(r'^polls/(?P<poll_id>[0-9]+)/results$', poll_results_view, name='poll_results'),
]
