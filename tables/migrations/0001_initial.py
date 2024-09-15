# Generated by Django 5.0.6 on 2024-09-15 09:35

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Order",
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
                ("table_number", models.IntegerField()),
                ("timestamp", models.CharField(max_length=6)),
                ("waiter", models.CharField(default="unknown", max_length=100)),
                ("order_done", models.BooleanField(default=False)),
                ("printed", models.BooleanField(default=False)),
                ("order_id", models.CharField(max_length=10, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name="Product",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("category", models.CharField(max_length=100)),
                ("description", models.CharField(max_length=200)),
                ("price", models.FloatField()),
                ("amount", models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name="OrderProduct",
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
                ("quantity", models.IntegerField()),
                (
                    "order",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="tables.order"
                    ),
                ),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="tables.product"
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="order",
            name="products",
            field=models.ManyToManyField(
                through="tables.OrderProduct", to="tables.product"
            ),
        ),
    ]
