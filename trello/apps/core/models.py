from django.db import models
from django.utils.translation import gettext_lazy as _
from uuid import uuid4


class BaseModel(models.Model):

    id = models.UUIDField(editable=False, primary_key=True, default=uuid4)
    create_at = models.DateTimeField(_("Create at"), auto_now=False, auto_now_add=True)
    update_at = models.DateTimeField(_("Update at"), auto_now=True, auto_now_add=False)

    class Meta:
        abstract = True



