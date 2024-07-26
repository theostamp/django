# tables/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter
def calc_total_cost(orders):
    total = sum(order['total_cost'] for order in orders)
    return f"{total:.2f}"
