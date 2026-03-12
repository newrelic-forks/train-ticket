"""
Train-Ticket Load Generator Configuration

Configuration parameters for load testing including user behavior patterns,
resource constraints, routes, and system settings.
"""

# ============================================================================
# LOCUST STATISTICS CONFIGURATION
# ============================================================================

# Add "_spawning" suffix to request names during user spawn phase
# Useful for separating warmup metrics from steady-state performance
ADD_SPAWNING_SUFFIX = False

# Group statistics into 30-second chunks for time-series analysis
LOG_STATISTICS_IN_HALF_MINUTE_CHUNKS = False

# Response time percentiles for tail latency analysis
PERCENTILES_TO_REPORT = [0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80,
                         0.81, 0.82, 0.83, 0.84, 0.85, 0.86, 0.87, 0.88, 0.888, 0.89, 0.90, 0.91, 0.92, 0.93, 0.94,
                         0.95, 0.96, 0.97, 0.98, 0.99, 0.9973, 0.999, 0.9999, 1.0]

# ============================================================================
# THINK TIME CONFIGURATION (Simulates realistic user behavior)
# ============================================================================

# Automatic actions: Fast internal processing delays (1-200ms)
TT_AUTOMATIC_MIN = 0.001  # 1 millisecond
TT_AUTOMATIC_MAX = 0.200  # 200 milliseconds

# User think time: Human decision-making delays (1-5 seconds)
TT_USER_MIN = 1  # 1 second
TT_USER_MAX = 5  # 5 seconds

# ============================================================================
# CONNECTION CONFIGURATION
# ============================================================================

# Network and connection timeouts in seconds
# Set high (120s) to handle slow microservice responses and prevent false failures
NETWORK_TIMEOUT = 120.0     # Time to wait for network response
CONNECTION_TIMEOUT = 120.0  # Time to establish connection

# ============================================================================
# ACTOR DISTRIBUTION (User Type Weights)
# ============================================================================
# Simulates realistic mix of external browsers, logged-in users, and admins
# Total must equal 100 for proper distribution

EXTERNAL_PERCENTAGE = 60  # Anonymous users browsing without login (60%)
LOGGED_PERCENTAGE = 35    # Authenticated users booking tickets (35%)
ADMIN_PERCENTAGE = 5      # System administrators managing data (5%)

# ============================================================================
# TRAIN TYPE PREFERENCES
# ============================================================================
# Percentage split between high-speed (G/D) and regular (K/T/Z) trains
# MODIFIED: Swapped percentages because regular train routes have limited data in database
# High-speed routes (nanjing/shanghai/suzhou/wuxi/zhenjiang) have reliable data

HS_PERCENTAGE = 80     # High-speed trains (G-series, D-series) - 80% (WORKING ROUTES)
OTHER_PERCENTAGE = 20  # Regular trains (K, T, Z series) - 20% (LIMITED DATA)

# ============================================================================
# USER BEHAVIOR PROBABILITIES
# ============================================================================

# Probability weights for Locust task selection
# Higher value = more likely to execute that behavior vs resetting session
BEHAVIOR_PROBABILITY = 40  # Continue with normal behaviors (search, book, etc.)
RESET_PROBABILITY = 20     # Clear session and start fresh (simulates new user)

# ============================================================================
# REQUEST LOGGING CONFIGURATION
# ============================================================================

# Individual request logging (disabled for Kubernetes deployment)
# When enabled, writes CSV log of every request (high I/O overhead)
# Recommendation: Use Locust's built-in metrics or Prometheus instead
LOG_ALL_REQUESTS = False

# How often to flush log buffer to disk (seconds)
LOG_FLUSH_INTERVAL = 5

# ============================================================================
# AUTO-STOP CONFIGURATION
# ============================================================================

# Automatically exit after N requests (disabled for continuous load testing)
# Useful for batch testing or CI/CD pipelines
STOP_ON_REQUEST_COUNT = False
REQUEST_NUMBER_TO_STOP = 200  # Number of requests before auto-stop

# ============================================================================
# TRAIN TYPE IDENTIFIERS
# ============================================================================
# Maps to trainTypeId in the backend database

# High-speed train types (faster, more expensive, shorter routes)
HS_TRAIN_TYPE_ID = ["GaoTieOne", "DongCheOne"]  # G-series and D-series trains

# Regular train types (slower, cheaper, longer routes)
OTHER_TRAIN_TYPE_ID = ["ZhiDa", "TeKuai", "KuaiSu"]  # Z, T, K series trains

# ============================================================================
# PREDEFINED TRAVEL ROUTES
# ============================================================================
# Realistic station sequences based on actual Chinese railway lines
# Routes are directional: stations appear in travel order

# High-speed routes: MUST match exact route start/end in database
# Based on actual trips in database (G1234, G1235, G1236, G1237, D1345)
HS_TRIP_LIST = [
    ["nanjing", "shanghai"],  # G1234, G1235, G1236 routes (all start nanjing, end shanghai)
    ["suzhou", "shanghai"],    # G1237 route
    ["shanghai", "suzhou"],    # D1345 route
]

# Regular train routes: Longer distances, cross-regional travel
OTHER_TRIP_LIST = [
    ["shanghai", "nanjing", "shijiazhuang", "taiyuan"],      # East to North route
    ["nanjing", "xuzhou", "jinan", "beijing"],               # Nanjing-Beijing line
    ["taiyuan", "shijiazhuang", "nanjing", "shanghai"],      # North to East route
    ["shanghai", "taiyuan"],                                  # Direct long-distance
    ["shanghaihongqiao", "jiaxingnan", "hangzhou"],          # Shanghai-Hangzhou line
]

# ============================================================================
# TICKET STATUS CODES
# ============================================================================
# Represents ticket lifecycle from booking to execution
# These values match the backend order status enum

TICKET_STATUS_BOOKED = 0     # Order created, awaiting payment
TICKET_STATUS_PAID = 1       # Payment completed, ticket issued
TICKET_STATUS_COLLECTED = 2  # Ticket physically collected or e-ticket activated
TICKET_STATUS_CANCELLED = 4  # Order cancelled, refund processed
TICKET_STATUS_EXECUTED = 6   # Passenger boarded train, ticket used

# ============================================================================
# INSURANCE OPTIONS
# ============================================================================
# Travel insurance types available during booking
# "0" = No insurance, "1" = Basic travel insurance
ASSURANCE_TYPES = ["0", "1"]
