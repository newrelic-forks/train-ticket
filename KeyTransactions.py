import requests
import json
import os
import sys
import time

endpoint = "https://api.newrelic.com/graphql"
try:
  if os.environ['TF_VAR_NEW_RELIC_REGION'] == "EU":
    endpoint = "https://api.eu.newrelic.com/graphql"
except KeyError:
  pass

def nerdgraph_createkeytxn(apikey, guid, kt):
  # GraphQL query to NerdGraph
  query = """
  mutation {
    keyTransactionCreate(apdexTarget: 0.5,
                        applicationGuid: "@guid",
                        browserApdexTarget: 7,
                        metricName: "@kt",
                        name: "@kt") {
      apdexTarget
      browserApdexTarget
      guid
      metricName
      name
    }
  }"""

  query = query.replace("@guid", guid)
  query = query.replace("@kt", kt)
  headers = {'API-Key': f'{apikey}'}
  response = requests.post(endpoint, headers=headers, json={"query": query})

  if response.status_code != 200:
    raise Exception(f"Nerdgraph query failed with a {response.status_code}.")

def nerdgraph_getentityguid(key,entityname,accountId):
  # GraphQL query to NerdGraph
  global app_guid
  query = """
  {
  actor {
    entitySearch(queryBuilder: {name: \"""" + entityname + """\", tags: {key: "accountId", value: \"""" + accountId + """\"}}) {
      count
      query
      results {
        entities {
          guid
        }
      }
    }
  }
}"""

  headers = {'API-Key': f'{key}'}
  response = requests.post(endpoint, headers=headers, json={"query": query})

  if response.status_code == 200:
    dict_response = json.loads(response.content)
    guid = dict_response["data"]["actor"]["entitySearch"]["results"]["entities"][0]["guid"]
    return guid

  raise Exception(f"Nerdgraph query failed with a {response.status_code}.")


try:
  apikey = os.environ['TF_VAR_NEW_RELIC_API_KEY']
except:
  print("Error: No USER api key found in environment variable TF_VAR_NEW_RELIC_API_KEY")
  sys.exit(1)

try:
  accountid = os.environ['TF_VAR_NEW_RELIC_ACCOUNT_ID']
except:
  print("Error: No ACCOUNT ID found in environment variable TF_VAR_NEW_RELIC_ACCOUNT_ID")
  sys.exit(1)

# Train-Ticket Key Transactions
# Note: These transaction names are estimates and may need to be updated after deployment
# when actual transaction names are visible in New Relic APM
key_transactions = {
  "store-ts-auth-service": "WebTransaction/SpringController/AuthController/verifyToken",
  "store-ts-order-service": "WebTransaction/SpringController/OrderController/createNewOrder",
  "store-ts-preserve-service": "WebTransaction/SpringController/PreserveController/preserve",
  "store-ts-payment-service": "WebTransaction/SpringController/PaymentController/pay",
  "store-ts-travel-service": "WebTransaction/SpringController/TravelController/queryAll",
  "store-ts-ui-dashboard": "WebTransaction/Uri/index.html"
}

done = {}
attempts = 1
total_transactions = len(key_transactions)

print(f"Setting up {total_transactions} key transactions for Train-Ticket services...")
print("Note: If services are not yet instrumented or transaction names are incorrect,")
print("      this process may fail. You can re-run this script after services are running.\n")

while len(done) < total_transactions and attempts < 20:
  try:
    for app, kt in key_transactions.items():
      if app in done:
        continue
      print(f"Configuring key transaction for {app}.")
      # Check if one already exists
      try:
        nerdgraph_getentityguid(apikey, kt, accountid)
        print(f"Key transaction already exists for {app}.. skipping.")
      except IndexError:
        guid = nerdgraph_getentityguid(apikey, app, accountid)
        nerdgraph_createkeytxn(apikey, guid, kt)
        print(f"Key transaction created for {app}.")
        pass
      done[app] = True
  except Exception as e:
    print(f"Error: Failed with exception: {e}")
    print("Retrying..")
    time.sleep(1)
    pass
  attempts = attempts + 1

if len(done) == total_transactions:
  print(f"\nAll {total_transactions} key transactions created successfully.")
else:
  print(f"\nFailed to create key transactions after {attempts} attempts.")
  print(f"Successfully created {len(done)} out of {total_transactions} transactions.")
  print("\nThis is normal if:")
  print("  1. Services are not yet fully deployed and instrumented")
  print("  2. Transaction names don't match actual transaction names in New Relic")
  print("\nYou can:")
  print("  1. Wait for all services to be running and instrumented")
  print("  2. Check New Relic APM for actual transaction names")
  print("  3. Update transaction names in KeyTransactions.py")
  print("  4. Re-run this script: python3 KeyTransactions.py")
  sys.exit(1)
