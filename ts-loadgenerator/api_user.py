"""
User API Functions for Train-Ticket Load Testing

Provides user-facing API implementations for authentication, search, booking,
payment, and order management workflows. Supports both anonymous and
authenticated contexts with proper error handling.
"""

import random
import utils
from datetime import datetime, timedelta
import config


def login(client):
    """
    Authenticate user with default test credentials (fdse_microservice/111111).
    Returns (user_id, token) for authenticated session.
    """
    user_name = "fdse_microservice"
    password = "111111"
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    body = {"username": user_name, "password": password}
    response = client.post(url="/api/v1/users/login", headers=headers, context=body, json=body,
                           name=utils.get_name_suffix("login"))
    response_as_json = utils.get_json_from_response(response)
    data = response_as_json["data"]
    user_id = data["userId"]
    token = data["token"]
    return user_id, token


def home(client):
    """Load main application homepage for anonymous or authenticated users."""
    client.get("/index.html", name=utils.get_name_suffix("home"))
    pass


def client_login_page(client):
    """Load client login page interface for user authentication."""
    client.get("/client_login.html", name=utils.get_name_suffix("client_login_page"))


def search_travel(client, from_station, to_station, hs=True, logged=True, headers=None):
    """
    Search for available train trips with service routing based on train type.
    Routes to travelservice (HS) or travel2service (regular trains).
    Supports both anonymous and authenticated contexts.
    """
    departure_date = utils.get_departure_date()
    body = {"startingPlace": from_station, "endPlace": to_station, "departureTime": departure_date}

    if hs:
        # Route high-speed train searches to ts-travel-service
        url = "/api/v1/travelservice/trips/left"
        response = client.post(url=url, json=body, context=body, headers=headers,
                               name=utils.get_name_suffix(f"search_travel_hs_{'logged' if logged else 'external'}"))
    else:
        # Route regular train searches to ts-travel2-service
        url = "/api/v1/travel2service/trips/left"
        response = client.post(url=url, json=body, context=body, headers=headers,
                               name=utils.get_name_suffix(f"search_travel_other_{'logged' if logged else 'external'}"))

    result = utils.get_json_from_response(response)
    return result


def get_trip_information(client, from_station, to_station, hs=True):
    """Get trip information and availability without user context for general information purposes."""
    departure_date = utils.get_departure_date()
    body = {"startingPlace": from_station, "endPlace": to_station, "departureTime": departure_date}
    if hs:
        url = "/api/v1/travelservice/trips/left"
        response = client.post(url=url, json=body, context=body, name=utils.get_name_suffix("get_trip_information_hs"))
    else:
        url = "/api/v1/travel2service/trips/left"
        response = client.post(url=url, json=body, context=body,
                               name=utils.get_name_suffix("get_trip_information_other"))
    return utils.get_json_from_response(response)


def book(client, user_id, trip_id="D1345", from_station="Shang Hai", to_station="Su Zhou", hs=True, headers=None):
    """
    Complete ticket booking workflow with service integration.
    Handles contacts, food, insurance, and ticket reservation with optional consignment.
    Routes to preserveservice (HS) or preserveotherservice (regular trains).
    """
    tomorrow = datetime.now() + timedelta(1)
    next_monday = utils.next_weekday(tomorrow, 0)
    departure_date = next_monday.strftime("%Y-%m-%d")

    def api_call_insurance():
        response = client.get(url="/api/v1/assuranceservice/assurances/types", headers=headers,
                              name=utils.get_name_suffix("get_assurance_types"))
        return utils.get_json_from_response(response)

    def api_call_food():
        response = client.get(url=f"/api/v1/foodservice/foods/{departure_date}/{from_station}/{to_station}/{trip_id}",
                              headers=headers, name=utils.get_name_suffix("get_food_types"))
        return utils.get_json_from_response(response)

    def api_call_contacts():
        response = client.get(url=f"/api/v1/contactservice/contacts/account/{user_id}", headers=headers,
                              name=utils.get_name_suffix("query_contacts"))
        data = utils.get_json_from_response(response)["data"]
        contact_id = data[0]["id"]
        return contact_id

    def api_call_ticket(consign=False):
        body = {"accountId": user_id, "contactsId": contact_id, "tripId": trip_id, "seatType": "2",
                "date": departure_date, "from": from_station, "to": to_station,
                "assurance": random.choice(config.ASSURANCE_TYPES), "foodType": 1,
                "foodName": "Bone Soup", "foodPrice": 2.5, "stationName": "", "storeName": ""}
        if consign:
            body["consigneeName"] = utils.get_random_string(10)
            body["consigneePhone"] = utils.get_random_string(10)
            body["consigneeWeight"] = int(random.random() * 50)

        if hs:
            response = client.post(url="/api/v1/preserveservice/preserve", json=body, headers=headers, context=body,
                                   name=utils.get_name_suffix("preserve_ticket_hs"))
        else:
            response = client.post(url="/api/v1/preserveotherservice/preserveOther", json=body, headers=headers,
                                   context=body,
                                   name=utils.get_name_suffix("preserve_ticket_other"))
        return response

    contact_id = api_call_contacts()
    api_call_food()
    api_call_insurance()
    api_call_ticket(random.choice([True, False]))


def get_all_orders(client, user_id, hs=True, headers=None):
    """
    Retrieve all user orders with service routing based on train type.
    Routes to orderservice (HS) or orderOtherService (regular trains).
    Returns complete order history with all filtering disabled.
    """
    body = {"loginId": user_id, "enableStateQuery": "false", "enableTravelDateQuery": "false",
            "enableBoughtDateQuery": "false", "travelDateStart": "null", "travelDateEnd": "null",
            "boughtDateStart": "null", "boughtDateEnd": "null"}
    if hs:
        response = client.post(url="/api/v1/orderservice/order/refresh", json=body, headers=headers, context=body,
                               name=utils.get_name_suffix("get_order_information_hs"))
    else:
        response = client.post(url="/api/v1/orderOtherService/orderOther/refresh", json=body, headers=headers,
                               context=body,
                               name=utils.get_name_suffix("get_order_information_other"))
    return utils.get_json_from_response(response)['data']


def get_last_order(client, user_id, expected_status, hs=True, headers=None):
    """Find first order with specific status for order operations (payment, cancellation, etc.)."""
    data = get_all_orders(client, user_id, hs, headers)
    for entry in data:
        if entry["status"] == expected_status:
            return entry
    return None


def get_last_order_id(client, user_id, expected_status, hs=True, headers=None):
    """Extract order ID from first order matching the specified status."""
    order = get_last_order(client, user_id, expected_status, hs=hs, headers=headers)
    if order is not None:
        order_id = order["id"]
        return order_id

    return None


def pay(client, user_id, trip_id="D1345", hs=True, headers=None):
    """
    Process payment for booked ticket orders.
    Locates BOOKED order and submits payment, updating status to PAID.
    Raises exception if no booked orders available.
    """
    order_id = get_last_order_id(client, user_id, config.TICKET_STATUS_BOOKED, hs=hs, headers=headers)
    if order_id == None:
        raise Exception("Weird... There is no order to pay.")

    def api_call_pay(headers):
        body = {"orderId": order_id, "tripId": trip_id}
        response = client.post(url="/api/v1/inside_pay_service/inside_payment", json=body, headers=headers,
                               context=body,
                               name=utils.get_name_suffix(f"pay_order_{'hs' if hs else 'other'}"))

        return utils.get_json_from_response(response)

    api_call_pay(headers=headers)


def cancel(client, user_id, hs=True, headers=None):
    """
    Cancel booked ticket with two-step process: refund calculation and order cancellation.
    Locates BOOKED order and processes refund before final cancellation.
    Raises exception if no booked orders available.
    """
    order_id = get_last_order_id(client, user_id, config.TICKET_STATUS_BOOKED, hs, headers)
    if order_id is None:
        raise Exception("Weird... There is no order to cancel.")

    def api_call_cancel_refund():
        response = client.get(url=f"/api/v1/cancelservice/cancel/refound/{order_id}",
                              name=utils.get_name_suffix("cancel_refund_order"), headers=headers)
        return utils.get_json_from_response(response)

    def api_call_cancel():
        response = client.get(url=f"/api/v1/cancelservice/cancel/{order_id}/{user_id}",
                              name=utils.get_name_suffix("cancel_order"), headers=headers)
        return utils.get_json_from_response(response)

    api_call_cancel_refund()
    api_call_cancel()


def get_travel_plan(client, from_station, to_station):
    # Use fixed date that matches database trips (2013-05-04)
    departure_datetime = "2013-05-04 00:00:00"

    # Format station names with proper capitalization (e.g., "Nan Jing", "Shang Hai")
    def format_station_name(station):
        """Convert 'shanghai' -> 'Shang Hai', 'nanjing' -> 'Nan Jing'"""
        station_map = {
            "shanghai": "Shang Hai",
            "nanjing": "Nan Jing",
            "suzhou": "Su Zhou",
            "taiyuan": "Tai Yuan",
            "shijiazhuang": "Shi Jia Zhuang",
            "xuzhou": "Xu Zhou",
            "jinan": "Ji Nan",
            "beijing": "Bei Jing",
            "shanghaihongqiao": "Shang Hai Hong Qiao",
            "jiaxingnan": "Jia Xing Nan",
            "hangzhou": "Hang Zhou",
            "zhenjiang": "Zhen Jiang",
            "wuxi": "Wu Xi"
        }
        return station_map.get(station.lower(), station.title())

    body = {
        "startPlace": format_station_name(from_station),
        "endPlace": format_station_name(to_station),
        "departureTime": departure_datetime
    }
    response = client.post(url="/api/v1/travelplanservice/travelPlan/cheapest", json=body, context=body,
                           name=utils.get_name_suffix("get_travel_plan"))
    return utils.get_json_from_response(response)


# ============================================================================
# BASIC SERVICE - Route and station queries
# ============================================================================

def query_basic_travel(client, trip_id, from_station, to_station, headers=None):
    """Query route information by trip ID and stations."""
    body = {
        "trip": {"tripId": trip_id},
        "startPlace": from_station,
        "endPlace": to_station
    }
    response = client.post(url="/api/v1/basicservice/basic/travel", json=body, context=body, headers=headers,
                          name=utils.get_name_suffix("query_basic_travel"))
    return utils.get_json_from_response(response)


def query_basic_travels(client, trip_ids, headers=None):
    """Query route information by multiple trip IDs."""
    body = trip_ids if isinstance(trip_ids, list) else [trip_ids]
    response = client.post(url="/api/v1/basicservice/basic/travels", json=body, context=body, headers=headers,
                          name=utils.get_name_suffix("query_basic_travels"))
    return utils.get_json_from_response(response)


def query_station_by_name(client, station_name, headers=None):
    """Query station information by name"""
    response = client.get(url=f"/api/v1/basicservice/basic/{station_name}", headers=headers,
                         name=utils.get_name_suffix("query_station_by_name"))
    return utils.get_json_from_response(response)


# ============================================================================
# USER SERVICE - User management
# ============================================================================

def get_all_users(client, headers=None):
    """Get all users"""
    response = client.get(url="/api/v1/userservice/users", headers=headers,
                         name=utils.get_name_suffix("get_all_users"))
    return utils.get_json_from_response(response)


def get_user_by_name(client, user_name, headers=None):
    """Get user by username"""
    response = client.get(url=f"/api/v1/userservice/users/{user_name}", headers=headers,
                         name=utils.get_name_suffix("get_user_by_name"))
    return utils.get_json_from_response(response)


def get_user_by_id(client, user_id, headers=None):
    """Get user by ID"""
    response = client.get(url=f"/api/v1/userservice/users/id/{user_id}", headers=headers,
                         name=utils.get_name_suffix("get_user_by_id"))
    return utils.get_json_from_response(response)


def register_user(client, user_name, password, email=None, document_type=1, document_num=None, headers=None):
    """Register a new user"""
    body = {
        "userName": user_name,
        "password": password,
        "email": email or f"{user_name}@example.com",
        "documentType": document_type,
        "documentNum": document_num or utils.get_random_string(10)
    }
    response = client.post(url="/api/v1/userservice/users/register", json=body, context=body, headers=headers,
                          name=utils.get_name_suffix("register_user"))
    return utils.get_json_from_response(response)


def update_user(client, user_id, user_name, password, headers=None):
    """Update user information"""
    body = {"userId": user_id, "userName": user_name, "password": password}
    response = client.put(url="/api/v1/userservice/users", json=body, context=body, headers=headers,
                         name=utils.get_name_suffix("update_user"))
    return utils.get_json_from_response(response)


def delete_user(client, user_id, headers=None):
    """Delete user by ID"""
    response = client.delete(url=f"/api/v1/userservice/users/{user_id}", headers=headers,
                            name=utils.get_name_suffix("delete_user"))
    return utils.get_json_from_response(response)


# ============================================================================
# VERIFICATION CODE SERVICE - Code generation and verification
# ============================================================================

def generate_verification_code(client, headers=None):
    """Generate verification code"""
    response = client.get(url="/api/v1/verifycode/generate", headers=headers,
                         name=utils.get_name_suffix("generate_verification_code"))
    return utils.get_json_from_response(response)


def verify_code(client, verify_code, headers=None):
    """Verify verification code"""
    response = client.get(url=f"/api/v1/verifycode/verify/{verify_code}", headers=headers,
                         name=utils.get_name_suffix("verify_code"))
    return utils.get_json_from_response(response)


# ============================================================================
# AVATAR SERVICE - Avatar upload and face detection
# ============================================================================

def upload_avatar(client, image_base64, headers=None):
    """Upload and process avatar image with face detection"""
    body = {"img": image_base64}
    response = client.post(url="/api/v1/avatar", json=body, context=body, headers=headers,
                          name=utils.get_name_suffix("upload_avatar"))
    return utils.get_json_from_response(response)


# ============================================================================
# CONSIGN PRICE SERVICE - Consignment pricing
# ============================================================================

def get_consign_price(client, weight, is_within_region, headers=None):
    """Get consignment price by weight and region"""
    response = client.get(url=f"/api/v1/consignpriceservice/consignprice/{weight}/{is_within_region}",
                         headers=headers,
                         name=utils.get_name_suffix("get_consign_price"))
    return utils.get_json_from_response(response)


def get_consign_price_info(client, headers=None):
    """Get all consignment price information"""
    response = client.get(url="/api/v1/consignpriceservice/consignprice/price",
                         headers=headers,
                         name=utils.get_name_suffix("get_consign_price_info"))
    return utils.get_json_from_response(response)


def get_consign_price_config(client, headers=None):
    """Get consignment price configuration"""
    response = client.get(url="/api/v1/consignpriceservice/consignprice/config",
                         headers=headers,
                         name=utils.get_name_suffix("get_consign_price_config"))
    return utils.get_json_from_response(response)


def modify_consign_price_config(client, price_config, headers=None):
    """Modify consignment price configuration"""
    response = client.post(url="/api/v1/consignpriceservice/consignprice",
                          json=price_config, context=price_config, headers=headers,
                          name=utils.get_name_suffix("modify_consign_price_config"))
    return utils.get_json_from_response(response)


# ============================================================================
# CONSIGN SERVICE - Consignment management
# ============================================================================

def create_consign(client, consign_data, headers=None):
    """Create new consignment"""
    response = client.post(url="/api/v1/consignservice/consigns",
                          json=consign_data, context=consign_data, headers=headers,
                          name=utils.get_name_suffix("create_consign"))
    return utils.get_json_from_response(response)


def update_consign(client, consign_data, headers=None):
    """Update consignment"""
    response = client.put(url="/api/v1/consignservice/consigns",
                         json=consign_data, context=consign_data, headers=headers,
                         name=utils.get_name_suffix("update_consign"))
    return utils.get_json_from_response(response)


def get_consign_by_account(client, account_id, headers=None):
    """Get consignments by account ID"""
    response = client.get(url=f"/api/v1/consignservice/consigns/account/{account_id}",
                         headers=headers,
                         name=utils.get_name_suffix("get_consign_by_account"))
    return utils.get_json_from_response(response)


def get_consign_by_order(client, order_id, headers=None):
    """Get consignment by order ID"""
    response = client.get(url=f"/api/v1/consignservice/consigns/order/{order_id}",
                         headers=headers,
                         name=utils.get_name_suffix("get_consign_by_order"))
    return utils.get_json_from_response(response)


def get_consign_by_consignee(client, consignee_name, headers=None):
    """Get consignment by consignee name"""
    response = client.get(url=f"/api/v1/consignservice/consigns/{consignee_name}",
                         headers=headers,
                         name=utils.get_name_suffix("get_consign_by_consignee"))
    return utils.get_json_from_response(response)


def collect_ticket(client, headers, order):
    order_id = order["id"]
    response = client.get(url=f"/api/v1/executeservice/execute/collected/{order_id}",
                          name=utils.get_name_suffix("collect_ticket"), headers=headers)
    return utils.get_json_from_response(response)


def execute_ticket(client, headers, order):
    order_id = order["id"]
    response = client.get(url=f"/api/v1/executeservice/execute/execute/{order_id}",
                          name=utils.get_name_suffix("execute_ticket"), headers=headers)
    return utils.get_json_from_response(response)


def get_voucher(client, headers, order_id, hs=True):
    """Get voucher for an order. Works with any valid order (not just EXECUTED)."""
    body = {"orderId": order_id, "type": 1 if hs else 0}
    response = client.post(url="/getVoucher", json=body, headers=headers, context=body,
                          name=utils.get_name_suffix("get_voucher"))
    return utils.get_json_from_response(response)

# def search_departure(client, from_station="Shang Hai", to_station="Su Zhou", hs=True):
#     if hs:
#         url = "/api/v1/travelservice/trips/left"
#     else:
#         url = "/api/v1/travel2service/trips/left"
#     departure_date = utils.get_departure_date()
#
#     body = {"startingPlace": from_station, "endPlace": to_station, "departureTime": departure_date}
#     response = client.post(url="/api/v1/travelservice/trips/left", json=body, catch_response=True,
#                            name=utils.get_name_suffix("get_trip_information"))
#     return utils.get_json_from_response(response)
#
#
# def search_return(client, from_station="Su Zhou", to_station="Shang Hai"):
#     departure_date = utils.get_departure_date()
#
#     body = {"startingPlace": from_station, "endPlace": to_station, "departureTime": departure_date}
#     response = client.post(url="/api/v1/travel2service/trips/left", json=body, catch_response=True,
#                            name=utils.get_name_suffix("get_trip_information"))
#     return utils.get_json_from_response(response)
