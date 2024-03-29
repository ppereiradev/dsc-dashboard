# Generated by Django 3.2.15 on 2022-09-29 20:41

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_ticket', models.CharField(max_length=50)),
                ('number', models.CharField(max_length=50)),
                ('created_at', models.DateTimeField()),
                ('close_at', models.DateTimeField(blank=True, null=True)),
                ('updated_at', models.DateTimeField(blank=True, null=True)),
                ('create_article_type', models.CharField(max_length=50)),
                ('state', models.CharField(max_length=50)),
                ('group', models.CharField(max_length=50)),
            ],
        ),
    ]
