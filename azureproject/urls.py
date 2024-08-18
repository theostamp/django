# azureproject/urls.py

from django.contrib import admin
from django.urls import include, path
from authentication.views import check_subscription_status, check_mac_address, register_mac_address, check_login, index, payment_error,get_mac_address, register_mac_address
from tables.views import check_permissions, table_orders, serve_reservations, serve_occupied_tables, update_time_diff, serve_order_file, get_occupied_tables, list_received_orders, test_read_file, order_details, load_positions, check_for_refresh, save_positions,signal_refresh_order_summary, delete_received_orders, get_orders,cancel_order,delete_order_file, process_orders, update_order,  get_json,get_orders_json, success,submit_order, order_for_table,table_selection,get_order,order_summary, table_selection_with_time_diff, upload_json,products_json,list_order_files

urlpatterns = [

    path('api/get-mac-address/<str:username>/', get_mac_address, name='get_mac_address'),
    path('api/register-mac-address/<str:username>/', register_mac_address, name='register_mac_address'),
    path('api/check-login/', check_login, name='check_login'),
    path('api/check-mac-address/', check_mac_address, name='check_mac_address'),
    path('api/check-subscription/<str:username>/', check_subscription_status, name='check_subscription_status'),
    


    path('', index, name='index'),
    path('tables/', include('tables.urls')),
    path('table_selection/', include('tables.urls')),
    path('admin/', admin.site.urls),
    path('authentication/', include('authentication.urls')),
    path('get-csrf-token/', include('authentication.urls')),
    path('paypal/', include('paypal.standard.ipn.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('error/', payment_error, name='error'),  # Προσθήκη του URL pattern για το error

    # Χρήση των σωστών εισαγόμενων views
    path('table_selection_with_time_diff/', table_selection_with_time_diff, name='table_selection_with_time_diff'),
    path('order_summary/', order_summary, name='order_summary'),

    path('upload_json/<str:tenant>/', upload_json, name='upload_json'),
    path('upload_json/products.json', products_json, name='products_json'),
    path('list_order_files/<str:tenant>/', list_order_files, name='list_order_files'),
    path('get_order/<str:tenant>/<str:filename>/', get_order, name='get_order_tenant'),
    path('table_selection/', table_selection, name='table_selection'),
    # path('tables/table_selection/', table_selection, name='table_selection'),  # Επαναφορά της διαδρομής
    path('order_for_table/<int:table_number>/', order_for_table, name='order_for_table'),
    path('submit_order/', submit_order, name='submit_order'),
    path('order_for_table/<int:table_number>/submit_order/', submit_order, name='submit_order_specific'),
    path('success/', success, name='success'),
    path('orders_json/', get_orders_json, name='get_orders_json'),
    path('get_json/', get_json, name='get_json'),
    path('order_summary/', order_summary, name='order_summary'),
    path('update_order/', update_order, name='update_order'),
    path('order-summary/', order_summary, name='order_summary'),  # Επαναφορά της διαδρομής
    path('process-orders/', process_orders, name='process_orders'),
    path('delete_order_file/<str:filename>/', delete_order_file, name='delete_order_file'),
    path('cancel_order/', cancel_order, name='cancel_order'),
    path('get-orders/', get_orders, name='get_orders'),
    path('delete_received_orders/<str:tenant>/', delete_received_orders, name='delete_received_orders'),
    path('signal_refresh_order_summary/', signal_refresh_order_summary, name='signal_refresh_order_summary'),
    path('check_for_refresh/', check_for_refresh, name='check_for_refresh'),
    path('', index, name='index'),
    path('table_selection_with_time_diff/', table_selection_with_time_diff, name='table_selection_with_time_diff'),
    path('tenants_folders/<str:tenant>_upload_json/occupied_tables.json', get_occupied_tables, name='get_occupied_tables'),
    path('tenants_folders/<str:tenant>_received_orders/<str:filename>/', serve_order_file, name='serve_order_file'),
    path('save_positions', save_positions, name='save_positions'),
    path('load_positions', load_positions, name='load_positions'),
    path('update_time_diff/<str:tenant>/<str:filename>', update_time_diff, name='update_time_diff'),
    path('order_details/', order_details, name='order_details'),
    path('test_read_file/', test_read_file, name='test_read_file'),
    path('list_received_orders/<str:tenant>/', list_received_orders, name='list_received_orders'),
    path('tenants_folders/<str:tenant>_received_orders/<str:filename>', serve_order_file, name='serve_order_file'),
    path('tenants_folders/<str:tenant>_upload_json/occupied_tables.json', serve_occupied_tables, name='get_occupied_tables'),
    path('tenants_folders/<str:tenant>_upload_json/reservations.json', serve_reservations, name='get_reservations'),
    path('table_orders/<str:tenant>/<int:table_number>/', table_orders, name='table_orders'),
    path('check_permissions/', check_permissions, name='check_permissions'),

    path('register-mac-address/<str:username>/', register_mac_address, name='register_mac_address'),
    path('check-mac-address/', check_mac_address, name='check_mac_address'),



]
