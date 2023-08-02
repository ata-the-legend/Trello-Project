from django.db import models
from django.utils.translation import gettext_lazy as _
from uuid import uuid4


class BaseModel(models.Model):

    id = models.UUIDField(editable=False, primary_key=True, default=uuid4)
    create_at = models.DateTimeField(_("Create at"), auto_now=False, auto_now_add=True)
    update_at = models.DateTimeField(_("Update at"), auto_now=True, auto_now_add=False)

    class Meta:
        abstract = True



class SoftQuerySet(models.QuerySet):
    def archive(self):
        return self.update(is_active= False)
    
    def restore(self):
        return self.update(is_active= True)
    
class SoftManager(models.Manager):
    def get_queryset(self):
        return SoftQuerySet(self.model, self._db).filter(is_active = True)

class SoftDeleteMixin(models.Model):

    is_active = models.BooleanField(_("Is Active"), default=True)

    objects = SoftManager

    def archive(self):
        self.is_active = False
        self.save()

    def restore(self):
        self.is_active= True
        self.save()

    class Meta:
        abstract = True


