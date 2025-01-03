#!/bin/bash

# Configuration
SCHEMA="http://"
IP="192.168.0.148:8000"  # Replace with your Unity IP
USER="admin"
PASS="Password123!"  # Replace with your password
AUTH=$(echo -n "$USER:$PASS" | base64)

# Get CSRF Token
CSRF_TOKEN=$(curl --location "$SCHEMA$IP/api/types/fcPort/instances?fields=id%2CslotNumber%2Chealth%2CcurrentSpeed&compact=true" \
  --header "Accept: application/json" \
  --header "Content-type: application/json" \
  --header "X-EMC-REST-CLIENT: true" \
  --header "Authorization: Basic $AUTH" \
  | grep -oP '(?<="EMC-CSRF-TOKEN": ")[^"]+')

# 1. Get FC Ports
curl --location "$SCHEMA$IP/api/types/fcPort/instances?fields=id%2CslotNumber%2Chealth%2CcurrentSpeed&compact=true" \
  --header "Accept: application/json" \
  --header "Content-type: application/json" \
  --header "X-EMC-REST-CLIENT: true" \
  --header "Authorization: Basic $AUTH" \
  --header "EMC-CSRF-TOKEN: $CSRF_TOKEN"

# 2. Get Pools
curl --location "$SCHEMA$IP/api/types/pool/instances" \
  --header "Accept: application/json" \
  --header "Content-type: application/json" \
  --header "X-EMC-REST-CLIENT: true" \
  --header "Authorization: Basic $AUTH" \
  --header "EMC-CSRF-TOKEN: $CSRF_TOKEN"

# 3. Get LUNs (basic)
curl --location "$SCHEMA$IP/api/types/lun/instances" \
  --header "Accept: application/json" \
  --header "Content-type: application/json" \
  --header "X-EMC-REST-CLIENT: true" \
  --header "Authorization: Basic $AUTH" \
  --header "EMC-CSRF-TOKEN: $CSRF_TOKEN"

# 4. Get LUNs (detailed)
curl --location "$SCHEMA$IP/api/types/lun/instances?fields=id%2Cname%2Chealth%2CsizeTotal&compact=true" \
  --header "Accept: application/json" \
  --header "Content-type: application/json" \
  --header "X-EMC-REST-CLIENT: true" \
  --header "Authorization: Basic $AUTH" \
  --header "EMC-CSRF-TOKEN: $CSRF_TOKEN"

# 5. Create LUN
curl --location "$SCHEMA$IP/api/types/storageResource/action/createLun" \
  --header "Accept: application/json" \
  --header "Content-type: application/json" \
  --header "X-EMC-REST-CLIENT: true" \
  --header "Authorization: Basic $AUTH" \
  --header "EMC-CSRF-TOKEN: $CSRF_TOKEN" \
  --request POST \
  --data '{"name":"Alberto1","description":"Alberto testing the Rest API","lunParameters":{"pool":{"id":"pool_2"},"size":2000000000}}'

# 6. Delete LUN
LUN_ID="sv_72"  # Replace with actual LUN ID
curl --location "$SCHEMA$IP/api/instances/storageResource/$LUN_ID" \
  --header "Accept: application/json" \
  --header "Content-type: application/json" \
  --header "X-EMC-REST-CLIENT: true" \
  --header "Authorization: Basic $AUTH" \
  --header "EMC-CSRF-TOKEN: $CSRF_TOKEN" \
  --request DELETE

# 7. Get File Systems
curl --location "$SCHEMA$IP/api/types/filesystem/instances?fields=id%2Cname%2Chealth%2CsizeTotal&compact=true" \
  --header "Accept: application/json" \
  --header "Content-type: application/json" \
  --header "X-EMC-REST-CLIENT: true" \
  --header "Authorization: Basic $AUTH" \
  --header "EMC-CSRF-TOKEN: $CSRF_TOKEN"

# 8. Get File System Details
FS_ID="fs_3"  # Replace with actual File System ID
curl --location "$SCHEMA$IP/api/instances/filesystem/$FS_ID?fields=id%2Cname%2Chealth%2CsizeTotal&compact=true" \
  --header "Accept: application/json" \
  --header "Content-type: application/json" \
  --header "X-EMC-REST-CLIENT: true" \
  --header "Authorization: Basic $AUTH" \
  --header "EMC-CSRF-TOKEN: $CSRF_TOKEN"

# 9. Get Metric Details
METRIC_ID="14236"  # Replace with actual Metric ID
curl --location "$SCHEMA$IP/api/instances/metric/$METRIC_ID" \
  --header "Accept: application/json" \
  --header "Content-type: application/json" \
  --header "X-EMC-REST-CLIENT: true" \
  --header "Authorization: Basic $AUTH" \
  --header "EMC-CSRF-TOKEN: $CSRF_TOKEN"

# 10. Get Historical Metric Values
curl --location "$SCHEMA$IP/api/types/metricValue/instances?filter=path%20EQ%20%22sp.*.physical.disk.*.responseTime%20AND%20interval%20EQ%2060%22" \
  --header "Accept: application/json" \
  --header "Content-type: application/json" \
  --header "X-EMC-REST-CLIENT: true" \
  --header "Authorization: Basic $AUTH" \
  --header "EMC-CSRF-TOKEN: $CSRF_TOKEN"

# 11. Create Realtime Metric Query
curl --location "$SCHEMA$IP/api/types/metricRealTimeQuery/instances" \
  --header "Accept: application/json" \
  --header "Content-type: application/json" \
  --header "X-EMC-REST-CLIENT: true" \
  --header "Authorization: Basic $AUTH" \
  --header "EMC-CSRF-TOKEN: $CSRF_TOKEN" \
  --request POST \
  --data '{"paths":["sp.*.cpu.summary.busyTicks","sp.*.cpu.summary.idleTicks"],"interval":10}'

# 12. Get Realtime Metric Instances
curl --location "$SCHEMA$IP/api/types/metricRealTimeQuery/instances" \
  --header "Accept: application/json" \
  --header "Content-type: application/json" \
  --header "X-EMC-REST-CLIENT: true" \
  --header "Authorization: Basic $AUTH" \
  --header "EMC-CSRF-TOKEN: $CSRF_TOKEN"

# 13. Get Realtime Metric Values
QUERY_ID="88"  # Replace with actual Query ID
curl --location "$SCHEMA$IP/api/types/metricQueryResult/instances?filter=queryId%20eq%20$QUERY_ID" \
  --header "Accept: application/json" \
  --header "Content-type: application/json" \
  --header "X-EMC-REST-CLIENT: true" \
  --header "Authorization: Basic $AUTH" \
  --header "EMC-CSRF-TOKEN: $CSRF_TOKEN"
