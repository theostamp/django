# Generated by Django 5.0.6 on 2024-07-29 18:12

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("tenants", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="License",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("license_key", models.CharField(max_length=100, unique=True)),
                (
                    "hardware_id",
                    models.CharField(blank=True, max_length=100, null=True),
                ),
                ("expiration_date", models.DateField()),
                ("active", models.BooleanField(default=True)),
                (
                    "tenant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="tenants.tenant"
                    ),
                ),
            ],
        ),
    ]
