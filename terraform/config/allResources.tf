terraform {
  required_providers {
    newrelic = {
      source  = "newrelic/newrelic"
    }
  }
}

provider "newrelic" {
  api_key = var.NEW_RELIC_API_KEY
  account_id = var.NEW_RELIC_ACCOUNT_ID
  region = var.NEW_RELIC_REGION
}

# Create Workload for Train-Ticket Microservices

resource "newrelic_workload" "train-ticket-workload" {
    name = "Train-Ticket Microservices Workload"
    account_id = var.NEW_RELIC_ACCOUNT_ID
    entity_search_query {
        query = "(name like '%store-ts-%' AND type = 'APPLICATION') OR (type = 'KUBERNETES_POD' AND `tags.namespace` = 'store') OR (type ='CONTAINER' AND `tags.namespace` = 'store') or type = 'KEY_TRANSACTION' or type = 'KUBERNETESCLUSTER' or (name like '%Train-Ticket%' AND type = 'SERVICE_LEVEL')"
    }

    scope_account_ids =  [var.NEW_RELIC_ACCOUNT_ID]
}

# Create Service Levels for Critical Services based on Latency & Error Rate

# Authentication Service
data "newrelic_entity" "ts-auth-service-app" {
  name = "store-ts-auth-service"
  domain = "APM"
  type = "APPLICATION"
}

resource "newrelic_service_level" "ts-auth-service-latency-sl" {
  guid = "${data.newrelic_entity.ts-auth-service-app.guid}"
    name = "Train-Ticket Auth Service Latency SL"
    description = "Proportion of requests that are served faster than a threshold."

    events {
        account_id = var.NEW_RELIC_ACCOUNT_ID
        valid_events {
            from = "Transaction"
            where = "appName = 'store-ts-auth-service' AND (transactionType='Web')"
        }
        good_events {
            from = "Transaction"
            where = "appName = 'store-ts-auth-service' AND (transactionType= 'Web') AND duration < 0.05"
        }
    }

    objective {
        target = 99.00
        time_window {
            rolling {
                count = 7
                unit = "DAY"
            }
        }
    }
}

resource "newrelic_service_level" "ts-auth-service-error-sl" {
  guid = "${data.newrelic_entity.ts-auth-service-app.guid}"
    name = "Train-Ticket Auth Service Error Rate SL"
    description = "Proportion of requests that are failing"

    events {
        account_id = var.NEW_RELIC_ACCOUNT_ID
        valid_events {
            from = "Transaction"
            where = "appName = 'store-ts-auth-service'"
        }
        bad_events {
            from = "TransactionError"
            where = "appName = 'store-ts-auth-service' AND error.expected IS FALSE"
        }
    }

    objective {
        target = 99.00
        time_window {
            rolling {
                count = 7
                unit = "DAY"
            }
        }
    }
}

# Order Service
data "newrelic_entity" "ts-order-service-app" {
  name = "store-ts-order-service"
  domain = "APM"
  type = "APPLICATION"
}

resource "newrelic_service_level" "ts-order-service-latency-sl" {
  guid = "${data.newrelic_entity.ts-order-service-app.guid}"
    name = "Train-Ticket Order Service Latency SL"
    description = "Proportion of requests that are served faster than a threshold."

    events {
        account_id = var.NEW_RELIC_ACCOUNT_ID
        valid_events {
            from = "Transaction"
            where = "appName = 'store-ts-order-service' AND (transactionType='Web')"
        }
        good_events {
            from = "Transaction"
            where = "appName = 'store-ts-order-service' AND (transactionType= 'Web') AND duration < 0.05"
        }
    }

    objective {
        target = 99.00
        time_window {
            rolling {
                count = 7
                unit = "DAY"
            }
        }
    }
}

resource "newrelic_service_level" "ts-order-service-error-sl" {
  guid = "${data.newrelic_entity.ts-order-service-app.guid}"
    name = "Train-Ticket Order Service Error Rate SL"
    description = "Proportion of requests that are failing"

    events {
        account_id = var.NEW_RELIC_ACCOUNT_ID
        valid_events {
            from = "Transaction"
            where = "appName = 'store-ts-order-service'"
        }
        bad_events {
            from = "TransactionError"
            where = "appName = 'store-ts-order-service' AND error.expected IS FALSE"
        }
    }

    objective {
        target = 99.00
        time_window {
            rolling {
                count = 7
                unit = "DAY"
            }
        }
    }
}

# Preserve Service
data "newrelic_entity" "ts-preserve-service-app" {
  name = "store-ts-preserve-service"
  domain = "APM"
  type = "APPLICATION"
}

resource "newrelic_service_level" "ts-preserve-service-latency-sl" {
  guid = "${data.newrelic_entity.ts-preserve-service-app.guid}"
    name = "Train-Ticket Preserve Service Latency SL"
    description = "Proportion of requests that are served faster than a threshold."

    events {
        account_id = var.NEW_RELIC_ACCOUNT_ID
        valid_events {
            from = "Transaction"
            where = "appName = 'store-ts-preserve-service' AND (transactionType='Web')"
        }
        good_events {
            from = "Transaction"
            where = "appName = 'store-ts-preserve-service' AND (transactionType= 'Web') AND duration < 0.05"
        }
    }

    objective {
        target = 99.00
        time_window {
            rolling {
                count = 7
                unit = "DAY"
            }
        }
    }
}

resource "newrelic_service_level" "ts-preserve-service-error-sl" {
  guid = "${data.newrelic_entity.ts-preserve-service-app.guid}"
    name = "Train-Ticket Preserve Service Error Rate SL"
    description = "Proportion of requests that are failing"

    events {
        account_id = var.NEW_RELIC_ACCOUNT_ID
        valid_events {
            from = "Transaction"
            where = "appName = 'store-ts-preserve-service'"
        }
        bad_events {
            from = "TransactionError"
            where = "appName = 'store-ts-preserve-service' AND error.expected IS FALSE"
        }
    }

    objective {
        target = 99.00
        time_window {
            rolling {
                count = 7
                unit = "DAY"
            }
        }
    }
}

# Payment Service
data "newrelic_entity" "ts-payment-service-app" {
  name = "store-ts-payment-service"
  domain = "APM"
  type = "APPLICATION"
}

resource "newrelic_service_level" "ts-payment-service-latency-sl" {
  guid = "${data.newrelic_entity.ts-payment-service-app.guid}"
    name = "Train-Ticket Payment Service Latency SL"
    description = "Proportion of requests that are served faster than a threshold."

    events {
        account_id = var.NEW_RELIC_ACCOUNT_ID
        valid_events {
            from = "Transaction"
            where = "appName = 'store-ts-payment-service' AND (transactionType='Web')"
        }
        good_events {
            from = "Transaction"
            where = "appName = 'store-ts-payment-service' AND (transactionType= 'Web') AND duration < 0.05"
        }
    }

    objective {
        target = 99.00
        time_window {
            rolling {
                count = 7
                unit = "DAY"
            }
        }
    }
}

resource "newrelic_service_level" "ts-payment-service-error-sl" {
  guid = "${data.newrelic_entity.ts-payment-service-app.guid}"
    name = "Train-Ticket Payment Service Error Rate SL"
    description = "Proportion of requests that are failing"

    events {
        account_id = var.NEW_RELIC_ACCOUNT_ID
        valid_events {
            from = "Transaction"
            where = "appName = 'store-ts-payment-service'"
        }
        bad_events {
            from = "TransactionError"
            where = "appName = 'store-ts-payment-service' AND error.expected IS FALSE"
        }
    }

    objective {
        target = 99.00
        time_window {
            rolling {
                count = 7
                unit = "DAY"
            }
        }
    }
}

# Travel Service
data "newrelic_entity" "ts-travel-service-app" {
  name = "store-ts-travel-service"
  domain = "APM"
  type = "APPLICATION"
}

resource "newrelic_service_level" "ts-travel-service-latency-sl" {
  guid = "${data.newrelic_entity.ts-travel-service-app.guid}"
    name = "Train-Ticket Travel Service Latency SL"
    description = "Proportion of requests that are served faster than a threshold."

    events {
        account_id = var.NEW_RELIC_ACCOUNT_ID
        valid_events {
            from = "Transaction"
            where = "appName = 'store-ts-travel-service' AND (transactionType='Web')"
        }
        good_events {
            from = "Transaction"
            where = "appName = 'store-ts-travel-service' AND (transactionType= 'Web') AND duration < 0.05"
        }
    }

    objective {
        target = 99.00
        time_window {
            rolling {
                count = 7
                unit = "DAY"
            }
        }
    }
}

resource "newrelic_service_level" "ts-travel-service-error-sl" {
  guid = "${data.newrelic_entity.ts-travel-service-app.guid}"
    name = "Train-Ticket Travel Service Error Rate SL"
    description = "Proportion of requests that are failing"

    events {
        account_id = var.NEW_RELIC_ACCOUNT_ID
        valid_events {
            from = "Transaction"
            where = "appName = 'store-ts-travel-service'"
        }
        bad_events {
            from = "TransactionError"
            where = "appName = 'store-ts-travel-service' AND error.expected IS FALSE"
        }
    }

    objective {
        target = 99.00
        time_window {
            rolling {
                count = 7
                unit = "DAY"
            }
        }
    }
}

# UI Dashboard Service
data "newrelic_entity" "ts-ui-dashboard-app" {
  name = "store-ts-ui-dashboard"
  domain = "APM"
  type = "APPLICATION"
}

resource "newrelic_service_level" "ts-ui-dashboard-latency-sl" {
  guid = "${data.newrelic_entity.ts-ui-dashboard-app.guid}"
    name = "Train-Ticket UI Dashboard Latency SL"
    description = "Proportion of requests that are served faster than a threshold."

    events {
        account_id = var.NEW_RELIC_ACCOUNT_ID
        valid_events {
            from = "Transaction"
            where = "appName = 'store-ts-ui-dashboard' AND (transactionType='Web')"
        }
        good_events {
            from = "Transaction"
            where = "appName = 'store-ts-ui-dashboard' AND (transactionType= 'Web') AND duration < 0.1"
        }
    }

    objective {
        target = 99.00
        time_window {
            rolling {
                count = 7
                unit = "DAY"
            }
        }
    }
}

resource "newrelic_service_level" "ts-ui-dashboard-error-sl" {
  guid = "${data.newrelic_entity.ts-ui-dashboard-app.guid}"
    name = "Train-Ticket UI Dashboard Error Rate SL"
    description = "Proportion of requests that are failing"

    events {
        account_id = var.NEW_RELIC_ACCOUNT_ID
        valid_events {
            from = "Transaction"
            where = "appName = 'store-ts-ui-dashboard'"
        }
        bad_events {
            from = "TransactionError"
            where = "appName = 'store-ts-ui-dashboard' AND error.expected IS FALSE"
        }
    }

    objective {
        target = 99.00
        time_window {
            rolling {
                count = 7
                unit = "DAY"
            }
        }
    }
}

# Create Alert Policy and Conditions

resource "newrelic_alert_policy" "train-ticket-alert-policy" {
  name = "Train-Ticket All Alerts"
}

resource "newrelic_nrql_alert_condition" "train-ticket-latency-condition" {
  account_id                     = var.NEW_RELIC_ACCOUNT_ID
  policy_id                      = newrelic_alert_policy.train-ticket-alert-policy.id
  type                           = "static"
  name                           = "High Latency"
  description                    = "Alert when transactions are taking too long"
  enabled                        = true
  violation_time_limit_seconds   = 3600
  fill_option                    = "static"
  fill_value                     = 1.0
  aggregation_window             = 60
  aggregation_method             = "event_flow"
  aggregation_delay              = 30
  expiration_duration            = 120
  open_violation_on_expiration   = true
  close_violations_on_expiration = true
  slide_by                       = 30

  nrql {
    query = "SELECT average(duration) FROM Transaction where appName LIKE 'store-ts-%' FACET appName"
  }

  critical {
    operator              = "above"
    threshold             = 1
    threshold_duration    = 120
    threshold_occurrences = "ALL"
  }

  warning {
    operator              = "above"
    threshold             = 0.5
    threshold_duration    = 120
    threshold_occurrences = "ALL"
  }
}

resource "newrelic_nrql_alert_condition" "train-ticket-pod-stability-condition" {
  account_id                     = var.NEW_RELIC_ACCOUNT_ID
  policy_id                      = newrelic_alert_policy.train-ticket-alert-policy.id
  type                           = "static"
  name                           = "POD Stability"
  description                    = "Alert when PODs are unstable"
  enabled                        = true
  violation_time_limit_seconds   = 3600
  fill_option                    = "static"
  fill_value                     = 1.0
  aggregation_window             = 60
  aggregation_method             = "event_flow"
  aggregation_delay              = 30
  expiration_duration            = 120
  open_violation_on_expiration   = true
  close_violations_on_expiration = true
  slide_by                       = 30

  nrql {
    query = "from K8sPodSample SELECT latest(isReady) where namespaceName = 'store' facet podName"
  }

  critical {
    operator              = "equals"
    threshold             = 0
    threshold_duration    = 300
    threshold_occurrences = "ALL"
  }
  warning {
    operator              = "equals"
    threshold             = 0
    threshold_duration    = 120
    threshold_occurrences = "ALL"
  }
}

resource "newrelic_nrql_alert_condition" "train-ticket-cluster-stability-condition" {
  account_id                     = var.NEW_RELIC_ACCOUNT_ID
  policy_id                      = newrelic_alert_policy.train-ticket-alert-policy.id
  type                           = "static"
  name                           = "Cluster Stability"
  description                    = "Alert when Cluster is unstable"
  enabled                        = true
  violation_time_limit_seconds   = 3600
  fill_option                    = "static"
  fill_value                     = 0
  aggregation_window             = 60
  aggregation_method             = "event_flow"
  aggregation_delay              = 30
  expiration_duration            = 60
  open_violation_on_expiration   = true
  close_violations_on_expiration = true
  slide_by                       = 30

  nrql {
    query = "SELECT uniqueCount(host) from K8sClusterSample where hostStatus != 'running' and clusterName = 'store-kubecluster' facet hostStatus, clusterName"
  }

  critical {
    operator              = "above"
    threshold             = 0
    threshold_duration    = 300
    threshold_occurrences = "ALL"
  }
}

resource "newrelic_nrql_alert_condition" "train-ticket-container-stability-condition" {
  account_id                     = var.NEW_RELIC_ACCOUNT_ID
  policy_id                      = newrelic_alert_policy.train-ticket-alert-policy.id
  type                           = "static"
  name                           = "Container CPU Utilization"
  description                    = "Alert when Containers consume more CPU"
  enabled                        = true
  violation_time_limit_seconds   = 3600
  fill_option                    = "static"
  fill_value                     = 1.0
  aggregation_window             = 60
  aggregation_method             = "event_flow"
  aggregation_delay              = 30
  expiration_duration            = 120
  open_violation_on_expiration   = true
  close_violations_on_expiration = true
  slide_by                       = 30

  nrql {
    query = "from K8sContainerSample SELECT average(cpuCoresUtilization) where namespaceName = 'store' facet containerID"
  }

  critical {
    operator              = "above"
    threshold             = 50
    threshold_duration    = 120
    threshold_occurrences = "ALL"
  }
  warning {
    operator              = "above"
    threshold             = 40
    threshold_duration    = 120
    threshold_occurrences = "ALL"
  }
}
