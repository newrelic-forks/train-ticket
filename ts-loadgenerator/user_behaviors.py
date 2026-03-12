"""
User Behavior Functions for Train-Ticket Load Testing

Implements behavior patterns for three user personas: External (anonymous),
Logged (authenticated), and Admin users. Each function represents complete
user journeys with realistic timing and error handling.
"""
import random
import os
import api_user
import api_admin
import utils
import config


# ============================================================================
# LOGGED USER BEHAVIORS
# ============================================================================

def browse_infrastructure(l):
    """Browse system infrastructure: stations, trains, routes, and pricing information."""
    # Support both authenticated (logged) and anonymous (external) users
    headers = getattr(l.user, 'headers', None)

    # Explore station network
    l.client.get("/api/v1/stationservice/stations",
                headers=headers,
                name=utils.get_name_suffix("get_stations"))
    utils.sleep_user()  # User reviews station list

    # Browse available train types
    l.client.get("/api/v1/trainservice/trains",
                headers=headers,
                name=utils.get_name_suffix("get_trains"))
    utils.sleep_user()  # User compares train features

    # Explore route connections
    l.client.get("/api/v1/routeservice/routes",
                headers=headers,
                name=utils.get_name_suffix("get_routes"))
    utils.sleep_user()  # User studies route network

    # Review pricing structure
    l.client.get("/api/v1/priceservice/prices",
                headers=headers,
                name=utils.get_name_suffix("get_prices"))
    utils.sleep_user()  # User analyzes pricing options


def search_trips(l):
    """Search for trips using user's train type preference with authenticated context."""
    start, end = utils.get_random_start_end_stations(hs=l.user.hs)
    api_user.search_travel(l.client, start, end, hs=l.user.hs, headers=l.user.headers)
    utils.sleep_user()  # User reviews personalized search results


def book_ticket_complete_flow(l):
    """
    Complete end-to-end ticket booking workflow with payment.
    Includes contact retrieval, trip search, food/insurance options, reservation, and payment.
    Primary revenue-generating behavior using user preferences and service routing.
    """
    departure_date = utils.get_departure_date()

    # Step 1: Retrieve user contact information for booking
    l.client.get(f"/api/v1/contactservice/contacts/account/{l.user.user_id}",
                headers=l.user.headers,
                name=utils.get_name_suffix("query_contacts"))
    utils.sleep_automatic()  # System loads contact data

    # Step 2: Search for available trips
    search_trips(l)

    # Step 3: Check available food/meal options for the route
    l.client.get(f"/api/v1/foodservice/foods/{departure_date}/shanghai/suzhou/G1234",
                headers=l.user.headers,
                name=utils.get_name_suffix("get_food_types"))
    utils.sleep_automatic()  # System loads meal options

    # Step 4: Review insurance/assurance options
    l.client.get("/api/v1/assuranceservice/assurances/types",
                headers=l.user.headers,
                name=utils.get_name_suffix("get_assurance_types"))
    utils.sleep_automatic()  # System loads insurance options

    # Step 5: Create ticket reservation with all options
    body = {
        "accountId": l.user.user_id,
        "contactsId": utils.get_random_string(10),  # Random contact for testing
        "tripId": "G1234" if l.user.hs else "Z1234",  # Train type based on preference
        "seatType": "2" if l.user.hs else "3",  # Seat class based on train type
        "date": departure_date,
        "from": "shanghai",
        "to": "suzhou" if l.user.hs else "beijing",  # Route based on train type
        "assurance": random.choice(config.ASSURANCE_TYPES),  # Random insurance choice
        "foodType": 1,
        "foodName": "Bone Soup",  # Standard meal option
        "foodPrice": 2.5,
        "stationName": "",  # Optional pickup location
        "storeName": ""     # Optional store/vendor
    }

    # Route to appropriate service based on train type
    if l.user.hs:
        l.client.post("/api/v1/preserveservice/preserve",
                     json=body,
                     headers=l.user.headers,
                     context=body,
                     name=utils.get_name_suffix("preserve_ticket_hs"))
    else:
        l.client.post("/api/v1/preserveotherservice/preserveOther",
                     json=body,
                     headers=l.user.headers,
                     context=body,
                     name=utils.get_name_suffix("preserve_ticket_other"))
    utils.sleep_user()

    # Pay
    body = {
        "orderId": utils.get_random_string(10),
        "tripId": "G1234" if l.user.hs else "Z1234"
    }
    l.client.post("/api/v1/inside_pay_service/inside_payment",
                 json=body,
                 headers=l.user.headers,
                 context=body,
                 name=utils.get_name_suffix("pay_order"))
    utils.sleep_user()


def manage_orders(l):
    """View user orders and attempt cancellation with graceful error handling."""
    api_user.get_all_orders(l.client, l.user.user_id, l.user.hs, l.user.headers)
    utils.sleep_user()

    try:
        api_user.cancel(l.client, l.user.user_id, l.user.hs, l.user.headers)
    except:
        pass
    utils.sleep_user()


def collect_and_execute_ticket(l):
    """
    Complete ticket collection and execution workflow.
    Collects paid tickets (status 1→2) and executes collected tickets (status 2→completed).
    """
    orders_hs = api_user.get_all_orders(l.client, l.user.user_id, hs=True, headers=l.user.headers)
    orders_other = api_user.get_all_orders(l.client, l.user.user_id, hs=False, headers=l.user.headers)
    utils.sleep_user()

    orders = orders_hs + orders_other
    for o in orders:
        if o["status"] == 1:
            api_user.collect_ticket(l.client, l.user.headers, o)
            break
    utils.sleep_user()

    orders_hs = api_user.get_all_orders(l.client, l.user.user_id, hs=True, headers=l.user.headers)
    orders_other = api_user.get_all_orders(l.client, l.user.user_id, hs=False, headers=l.user.headers)
    utils.sleep_user()

    orders = orders_hs + orders_other
    for o in orders:
        if o["status"] == 2:
            api_user.execute_ticket(l.client, l.user.headers, o)
            break
    utils.sleep_user()


def manage_consignment(l):
    """
    Check consignment pricing and user shipment history.
    Queries pricing by weight/region and retrieves account consignment records.
    """
    # Get consignment price by weight and region
    weight = random.uniform(5.0, 20.0)
    is_within_region = random.choice(["true", "false"])
    l.client.get(f"/api/v1/consignpriceservice/consignprice/{weight}/{is_within_region}",
                headers=l.user.headers,
                name=utils.get_name_suffix("get_consign_price"))
    utils.sleep_user()

    # Get consignment records for account
    l.client.get(f"/api/v1/consignservice/consigns/account/{l.user.user_id}",
                headers=l.user.headers,
                name=utils.get_name_suffix("get_consign_records"))
    utils.sleep_user()


def rebook_ticket(l):
    """
    Rebook ticket to different trip with new travel details.
    Changes from old trip to new trip with seat and date preferences.
    """
    body = {
        "oldTripId": "G1234",
        "tripId": "G1235",
        "seatType": 2,
        "date": utils.get_departure_date(),
        "orderId": utils.get_random_string(10)
    }
    l.client.post("/api/v1/rebookservice/rebook",
                 json=body,
                 headers=l.user.headers,
                 context=body,
                 name=utils.get_name_suffix("rebook_ticket"))
    utils.sleep_user()


def get_travel_plan(l):
    """Get cost-optimized travel plan using user's train type preference."""
    start, end = utils.get_random_start_end_stations(l.user.hs)
    api_user.get_travel_plan(l.client, start, end)
    utils.sleep_user()


def get_voucher_for_order(l):
    """Get voucher/receipt for paid orders"""
    # Get orders (both HS and other)
    try:
        orders_hs = api_user.get_all_orders(l.client, l.user.user_id, hs=True, headers=l.user.headers)
        orders_other = api_user.get_all_orders(l.client, l.user.user_id, hs=False, headers=l.user.headers)
        utils.sleep_user()

        orders = orders_hs + orders_other

        # Try to get voucher for any paid, collected, or executed order
        found_valid_order = False
        for o in orders:
            if o.get("status") in [1, 2, 6]:  # PAID, COLLECTED, or EXECUTED
                order_id = o.get("id")
                if order_id:
                    # Determine if it's HS or OTHER based on trip ID
                    trip_id = o.get("trainNumber", "")
                    hs = trip_id.startswith("G") or trip_id.startswith("D")
                    try:
                        api_user.get_voucher(l.client, l.user.headers, order_id, hs=hs)
                        found_valid_order = True
                        break
                    except:
                        pass  # Try next order if this one fails

        # If no valid orders found, don't fail - just skip silently
        if not found_valid_order:
            pass  # No valid orders to get voucher for, that's okay
    except:
        pass  # Silently handle any errors in order retrieval

    utils.sleep_user()


def browse_basic_info(l):
    """Browse basic travel information: stations and routes"""
    # Query station information
    stations = ["shanghai", "nanjing", "suzhou", "beijing"]
    station = random.choice(stations)
    api_user.query_station_by_name(l.client, station, headers=getattr(l.user, 'headers', None))
    utils.sleep_user()

    # Query route for a trip
    trip_id = "G1234" if l.user.hs else "Z1234"
    start, end = utils.get_random_start_end_stations(l.user.hs)
    api_user.query_basic_travel(l.client, trip_id, start, end, headers=getattr(l.user, 'headers', None))
    utils.sleep_user()


def manage_user_profile(l):
    """View and update user profile information with randomized username and password."""
    # Get user information by ID
    api_user.get_user_by_id(l.client, l.user.user_id, headers=l.user.headers)
    utils.sleep_user()

    # Update user information
    api_user.update_user(l.client, l.user.user_id, f"user_{utils.get_random_string(5)}",
                        "newpassword123", headers=l.user.headers)
    utils.sleep_user()


def upload_user_avatar(l):
    """
    Upload user avatar with cached test image data and fallback handling.
    Uses base64 encoding with face detection processing.
    """
    # Load real test image with face (cached in function attribute)
    if not hasattr(upload_user_avatar, '_test_image_b64'):
        avatar_file = os.path.join(os.path.dirname(__file__), 'test_avatar.b64')
        try:
            with open(avatar_file, 'r') as f:
                upload_user_avatar._test_image_b64 = f.read().strip()
        except FileNotFoundError:
            # Fallback to placeholder if file not found
            upload_user_avatar._test_image_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="

    api_user.upload_avatar(l.client, upload_user_avatar._test_image_b64, headers=l.user.headers)
    utils.sleep_user()


# ============================================================================
# EXTERNAL USER BEHAVIORS (Anonymous)
# ============================================================================

def browse_home(l):
    """Visit application homepage."""
    api_user.home(l.client)
    utils.sleep_user()


def view_login_page(l):
    """Visit client login page"""
    api_user.client_login_page(l.client)
    utils.sleep_automatic()


def search_roundtrip(l):
    """Search for roundtrip tickets"""
    utils.search_travels_roudtrip(l.client, l.user.hs)


def search_oneway(l):
    """Search for one-way tickets"""
    utils.search_travels_oneway(l.client, l.user.hs)


def register_with_verification(l):
    """
    Register new user with verification code validation.
    Generates verification code and creates account with unique username and test password.
    """
    # Generate verification code
    api_user.generate_verification_code(l.client)
    utils.sleep_automatic()

    # Register new user
    user_name = f"testuser_{utils.get_random_string(8)}"
    password = "testpass123"
    api_user.register_user(l.client, user_name, password)
    utils.sleep_user()


# ============================================================================
# ADMIN BEHAVIORS
# ============================================================================

def admin_manage_travels(l):
    """
    Manage travel routes by viewing routes/travels and randomly creating or updating routes.
    Uses real route IDs and maintains data integrity with fallback handling.
    """
    # Step 1: Load current route network for administrative context
    routes_response = api_admin.get_all_routes(l.client, headers=l.user.headers)
    routes = routes_response.get("data", []) if routes_response else []
    utils.sleep_user()  # Admin reviews route network structure

    # Step 2: Load current travel inventory for management decisions
    travels_response = api_admin.get_all_travels(l.client, headers=l.user.headers)
    travels = travels_response.get("data", []) if travels_response else []
    utils.sleep_user()  # Admin analyzes current travel offerings

    # Step 3: Perform administrative action (create or update)
    if random.choice([True, False]):
        # Create new travel route (50% probability)
        # Always attempt for consistent load testing metrics
        route = random.choice(routes) if routes else None
        api_admin.create_travel(l.client, route, hs=random.choice([True, False]),
                               headers=l.user.headers)
    else:
        # Update existing travel route (50% probability)
        if travels:
            travel = random.choice(travels)
            api_admin.update_travel(l.client, travel, headers=l.user.headers)
    utils.sleep_user()  # Admin reviews operation results


def admin_manage_orders(l):
    """View all orders and randomly update existing order or create new test order."""
    orders = api_admin.get_all_orders(l.client, headers=l.user.headers)
    utils.sleep_user()

    if random.choice([True, False]) and orders and 'data' in orders and orders['data']:
        order = random.choice(orders['data'])
        api_admin.update_order(l.client, order, headers=l.user.headers)
    else:
        api_admin.create_order(l.client, hs=random.choice([True, False]), headers=l.user.headers)
    utils.sleep_user()


def admin_manage_pricing(l):
    """View pricing configurations and modify random price with rate adjustments."""
    prices = api_admin.get_all_prices(l.client, headers=l.user.headers)
    utils.sleep_user()

    if prices and 'data' in prices and prices['data']:
        price = random.choice(prices['data'])
        api_admin.modify_price(l.client, headers=l.user.headers, price=price)
        utils.sleep_user()


def admin_manage_contacts(l):
    """View all contacts and modify random contact for data maintenance."""
    contacts = api_admin.get_all_contacts(l.client, headers=l.user.headers)
    utils.sleep_user()

    if contacts and 'data' in contacts and contacts['data']:
        contact = random.choice(contacts['data'])
        api_admin.modify_contact(l.client, headers=l.user.headers, contact=contact)
        utils.sleep_user()


def admin_manage_users(l):
    """View all users and create new randomized user account for testing."""
    api_admin.get_all_users(l.client, l.user.headers)
    utils.sleep_user()

    api_admin.create_random_user(l.client, l.user.headers)
    utils.sleep_user()


def admin_delete_travels(l):
    """
    View travels and safely delete random travel with ID constraints.
    Only deletes trips with numbers >= 2000 to protect production data.
    """
    travels_response = api_admin.get_all_travels(l.client, headers=l.user.headers)
    travels = travels_response.get("data", []) if travels_response else []
    utils.sleep_user()

    if travels:
        # Delete a random travel (only deletes trips with number >= 2000)
        api_admin.delete_random_travel(l.client, travels, hs=random.choice([True, False]), headers=l.user.headers)
        utils.sleep_user()


def admin_delete_orders(l):
    """
    View orders and safely delete random order with safety constraints.
    Only deletes orders with train numbers >= 2000 to protect customer data.
    """
    orders = api_admin.get_all_orders(l.client, headers=l.user.headers)
    utils.sleep_user()

    if orders and 'data' in orders and orders['data']:
        # Delete a random order (only deletes orders with number >= 2000)
        api_admin.delete_random_order(l.client, orders, hs=random.choice([True, False]), headers=l.user.headers)
        utils.sleep_user()


def admin_browse_infrastructure(l):
    """Browse all infrastructure components: stations, trains, configs, contacts, and prices."""
    # View all stations
    api_admin.get_all_stations(l.client, headers=l.user.headers)
    utils.sleep_user()

    # View all trains
    api_admin.get_all_trains(l.client, headers=l.user.headers)
    utils.sleep_user()

    # View all configs
    api_admin.get_all_configs(l.client, headers=l.user.headers)
    utils.sleep_user()

    # View all contacts
    api_admin.get_all_contacts(l.client, headers=l.user.headers)
    utils.sleep_user()

    # View all prices
    api_admin.get_all_prices(l.client, headers=l.user.headers)
    utils.sleep_user()


def admin_manage_system_users(l):
    """
    Manage system users by viewing all users, querying specific user by ID, and updating user information.
    Includes error handling for empty user lists and data validation.
    """
    # Get all users
    users = api_user.get_all_users(l.client, headers=l.user.headers)
    utils.sleep_user()

    # Get specific user by ID (if users exist)
    if users and 'data' in users and users['data'] and len(users['data']) > 0:
        user = random.choice(users['data'])
        if 'userId' in user:
            api_user.get_user_by_id(l.client, user['userId'], headers=l.user.headers)
            utils.sleep_user()

            # Update user
            if 'userName' in user:
                api_user.update_user(l.client, user['userId'], user['userName'], "updated_pass", headers=l.user.headers)
                utils.sleep_user()
