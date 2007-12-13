
import datetime

from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType

class CommentManager(models.Manager):
    pass

class Comment(models.Model):
    content_type = models.ForeignKey(ContentType)
    object_id = models.IntegerField(db_index=True)
    content_object = generic.GenericForeignKey("content_type", "object_id")
    user = models.ForeignKey(User, null=True, raw_id_admin=True)
    person_name = models.CharField(max_length=50)
    comment = models.TextField(max_length=3000)
    submit_date = models.DateTimeField(default=datetime.datetime.now)
    is_public = models.BooleanField()
    is_removed = models.BooleanField()
    ip_address = models.IPAddressField()
    
    objects = CommentManager()
    
    class Meta:
        app_label = "djog"
        ordering = ("-submit_date",)
    
    class Admin:
        fields = (
            (None, {"fields": ("content_type", "object_id")}),
            ("Content", {"fields": ("user", "person_name", "comment")}),
            ("Meta", {"fields": ("is_public", "is_removed", "ip_address")}),
        )
        list_display = ("user", "person_name", "submit_date", "content_type", "content_object")
        list_filter = ("submit_date",)
        date_hierarchy = "submit_date"
        search_fields = ("comment", "user__username", "person_name")
    
    def __unicode__(self):
        return "%s: %s..." % (self.person_name, self.comment[:100])
    
    def get_absolute_url(self):
        try:
            return self.content_object.get_absolute_url() + "#c" + str(self.pk)
        except AttributeError:
            return ""
