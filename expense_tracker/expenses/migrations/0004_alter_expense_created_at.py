# Generated by Django 5.0.6 on 2024-06-16 12:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('expenses', '0003_alter_expense_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expense',
            name='created_at',
            field=models.DateTimeField(),
        ),
    ]