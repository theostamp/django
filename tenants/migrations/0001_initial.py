# Generated by Django 5.0.6 on 2024-07-29 07:59

import django.db.models.deletion
import django_tenants.postgresql_backend.base
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Tenant",
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
                (
                    "schema_name",
                    models.CharField(
                        db_index=True,
                        max_length=63,
                        unique=True,
                        validators=[
                            django_tenants.postgresql_backend.base._check_schema_name
                        ],
                    ),
                ),
                ("name", models.CharField(max_length=100, unique=True)),
                ("created_on", models.DateField(auto_now_add=True)),
                ("subscription_type", models.CharField(max_length=100)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Subscription",
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
                ("start_date", models.DateField()),
                ("end_date", models.DateField()),
                (
                    "subscription_type",
                    models.CharField(
                        choices=[
                            ("trial", "One Month Trial"),
                            ("basic", "Basic"),
                            ("premium", "Premium"),
                            ("enterprise", "Enterprise"),
                        ],
                        max_length=100,
                    ),
                ),
                ("price", models.DecimalField(decimal_places=2, max_digits=6)),
                ("active", models.BooleanField(default=False)),
                (
                    "tenant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="tenants.tenant"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Domain",
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
                (
                    "domain",
                    models.CharField(db_index=True, max_length=253, unique=True),
                ),
                ("is_primary", models.BooleanField(db_index=True, default=True)),
                (
                    "tenant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="tenants.tenant"
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
