from rest_framework import serializers
from.models import User
import traceback
from rest_framework.utils import model_meta

class UserSerializer(serializers.ModelSerializer):

    password_confirm = serializers.CharField(required=True, write_only= True)

    class Meta:
        model = User
        # fields = ['first_name', 'last_name', 'email', 'avatar', 'password', 'mobile', ]
        exclude = ['is_active', 'is_superuser', 'is_staff', 'groups', 'user_permissions']
        read_only_fields = ['id', 'last_login', 'date_joined', ]
        extra_kwargs = {'password': {'write_only': True}}
        
    def validate(self, attrs):
        if attrs['password_confirm'] != attrs['password']:
            raise serializers.ValidationError('Passwords does not match.')
        del attrs['password_confirm']
        return super().validate(attrs)

    def create(self, validated_data):

        # # Remove many-to-many relationships from validated_data.
        # # They are not valid arguments to the default `.create()` method,
        # # as they require that the instance has already been saved.
        # info = model_meta.get_field_info(User)
        # many_to_many = {}
        # for field_name, relation_info in info.relations.items():
        #     if relation_info.to_many and (field_name in validated_data):
        #         many_to_many[field_name] = validated_data.pop(field_name)

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
        
        # # Save many-to-many relationships after the instance is created.
        # if many_to_many:
        #     for field_name, value in many_to_many.items():
        #         field = getattr(instance, field_name)
        #         field.set(value)

        return instance

    def update(self, instance, validated_data):
        if 'password' in validated_data.keys():
            validated_data.pop('password')
        return super().update(instance, validated_data)
