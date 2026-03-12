"""
Train-Ticket Load Generator - Main Locust Entry Point

Defines three user personas for load testing: External (60%), Logged (35%), and Admin (5%).
Simulates realistic user behavior with weighted tasks, authentication flows, and human timing.
"""

import random
import time
from locust import FastHttpUser, TaskSet, task, between, events
import locust.stats

import api_user
import api_admin
import utils
import config
import user_behaviors as ub

# Configure Locust to report detailed percentile metrics for tail latency analysis
locust.stats.PERCENTILES_TO_REPORT = config.PERCENTILES_TO_REPORT

# Global request counter for optional auto-stop functionality
count = 0

# Optional CSV logging for detailed request analysis (disabled in K8s for performance)
test_log = None
if config.LOG_ALL_REQUESTS:
    test_log = open('test_log.csv', 'w')
    test_log.write(f'request_type;name;response_time;error;start_time;url\n')

# Timer for periodic log buffer flushing
log_flush_timer = time.time()


@events.request.add_listener
def my_request_handler(request_type, name, response_time, response_length, response,
                       context, exception, start_time, url, **kwargs):
    """Global request event handler for optional CSV logging and auto-stop functionality."""
    global log_flush_timer

    # Optional CSV logging for detailed request analysis
    if config.LOG_ALL_REQUESTS:
        test_log.write(f'{request_type};{name};{response_time};{1 if exception else 0};{start_time};{url}\n')
        t = time.time()
        # Periodically flush log buffer to prevent data loss
        if t - log_flush_timer > config.LOG_FLUSH_INTERVAL:
            log_flush_timer = t
            test_log.flush()

    # Optional auto-stop functionality for batch testing
    if config.STOP_ON_REQUEST_COUNT:
        global count
        count += 1
        if count > config.REQUEST_NUMBER_TO_STOP:
            if test_log:
                test_log.flush()
            exit(0)


def choice_train_type() -> bool:
    """Select train type using weighted distribution: 80% high-speed, 20% regular trains."""
    return random.choices([True, False], weights=[config.HS_PERCENTAGE, config.OTHER_PERCENTAGE], k=1)[0]


# ============================================================================
# EXTERNAL USER (Anonymous browsing - 60%)
# ============================================================================

class ExternalBehavior(TaskSet):
    """Anonymous user behavior patterns for browsing, searching, and exploring without authentication."""

    def on_start(self):
        """Initialize anonymous user session with homepage visit."""
        ub.browse_home(self)

    # Weighted task distribution for anonymous user behaviors
    tasks = {
        ub.search_roundtrip: 10,          # 29% - Primary search activity
        ub.search_oneway: 10,             # 29% - Primary search activity
        ub.browse_infrastructure: 5,       # 14% - System exploration (stations, routes)
        ub.browse_basic_info: 3,          # 9%  - Information gathering
        ub.get_travel_plan: 3,            # 9%  - Trip planning functionality
        ub.browse_home: 2,                # 6%  - Return to homepage
        ub.view_login_page: 2,            # 6%  - Login consideration (conversion funnel)
        ub.register_with_verification: 1   # 3%  - Account creation (conversion)
    }


class External(FastHttpUser):
    """Anonymous user class (60% of traffic) for browsing and search without authentication."""
    wait_time = between(config.TT_USER_MIN, config.TT_USER_MAX)
    network_timeout = config.NETWORK_TIMEOUT
    connection_timeout = config.CONNECTION_TIMEOUT
    weight = config.EXTERNAL_PERCENTAGE
    tasks = [ExternalBehavior]

    def on_start(self):
        """Initialize user with train type preference (high-speed or regular)."""
        self.hs = choice_train_type()


# ============================================================================
# LOGGED USER (Authenticated booking - 35%)
# ============================================================================

class LoggedBehavior(TaskSet):
    """Authenticated user behavior patterns for booking, order management, and business operations."""

    def on_start(self):
        """Initialization - authentication handled by parent Logged user class."""
        pass

    # Weighted task distribution prioritizing business-critical operations
    tasks = {
        ub.book_ticket_complete_flow: 15,    # 27% - Core revenue-generating activity
        ub.search_trips: 10,                 # 18% - Authenticated trip search
        ub.browse_infrastructure: 8,         # 14% - System exploration with user context
        ub.manage_orders: 5,                 # 9%  - Order lifecycle management
        ub.browse_basic_info: 3,             # 5%  - Information viewing
        ub.collect_and_execute_ticket: 3,    # 5%  - Ticket fulfillment workflow
        ub.manage_consignment: 3,            # 5%  - Baggage and shipping services
        ub.manage_user_profile: 2,           # 4%  - Account management
        ub.rebook_ticket: 2,                 # 4%  - Change management
        ub.get_travel_plan: 2,               # 4%  - Trip planning with user context
        ub.get_voucher_for_order: 2,         # 4%  - Promotional features
        ub.upload_user_avatar: 1             # 2%  - Profile customization
    }


class Logged(FastHttpUser):
    """Authenticated user class (35% of traffic) performing booking and order management."""
    wait_time = between(config.TT_USER_MIN, config.TT_USER_MAX)
    network_timeout = config.NETWORK_TIMEOUT
    connection_timeout = config.CONNECTION_TIMEOUT
    weight = config.LOGGED_PERCENTAGE
    tasks = [LoggedBehavior]

    def on_start(self):
        """Authenticate user, establish session with Bearer token, and initialize preferences."""
        self.hs = choice_train_type()
        # Authenticate with default test user credentials
        self.user_id, token = api_user.login(self.client)
        # Set up authenticated session headers
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        # Simulate brief system processing delay
        utils.sleep_automatic()
        # Load authenticated homepage
        api_user.home(self.client)
        # Simulate user reading homepage content
        utils.sleep_user()


# ============================================================================
# ADMIN USER (System administration - 5%)
# ============================================================================

class AdminBehavior(TaskSet):
    """Administrative behavior patterns for system management and data administration."""

    def on_start(self):
        """Initialization - authentication and data retrieval handled by parent Admin class."""
        pass

    # Weighted task distribution for administrative operations
    tasks = {
        ub.admin_manage_travels: 10,         # 19% - Route and travel management
        ub.admin_manage_orders: 10,          # 19% - Order administration
        ub.admin_manage_pricing: 8,          # 15% - Revenue management
        ub.admin_manage_contacts: 8,         # 15% - Customer data management
        ub.admin_browse_infrastructure: 7,   # 13% - System monitoring and exploration
        ub.admin_manage_system_users: 6,     # 12% - System user administration
        ub.admin_manage_users: 5,            # 10% - Customer account management
        ub.admin_delete_travels: 2,          # 4%  - Travel route cleanup (destructive)
        ub.admin_delete_orders: 2            # 4%  - Order cleanup (destructive, ID >= 2000)
    }


class Admin(FastHttpUser):
    """Administrative user class (5% of traffic) for system management and maintenance operations."""
    wait_time = between(config.TT_USER_MIN, config.TT_USER_MAX)
    network_timeout = config.NETWORK_TIMEOUT
    connection_timeout = config.CONNECTION_TIMEOUT
    weight = config.ADMIN_PERCENTAGE
    tasks = [AdminBehavior]

    def on_start(self):
        """Authenticate admin user, establish session, and preload administrative data."""
        # Load admin interface homepage
        api_admin.home(self.client)
        utils.sleep_user()

        # Authenticate with admin credentials
        self.user_id, token = api_admin.login(self.client)

        # Set up admin session headers
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        utils.sleep_automatic()

        # Load authenticated admin homepage
        api_admin.home(self.client, headers=self.headers)
        utils.sleep_automatic()

        # Preload administrative data for efficient operations
        self.orders = api_admin.get_all_orders(self.client, self.headers)
        utils.sleep_user()
