from django.contrib import admin

import models

admin.site.register(models.Alumnus)
admin.site.register(models.Poll)
admin.site.register(models.PollOption)
admin.site.register(models.PollVote)
admin.site.register(models.PollVoteOption)
