#!/usr/bin/python
#
# Train-Ticket Load Generator
# Simulates realistic user behavior for the Train-Ticket booking system

import random
import json
from locust import HttpUser, TaskSet, between, task

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
# Only fdse_microservice exists in the database by default
test_users = [
    {'username': 'fdse_microservice', 'password': '111111'}
]


class UserBehavior(TaskSet):

    def on_start(self):
        """Called when a simulated user starts"""
        # Always login to ensure authenticated endpoints can be tested
        self.login()

    def login(self):
        """Login to the system"""
        user = random.choice(test_users)
        response = self.client.post("/api/v1/users/login",
            json={
                "username": user['username'],
                "password": user['password'],
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

    @task(20)
    def search_tickets(self):
        """Search for train tickets - most common action"""
        start_station = random.choice(stations)
        end_station = random.choice([s for s in stations if s != start_station])

        # Query trips between stations
        self.client.post("/api/v1/travelservice/trips/left",
            json={
                "startingPlace": start_station,
                "endPlace": end_station,
                "departureTime": "2024-12-25"
            },
            name="Search Tickets")

    @task(10)
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

    @task(3)
    def view_contacts(self):
        """View saved contacts"""
        if hasattr(self, 'token'):
            self.client.get("/api/v1/contactservice/contacts",
                headers={"Authorization": f"Bearer {self.token}"},
                name="View Contacts")

    @task(2)
    def view_orders(self):
        """View user's orders"""
        if hasattr(self, 'token'):
            self.client.post("/api/v1/orderservice/order/refresh",
                json={
                    "loginId": test_users[0]['username'],
                    "enableStateQuery": False,
                    "enableTravelDateQuery": False,
                    "enableBoughtDateQuery": False
                },
                headers={"Authorization": f"Bearer {self.token}"},
                name="View Orders")

    @task(5)
    def check_station_info(self):
        """Check if station exists"""
        station = random.choice(stations)
        self.client.get(f"/api/v1/stationservice/stations/id/{station}",
            name="Check Station")

    @task(3)
    def query_train_info(self):
        """Query train information"""
        train_id = f"{random.choice(train_types)}{random.randint(1000, 9999)}"
        self.client.get(f"/api/v1/trainservice/trains/{train_id}",
            name="Query Train Info")

    @task(2)
    def check_route_info(self):
        """Check route information"""
        self.client.post("/api/v1/configservice/configs",
            json={"name": "DirectTicketAllocationProportion"},
            name="Check Config")


class TrainTicketUser(HttpUser):
    """
    Simulates a user on the Train-Ticket booking system

    Configuration:
    - wait_time: Random wait between 1-10 seconds (simulates thinking time)
    - tasks: Weighted tasks representing user behavior

    Task weights represent relative frequency:
    - search_tickets (20): Most users search for tickets
    - query_high_speed_tickets (10): High-speed train queries
    - check_station_info (5): Station validation
    - Other tasks (2-3): Browsing, checking info, contacts, orders
    """
    tasks = [UserBehavior]
    wait_time = between(1, 10)  # Wait 1-10 seconds between actions
