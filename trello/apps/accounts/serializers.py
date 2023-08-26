from rest_framework import serializers
from.models import User, _
import traceback
# from rest_framework.utils import model_meta
from rest_framework.validators import UniqueValidator



class UserSerializer(serializers.ModelSerializer):

    password_confirm = serializers.CharField(required=True, write_only= True)

    class Meta:
        model = User
        # fields = ['first_name', 'last_name', 'email', 'avatar', 'password', 'mobile', ]
        exclude = ['is_active', 'is_superuser', 'is_staff', 'groups', 'user_permissions']
        read_only_fields = ['id', 'last_login', 'date_joined', ]
        extra_kwargs = {'password': {'write_only': True},
                        'email': {
                            'validators':[
                                UniqueValidator(
                                    queryset=User.original_objects.all(), 
                                    message= _("A user with that email already exists.")
                                    ),
                                ]
                            },
                        'mobile': {
                            'validators':[
                                UniqueValidator(
                                    queryset=User.original_objects.all(), 
                                    message= _("A user with that mobile already exists.")
                                    ),
                                ]
                            },
                        }
        
    def validate(self, attrs):
        if attrs.get('password_confirm', None) or attrs.get('password', None):
            if not attrs.get('password_confirm', None) or not attrs.get('password', None):
                raise serializers.ValidationError('Passwords does not match.')
            if attrs['password_confirm'] != attrs['password']:
                raise serializers.ValidationError('Passwords does not match.')
            del attrs['password_confirm']
        return super().validate(attrs)

    def create(self, validated_data):
        try:
            instance = User.objects.create_user(**validated_data)
        except TypeError:
            tb = traceback.format_exc()
            msg = (
                'Got a `TypeError` when calling `%s.%s.create()`. '
                'This may be because you have a writable field on the '
                'serializer class that is not a valid argument to '
                '`%s.%s.create()`. You may need to make the field '
                'read-only, or override the %s.create() method to handle '
                'this correctly.\nOriginal exception was:\n %s' %
                (
                    User.__name__,
                    User._default_manager.name,
                    User.__name__,
                    User._default_manager.name,
                    self.__class__.__name__,
                    tb
                )
            )
            raise TypeError(msg)
        
        return instance

    def update(self, instance, validated_data):
        if 'password' in validated_data.keys() or 'password_confirm' in validated_data.keys():
            validated_data.pop('password')
        return super().update(instance, validated_data)


class UserPasswordSerializer(serializers.Serializer):
    
    password = serializers.CharField(required=True, write_only= True)
    password_confirm = serializers.CharField(required=True, write_only= True)

    def validate(self, attrs):
        if attrs['password_confirm'] != attrs['password']:
            raise serializers.ValidationError('Passwords does not match.')
        return super().validate(attrs)
    
class UserListSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'avatar', ]