"""
Administrative API Functions for Train-Ticket Load Testing

Provides admin API implementations for system management, user administration,
travel route management, order processing, and system configuration.
Functions require admin authentication and handle data validation.
"""

import random
from datetime import datetime, timedelta
import pandas as pd
import utils
import config



def home(client, headers=None):
    """Load administrative homepage and dashboard interface."""
    client.get("/admin.html", name=utils.get_name_suffix("admin_home"), headers=headers)


''' --------- User --------- '''

def login(client):
    """
    Authenticate admin user with default credentials (admin/222222).
    Returns (user_id, token) for authenticated admin session.
    """
    user_name = "admin"
    password = "222222"
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    body = {"username": user_name, "password": password}
    response = client.post(url="/api/v1/users/login", headers=headers, json=body, context=body,
                           name=utils.get_name_suffix("admin_login"))
    response_as_json = utils.get_json_from_response(response)
    data = response_as_json["data"]
    user_id = data["userId"]
    token = data["token"]
    return user_id, token

def api_call_admin_create_user(client, token, user_name, password):
    """Create new user account with specified credentials through admin interface."""
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json", "Content-Type": "application/json"}
    body = {"documentNum": None, "documentType": 0, "email": "string", "gender": 0, "password": password,
            "userName": user_name}
    response = client.post(url="/api/v1/adminuserservice/users", headers=headers, json=body, context=body,
                           name=utils.get_name_suffix("admin_create_user"))
    response_as_json = utils.get_json_from_response(response)
    return response_as_json

def get_all_users(client, headers=None):
    """Retrieve all user accounts for administrative management and monitoring."""
    response = client.get(url='/api/v1/adminuserservice/users', name='admin_get_all_users',
                          headers=headers)
    response_as_json = utils.get_json_from_response(response)
    return response_as_json


def create_random_user(client, headers):
    """Create user account with randomized test data for load testing scenarios."""
    body = {"userName": utils.get_random_string(),
            "password": utils.get_random_string(),
            "gender": int(random.random()),
            "email": utils.get_random_string(),
            "documentType": int(random.random()),
            "documentNum": utils.get_random_string()}
    response = client.post(url='/api/v1/adminuserservice/users', name='admin_add_random_user',
                          headers=headers, json=body, context=body)
    response_as_json = utils.get_json_from_response(response)
    return response_as_json


''' --------- Travel --------- '''

def get_all_travels(client, headers=None):
    """Retrieve all travel routes and schedules for administrative management."""
    response = client.get(url="/api/v1/admintravelservice/admintravel", headers=headers,
                          name=utils.get_name_suffix("admin_get_all_travels"))
    response_as_json = utils.get_json_from_response(response)
    return response_as_json


def update_travel(client, trip, headers=None):
    """
    Update existing travel route with modified schedule times.
    Adjusts start/end times by ±1 hour and maintains data integrity with fallback values.
    """
    trip_id = f'{trip["trip"]["tripId"]["type"]}{trip["trip"]["tripId"]["number"]}'
    x = pd.to_datetime(trip["trip"]["startTime"])
    starting_time = x + timedelta(hours=random.choice([-1, +1]))

    # Use the exact date format from InitData.java
    start_time_str = starting_time.strftime("%Y-%m-%d %H:%M:%S")
    end_time = starting_time + timedelta(hours=random.randint(2, 8))
    end_time_str = end_time.strftime("%Y-%m-%d %H:%M:%S")

    # Safely extract fields with fallbacks using real InitData patterns
    trip_data = trip["trip"]

    body = {
        "loginId": "admin",
        "tripId": trip_id,
        "trainTypeName": trip_data.get("trainTypeName", "GaoTieOne"),
        "routeId": trip_data.get("routeId", "92708982-77af-4318-be25-57ccb0ff69ad"),
        "startStationName": trip_data.get("startStationName", "shanghai"),
        "stationsName": trip_data.get("stationsName", "suzhou"),  # Single station
        "terminalStationName": trip_data.get("terminalStationName", "taiyuan"),
        "startTime": start_time_str,
        "endTime": end_time_str
    }
    response = client.put(url="/api/v1/admintravelservice/admintravel", json=body, context=body, headers=headers,
                          name=utils.get_name_suffix("admin_uptdate_travel"))
    response_as_json = utils.get_json_from_response(response)
    return response_as_json


def create_travel(client, route, hs=True, headers=None):
    """
    Create new travel route using real InitData.java patterns for validation.
    Supports both high-speed (G/D series) and regular trains (Z/T/K series).
    Trip numbers use 2000-4000 range for load testing.
    """
    if hs:
        train_type_id = random.choice(config.HS_TRAIN_TYPE_ID)
    else:
        train_type_id = random.choice(config.OTHER_TRAIN_TYPE_ID)

    number = random.randint(2000, 4000)

    # Use the exact date format from InitData.java: "2013-05-04 09:00:00"
    start_time_str = "2013-05-04 09:00:00"
    end_time_str = "2013-05-04 15:51:52"

    # Use actual valid route IDs and station patterns from InitData.java
    if hs:
        # High-speed train pattern (G/D series)
        start_station = "shanghai"
        intermediate_station = "suzhou"  # Single station, not comma-separated
        terminal_station = "taiyuan"
        # Use actual route IDs from ts-travel-service InitData
        route_id = random.choice([
            "92708982-77af-4318-be25-57ccb0ff69ad",
            "aefcef3f-3f42-46e8-afd7-6cb2a928bd3d",
            "a3f256c1-0e43-4f7d-9c21-121bf258101f",
            "084837bb-53c8-4438-87c8-0321a4d09917",
            "f3d4d4ef-693b-4456-8eed-59c0d717dd08"
        ])
        # Use actual train type names from InitData
        train_type_name = random.choice(["GaoTieOne", "GaoTieTwo", "DongCheOne"])
    else:
        # Regular train pattern (Z/T/K series)
        start_station = "shanghai"
        intermediate_station = "nanjing"  # Single station, not comma-separated
        terminal_station = "beijing"
        # Use actual route IDs from ts-travel2-service InitData
        route_id = random.choice([
            "0b23bd3e-876a-4af3-b920-c50a90c90b04",
            "9fc9c261-3263-4bfa-82f8-bb44e06b2f52",
            "d693a2c5-ef87-4a3c-bef8-600b43f62c68",
            "20eb7122-3a11-423f-b10a-be0dc5bce7db",
            "1367db1f-461e-4ab7-87ad-2bcc05fd9cb7"
        ])
        # Use actual train type names from InitData
        train_type_name = random.choice(["ZhiDa", "TeKuai", "KuaiSu"])

    # Handle route parameter - use from routes if available, otherwise use default
    if route and isinstance(route, dict) and "id" in route:
        route_id = route["id"]

    body = {
        "loginId": "admin",
        "tripId": f'{train_type_id[0]}{number}',
        "trainTypeName": train_type_name,
        "routeId": route_id,
        "startStationName": start_station,
        "stationsName": intermediate_station,  # Single station, not comma-separated
        "terminalStationName": terminal_station,
        "startTime": start_time_str,
        "endTime": end_time_str
    }
    response = client.post(url="/api/v1/admintravelservice/admintravel", json=body, headers=headers, context=body,
                           name=utils.get_name_suffix("admin_create_travel"))
    response_as_json = utils.get_json_from_response(response)
    return response_as_json


def delete_travel(client, travel_id, headers=None):
    """Delete travel route by ID. Used for route cleanup and test data management."""
    response = client.post(url=f"/api/v1/admintravelservice/admintravel/{travel_id}", headers=headers,
                           name=utils.get_name_suffix("admin_delete_travel"))
    response_as_json = utils.get_json_from_response(response)
    return response_as_json


def delete_random_travel(client, travels, hs=True, headers=None):
    """
    Safely delete random travel with train type filtering and ID constraints.
    Only deletes trips with numbers >= 2000 to protect production data.
    Returns None if no suitable travel found after 20 iterations.
    """
    travel = random.choice(travels)
    trip_id = travel["trip"]["tripId"]
    iteration = 0
    if hs:
        while not ((trip_id['type'] == 'D' or trip_id['type'] == 'G') and (int(trip_id['number']) >= 2000)):
            travel = random.choice(travels)
            trip_id = travel["trip"]["tripId"]
            if iteration >= 20:
                print("No trip to delete hs")
                return None
            iteration += 1
    else:
        while not (not (trip_id['type'] == 'D' or trip_id['type'] == 'G') and (int(trip_id['number']) >= 2000)):
            travel = random.choice(travels)
            trip_id = travel["trip"]["tripId"]
            if iteration >= 20:
                print("No trip to delete other")
                return None
            iteration += 1
    return delete_travel(client, f'{travel["trip"]["tripId"]}{travel["trip"]["number"]}', headers=headers)


''' --------- Order --------- '''

def get_all_orders(client, headers=None):
    """Retrieve all customer orders for administrative management and monitoring."""
    response = client.get(url="/api/v1/adminorderservice/adminorder", headers=headers,
                          name=utils.get_name_suffix("admin_get_all_orders"))
    response_as_json = utils.get_json_from_response(response)
    return response_as_json


def create_order(client, hs=True, headers=None):
    """
    Create new order with realistic test data for load testing scenarios.
    Generates orders with random routes, prices, and appropriate train types.
    """
    start, end = utils.get_random_start_end_stations(hs)
    body = {"boughtDate": f"{str(datetime.now()).replace(' ', 'T')[:-3]}Z",
            "travelDate": 1,
            "travelTime": 2,
            "accountId": "4d2a46c7-71cb-4cf1-b5bb-b68406d9da6f",
            "contactsName": f"Contact_{random.randint(1, 10)}",
            "documentType": 1,
            "contactsDocumentNumber": f"DocumentNumber_{random.randint(1, 10)}",
            "trainNumber": f"{'G' if hs else 'K'}{random.randint(2000, 4000)}",
            "coachNumber": 5,
            "seatClass": 2,
            "seatNumber": f"FirstClass-{random.randint(1, 30)}",
            "from": start,
            "to": end,
            "status": 0,
            "price": str(round(random.random() * 100, 2))}
    response = client.post(url="/api/v1/adminorderservice/adminorder", json=body, headers=headers, context=body,
                           name=utils.get_name_suffix("admin_create_order"))

    response_as_json = utils.get_json_from_response(response)
    return response_as_json


def get_all_prices(client, headers=None):
    """Retrieve all pricing configurations for administrative management."""
    response = client.get(url='/api/v1/adminbasicservice/adminbasic/prices', name='admin_get_all_prices',
                          headers=headers)
    response_as_json = utils.get_json_from_response(response)
    return response_as_json


def modify_price(client, headers=None, price=None):
    """Modify pricing configuration with randomized rate adjustments for testing."""
    body = {"id": price["id"],
            "trainType": price["trainType"],
            "routeId": price["routeId"],
            "basicPriceRate": random.random(),
            "firstClassPriceRate": random.random()}
    response = client.put(url='/api/v1/adminbasicservice/adminbasic/prices', name='admin_modify_price', headers=headers,
                          context=body, json=body)
    response_as_json = utils.get_json_from_response(response)
    return response_as_json


def update_order(client, order, headers=None):
    """Update existing order with random price adjustments (±10 units)."""
    new_price = float(order['price']) + (random.random() * 20 - 10)
    order['price'] = str(round(new_price, 2))
    response = client.put(url='/api/v1/adminorderservice/adminorder', name='admin_update_order', headers=headers,
                          context=order, json=order)
    response_as_json = utils.get_json_from_response(response)
    return response_as_json


def delete_order(client, order_id, train_number, headers=None):
    """Delete order by ID and train number with dual parameter validation."""
    response = client.post(url=f"/api/v1/admintravelservice/admintravel/{order_id}/{train_number}", headers=headers,
                           name=utils.get_name_suffix("admin_delete_order"))
    response_as_json = utils.get_json_from_response(response)
    return response_as_json


def delete_random_order(client, orders, hs=True, headers=None):
    """
    Safely delete random order with train type filtering and safety constraints.
    Only deletes orders with train numbers >= 2000 to protect production data.
    Returns None if no suitable order found after 20 iterations.
    """
    order = random.choice(orders['data'])
    train_number = order['trainNumber']
    iteration = 0
    if hs:
        while not ((train_number[0] == 'D' or train_number[0] == 'G') and (int(train_number[1:]) >= 2000)):
            order = random.choice(orders)
            train_number = order['trainNumber']
            if iteration >= 20:
                print("No trip to delete hs")
                return None
            iteration += 1
    else:
        while not (not (train_number[0] == 'D' or train_number[0] == 'G') and (int(train_number[1:]) >= 2000)):
            order = random.choice(orders)
            train_number = order['trainNumber']
            if iteration >= 20:
                print("No trip to delete other")
                return None
            iteration += 1
    return delete_order(client, order['id'], train_number, headers=headers)


''' --------- Route --------- '''

def get_all_routes(client, headers=None):
    """Retrieve all route definitions for administrative management and network planning."""
    response = client.get(url="/api/v1/adminrouteservice/adminroute", headers=headers,
                          name=utils.get_name_suffix("admin_get_all_routes"))
    response_as_json = utils.get_json_from_response(response)
    return response_as_json


''' --------- Basic --------- '''

def get_all_contacts(client, headers=None):
    """Retrieve all customer contact records for administrative management."""
    response = client.get(url='/api/v1/adminbasicservice/adminbasic/contacts', name='admin_get_all_contacts',
                          headers=headers)
    response_as_json = utils.get_json_from_response(response)
    return response_as_json


def modify_contact(client, headers=None, contact=None):
    """
    Modify existing contact with randomized document type and phone number updates.
    Preserves ID and name while updating other fields for testing scenarios.
    """
    body = {"id": contact["id"],
            "name": contact["name"],
            "documentType": int(random.random() * 5),
            "documentNumber": contact["documentNumber"],
            "phoneNumber": f'{contact["phoneNumber"][:-1]}{int(random.random() * 9)}'}
    response = client.put(url='/api/v1/adminbasicservice/adminbasic/contacts', name='admin_modify_contact',
                          headers=headers, context=body, json=body)
    response_as_json = utils.get_json_from_response(response)
    return response_as_json


''' --------- Stations --------- '''

def get_all_stations(client, headers=None):
    """Retrieve all railway stations for infrastructure management and monitoring."""
    response = client.get(url='/api/v1/adminbasicservice/adminbasic/stations', name='admin_get_all_stations',
                          headers=headers)
    response_as_json = utils.get_json_from_response(response)
    return response_as_json


''' --------- Trains --------- '''

def get_all_trains(client, headers=None):
    """Retrieve all train types (G/D/Z/T/K series) for fleet management and service planning."""
    response = client.get(url='/api/v1/adminbasicservice/adminbasic/trains', name='admin_get_all_trains',
                          headers=headers)
    response_as_json = utils.get_json_from_response(response)
    return response_as_json


''' --------- Configs --------- '''

def get_all_configs(client, headers=None):
    """Retrieve all system configurations and operational parameters for administration."""
    response = client.get(url='/api/v1/adminbasicservice/adminbasic/configs', name='admin_get_all_configs',
                          headers=headers)
    response_as_json = utils.get_json_from_response(response)
    return response_as_json

