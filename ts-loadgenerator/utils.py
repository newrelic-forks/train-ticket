"""
Utility Functions for Train-Ticket Load Testing

Provides common utilities including string generation, HTTP response parsing,
date calculations, route selection, sleep functions, and booking workflows
with retry logic for realistic load testing scenarios.
"""

import json
import random
import time

import api_user
import string
import api_admin
from datetime import datetime, timedelta
from locust import events
import config

# Global flag to track when Locust has finished spawning all users
spawning_complete = False


def get_random_string(length=10):
    """Generate random lowercase string of specified length for test data."""
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str


@events.spawning_complete.add_listener
def on_spawning_complete(user_count, **kwargs):
    """Event listener that sets global flag when all users are spawned."""
    global spawning_complete
    spawning_complete = True


def get_json_from_response(response):
    """Safely parse HTTP response to JSON, returns None on parsing errors."""
    try:
        response_as_text = response.content.decode('UTF-8')
        response_as_json = json.loads(response_as_text)
        return response_as_json
    except:
        # Return None for any parsing error (malformed JSON, encoding issues, etc.)
        return None


def next_weekday(d, weekday):
    """Calculate next occurrence of specified weekday (0=Monday, 6=Sunday)."""
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0:  # Target day has passed or is today
        days_ahead += 7  # Get next week's occurrence
    return d + timedelta(days_ahead)


def get_name_suffix(name):
    """
    Generate request names with optional spawning and timestamp suffixes.
    Adds "_spawning" during user spawn phase or "@timestamp" for time-series analysis.
    """
    global spawning_complete

    # Optional suffix to separate spawning phase metrics
    if config.ADD_SPAWNING_SUFFIX and not spawning_complete:
        name = name + "_spawning"

    # Optional timestamp for time-series analysis in 30-second chunks
    if config.LOG_STATISTICS_IN_HALF_MINUTE_CHUNKS:
        now = datetime.now()
        # Round to nearest 30-second boundary
        now = datetime(now.year, now.month, now.day, now.hour, now.minute,
                      0 if now.second < 30 else 30, 0)
        now_as_timestamp = int(now.timestamp())
        return f"{name}@{now_as_timestamp}"
    else:
        return name


def get_departure_date():
    """
    Get departure date for trip booking requests.
    Returns fixed date "2013-05-04" to match existing test data in database.
    """
    return "2013-05-04"

    # Original dynamic logic (commented out until trip dates are updated):
    # tomorrow = datetime.now() + timedelta(1)
    # next_monday = next_weekday(tomorrow, 0)
    # departure_date = next_monday.strftime("%Y-%m-%d")
    # return departure_date


def get_random_start_end_stations(hs=True):
    """
    Select random start and end stations from configured routes.
    Uses high-speed routes (HS) or regular train routes, ensuring proper station sequence.
    """
    if hs:
        route = random.choice(config.HS_TRIP_LIST)    # High-speed routes
    else:
        route = random.choice(config.OTHER_TRIP_LIST) # Regular train routes

    # Select start station (can't be the last station)
    index = random.randint(0, len(route) - 2)
    start = route[index]

    # Select end station (must be after start station)
    end = route[random.randint(index + 1, len(route) - 1)]

    return start, end


def sleep_user():
    """Simulate human thinking time (1-5 seconds) between major user actions."""
    time.sleep(random.uniform(config.TT_USER_MIN, config.TT_USER_MAX))


def sleep_automatic():
    """Simulate system processing time (1-200ms) for fast internal operations."""
    time.sleep(random.uniform(config.TT_AUTOMATIC_MIN, config.TT_AUTOMATIC_MAX))


def search_travels_roudtrip(client, hs):
    """
    Perform round-trip travel search for anonymous users.
    Searches outbound and return journeys with user thinking time between searches.
    """
    start, end = get_random_start_end_stations(hs=hs)
    sleep_user()  # User selects route
    a = api_user.search_travel(client, start, end, hs=hs, logged=False)
    sleep_user()  # User reviews outbound options
    b = api_user.search_travel(client, end, start, hs=hs, logged=False)


def search_travels_oneway(client, hs):
    """
    Perform one-way travel search for anonymous users.
    Single journey search with user planning time.
    """
    start, end = get_random_start_end_stations(hs=hs)
    sleep_user()  # User plans journey
    a = api_user.search_travel(client, start, end, hs=hs, logged=False)


def perform_login_user(client):
    """
    Complete user login workflow with realistic timing.
    Includes homepage visits, login page, authentication, and post-login homepage.
    Returns (user_id, headers) for authenticated session.
    """
    api_user.home(client)
    sleep_user()  # User browses homepage
    api_user.client_login_page(client)
    sleep_user()  # User fills login form
    user_id, token = api_user.login(client)
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json", "Accept": "application/json"}
    sleep_automatic()  # System processes authentication
    api_user.home(client)
    sleep_user()  # User reviews authenticated interface
    return user_id, headers


def perform_login_admin(client):
    """
    Complete admin login workflow with data preloading.
    Includes admin authentication and preloads order data for efficient operations.
    Returns (user_id, headers, orders) for authenticated admin session.
    """
    api_admin.home(client)
    sleep_user()  # Admin reviews interface
    user_id, token = api_admin.login(client)
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json", "Accept": "application/json"}
    sleep_automatic()  # System processes admin authentication
    api_admin.home(client, headers=headers)
    sleep_automatic()  # Admin interface loads
    orders = api_admin.get_all_orders(client, headers)
    sleep_user()  # Admin reviews dashboard and order data
    return user_id, headers, orders


def search_and_preserve_travel(client, user_id, headers, hs, start, end):
    """
    Complete search and booking workflow with retry logic and error handling.
    Searches for trips, handles multiple response formats, and completes booking and payment.
    Returns (start, end) if succeeded, (None, None) if failed.
    """
    flag = False  # Track if search found valid results

    # Retry search up to 4 times with route fallback
    for i in range(1, 5):
        a = api_user.search_travel(client, start, end, hs=hs, headers=headers)

        # Handle multiple API response formats with defensive programming
        data_array = None
        if a is None:
            # API returned None - continue to next attempt
            pass
        elif isinstance(a, dict) and "data" in a:
            # Standard response format: {"status": 1, "data": [...]}
            data_array = a["data"] if isinstance(a["data"], list) else None
        elif isinstance(a, list):
            # Direct list response format: [...]
            data_array = a
        else:
            # Unexpected response format - continue to next attempt
            pass

        # Retry with new route if no valid data found
        if data_array is None or len(data_array) == 0:
            start, end = get_random_start_end_stations(hs=hs)  # Try different route
        else:
            a = data_array  # Normalize to list format for consistent processing
            flag = True
            break

    # Process booking if search succeeded
    if flag:
        # At this point, 'a' is guaranteed to be a non-empty list
        if isinstance(a, list) and len(a) > 0:
            trip_data = a[0]  # Use first available trip

            if "tripId" in trip_data:
                # Handle both trip ID formats with robust parsing
                if isinstance(trip_data["tripId"], dict):
                    # Dict format: {"type": "G", "number": "1234"}
                    trip_id_a = f'{trip_data["tripId"]["type"]}{trip_data["tripId"]["number"]}'
                elif isinstance(trip_data["tripId"], str):
                    # String format: "G1234"
                    trip_id_a = trip_data["tripId"]
                else:
                    # Unexpected trip ID format
                    return None, None

                sleep_user()  # User reviews trip options and decides to book

                # Attempt booking with error handling
                try:
                    api_user.book(client, user_id, trip_id=trip_id_a, from_station=start,
                                  to_station=end, hs=hs, headers=headers)
                except Exception:
                    # Booking failed - return failure
                    return None, None

                sleep_user()  # User reviews booking confirmation and proceeds to payment

                # Attempt payment with graceful failure handling
                try:
                    api_user.pay(client, user_id, trip_id_a, hs=hs, headers=headers)
                except Exception:
                    # Payment failed but booking succeeded - partial success
                    # Return route info since booking reservation was created
                    return start, end

                # Full success - both booking and payment completed
                return start, end

    # Complete failure - no valid search results found after retries
    return None, None
