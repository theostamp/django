import logging
from logging.handlers import RotatingFileHandler
import json
import os
import threading
import time
from datetime import datetime, timedelta
from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import DisallowedHost
from django.http import JsonResponse, HttpResponse, Http404, HttpResponseNotFound, HttpResponseBadRequest
from django.shortcuts import render
from django.template.loader import get_template
from django.utils.timezone import localtime, make_aware
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_http_methods
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Order, Product
from django.db import connection
from django_tenants.utils import (
    get_public_schema_name,
    get_public_schema_urlconf,
    get_tenant_types,
    has_multi_type_tenants,
    remove_www,
)
from django.urls import set_urlconf
from django.utils.deprecation import MiddlewareMixin
from django.views.decorators.cache import never_cache
import hashlib


# Ρύθμιση του logging
LOG_FILENAME = 'order_submissions.log'

# Δημιουργία logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Δημιουργία RotatingFileHandler
file_handler = RotatingFileHandler(LOG_FILENAME, maxBytes=5*1024*1024, backupCount=5)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

# Προσθήκη του handler στο logger
logger.addHandler(file_handler)

# Δημιουργία console handler για την εμφάνιση logs στην κονσόλα
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(console_handler)

# Έλεγχος αν το αρχείο log υπάρχει και δημιουργία αν δεν υπάρχει
if not os.path.exists(LOG_FILENAME):
    open(LOG_FILENAME, 'a').close()

# Αντικαταστήστε το WORKSPACE_FOLDER με το BASE_DIR
workspace_folder = settings.BASE_DIR
tenants_base_folder = os.path.join(workspace_folder, 'tenants_folders')

def log_file_modification(file_path):
    if os.path.exists(file_path):
        modification_time = time.ctime(os.path.getmtime(file_path))
        logging.info(f"File {file_path} modified at {modification_time}")

def calculate_file_hash(file_path):
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return None
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def update_json_file(file_path, data):
    try:
        with open(file_path, 'w') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        log_file_modification(file_path)
    except Exception as e:
        logging.error(f"Error updating JSON file: {e}")


        


def has_write_permission(path):
    return os.access(path, os.W_OK)

@csrf_exempt
@require_http_methods(["POST"])
def upload_json(request, tenant):
    tenant_folder = os.path.join(settings.TENANTS_BASE_FOLDER, f'{tenant}_upload_json/')
    
    if not has_write_permission(settings.TENANTS_BASE_FOLDER):
        logger.error(f"Permission denied for creating directory: {settings.TENANTS_BASE_FOLDER}")
        return JsonResponse({'status': 'error', 'message': 'Permission denied for base directory'}, status=500)
    
    try:
        os.makedirs(tenant_folder, exist_ok=True)
    except PermissionError as e:
        logger.error(f"Permission denied: {e}")
        return JsonResponse({'status': 'error', 'message': 'Permission denied'}, status=500)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return JsonResponse({'status': 'error', 'message': 'Unexpected error occurred'}, status=500)

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            logger.debug(f"Received data for upload: {data}")
            if not isinstance(data, dict) or not data:
                return JsonResponse({'status': 'error', 'message': 'Invalid JSON data'}, status=400)
            
            for key, content in data.items():
                file_name = f"{key}.json"
                file_path = os.path.join(tenant_folder, file_name)
                with open(file_path, 'w', encoding='utf-8') as file:
                    json.dump(content, file, ensure_ascii=False, indent=4)
                logger.info(f"File saved successfully: {file_path}")

            return JsonResponse({'status': 'success'})
        except json.JSONDecodeError:
            logger.error("Invalid JSON data")
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON data'}, status=400)
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return JsonResponse({'status': 'error', 'message': 'Unexpected error occurred'}, status=500)

    logger.error("Invalid request method")
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)




@csrf_exempt
def list_order_files(request, tenant):
    folder_path = os.path.join(settings.TENANTS_BASE_FOLDER, f'{tenant}_received_orders')
    logger.debug(f"Checking for order files in: {folder_path}")

    if os.path.exists(folder_path):
        file_list = os.listdir(folder_path)
        logger.debug(f"Found files: {file_list}")
        return JsonResponse({'files': file_list})
    else:
        logger.error(f"Directory not found: {folder_path}")
        return JsonResponse({'status': 'error', 'message': 'Directory not found'}, status=404)

@csrf_exempt
def check_permissions(request):
    base_dir = settings.TENANTS_BASE_FOLDER
    has_permission = os.access(base_dir, os.W_OK)
    logger.debug(f"Checking write permission for {base_dir}: {has_permission}")
    return JsonResponse({'base_dir': base_dir, 'has_write_permission': has_permission})

@csrf_exempt
def test_read_file(request):
    file_path = os.path.join(workspace_folder, 'tenants_folders', 'theo_received_orders', 'order_table_1_540102.json')
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as file:
                data = json.load(file)
                return JsonResponse(data)
        except json.JSONDecodeError as e:
            return HttpResponseBadRequest(f"JSON decode error: {e}")
        except Exception as e:
            return HttpResponseBadRequest(f"Error reading file: {e}")
    else:
        raise Http404("File not found")

def index(request):
    return render(request, 'tables/index.html')

@csrf_exempt
def check_for_refresh(request):
    refresh_needed = cache.get('refresh_order_summary', False)
    if refresh_needed:
        cache.delete('refresh_order_summary')
    return JsonResponse({'refresh': refresh_needed})

@csrf_exempt
def signal_refresh_order_summary(request):
    data = json.loads(request.body)
    if data.get('refresh'):
        cache.set('refresh_order_summary', True, timeout=90)
    return JsonResponse({'status': 'success'})

@csrf_exempt
@require_http_methods(["DELETE"])
def delete_received_orders(request, tenant):
    logger.debug(f"delete_received_orders called with tenant={tenant}")
    response_data = {
        'checked_files': [],
        'deleted_files': [],
        'not_found_files': [],
        'errors': [],
        'file_paths_checked': [],
        'order_ids_found': []
    }

    try:
        data = json.loads(request.body)
        order_ids = set(map(str, data.get('order_ids', [])))
        directory = os.path.join(workspace_folder, 'tenants_folders', f'{tenant}_received_orders')

        if not os.path.exists(directory):
            response_data['errors'].append('Directory not found.')
            return JsonResponse(response_data, status=404)

        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            response_data['checked_files'].append(filename)
            response_data['file_paths_checked'].append(file_path)

            with open(file_path, 'r') as file:
                try:
                    file_data = json.load(file)
                    file_order_id = str(file_data.get('order_id'))
                    response_data['order_ids_found'].append(file_order_id)
                except json.JSONDecodeError:
                    continue

                if file_order_id in order_ids:
                    os.remove(file_path)
                    response_data['deleted_files'].append(filename)
                else:
                    response_data['not_found_files'].append(filename)

        return JsonResponse({'message': 'Files processed successfully.', **response_data})
    except Exception as e:
        response_data['errors'].append(str(e))
        return JsonResponse(response_data, status=500)

@csrf_exempt
def check_occupied_tables(request, username):
    tenant_folder = os.path.join(workspace_folder, 'tenants_folders', f'{username}_upload_json/')
    file_path = os.path.join(tenant_folder, 'tables.json')
    
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return JsonResponse({'status': 'success', 'data': data})
    else:
        return JsonResponse({'status': 'error', 'message': 'File not found'}, status=404)

@never_cache
@csrf_exempt
def get_order(request, tenant, filename):
    logger.debug(f"get_order called with tenant={tenant} and filename={filename}")
    file_path = os.path.join(workspace_folder, 'tenants_folders', f'{tenant}_received_orders', filename)
    logger.debug(f"Checking file path: {file_path}")

    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as file:
                data = json.load(file)
                logger.debug(f"File read successfully: {file_path}")
                return JsonResponse(data)
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return HttpResponseBadRequest(f"JSON decode error: {e}")
        except Exception as e:
            logger.error(f"Error reading file: {e}")
            return HttpResponseBadRequest(f"Error reading file: {e}")
    else:
        logger.error(f"File not found: {file_path}")
        return JsonResponse({'error': 'File not found', 'file_path': file_path}, status=404)


@never_cache
@csrf_exempt
def get_order_summary(request, tenant, filename):
    logger.debug(f"get_order_summary called with tenant={tenant} and filename={filename}")
    file_path = os.path.join(workspace_folder, 'tenants_folders', f'{tenant}_received_orders', filename)
    logger.debug(f"Checking file path: {file_path}")

    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as file:
                data = json.load(file)
                logger.debug(f"File read successfully: {file_path}")
                return JsonResponse(data)
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return HttpResponseBadRequest(f"JSON decode error: {e}")
        except Exception as e:
            logger.error(f"Error reading file: {e}")
            return HttpResponseBadRequest(f"Error reading file: {e}")
    else:
        logger.error(f"File not found: {file_path}")
        return JsonResponse({'error': 'File not found', 'file_path': file_path}, status=404)



def table_selection(request):
    tenant = connection.get_tenant()
    tenant_name = tenant.name

    occupied_tables_file = os.path.join(workspace_folder, 'tenants_folders', f'{tenant_name}_upload_json', 'tables.json')

    try:
        with open(occupied_tables_file, 'r') as file:
            tables_data = json.load(file)
            if not isinstance(tables_data, dict) or 'tables' not in tables_data:
                raise TypeError("Expected 'tables' key with a list of tables")

            tables_list = tables_data['tables']
            if not isinstance(tables_list, list):
                raise TypeError("Expected list of tables")

            return render(request, 'tables/table_selection.html', {'tables': tables_list})
    except FileNotFoundError:
        return HttpResponseNotFound('File not found')
    except json.JSONDecodeError as e:
        return HttpResponseBadRequest(f"JSON decode error: {e}")
    except TypeError as e:
        return HttpResponseBadRequest(f"Type error: {e}")



def order_for_table(request, table_number):
    schema_name = connection.get_schema()
    username = connection.get_tenant()

    products_file_path = os.path.join(workspace_folder, 'tenants_folders', f'{username}_upload_json', 'products.json')
    logger.debug(f"Loading products from {products_file_path}")
    
    try:
        with open(products_file_path, 'r') as file:
            data = json.load(file)
            products_data = data.get('products', [])
            logger.debug(f"Loaded products data: {products_data}")
    except Exception as e:
        logger.error(f"Error loading products data: {e}")
        return render(request, 'tables/order_for_table.html', {'table_number': table_number, 'categories': {}})

    categorized_products = {}
    for product in products_data:
        logger.debug(f"Processing product: {product}")
        if not isinstance(product, dict):
            logger.error(f"Invalid product data: {product}")
            continue

        category = product.get('category')
        if category not in categorized_products:
            categorized_products[category] = []
        categorized_products[category].append(product)

    first_three_categories = dict(list(categorized_products.items())[:3])
    return render(request, 'tables/order_for_table.html', {'table_number': table_number, 'categories': first_three_categories})

def success(request):
    return render(request, 'tables/success.html')

def serve_reservations(request, tenant):
    file_path = os.path.join(workspace_folder, 'tenants_folders', f'{tenant}_upload_json', 'reservations.json')
    logger.debug(f"Serving file: {file_path}")

    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as file:
                data = file.read()
                return JsonResponse(json.loads(data), safe=False)
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return HttpResponseNotFound(f"Error reading file {file_path}: {e}")
    else:
        logger.error(f"File not found: {file_path}")
        return HttpResponseNotFound(f"File not found: {file_path}")

def serve_occupied_tables(request, tenant):
    file_path = os.path.join(workspace_folder, 'tenants_folders', f'{tenant}_upload_json', 'tables.json')
    logger.debug(f"Serving file: {file_path}")

    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as file:
                data = file.read()
                return JsonResponse(json.loads(data), safe=False)
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return HttpResponseNotFound(f"Error reading file {file_path}: {e}")
    else:
        logger.error(f"File not found: {file_path}")
        return HttpResponseNotFound(f"File not found: {file_path}")

def serve_order_file(request, tenant, filename):
    file_path = os.path.join(workspace_folder, 'tenants_folders', f'{tenant}_received_orders', filename)
    logger.debug(f"Serving file: {file_path}")

    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as file:
                data = file.read()
                return JsonResponse(json.loads(data), safe=False)
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return HttpResponseNotFound(f"Error reading file {file_path}: {e}")
    else:
        logger.error(f"File not found: {file_path}")
        return HttpResponseNotFound(f"File not found: {file_path}")

@csrf_exempt
def update_product_status(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print("Ληφθέντα δεδομένα:", data)
            unique_product_id = data.get('uniqueProductId')
            order_done = data.get('order_done')
            table_number = data.get('table_number')
            quantity = data.get('quantity')

            product_id, time_id = unique_product_id.rsplit('-', 1)

            product_data = {
                "product_id": product_id,
                "time_id": time_id,
                "order_done": order_done,
                "table_number": table_number,
                "quantity": quantity
            }
            print(product_data)
            folder_name = "orders_completed"
            file_name = f"updated_product_status_{unique_product_id}.json"
            folder_path = os.path.join(workspace_folder, 'rest_order', folder_name)
            file_path = os.path.join(folder_path, file_name)

            os.makedirs(folder_path, exist_ok=True)

            with open(file_path, 'w') as file:
                json.dump(product_data, file)
                logger.info(f"Δημιουργία αρχείου: {file_path}")

            return JsonResponse({'status': 'success'})
        except json.JSONDecodeError as e:
            logger.error(f"Σφάλμα JSON Decode: {e}")
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
        except Exception as e:
            logger.error(f"Γενικό σφάλμα: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        logger.error("Λάθος μέθοδος αιτήματος")
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

@csrf_exempt
def list_orders(request):
    orders_by_table = {}
    folder_path = os.path.join(workspace_folder, 'received_orders')

    for filename in os.listdir(folder_path):
        if filename.endswith('.json'):
            with open(os.path.join(folder_path, filename), 'r') as file:
                order = json.load(file)
                table_number = order['table_number']

                if table_number not in orders_by_table:
                    orders_by_table[table_number] = {
                        'orders': [], 'waiter': order.get('waiter'), 'table_number': table_number
                    }

                orders_by_table[table_number]['orders'].append(order)

    return render(request, 'tables/list_orders.html', {'orders_by_table': orders_by_table})

@csrf_exempt
def get_json(request):
    folder_path = os.path.join(workspace_folder, 'received_orders')
    if os.path.exists(folder_path):
        file_list = os.listdir(folder_path)
        return JsonResponse({'files': file_list})
    else:
        return JsonResponse({'status': 'error', 'message': 'Directory not found'}, status=404)

@csrf_exempt
def products_json(request):
    with open(os.path.join(workspace_folder, 'upload_json', 'products.json'), 'r') as file:
        data = json.load(file)
        return JsonResponse(data)

@csrf_exempt
def process_orders(folder_path, output_file):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    all_orders = []
    unique_order_ids = set()

    for filename in os.listdir(folder_path):
        if filename.endswith('.json'):
            file_path = os.path.join(folder_path, filename)
            try:
                with open(file_path, 'r') as file:
                    order_data = json.load(file)

                    if isinstance(order_data, dict):
                        order_data = [order_data]

                    for order in order_data:
                        if not isinstance(order, dict):
                            continue

                        order_id = order.get('order_id')
                        if order_id and order_id not in unique_order_ids:
                            unique_order_ids.add(order_id)
                            all_orders.append(order)
            except Exception as e:
                print(f"Προέκυψε σφάλμα κατά την επεξεργασία του αρχείου {filename}: {e}")

    with open(output_file, 'w') as file:
        json.dump(all_orders, file)




def order_summary(request):
    tenant = connection.get_tenant()
    tenant_name = tenant.name  # Χρήση του ονόματος του tenant από τη σύνδεση

    products_dict = load_products(tenant_name)
    folder_path = os.path.join(workspace_folder, 'tenants_folders', f'{tenant_name}_received_orders')

    if not os.path.exists(folder_path):
        context = {'error_message': f"Σφάλμα: Ο φάκελος {folder_path} δεν υπάρχει"}
        return render(request, 'tables/error_page.html', context)

    current_time = datetime.now()
    orders_by_table = {}
    processed_order_ids = set()

    for filename in os.listdir(folder_path):
        if filename.endswith('.json'):
            file_path = os.path.join(folder_path, filename)
            try:
                with open(file_path, 'r') as file:
                    order = json.load(file)

                if not isinstance(order, dict):
                    raise TypeError("Expected dict for order")

                order_id = order.get('order_id')
                if order_id in processed_order_ids:
                    continue

                processed_order_ids.add(order_id)

                if order.get('order_done') == 0:
                    table_number = order.get('table_number')
                    if table_number not in orders_by_table:
                        orders_by_table[table_number] = {'orders': [], 'waiter': order.get('waiter')}

                    order_time_str = order.get('timestamp')
                    if order_time_str:
                        order_time = datetime.strptime(order_time_str, "%Y-%m-%d %H:%M:%S")
                        if order_time > current_time:
                            order_time -= timedelta(days=1)
                        time_passed = current_time - order_time
                        order['time_passed'] = int(time_passed.total_seconds() // 60)
                        order['time_diff'] = order['time_passed']

                        with open(file_path, 'w') as update_file:
                            json.dump(order, update_file, indent=4)
                    else:
                        order['time_passed'] = 'Άγνωστος χρόνος'

                    for product in order.get('products', []):
                        product_id = str(product['id'])
                        product_info = products_dict.get(product_id, {})
                        product['name'] = product_info.get('description', 'Unknown Product')

                    orders_by_table[table_number]['orders'].append(order)

            except json.JSONDecodeError as e:
                logger.error(f"Σφάλμα κατά την ανάγνωση του JSON: {e}")
                continue
            except TypeError as e:
                logger.error(f"Type error: {e}")
                continue

    sorted_orders_by_table = dict(sorted(orders_by_table.items(), key=lambda item: max(order['time_passed'] if isinstance(order['time_passed'], int) else 0 for order in item[1]['orders']), reverse=True))

    return render(request, 'tables/order_summary.html', {'sorted_orders_by_table': sorted_orders_by_table})




def load_products(tenant_name):
    products_file_path = os.path.join(workspace_folder, 'tenants_folders', f'{tenant_name}_upload_json', 'products.json')
    if not os.path.exists(products_file_path):
        raise FileNotFoundError(f"File not found: {products_file_path}")
    with open(products_file_path, 'r') as file:
        data = json.load(file)
    return {str(product['id']): product for product in data['products']}




@csrf_exempt
def submit_order(request, table_number=None):
    tenant = connection.get_tenant()
    products_dict = load_products(tenant)
    
    if request.method == 'POST':
        try:
            order_data = json.loads(request.body)
            current_time = datetime.now()
            order_id_base = int(current_time.strftime("%H%M%S"))
            products = order_data.get('products', [])

            for index, product in enumerate(products, start=1):
                product_order_id = f"{order_id_base}{index}"
                product_info = products_dict.get(str(product['id']))
                if product_info:
                    description = product_info['description']
                    price = product_info['price']

                    timestamp = current_time.strftime("%Y-%m-%d %H:%M:%S")
                    new_order_data = {
                        'table_number': order_data['table_number'],
                        'product_description': description,
                        'quantity': product['quantity'],
                        'total_cost': price * int(product['quantity']),
                        'waiter': order_data.get('waiter', 'unknown'),
                        'order_done': False,
                        'printed': False,
                        'order_id': product_order_id,
                        'timestamp': timestamp
                    }

                    filename = f"order_table_{table_number}_{product_order_id}.json"
                    time_diff = int((datetime.now() - datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")).total_seconds() // 60)
                    new_order_data['time_diff'] = time_diff

                    folder_path = os.path.join(workspace_folder, 'tenants_folders', f'{tenant.name}_received_orders')
                    file_path = os.path.join(folder_path, filename)

                    if not os.path.exists(folder_path):
                        os.makedirs(folder_path)

                    with open(file_path, 'w') as file:
                        json.dump(new_order_data, file)
                    logger.debug(f"Order saved to: {file_path}")
                else:
                    logger.error(f"Product info not found for product ID {product['id']}")

            return JsonResponse({'status': 'success', 'message': 'Η παραγγελία υποβλήθηκε με επιτυχία'})
        except Exception as e:
            logger.error(f"Γενικό σφάλμα: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Μη έγκυρο αίτημα'})

@csrf_exempt
def list_received_orders(request, tenant):
    folder_path = os.path.join(workspace_folder, 'tenants_folders', f'{tenant}_received_orders')

    if os.path.exists(folder_path):
        file_list = os.listdir(folder_path)
        return JsonResponse({'files': file_list})
    else:
        return JsonResponse({'status': 'error', 'message': 'Directory not found'}, status=404)

@csrf_exempt
def update_order_status_in_json(order_id, new_status=1):
    file_path = os.path.join(workspace_folder, 'all_orders.json')

    try:
        with open(file_path, 'r') as file:
            orders = json.load(file)

        order_found = False
        for order in orders:
            if str(order.get('order_id')) == str(order_id):
                print(f"Updating order with ID: {order_id}")
                order['order_done'] = new_status
                order_found = True
                break

        if not order_found:
            print(f"Order with ID: {order_id} not found")
            return False, "Order not found"

        with open(file_path, 'w') as file:
            json.dump(orders, file, indent=4)

        return True, "Order updated successfully"
    except Exception as e:
        print(f"Error in update_order_status_in_json: {e}")
        return False, str(e)

def update_order_status_in_folder(order_id, new_status=1, folder_path=None):
    try:
        if folder_path is None:
            tenant = connection.get_tenant()
            tenant_name = tenant.name
            folder_path = os.path.join(workspace_folder, 'tenants_folders', f'{tenant_name}_received_orders')

        order_found = False
        for filename in os.listdir(folder_path):
            if filename.endswith('.json'):
                file_path = os.path.join(folder_path, filename)
                with open(file_path, 'r') as file:
                    order = json.load(file)

                if str(order.get('order_id')) == str(order_id):
                    print(f"Updating order with ID: {order_id}")
                    order['order_done'] = new_status
                    order_found = True

                    with open(file_path, 'w') as file:
                        json.dump(order, file, indent=4)
                    break

        if not order_found:
            print(f"Order with ID: {order_id} not found")
            return False, "Order not found"

        return True, "Order updated successfully"
    except Exception as e:
        print(f"Error in update_order_status_in_folder: {e}")
        return False, str(e)

@csrf_exempt
def update_order(request):
    try:
        data = json.loads(request.body)
        print(f"Received data: {data}")

        if not isinstance(data, list):
            raise ValueError("Invalid data format: expected a list of orders")

        for order in data:
            order_id = order.get('order_id')
            if not order_id:
                raise ValueError("No order_id provided in one of the orders")

            new_status = order.get('order_done', 1)
            print(f"Order ID: {order_id}, New Status: {new_status}")

            success, message = update_order_status_in_folder(order_id, new_status)
            if not success:
                print(f"Order update failed for {order_id}: {message}")

        return JsonResponse({"success": True})
    except json.JSONDecodeError as e:
        print(f"JSON Decode Error: {e}")
        return JsonResponse({"success": False, "error": "Invalid JSON data"}, status=400)
    except Exception as e:
        print(f"General error in update_order: {e}")
        return JsonResponse({"success": False, "error": str(e)}, status=500)



@csrf_exempt
def delete_order_file(request, filename):
    if request.method == 'DELETE':
        tenant = connection.get_tenant()
        tenant_name = tenant.name
        file_path = os.path.join(workspace_folder, 'tenants_folders', f'{tenant_name}_received_orders', filename)

        if os.path.exists(file_path):
            os.remove(file_path)
            return JsonResponse({'status': 'success', 'message': 'File deleted successfully'})
        else:
            return JsonResponse({'status': 'error', 'message': 'File not found'}, status=404)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)



@csrf_exempt
def cancel_order(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            tenant = connection.get_tenant()
            tenant_name = tenant.name
            folder_path = os.path.join(workspace_folder, 'tenants_folders', f'{tenant_name}_received_orders')

            for order in data:
                order_id = order.get('order_id')

                for filename in os.listdir(folder_path):
                    if filename.endswith('.json') and order_id in filename:
                        file_path = os.path.join(folder_path, filename)
                        os.remove(file_path)
                        break

            return JsonResponse({'status': 'success', 'message': 'Οι παραγγελίες ακυρώθηκαν'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    else:
        return JsonResponse({'status': 'error', 'message': 'Μη έγκυρη μέθοδος αιτήματος'})



@csrf_exempt
def get_orders_json(request):
    logger.debug("get_orders_json called")
    orders = []
    folder_path = os.path.join(workspace_folder, 'received_orders')

    logger.debug(f"Processing folder: {folder_path}")

    for filename in os.listdir(folder_path):
        if filename.endswith('.json'):
            file_path = os.path.join(folder_path, filename)
            logger.debug(f"Processing file: {file_path}")
            with open(file_path, 'r') as file:
                orders.append(json.load(file))

    logger.debug("Completed processing folder")
    return JsonResponse({'orders': orders})

@csrf_exempt
def get_orders(request):
    logger.debug("get_orders called")
    orders = Order.objects.all()
    order_data = [{'order_id': order.id, 'product_description': order.product_description, 'quantity': order.quantity, 'timestamp': order.timestamp} for order in orders]
    
    logger.debug(f"Retrieved orders: {order_data}")
    return JsonResponse(order_data, safe=False)

def table_selection_with_time_diff(request):
    tenant = connection.get_tenant()
    tenant_name = tenant.name

    occupied_tables_file = os.path.join(workspace_folder, 'tenants_folders', f'{tenant_name}_upload_json', 'tables.json')

    if not os.path.exists(occupied_tables_file):
        logger.error(f"Occupied tables file not found: {occupied_tables_file}")
        return HttpResponseNotFound(f'Occupied tables file not found: {occupied_tables_file}')

    try:
        with open(occupied_tables_file, 'r') as file:
            tables_data = json.load(file)
            if not isinstance(tables_data, dict) or 'tables' not in tables_data:
                raise TypeError("Expected 'tables' key with a list of tables")

            tables_list = tables_data['tables']
            if not isinstance(tables_list, list):
                raise TypeError("Expected list of tables")

            for table in tables_list:
                if not isinstance(table, dict):
                    raise TypeError("Expected dict for table")
                table_number = table.get('table_number')
                if table_number is None:
                    raise ValueError("Table number is missing in the table data")
                time_diff = get_time_diff_from_file(tenant_name, table_number)
                table['time_diff'] = time_diff

            return render(request, 'tables/table_selection_with_time_diff.html', {'tables': tables_list})
    except FileNotFoundError:
        logger.error(f"File not found: {occupied_tables_file}")
        return HttpResponseNotFound('File not found')
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON from {occupied_tables_file}: {e}")
        return HttpResponseNotFound('Error decoding JSON file')
    except (TypeError, ValueError) as e:
        logger.error(f"Error in JSON data: {e}")
        return HttpResponseNotFound('Error in JSON data')

def get_time_diff_from_file(tenant_name, table_number):
    folder_path = os.path.join(workspace_folder, 'tenants_folders', f'{tenant_name}_received_orders')

    if not os.path.exists(folder_path):
        logger.error(f"Received orders folder not found: {folder_path}")
        return 'N/A'

    for filename in sorted(os.listdir(folder_path)):
        if filename.endswith('.json') and f"order_table_{table_number}_" in filename:
            file_path = os.path.join(folder_path, filename)
            try:
                with open(file_path, 'r') as file:
                    order_data = json.load(file)
                    time_diff = order_data.get('time_diff')
                    if time_diff is not None:
                        hours, minutes = divmod(time_diff, 60)
                        return f"{int(hours):02}:{int(minutes):02}"
            except json.JSONDecodeError as e:
                logger.error(f"Error decoding JSON from {file_path}: {e}")
                continue
            except Exception as e:
                logger.error(f"Error reading file {file_path}: {e}")
                continue

    return 'N/A'

def get_occupied_tables(request, tenant):
    tenant_folder = os.path.join(workspace_folder, 'tenants_folders', f'{tenant}_upload_json')
    file_path = os.path.join(tenant_folder, 'tables.json')

    if not os.path.exists(file_path):
        return HttpResponseNotFound('File not found')

    with open(file_path, 'r') as file:
        data = json.load(file)
    return JsonResponse(data, safe=False)

@csrf_exempt
def save_positions(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            positions_file_path = os.path.join(workspace_folder, 'button_positions.json')
            with open(positions_file_path, 'w') as file:
                json.dump(data, file, indent=4)
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

@csrf_exempt
def load_positions(request):
    try:
        positions_file_path = os.path.join(workspace_folder, 'button_positions.json')
        if os.path.exists(positions_file_path):
            with open(positions_file_path, 'r') as file:
                data = json.load(file)
                return JsonResponse(data)
        else:
            return JsonResponse({})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@csrf_exempt
def update_time_diff(request, tenant, filename):
    if request.method == 'POST':
        try:
            print(f"Received request to update time_diff for tenant: {tenant}, file: {filename}")
            file_path = os.path.join(workspace_folder, 'tenants_folders', f'{tenant}_received_orders', filename)
            print(f"File path: {file_path}")

            if not os.path.exists(file_path):
                print("File not found")
                return HttpResponseBadRequest("File not found")

            with open(file_path, 'r') as file:
                order_data = json.load(file)
            print(f"Current order data: {order_data}")

            if 'time_diff' in request.POST:
                time_diff = request.POST['time_diff']
                order_data['time_diff'] = time_diff
                print(f"Updated time_diff to: {time_diff}")
            else:
                print("time_diff not found in POST data")
                return HttpResponseBadRequest("time_diff not found in POST data")

            with open(file_path, 'w') as file:
                json.dump(order_data, file)
            print("File updated successfully")

            return JsonResponse({"status": "success"})
        except json.JSONDecodeError as json_error:
            print(f"JSON decode error: {json_error}")
            return HttpResponseBadRequest(f"JSON decode error: {json_error}")
        except Exception as e:
            print(f"Exception occurred: {e}")
            return HttpResponseBadRequest(str(e))
    else:
        print("Invalid request method")
        return HttpResponseBadRequest("Invalid request method")

def order_details(request):
    table_number = request.GET.get('table')
    tenant = request.GET.get('tenant')
    file_path = os.path.join(workspace_folder, 'tenants_folders', f'{tenant}_received_orders', f'order_table_{table_number}.json')
    
    try:
        with open(file_path, 'r') as file:
            order_data = json.load(file)
    except FileNotFoundError:
        order_data = {'items': []}

    return render(request, 'tables/order_details.html', {'order_data': order_data, 'table_number': table_number})

def table_orders(request, tenant, table_number):
    base_dir = os.path.join(workspace_folder, 'tenants_folders', f'{tenant}_received_orders')
    order_files = [f for f in os.listdir(base_dir) if f.startswith(f'order_table_{table_number}_')]

    orders = []
    for file in order_files:
        with open(os.path.join(base_dir, file), 'r') as f:
            order_data = json.load(f)
            if order_data.get('order_done') == 1:
                orders.append(order_data)

    for order in orders:
        print(f"Order ID: {order.get('order_id')}")
        print(f"Order Products: {order.get('products')}")
        print(f"Order Time: {order.get('timestamp')}")

    context = {
        'table_number': table_number,
        'orders': orders,
    }
    return render(request, 'tables/table_orders.html', context)
