# Generated by Django 4.2.3 on 2023-08-18 09:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboards', '0004_alter_task_order'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='workspace',
            options={'ordering': ['-create_at'], 'verbose_name': 'WorkSpace', 'verbose_name_plural': 'WorkSpaces'},
        ),
    ]