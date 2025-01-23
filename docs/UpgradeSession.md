## UpgradeSessionTypeEnum

| Value | Enumeration |
| --- | --- |
| 0 | Upgrade |
|  | Health_Check |
| N | Storageprocessor_Upgrade |
| 3 | Offline_Storageprocessor_Upgrade |

# UpgradeStatusEnum

Current status of the associated upgrade session.

| Value | Enumeration | Description |
| --- | --- | --- |
|  | Upgrade_Not_Started | Upgrade session was not started. |
|  | Upgrade_In_Progress | Upgrade session is in the process of upgrading the system software, language pack, or drive firmware. |

| 2 | Upgrade Completed | Upgrade session completed successfully. |
| --- | --- | --- |
| 3 | Upgrade Failed | Upgrade session did not complete successfully. |
| 4 | Upgrade_Failed_Lock | Upgrade session failed, and the system is in a locked state. |
| 5 | Upgrade Cancelled | Upgrade session was cancelled. |
| 6 | Upgrade_Paused | Upgrade session is paused. |
| 7 | Upgrade_Acknowledged | Upgrade session was acknowledged. |
| 8 | Upgrade Waiting_For_User | Upgrade session is waiting for user action to continue the upgrade |
| 9 | Upgrade_Paused_Lock | Upgrade session is paused past the point of cancellation. |

### UpgradeTypeEnum

| Value | Enumeration |
| --- | --- |
| 0 | Software |
|  | Firmware |
| 2 | LanguagePack |

## softwareUpgradeSession

Information about a storage system upgrade session.

Create an upprade session to upprade the system software or view existing upprade sessions. The upgrade sessions installs an uporade candidate file ryslem. Download the hast Support website. Use the CLI to upload the upgrade candidate to the system before creating the upgrade session. For information, see theUnisphere CLI User Guide.

The latest software upgrade candidate contains all available hot fixes. If you have applied hot fixes to your system, the hot fixes are included in the latest upgrade candi

Note: All system components must be healthy prior to upgrading the system software. If any system components are degraded, the software update will fail

### Embedded resource types

upgradeMessage, upgradeTask

# Supported operations

Collection query , Instance query ,Create ,VerifyUpgradeEligibility ,Resume

### Attributes

| Attribute | Type | Description |
| --- | --- | --- |
| id | String | Unique identifier for the softwareUpgradeSession instance. |
| type | UpgradeSessionTypeEnum | Type of software to upgrade. |
| candidate | candidateSoftwareVersion | Candidate software to install in the upgrade session, as defined by |
|  |  | the candidateSoftwareVersion resource type. |
| caption | String | Caption for this upgrade session. |
| status | UpgradeStatusEnum | Status of the current upgrade session. |
| messages | List < upgradeMessage> | List of upgrade messages. |
| creationTime | DateTime | Date and time when the upgrade session was started. |
| elapsedTime | Date Time[Interval] | Amount of time for which the upgrade session was running. |
| percentComplete | unsigned Integer[16(percent)] | Percentage of the upgrade that is completed. |
|  | [0.. 100] |  |
| tasks | List < upgrade Task> | Current upgrade activity in the upgrade session, as defined by the |
|  |  | upgradeTask resource type. |

### Attributes for upgradeMessage

A message occurrence. This is also the message object returned in the body of non-2xx return code REST responses.

| Attribute | Type | Description |
| --- | --- | --- |
| errorCode | String | Error code for this message. |
| messages | List<localizedMessage> | List of localized messages. |
| severity | SeverityEnum | Severity level associated with this message. |
| httpStatus | unsigned Integer[32] | HTTP status code for this message. |

Attributes for upgradeTask

| Attribute | Type | Description |
| --- | --- | --- |
| caption | String | Caption for this task. |
| creationTime | DateTime | Date and time when the upgrade task was started. |
| status | UpgradeStatusEnum | Current status of the upgrade activity. |
| type | UpgradeSessionTypeEnum | Upgrade session type. |
| estRemainTime | DateTime[Interval] | Estimated time remaining for the upgrade task. |

#### Query all members of the softwareUpgradeSession collection

| Header | Accept: application/json |
| --- | --- |
|  | Content - Type: application/json |
| Method and URI | GET api/types/softwareUpgradeSession/instances |
| Request body arguments | None |
| Successful return status | 200 OK |
| Successful response body | JSON representation of all members of the softwareUpgradeSession collection. |

#### Query a specific softwareUpgradeSession instance

| Header | Accept: application/json |
| --- | --- |
|  | Content - Type: application/json |
| Method and URI | GET /api/instances/softwareUpgradeSession/<id> |
|  | where <id> is the unique identifier of the softwareUpgradeSession instance to query. |
| Request body arguments | None |
| Successful return status | 200 OK |
| Successful response body | JSON representation of a specific softwareUpgradeSession instance. |

# Create operation

Start a session to upgrade the system software with an uploaded upgrade candidate

| Header | Accept: application/json |
| --- | --- |
|  | Content - Type: application/json |
| Method and URI | POST api/types/softwareUpgradeSession/instances |
| Request body arguments | See the arquments table below. |
| Successful return status | 201 Created |
| Successful response body | JSON representation of the <id> attribute |

# Arguments for the Create operation

| Arqument | In/ | Type | Required? | Description |
| --- | --- | --- | --- | --- |
|  | out |  |  |  |
| candidate | in | candidateSoftwareVersion | Optional | Candidate software to install in the upgrade |
|  |  |  |  | session, as defined by the |
|  |  |  |  | candidateSoftwareVersion resource type. |
| selectedModel | in | SPModelNameEnum | Optional |  |
| pauseBeforeReboot | in | Boolean | Optional | Flag to tell that session should stop after the |
|  |  |  |  | "preinstall" tasks and before first SP reboot. |
| id | out | softwareUpgradeSession | N/A | The new upgrade session. |

# VerifyUpgradeEligibility operation

Validate that the system is in a healthy state. This is required for an upgrade is started. You can use this operation to peration to perdion to perdion to perdion no perfo

| Header | Accept: application/json |
| --- | --- |
|  | Content - Type: application/json |
| Method and URI | POST |
|  | api/types/softwareUpgradeSession/action/verifyUpgradeEligibility |
| Request body arguments | See the arquments table below. |
| Successful return status | 200 OK, 202 Accepted (async response) |
| Successful response body | JSON representation of the returned attributes. |

### Arguments for the VerifyUpgradeEligibility operation

| Arqument | In/ | Type | Required? | Description |
| --- | --- | --- | --- | --- |
|  | out |  |  |  |
| messages | out | List < upgradeMessage> | N/A | List of embedded upgradeMessage which contain the info |
|  |  |  |  | of message's identifier, localized text, severity and so on. |

# Resume operation

Resume a session that is currently in paused, failed, or failed_lock state.

| Header | Accept: application/json |
| --- | --- |
|  | Content - Type: application/json |
| Method and URI POST | /api/instances/softwareUpgradeSession/<id>/action/resume |
|  | where <id> is the unique identifier of the softwareUpgradeSession instance. |
| Request body arguments None |  |
| Successful return status | 204 No Content |
| Successful response body | No body content. |

# system

Information about general settings for the storage system.

### Supported operations

Collection query , Instance query ,Failback ,Modify

# Attributes

| Attribute | Type | Description |
| --- | --- | --- |
| id | String | Unique identifier of the system instance. |
| health | health | Health information for the system, as defined by the |
|  |  | health resource type. |
| name | String | System name. |
| model | String | System model name. |
| serialNumber | String | System product serial number. |
| uuidBase | unsigned Integer[32] | Base value used to generate UUIDs in the host |
|  |  | environment(e.g. OVMS host). |
| internalModel | String | Internal model name for the system. |
| platform | String | Hardware platform for the system. |
| isAllFlash | Boolean | Indicates whether sytem is all flash. |
| macAddress | String | MAC address of the management interface. |
| isEULAAccepted | Boolean | Indicates whether the End User License Agreement |
|  |  | (EULA) was accepted for an upgrade. Once the EULA |
|  |  | is accepted, users can upload product licenses and |
|  |  | configure the system, or both. Values are: |
|  |  | . true - EULA was accepted on the system. Once |
|  |  | you set this value, you cannot set it to false later on. |
|  |  | false - EULA was not accepted on the system. . |
| isUpgradeComplete | Boolean | Indicates whether an upgrade completed. Operations |
|  |  | that change the configuration of the system are not |
|  |  | allowed while an upgrade is in progress. |
|  |  | Values are: |
|  |  | . true - Upgrade completed. |
|  |  | . false - Upgrade did not complete. |
| isAutoFailbackEnabled | Boolean | Indicates whether the automatic failback of NAS |
|  |  | servers is enabled for the system. Values are: |
|  |  | . true - Automatic failback for NAS servers is |
|  |  | enabled. |
|  |  | . false - Automatic failback for NAS servers is |
|  |  | disabled. |
| currentPower | unsigned Integer[32(watts)] | Current amount of power used by the system. |
| avgPower | unsigned Integer[32(watts)] | Average amount of power used by the system. The |
|  |  | system uses a one hour window of 30-second samples |
|  |  | to determine this value. |
| supportedUpgradeModels | List< SPModelNameEnum> | List of all supported models for hardware upgrade. |
| isHemoteSysInterfaceAutoPair | Boolean |  |
|  |  | Indicates whether remote system interface automatic pairing is enabled for the system. When enabled, only |
|  |  | pingable replication interfaces between two Unity |
|  |  | systems are used by replication remote system. The |
|  |  | default value is true. Modify the value to false if it is |
|  |  | intended to use all replication interfaces for the replication remote system despite their connectivity. |
|  |  | Values are: |
|  |  | . true - Remote system interface automatic pairing is |
|  |  | enabled. |
|  |  | . false - Remote system interface automatic pairing |
|  |  | is disabled. |

| Header | Accept: application/json |
| --- | --- |
|  | Content - Type: application/json |
| Method and URI GET | /api/types/system/instances |
| Request body arguments | None |
| Successful return status | 200 OK |
| Successful response body | JSON representation of all members of the system collection. |

# Query a specific system instance

| Header | Accept: application/json |
| --- | --- |
|  | Content - Type: application/json |
| Method and URI | GET /api/instances/system/<id> |
|  | where <id> is the unique identifier of the system instance to query. |
| Or |  |
|  | GET /api/instances/system/name: < value> |
|  | where <value> is the name of the system instance to query. |
| Request body arguments None |  |
| Successful return status | 200 OK |
| Successful response body | JSON representation of a specific system instance. |

# Failback operation

Immediately fail back the storage system to the other storage processor.

| Header | Accept: application/json |
| --- | --- |
|  | Content - Type: application/json |
| Method and URI | POST /api/instances/system/<id>/action/failback |
|  | where <id> is the unique identifier of the system instance. |
| Or |  |
|  | POST /api/instances/system/name: < value>/action/failback |
|  | where < value> is the name of the system instance. |
| Request body arguments | None |
| Successful return status | 204 No Content, 202 Accepted (async response) |
| Successful response body | No body content. |

# Modify operation

Modify the system configuration.

| Header | Accept: application/json |
| --- | --- |
|  | Content - Type: application/json |
| Method and URI | POST /api/instances/system/<id>/action/modify |
|  | where <id> is the unique identifier of the system instance. |
| Or |  |
|  | POST /api/instances/system/name: <value>/action/modify |
|  | where < value> is the name of the system instance. |
| Request body arguments | See the arquments table below. |
| Successful return status | 204 No Content, 202 Accepted (async response) |
| Successful response body | No body content. |

# Arguments for the Modify operation

| Arqument | In/ | Type | Required? | Description |
| --- | --- | --- | --- | --- |
|  | out |  |  |  |
| name | in | String | Optional | System name. |
| uuidBase | in | unsigned | Optional | Base value used to generate UUIDs in the host |
|  |  | Integer[32] |  | environment(e.g. OVMS host). This value should be |
|  |  |  |  | a non-negative number, and not greater than |
|  |  |  |  | 16385. OpenVMS requires an unique OVMS device |
|  |  |  |  | UUID for every device visible to an OVMS host, the |
|  |  |  |  | OVMS device UUID must also be consistent for any |
|  |  |  |  | given device across all nodes of an OVMS cluster. |
|  |  |  |  | Dell VNX and Unity systems create the OVMS |
|  |  |  |  | device UUID by appending the LUN number to the |
|  |  |  |  | configured Unity or VNX OVMS base UUID. In the |
|  |  |  |  | situation of multiple storage systems visible to the |
|  |  |  |  | same OVMS host(s) the storage systems must be |
|  |  |  |  | configured with unique values which avoid |
|  |  |  |  | conflicting OVMS device UUIDs. Unity and VNX |
|  |  |  |  | devices connected to multi-node OVMS clusters |
|  |  |  |  | should be configured into a consistency group to |
|  |  |  |  | ensure a consistent OVMS device UUID for the |
|  |  |  |  | same device across all OVMS cluster nodes. |

| isUpgradeCompleted | in | Boolean | Optional | Indicates whether to manually mark an upgrade |
| --- | --- | --- | --- | --- |
|  |  |  |  | process completed. This value is automatically set |
|  |  |  |  | to true by the upgrade provider at the end of the |
|  |  |  |  | upgrade process and back to false by the first GUI |
|  |  |  |  | request. |
|  |  |  |  | Values are: |
|  |  |  |  | . true - Mark the upgrade completed. |
|  |  |  |  | . false - Do not mark upgrade completed. |
|  |  |  |  | This attribute is required by the GUI to display the |
|  |  |  |  | upgrade details window on the first login after the |
|  |  |  |  | upgrade completes. It does not depend on the |
|  |  |  |  | session. The user who started an upgrade may not |
|  |  |  |  | see its results, if another user logged in earlier. |
| isEulaAccepted | in | Boolean | Optional | Indicates whether to accept the End User License |
|  |  |  |  | Agreement (EULA) for an upgrade. Once the EULA |
|  |  |  |  | is accepted, users can upload product licenses and |
|  |  |  |  | configure the system, or both. Values are: |
|  |  |  |  | . true - Accept the EULA .. |
|  |  |  |  | . false - Do not accept the EULA. |
| isAutoFailbackEnabled | in | Boolean | Optional | Indicates whether to enable the automatic failback |
|  |  |  |  | of NAS servers in the system. Values are: |
|  |  |  |  | . true - Enable the automatic failback of NAS |
|  |  |  |  | servers. |
|  |  |  |  | . false - Disable the automatic failback of NAS |
|  |  |  |  | servers. |
| isRemoteSysInterfaceAutoPair | in | Boolean | Optional | Indicates whether remote system interface |
|  |  |  |  | automatic pairing is enabled for the system. Values |
|  |  |  |  | are: |
|  |  |  |  | . true - Remote system interface automatic |
|  |  |  |  | pairing is enabled. |
|  |  |  |  | . false - Remote system interface automatic |
|  |  |  |  | pairing is disabled. |

# systemInformation

### Contact information for storage system.

Supported operations

Collection query , Instance query ,Modify

#### Attributes

| Attribute | Type | Description |
| --- | --- | --- |
| id | String | Unique identifier of the systemInformation instance. |
| contactFirstName | String | Contact first name for the storage system. |
| contactLastName | String | Contact last name for the storage system. |
| contactCompany | String | Contact company name for the storage system. |
| contactPhone | String | Phone number for the person who should be contacted by the |
|  |  | service provider for service issues. |
| contactEmail | String | Contact email address for the storage system. |
| locationName | String | The physical location of this system within the user's environment. |
|  |  | For example: Building C, lab 5, tile C25 |
| streetAddress | String | Street address for the storage system. |
| city | String | City where the storage system resides. |
| state | String | State where the storage system resides. |
| zipcode | String | Zip code or postal code where the storage system resides. -- eng |
|  |  | Zip Code is not currently supported by the ESRS VE system |
|  |  | information api |
| country | String | Country where the storage system resides. |
| siteld | String | The ID identifying the site where this system is installed. |
| contactMobilePhone | String | Mobile phone number for the person who should be contacted by |
|  |  | the service provider for service issues. |

### Query all members of the systemInformation collection

| Header | Accept: application/json |
| --- | --- |
|  | Content - Type: application/json |
| Method and URI GET | /api/types/systemInformation/instances |
| None Request body arguments |  |
|  | 200 OK |
| Successful return status |  |
| Successful response body | JSON representation of all members of the systemInformation |
|  | collection. |

## Query a specific systemInformation instance

| Header | Accept: application/json |
| --- | --- |
|  | Content - Type: application/json |
| Method and URI | GET /api/instances/systemInformation/<id> |
|  | where <id> is the unique identifier of the systemInformation instance to query. |
| Request body arguments | None |
| Successful return status | 200 OK |
| Successful response body | JSON representation of a specific systemInformation instance. |

# Modify operation

Modify cotact and location information for the storage system displayed in Unisphere Central.

| Header | Accept: application/json |
| --- | --- |
|  | Content - Type: application/json |
| Method and URI | POST /api/instances/systemInformation/<id>/action/modify |
|  | where <id> is the unique identifier of the systemInformation instance. |
| Request body arguments | See the arquments table below. |
| Successful return status | 204 No Content, 202 Accepted (async response) |
| Successful response body | No body content. |

#### Arguments for the Modify operation

| Argument | In/ out | Type | Required? | Description |
| --- | --- | --- | --- | --- |
| contactFirstName | in | String | Optional |  |
| contactLastName | in | String | Optional |  |
| contactEmail | in | String | Optional |  |
| contactPhone | in | String | Optional |  |
| locationName | in | String | Optional |  |
| contactMobilePhone | in | String | Optional |  |
