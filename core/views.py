# coding=utf-8
import hashlib

from django.contrib import messages
from django.db.models import Count
from django.http import HttpResponse, HttpResponseNotAllowed
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.six import wraps

import auth
import core.models


def alumnus_required(*args):
    def deco(f):
        @wraps(f)
        def inner(*args, **kwargs):
            request = args[0]
            if 'alumnus' not in request.session:
                return redirect(reverse('login'))
            if load:
                alumnus = core.models.Alumnus.objects.get(id=request.session['alumnus']['id'])
                kwargs['alumnus'] = alumnus
            return f(*args, **kwargs)

        return inner

    if len(args) == 1 and callable(args[0]):
        load = False
        return deco(args[0])
    load = args[0]
    return deco


def login_view(request):
    if 'alumnus' in request.session:
        return redirect(reverse('public_polls'))
    if request.method == 'POST':
        auth_code = request.POST.get('auth_code', '')
        if auth_code:  # иначе анонимус
            data = auth.get_data(auth_code)
            if data['status'] == 'valid':
                alumnus, _ = core.models.Alumnus.objects.get_or_create(
                    cross_name_hash=hashlib.md5(data['cross_name'].encode('utf-8')).hexdigest(),
                    cross_name=data['cross_name'],
                )
                data['id'] = alumnus.id
                request.session['alumnus'] = data
                request.session['auth_code'] = auth_code
                return redirect(reverse('public_polls'))
        messages.error(request, u'Код не принят')
        return redirect(reverse('login'))
    return render(request, 'login.html')


def logout_view(request):
    if request.method == 'POST':
        del request.session['alumnus']
        del request.session['auth_code']
        return redirect(reverse('login'))
    return HttpResponseNotAllowed(['POST'])


@alumnus_required(True)
def polls_view(request, poll_id=None, alumnus=None):
    if poll_id is None:
        filters = {
            'public': True,
            'open_until__gt': timezone.now(),
        }
    else:
        filters = {
            'id': poll_id
        }
    polls = core.models.Poll.objects.filter(**filters).order_by('priority')
    poll_ids = [poll.id for poll in polls]
    poll_votes = core.models.PollVote.objects.filter(
        alumnus=alumnus,
        poll_id__in=poll_ids,
        active=True
    ).values_list('id', 'poll_id')
    voted_polls = set([poll_vote[1] for poll_vote in poll_votes])
    options = core.models.PollVoteOption.objects.filter(
        poll_vote_id__in=[poll_vote[0] for poll_vote in poll_votes]
    )
    options = {option.poll_option_id: option for option in options}

    return render(request,
                  'public_polls.html',
                  {
                      'polls': polls,
                      'voted_polls': voted_polls,
                      'voted_options': options,
                  })


@alumnus_required(True)
def poll_vote_view(request, poll_id=None, alumnus=None):
    post = request.POST

    poll = core.models.Poll.objects.get(id=poll_id)
    reverse_url = reverse('public_polls')
    if not poll.public or poll.open_until < timezone.now():
        reverse_url = reverse('poll', kwargs={'poll_id': poll.id})

    submitted_options = {int(x.replace('option_', '')) for x in post.keys()
                         if x.startswith('option_') and post[x] == u'on'}

    if request.method != "POST":
        return HttpResponseNotAllowed(['POST'])

    if timezone.now() > poll.open_until:
        messages.error(request, u'Голосование закрыто')
        return redirect(reverse_url)

    if len(submitted_options) < poll.min_votes:
        messages.error(request, u'Надо выбрать больше {} опций'.format(poll.min_votes))
        return redirect(reverse_url)

    if len(submitted_options) > poll.max_votes:
        messages.error(request, u'Надо выбрать не более {} опций'.format(poll.max_votes))
        return redirect(reverse_url)

    poll_vote = core.models.PollVote.objects.filter(
        poll=poll,
        alumnus=alumnus,
        active=True,
    ).first()
    if poll_vote:
        code = poll_vote.code
    else:
        code = request.session['auth_code']
        temp_code = auth.get_temporary_code(code, poll.auth_app)
        if temp_code.get('status') == 'bad_request':
            messages.error(request, u'Не удалось получить временный код: {}'.format(temp_code['error']))
            return redirect(reverse_url)
        code = temp_code['code']

    poll_vote = core.models.PollVote(poll=poll, alumnus=alumnus, code=code)
    poll_vote.save()

    core.models.PollVote.objects.filter(
        poll=poll,
        alumnus=alumnus,
        active=True,
    ).exclude(id=poll_vote.id).update(active=False)

    for option in poll.polloption_set.all():
        if option.id in submitted_options:
            poll_vote.pollvoteoption_set.create(
                poll_vote=poll_vote,
                poll_option=option,
                vote=True
            )

    return redirect(reverse_url)


@alumnus_required
def poll_results_view(request, poll_id=None):
    poll = core.models.Poll.objects.get(id=poll_id)
    option_ids = poll.polloption_set.values_list('id', flat=True)
    option_votes = core.models.PollVoteOption.objects.filter(
        poll_option_id__in=list(option_ids),
        poll_vote__active=True,
    ).values(
        'poll_option_id'
    ).annotate(
        votes=Count('vote')
    )
    option_votes = {vote['poll_option_id']: vote['votes'] for vote in option_votes}
    return render(request,
                  'poll_results.html',
                  {
                      'poll': poll,
                      'option_votes': option_votes,
                  })
