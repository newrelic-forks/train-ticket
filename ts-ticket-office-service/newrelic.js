'use strict'

exports.config = {
  app_name: ['ts-ticket-office-service'],
  license_key: process.env.NEW_RELIC_LICENSE_KEY,
  distributed_tracing: {
    enabled: true
  },
  logging: {
    level: 'info'
  },
  application_logging: {
    enabled: true,
    forwarding: {
      enabled: true
    }
  }
}