from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError




class CustomUserCreationForm(UserCreationForm):

    def clean_email(self):  
        email = self.cleaned_data['email'].lower()  
        if (
            email
            and self._meta.model.original_objects.filter(email=email).exists()
        ):
            self._update_errors(
                ValidationError(
                    {
                        "email": self.instance.unique_error_message(
                            self._meta.model, ["email"]
                        )
                    }
                ) 
            )
        return email 

    def clean_username(self):
        """Reject usernames that differ only in case."""
        username = self.cleaned_data.get("username")
        if (
            username
            and self._meta.model.objects.filter(username__iexact=username).exists()
        ):
            self._update_errors(
                ValidationError(
                    {
                        "username": self.instance.unique_error_message(
                            self._meta.model, ["username"]
                        )
                    }
                )
            )
        else:
            return username
    