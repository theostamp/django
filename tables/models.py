from django.db import models



class Product(models.Model):
    id = models.AutoField(primary_key=True)
    category = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    price = models.FloatField()
    amount = models.IntegerField()


class Order(models.Model):
    table_number = models.IntegerField()
    timestamp = models.CharField(max_length=6)
    waiter = models.CharField(max_length=100, default='unknown')
    order_done = models.BooleanField(default=False)
    printed = models.BooleanField(default=False)
    order_id = models.CharField(max_length=10, unique=True)

    products = models.ManyToManyField(Product, through='OrderProduct')


class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
