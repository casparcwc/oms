#encoding:utf-8
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

#log modlel
class userLog(models.Model):
    username = models.CharField("username",max_length=20)
    log_msg = models.TextField()
    create_time = models.DateTimeField("创建日期",auto_now_add=True)

    def _str_(self):
        return self.username

class omsUser(AbstractUser):
    real_name = models.CharField('姓名',max_length=20, unique=True)
    #USERNAME_FIELD = 'username'
    phone_num = models.CharField('电话',max_length=11)

    class Meta:
        db_table='oms_user'
        permissions = (
                    ('opmonitor','Can operation monitor'),
                    ('opjenkins','Can operation jenkins'),
                    ('opredis','Can operation redis')
          )
    def _str_(self):
        return self.username


