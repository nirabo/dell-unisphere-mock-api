## Authentication and Authorization

To make a Unity REST API request, there is something we need to know:

- Every Unity REST API request must be authenticated, except the query of basicSystemInfo resource type
- The Unity REST API uses the standard HTTP Basic authentication mechanism to authenticate the REST requests
- Header X-EMC-REST-CLIENT: true is required for logging into Unity REST API server
- Header EMC-CSRF-TOKEN is required for POST and DELETE requests
- The following headers should also be included:
	- Accept: application/json: to indicate the format of the response content is JSON
	- Content-type: application/json: to indicate the format of the request body is JSON, it is required if there is a request body

To get CSRF token, we could make a basic GET request and get the token from the response headers.

## Example - Get CSRF token

In this case, we learn how to get CSRF token for POST/DELETE request usage.

First, we send a GET request, in this case, we make a collection query for resource "user":

```bash

curl -i -k -L \ -u admin:Password123! \ -c cookie.txt \ -H "Accept: application/json" \

 -H "Content-Type: application/json" \ -H "X-EMC-REST-CLIENT: true" \ "https://10.245.83.44/api/types/user/instances"
```

#### This is the response:

```bash
HTTP/1.1 200 OK Date: Thu, 27 Aug 2020 01:39:17 GMT Server: Apache X-Frame-Options: SAMEORIGIN Strict-Transport-Security: max-age=63072000; includeSubdomains; Set-Cookie: mod_sec_emc=value3&1&value1&iqVsJ%2BQSevmw8FNGWoI%2FkWOzydl0oqhuJNaWfLy3oiq7iwH7fH ckEcjlZ2GBo5fg%0A&value2&eaae0856a499fcc3b91408224a7307abc203b6684401cf1b912098778c5 79548; path=/; secure; HttpOnly EMC-CSRF-TOKEN: A+QAtubhfNa0S6dkPyusYCuuHWnuFfzx7GteLQNEm8KOQgQHe0t90Vp0B09E6V7AwMo90iC0ee5EV GR0LQrWQcDLs3zLAD1vRThgPyPZWkY= Pragma: no-cache Cache-Control: no-cache, no-store, max-age=0 Expires: Thu, 01 Jan 1970 00:00:00 GMT Content-Language: en-US Vary: Accept-Encoding Transfer-Encoding: chunked Content-Type: application/json; version=1.0;charset=UTF-8

{"@base":"https://10.245.83.44/api/types/user/instances? per_page=2000","updated":"2020-08-27T01:39:17.471Z","links":[{"rel":"self","href":"&page=1"}],"entries": [{"@base":"https://10.245.83.44/api/instances/user","updated":"2020-08-27T01:39:17.471Z","links": [{"rel":"self","href":"/user_admin"}],"content":{"id":"user_admin"}}]}

```

We could get CSRF token from the headers of response, in this case, the CSRF token is dNrzcvqLkkzcWDNK1O1XBIUzsbldshcss5Jt+mye16D9GuRU+dFTgZN1zGJ1E/ jYm6Slo531D9JUdffuY4ViI+aL+MLsIXJ2cwS3T1t24fI=.

#### Now, we could use the token to send POST or DELETE request:

```bash

curl -i -k -L \ -u admin:Password123! \ -c cookie.txt \ -b cookie.txt \ -H "Accept: application/json" \ -H "Content-Type: application/json" \ -H "X-EMC-REST-CLIENT: true" \ -H "EMC-CSRF-TOKEN: A+QAtubhfNa0S6dkPyusYCuuHWnuFfzx7GteLQNEm8KOQgQHe0t90Vp0B09E6V7AwMo90iC0ee5EVG R0LQrWQcDLs3zLAD1vRThgPyPZWkY=" \ -X DELETE "https://10.245.83.44:443/api/instances/storageResource/sv_19166"
```

## How to get attributes of resource

As we discussed in the frst call, felds=id,name parameter is specifed in request URI to tell Unity which attributes we need. But actually most of the resources have a bunch of attributes, not only id and name.

In order to get all attributes of a resource, we could send a GET request to get the resource types.

## Example - Get attributes of pool

In this case, we learn how to get all attributes of pool.

We send a GET request to get pool types with felds=attributes.name parameter specifed:

bash

```
curl -i -k -L \
 -u admin:Password123! \
 -c cookie.txt \
 -H "Accept: application/json" \
 -H "Content-Type: application/json" \
 -H "X-EMC-REST-CLIENT: true" \
 "https://10.245.83.44/api/types/pool?compact=True&felds=attributes.name"
```
## Unity will return all the attribute names of pool:


```json
{
 "content": {
 "name": "pool",
 "attributes": [
 {
 "name": "dataReductionRatio"
 },
 {
 "name": "snapSpaceHarvestLowThreshold"
 },
 {
 "name": "sizeUsed"
 },
 {
 "name": "hasCompressionEnabledLuns"
 },
 {
 "name": "poolSpaceHarvestLowThreshold"
 },
 {
 "name": "sizePreallocated"
 },
 {
 "name": "snapSizeSubscribed"
 },
 {
 "name": "sizeFree"
 },
 {
 "name": "health"
```
