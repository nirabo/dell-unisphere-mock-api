## loginSessionInfo

Information about a REST API login session.

#### Supported operations

Collection query , Instance query ,Logout

# Attributes

| Attribute | Type | Description |
| --- | --- | --- |
| id | String | Unique identifier of the loginSessionInfo instance. |
| domain | String | Domain of the user logged into this session. |
| user | user | Information about the user logged into this session, as |
|  |  | defined by the user resource type. |
| roles | List<role> | List of roles for the user logged into this session, as |
|  |  | defined by the role resource type. |
| idle Timeout | unsigned Integer[32(seconds)] | Number of seconds after last use until this session expires. |
| isPasswordChangeRequired | Boolean |  |

| Indicates whether the password must be changed in order |
| --- |
| to use this session created for built-in admin account. |
| Values are: |
| . true - Password must be changed. |
| . false - Password does not need to be changed. |
| For information about changing the password for a local |
| user, see the Help topic for the user resource type. |

### Query all members of the loginSessionInfo collection

| Header | Accept: application/json |
| --- | --- |
|  | Content - Type: application/json |
| Method and URI | GET api/types/loginSessionInfo/instances |
| Request body arguments | None |
| Successful return status | 200 OK |
| Successful response body | JSON representation of all members of the loginSessionInfo |
|  | collection. |

# Query a specific loginSessionInfo instance

| Header | Accept: application/json |
| --- | --- |
|  | Content - Type: application/json |
| Method and URI | GET api/instances/loginSessionInfo/<id> |
|  | where <id> is the unique identifier of the loginSessionInfo instance to query. |
| Request body arguments | None |
| Successful return status | 200 OK |
| Successful response body | JSON representation of a specific loginSessionInfo instance. |

#### Loqout operation

### Log out of the session

| Header | Accept: application/json |
| --- | --- |
|  | Content - Type: application/json |
| Method and URI | POST /api/types/loginSessionInfo/action/logout |
| Request body arguments | See the arquments table below. |
| Successful return status | 200 OK |
| Successful response body | JSON representation of the returned attributes. |

### Arguments for the Logout operation

| Arqument | In/ | Type | Required? | Description |
| --- | --- | --- | --- | --- |
|  | out |  |  |  |
| localCleanupOnly | in | Boolean | Optional | Indicates whether to log out of all REST API sessions authenticated |
|  |  |  |  | by the Ticket Granting Token (TGT) with which this session was |
|  |  |  |  | established. |
|  |  |  |  | Values are: |
|  |  |  | . | true - Log out of this session only. |
|  |  |  | . | false - Log out of all sessions. |
| logoutOK | out | String | N/A | Indicates successful logout |

 loginSessionInfo

Information about a REST API login session

### Supported operations

Collection query , Instance query ,Logout

### Attributes

| Attribute | Type | Description |
| --- | --- | --- |
| id | String | Unique identifier of the loginSessionInfo instance. |
| domain | String | Domain of the user logged into this session. |
| user | user | Information about the user logged into this session, as |
|  |  | defined by the user resource type. |
| roles | List<role> | List of roles for the user logged into this session, as |
|  |  | defined by the role resource type. |
| idleTimeout | unsigned Integer[32(seconds)] | Number of seconds after last use until this session expires. |
| isPasswordChangeRequired | Boolean | Indicates whether the password must be changed in order |
|  |  | to use this session created for built-in admin account. |
|  |  | Values are: |
|  |  | . true - Password must be changed. |
|  |  | . false - Password does not need to be changed. |
|  |  | For information about changing the password for a local |
|  |  | user, see the Help topic for the user resource type. |

Query all members of the loginSessionInfo collection

| Header | Accept: application/json |
| --- | --- |
|  | Content - Type: application/ json |
| Method and URI | GET api/types/loginSessionInfo/instances |
| Request body arguments | None |
| Successful return status | 200 OK |
| Successful response body | JSON representation of all members of the loginSessionInfo |
|  | collection. |

Query a specific loginSessionInfo instance

| Header | Accept: application/json |
| --- | --- |
|  | Content - Type: application/json |
| Method and URI | GET /api/instances/loginSessionInfo/<id> |
|  | where <id> is the unique identifier of the loginSessionInfo instance to query. |
| Request body arguments | None |
| Successful return status | 200 OK |

# Logout operation

# Log out of the session

| Header | Accept: application/json |
| --- | --- |
|  | Content - Type: application/json |
| Method and URI | POST api/types/loginSessionInfo/action/logout |
| Request body arguments | See the arquments table below. |
| Successful return status | 200 OK |
| Successful response body | JSON representation of the returned attributes. |

### Arguments for the Logout operation

| Arqument | In/ | Type | Required? | Description |
| --- | --- | --- | --- | --- |
|  | out |  |  |  |
| localCleanupOnly | in | Boolean | Optional | Indicates whether to log out of all REST API sessions authenticated |
|  |  |  |  | by the Ticket Granting Token (TGT) with which this session was |
|  |  |  |  | established. |
|  |  |  |  | Values are: |
|  |  |  |  | . true - Log out of this session only. |
|  |  |  |  | . false - Log out of all sessions. |
| logoutOK | out | String | N/A | Indicates successful logout |
