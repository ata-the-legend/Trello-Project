from django import forms
from django.core.exceptions import ValidationError



class MembersM2MAdminForm(forms.ModelForm):
    def clean_user(self):
        workspace = self.cleaned_data['workspace']
        member = self.cleaned_data['user']
        print(workspace.owner)
        print(member)
        if workspace.owner == member:
            raise ValidationError('Owner cant be member')
        return self.cleaned_data["user"]