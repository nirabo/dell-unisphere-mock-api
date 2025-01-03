# basicSystemInfo

Provides unauthenticated access to system model, system name, software version, and API version information. This is a singleton resource type

# Supported operations

Collection query , Instance query

### Attributes

| Attribute | Type | Description |
| --- | --- | --- |
| id | String | Unique identifier of the basicSystemInfo instance. |
| model | String | Model name of this storage system. This value comes from the |
|  |  | model attribute of the system resource. |
| name | String | Name of this storage system. This value comes from the name |
|  |  | attribute of the system resource. |
| software Version | String | Software version of this storage system. This value comes from the |
|  |  | version attribute of the installedSoftwareVersion resource. |
| softwareFullVersion | String | Software full version of this storage system. This value comes from |
|  |  | the fullversion attribute of the installedSoftwareVersion resource. |
| apiVersion | String | Latest version of the REST API that this storage system supports. |
| earliestApiVersion | String | Earliest version of the REST API that this storage system supports. |

#### Query all members of the basicSystemInfo collection

| Header | Accept: application/json |
| --- | --- |
|  | Content - Type: application/json |
| Method and URI | GET /api/types/basicSystemInfo/instances |
| Request body arguments | None |
| Successful return status | 200 OK |
| Successful response body | JSON representation of all members of the basicSystemInfo |
|  | collection. |

## Query a specific basicSystemInfo instance

| Header | Accept: application/json |
| --- | --- |
|  | Content - Type: application/json |
| Method and URI | GET /api/instances/basicSystemInfo/<id> |
|  | where <id> is the unique identifier of the basicSystemInfo instance to query. |
|  | Or |
|  | GET /api/instances/basicSystemInfo/name: < value> |
|  | where < value> is the name of the basicSystemInfo instance to query. |
| Request body arguments | None |
| Successful return status | 200 OK |
| Successful response body | JSON representation of a specific basicSystemInfo instance. |
