from __future__ import unicode_literals

from django.db import models


class Alumnus(models.Model):
    cross_name_hash = models.CharField(max_length=32, db_index=True, unique=True)
    cross_name = models.CharField(max_length=200)

    def __unicode__(self):
        return self.cross_name


class Poll(models.Model):
    priority = models.PositiveSmallIntegerField()
    open_until = models.DateTimeField()
    public = models.BooleanField(default=False)
    title = models.CharField(max_length=200)
    description = models.TextField()
    min_votes = models.PositiveSmallIntegerField()
    max_votes = models.PositiveSmallIntegerField()
    binary = models.BooleanField(default=False)
    auth_app = models.CharField(max_length=30, default='')

    def __unicode__(self):
        return self.title


class PollOption(models.Model):
    poll = models.ForeignKey(Poll, db_index=True)
    priority = models.PositiveSmallIntegerField()
    open_until = models.DateTimeField(null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)

    def __unicode__(self):
        return '{}: {}'.format(unicode(self.poll), self.title)

    class Meta:
        ordering = ['priority']


class PollVote(models.Model):
    poll = models.ForeignKey(Poll, db_index=True)
    alumnus = models.ForeignKey(Alumnus, db_index=True)
    code = models.CharField(max_length=200)
    active = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return '{}{} for {}'.format(
            '[x] ' if self.active else '',
            self.alumnus,
            self.poll,
        )


class PollVoteOption(models.Model):
    poll_vote = models.ForeignKey(PollVote, db_index=True)
    poll_option = models.ForeignKey(PollOption)
    vote = models.BooleanField()
