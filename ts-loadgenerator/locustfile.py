#!/usr/bin/python
#
# Train-Ticket Load Generator
# Simulates realistic user behavior for the Train-Ticket booking system
#
# Based on golden-paths HTTP loadgenerator patterns:
# - @tag decorators for scenario filtering
# - Weighted task distribution matching real user behavior
# - Composite flows with data correlation
# - Unique user generation per instance

import random
import json
import uuid
from locust import HttpUser, TaskSet, between, task, tag

# Sample data for train ticket booking
stations = [
    'shanghai', 'beijing', 'nanjing', 'suzhou', 'taiyuan',
    'shijiazhuang', 'zhuzhou', 'jinan', 'xuzhou', 'jiaxing'
]

# Sample train types
train_types = ['G', 'D', 'K', 'T', 'Z']

# Sample seat types: 0=None, 1=Business, 2=First, 3=Second
seat_types = [2, 3]  # Most common: First and Second class

# Sample user credentials (for testing)
# Default user for authentication (exists in database)
DEFAULT_USER = {'username': 'fdse_microservice', 'password': '111111'}

def generate_unique_user():
    """Generate unique user ID per instance for realistic load testing"""
    return {
        'username': f"user_{uuid.uuid4().hex[:8]}",
        'password': '111111',
        'session_id': uuid.uuid4().hex
    }


class UserBehavior(TaskSet):

    def on_start(self):
        """Called when a simulated user starts"""
        # Generate unique session data per user instance (golden-paths pattern)
        self.user_data = DEFAULT_USER  # Use default user for now (valid credentials)
        self.session_id = uuid.uuid4().hex

        # Initialize order tracking for payment/cancellation flow
        self.pending_order_id = None
        self.completed_order_id = None
        self.last_trip_id = None
        self.last_route = None
        self.last_search_results = []

        # Always login to ensure authenticated endpoints can be tested
        self.login()

    def login(self):
        """Login to the system"""
        response = self.client.post("/api/v1/users/login",
            json={
                "username": self.user_data['username'],
                "password": self.user_data['password'],
                "verificationCode": "1234"
            },
            name="Login")

        # Store token if login successful
        if response.status_code == 200:
            try:
                result = response.json()
                if result.get('status') == 1 and result.get('data'):
                    data = result.get('data', {})
                    if 'token' in data:
                        self.token = data['token']
                        print(f"[DEBUG] Token acquired successfully: {self.token[:30]}...")
                    else:
                        print(f"[DEBUG] Login success but no token in response: {str(result)[:200]}")
                else:
                    print(f"[DEBUG] Login response status != 1: {result}")
            except Exception as e:
                print(f"[DEBUG] Login parse error: {e}, response: {response.text[:200]}")
        else:
            print(f"[DEBUG] Login failed with HTTP {response.status_code}")

    # ========================================================================
    # BROWSE PHASE: 60% of user behavior (golden-paths pattern)
    # ========================================================================

    @task(30)
    @tag('browse', 'critical', 'search')
    def search_tickets(self):
        """Search for train tickets - most common action"""
        start_station = random.choice(stations)
        end_station = random.choice([s for s in stations if s != start_station])

        # Store route for seat availability check
        self.last_route = {
            "startingPlace": start_station,
            "endPlace": end_station,
            "departureTime": "2024-12-25"
        }

        # Query trips between stations
        response = self.client.post("/api/v1/travelservice/trips/left",
            json=self.last_route,
            name="Search Tickets")

        # Store trip ID and search results for data correlation (golden-paths pattern)
        if response.status_code == 200:
            try:
                data = response.json()
                if data.get('status') == 1 and data.get('data'):
                    trips = data.get('data', [])
                    if trips:
                        self.last_search_results = trips
                        self.last_trip_id = trips[0].get('tripId')
            except:
                pass

    @task(15)
    @tag('browse', 'search')
    def query_high_speed_tickets(self):
        """Query high-speed train tickets (G/D trains)"""
        start_station = random.choice(stations)
        end_station = random.choice([s for s in stations if s != start_station])

        self.client.post("/api/v1/travel2service/trips/left",
            json={
                "startingPlace": start_station,
                "endPlace": end_station,
                "departureTime": "2024-12-25",
                "trainType": "G"
            },
            name="Query High-Speed Tickets")

    @task(5)
    @tag('browse', 'details')
    def check_station_info(self):
        """Check if station exists"""
        station = random.choice(stations)
        self.client.get(f"/api/v1/stationservice/stations/id/{station}",
            name="Check Station")

    @task(5)
    @tag('browse', 'details')
    def query_train_info(self):
        """Query train information - use correlated trip from search"""
        # Data correlation: query train from last search results (golden-paths pattern)
        if self.last_trip_id:
            train_id = self.last_trip_id
        else:
            train_id = f"{random.choice(train_types)}{random.randint(1000, 9999)}"

        self.client.get(f"/api/v1/trainservice/trains/{train_id}",
            name="Query Train Info")

    # ========================================================================
    # ACCOUNT MANAGEMENT: 15% of user behavior
    # ========================================================================

    @task(7)
    @tag('account', 'view')
    def view_contacts(self):
        """View saved contacts"""
        if hasattr(self, 'token'):
            self.client.get("/api/v1/contactservice/contacts",
                headers={"Authorization": f"Bearer {self.token}"},
                name="View Contacts")

    @task(8)
    @tag('account', 'view', 'critical')
    def view_orders(self):
        """View user's orders"""
        if hasattr(self, 'token'):
            self.client.post("/api/v1/orderservice/order/refresh",
                json={
                    "loginId": self.user_data['username'],
                    "enableStateQuery": False,
                    "enableTravelDateQuery": False,
                    "enableBoughtDateQuery": False
                },
                headers={"Authorization": f"Bearer {self.token}"},
                name="View Orders")

    @task(2)
    @tag('browse', 'config')
    def check_route_info(self):
        """Check route information"""
        self.client.post("/api/v1/configservice/configs",
            json={"name": "DirectTicketAllocationProportion"},
            name="Check Config")

    # ========================================================================
    # BOOKING FUNNEL: 25% of user behavior (golden-paths: 20% conversion)
    # Composite flow with data correlation
    # ========================================================================

    @task(12)
    @tag('booking', 'critical', 'journey')
    def complete_booking_journey(self):
        """
        COMPOSITE FLOW: Complete booking journey (golden-paths pattern)
        Search → Check Seat → Book → Pay
        Realistic 20% conversion rate with data correlation
        """
        if not hasattr(self, 'token'):
            return

        # Step 1: Search for tickets (if not already searched)
        if not self.last_route:
            start_station = random.choice(stations)
            end_station = random.choice([s for s in stations if s != start_station])
            self.last_route = {
                "startingPlace": start_station,
                "endPlace": end_station,
                "departureTime": "2024-12-25"
            }

            search_response = self.client.post("/api/v1/travelservice/trips/left",
                json=self.last_route,
                name="Booking Journey: Search")

            if search_response.status_code == 200:
                try:
                    data = search_response.json()
                    if data.get('status') == 1 and data.get('data'):
                        trips = data.get('data', [])
                        if trips:
                            self.last_search_results = trips
                            self.last_trip_id = trips[0].get('tripId')
                except:
                    return

        if not self.last_trip_id:
            return

        # Step 2: Check seat availability (data correlated from search)
        seat_response = self.client.post("/api/v1/seatservice/seats/left_tickets",
            json={
                "trainNumber": self.last_trip_id,
                "startStation": self.last_route.get("startingPlace", "shanghai"),
                "destStation": self.last_route.get("endPlace", "beijing"),
                "travelDate": "2024-12-25 00:00:00",
                "seatType": random.choice(seat_types),
                "totalNum": 100
            },
            name="Booking Journey: Check Seats")

        # Step 3: Book ticket
        book_response = self.client.post("/api/v1/preserveservice/preserve",
            json={
                "accountId": self.user_data['username'],
                "contactsId": "contact_" + str(random.randint(1, 100)),
                "tripId": self.last_trip_id,
                "seatType": random.choice(seat_types),
                "date": "2024-12-25",
                "from": self.last_route.get("startingPlace"),
                "to": self.last_route.get("endPlace")
            },
            headers={"Authorization": f"Bearer {self.token}"},
            name="Booking Journey: Book")

        # Store order ID for payment
        if book_response.status_code == 200:
            try:
                data = book_response.json()
                if data.get('status') == 1 and data.get('data'):
                    order_data = data.get('data', {})
                    order_id = order_data.get('orderId')

                    if order_id:
                        # Step 4: Pay immediately (golden-paths: tight coupling)
                        pay_response = self.client.post("/api/v1/inside_pay_service/inside_payment",
                            json={
                                "orderId": order_id,
                                "tripId": self.last_trip_id,
                                "paymentType": random.choice(["alipay", "wechat", "card"])
                            },
                            headers={"Authorization": f"Bearer {self.token}"},
                            name="Booking Journey: Pay")

                        if pay_response.status_code == 200:
                            try:
                                pay_data = pay_response.json()
                                if pay_data.get('status') == 1:
                                    self.completed_order_id = order_id
                            except:
                                pass
            except:
                pass

    @task(2)
    @tag('booking', 'check')
    def check_seat_availability_standalone(self):
        """Standalone seat check (not part of booking journey)"""
        if self.last_trip_id and self.last_route:
            self.client.post("/api/v1/seatservice/seats/left_tickets",
                json={
                    "trainNumber": self.last_trip_id,
                    "startStation": self.last_route.get("startingPlace", "shanghai"),
                    "destStation": self.last_route.get("endPlace", "beijing"),
                    "travelDate": "2024-12-25 00:00:00",
                    "seatType": random.choice(seat_types),
                    "totalNum": 100
                },
                name="Check Seat Availability")

    @task(1)
    @tag('booking', 'security')
    def security_check(self):
        """Security check for ID verification"""
        if hasattr(self, 'token'):
            self.client.post("/api/v1/securityservice/securityConfigs",
                json={
                    "accountId": self.user_data['username'],
                    "checkDate": "2024-12-25"
                },
                headers={"Authorization": f"Bearer {self.token}"},
                name="Security Check")

    @task(3)
    @tag('account', 'cancel', 'critical')
    def cancel_order(self):
        """Cancel completed order with refund"""
        if hasattr(self, 'token') and self.completed_order_id:
            response = self.client.get(
                f"/api/v1/cancelservice/cancel/{self.completed_order_id}/{self.user_data['username']}",
                headers={"Authorization": f"Bearer {self.token}"},
                name="Cancel Order")

            # Clear completed order after cancellation
            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get('status') == 1:
                        self.completed_order_id = None
                except:
                    pass


class TrainTicketUser(HttpUser):
    """
    Simulates realistic user behavior on Train-Ticket booking system

    Golden-Paths Pattern Implementation:
    =====================================
    - 60% Browse behavior (search, query, check details)
    - 20% Booking conversion (complete journey: search → seat → book → pay)
    - 15% Account management (view orders, contacts)
    - 5% Other (config checks, cancellations)

    Key Features:
    - @tag decorators for scenario filtering (--tags browse, --tags booking)
    - Data correlation: search results used in booking
    - Composite flows: complete_booking_journey follows realistic path
    - Unique session IDs per user instance
    - Think time: 1-10 seconds between actions

    Task Weight Distribution (Total: 100):
    - search_tickets (30): Primary browse behavior
    - query_high_speed_tickets (15): High-speed train queries
    - complete_booking_journey (12): COMPOSITE FLOW with 20% conversion
    - view_orders (8): Check booking history
    - view_contacts (7): Manage saved contacts
    - check_station_info, query_train_info (5 each): Detail checks
    - cancel_order (3): Post-purchase actions
    - check_seat_availability (2): Standalone seat check
    - security_check, check_route_info (1-2): Supporting endpoints

    Usage Examples:
    ---------------
    # Run all scenarios
    locust -f locustfile.py --host=http://gateway:18888

    # Run only browse scenarios
    locust -f locustfile.py --host=http://gateway:18888 --tags browse

    # Run critical paths only
    locust -f locustfile.py --host=http://gateway:18888 --tags critical

    # Run complete booking journey
    locust -f locustfile.py --host=http://gateway:18888 --tags journey
    """
    tasks = [UserBehavior]
    wait_time = between(1, 10)  # Realistic think time between actions
