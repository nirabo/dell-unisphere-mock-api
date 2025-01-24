## tenant

A lenerant is a representation of a datazenter client, who usea an independent and extusbive acsess to ersission and extusive assess to estabin strage resuvces. On the stor independent IP addressing. Al the norment, iSSS and management resources do not support multi-lengt access. For each enant a porresproling Linux nelwork nappesageis s geated, tenants is done by the VLAVs. Each tenant reserves a group of VLANs, and each VLAN can belong to one tenart maximum. Every lensat gets a rame and the Universaly Unique lear tenant life eyde. The asynchronous repication of the NAS serves is allawed only behewen the sane UUD. The NAS serves and VLANs cans UUD. The NAS seners and VL-Als can still operate in the Linux base nelwork namespage, topeller with nanagement and ISCSI intefaces. The control stack of the exsten does not alguy user op op in in the engants AMS se managed from the single system administrator account. To allow this, the corresponding GUI and CLI modifications are made.

#### Supported operations

Collection query , Instance query ,Create ,Modify ,Delete

# Attributes

| Attribute | Type | Description |
| --- | --- | --- |
| id | String | Unique identifier of the tenant instance. |
| name | String | User-specified name of the tenant. |
| uuid | String | UUID of the tenant. |
| vlans | List<Integer>[32][1.. 4094] | VLAN IDs assigned to the tenant. |
| hosts | List<host> | The hosts associated with the tenant. |

Query all members of the tenant collection

| Header | Accept: application/json |
| --- | --- |
|  | Content - Type: application/json |
| Method and URI | GET /api/types/tenant/instances |
| Request body arguments | None |
| Successful return status | 200 OK |
| Successful response body | JSON representation of all members of the tenant collection. |

### Query a specific tenant instance

| Header | Accept: application/json |
| --- | --- |
|  | Content - Type: application/json |
| Method and URI | GET /api/instances/tenant/<id> |
|  | where <id> is the unique identifier of the tenant instance to query. |
|  | Or |
|  | GET /api/instances/tenant/name: < value> |
|  | where <value> is the name of the tenant instance to query. |
| Request body arguments | None |
| Successful return status | 200 OK |
| Successful response body | JSON representation of a specific tenant instance. |

### Create operation

Create a tenant

| Header | Accept: application/json |
| --- | --- |
|  | Content - Type: application/json |
| Method and URI | POST api/types/tenant/instances |
| Request body arguments | See the arquments table below. |
| Successful return status | 201 Created, 202 Accepted (async response) |
| Successful response body | JSON representation of the <id> attribute |

#### Arquments for the Create operation

|
|  |

| name |  | Chilian Official | : INCHILL |  |
| --- | --- | --- | --- | --- |
| uuid | in | String | Optional | UUID of tenant object. |
| vlans | in | List<Integer>[32][1.. 4094] | Required | List of VLAN IDs. |
| id | out | tenant | N/A | Unique identifier of the new tenant instance. |

# Modify operation

### Modify a tenant.

| Header | Accept: application/json |
| --- | --- |
|  | Content - Type: application/json |
| Method and URI | POST /api/instances/tenant/<id>/action/modify |
|  | where <id> is the unique identifier of the tenant instance. |
|  | Or |
|  | POST /api/instances/tenant/name: < value>/action/modify |
|  | where < value> is the name of the tenant instance. |
| Request body arguments | See the arquments table below. |
| Successful return status | 204 No Content, 202 Accepted (async response) |
|  | No body content. |
| Successful response body |  |

### Arquments for the Modify operation

| Arqument | In/ out | Type | Required? | Description |
| --- | --- | --- | --- | --- |
| name | in | String | Optional | New tenant name. |
| vlans | in | List< Integer>[32][1.. 4094] | Optional | List of VLAN IDs to set. |

## Delete operation

# Destroy a tenant.

| Header | Accept: application/json |
| --- | --- |
|  | Content - Type: application/json |
| Method and URI | DELETE /api/instances/tenant/<id> |
|  | where <id> is the unique identifier of the tenant instance to delete. |
| Or |  |
|  | DELETE /api/instances/tenant/name: < value> |
|  | where <value> is the name of the tenant instance to delete. |
| Request body arguments | None |
| Successful return status | 204 No Content, 202 Accepted (async response) |
| Successful response body | No body content. |
