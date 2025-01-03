# **pool**

#### Information about pools in the storage system.

**Creating pools using Quick Start mode**

You can use Quick Start mode to create system recommended pools based on the type and availability of drives in the system. In Quick Start mode, the system recommends separate pools for different drive types and uses default RAID configurations for the drives. A pool configured in Quick Start mode has only one tier.

Quick Start mode is available when both of these conditions are met:

No pools exist on the system.

The system is not licensed for FAST VP or FAST Cache.

To create pools using Quick Start mode, follow these steps:

- 1. Run POST api/types/pool/action/recommendAutoConfiguration.
The response body contains a set of poolSetting instances.

2. For each poolSetting instance returned in Step 1, run POST /api/types/pool/instances with the following arguments, using values obtained from the poolSetting instance:

addRaidGroupParameters : [{dskGroup : poolSetting.storageConfiguration.possibleStorageConfigurations.diskGroup,

numDisks : poolSetting.storageConfiguration.possibleStorageConfigurations.raidGroupConfigurations.diskCount,

- raidType : poolSetting.storageConfiguration.raidType,
stripeWidth : poolSetting.storageConfiguration.possibleStorageConfigurations.raidGroupConfigurations.stripeWidths},...]

Pool creation examples: Simple pool with one RAID5 4+1: POST /api/types/pool/instances {"name" : "PerformancePool", "addRaidGroupParameters" : [ {"dskGroup" : {"id" : dg_15}, "numDisks" : 6, "raidType" : 1, "stripeWidth" : 5} ] }

## Pool with raid group RAID10 1+1:

{"name" : "SysDefPool00", "description" : "The pool is created with RAID10(1+1)", "addRaidGroupParameters" : [ {"dskGroup" : {"id" : "dg_16"}, "numDisks" : 5, "raidType" : 7, "stripeWidth" : 2} ] }

#### **Embedded resource types**

poolConfiguration, poolFASTVP, poolRaidStripeWidthInfo, poolTier

# **Supported operations**

Collection query , Instance query ,Create ,Delete ,Modify ,RecommendAutoConfiguration ,StartRelocation ,StopRelocation ,GetStorageTierConfiguration ,GetStorageTierConfigurationsForDynamicPool

#### **Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| id | String | Unique identifier of the pool instance. |
| health | health | Health information for the pool, as defined by the |
|  |  | health resource type. |
| name | String[1..85] | Pool name, unique in the storage system. |

| description | String[0 .. 170] | Pool description. |
| --- | --- | --- |
| raidType | RaidTypeEnum | RAID type with which the pool is configured. A value of |
|  |  | Mixed indicates that the pool consists of multiple RAID |
|  |  | types. |
| sizeFree | unsigned Integer[64(bytes)] | Size of free space available in the pool. |
| size Total | unsigned Integer[64(bytes)] | The total size of space from the pool, which will be the |
|  |  | sum of sizeFree, sizeUsed and sizePreallocated |
|  |  | space. |
| sizeUsed | unsigned Integer[64(bytes)] | Space allocated from the pool by storage resources, |
|  |  | used for storing data. This will be the sum of the sizeAllocated values of each storage resource in the |
|  |  | pool. |
| sizePreallocated | unsigned Integer[64(bytes)] | Space reserved form the pool by storage resources, |
|  |  | for future needs to make writes more efficient. The |
|  |  | pool may be able to reclaim some of this if space is running low. This will be the sum of the |
|  |  | sizePreallocated values of each storage resource in |
|  |  | the pool. |
| dataReductionSizeSaved | unsigned Integer[64(bytes)] | Amount of space saved for the pool by data reduction |
|  |  | (includes savings from compression, deduplication and |
|  |  | advanced deduplication). |
| dataReductionPercent | unsigned Integer[16(percent)] | Data reduction percentage is the percentage of the |
|  |  | data that does not consume storage - the savings due |
|  |  | to data reduction. For example, if 1 TB of data is stored in 250 GB, the data reduction percentage is |
|  |  | 75%. 75% data reduction percentage is equivalent to a |
|  |  | 4:1 data reduction ratio. |
| dataReductionRatio | Float | Data reduction ratio. The data reduction ratio is the |
|  |  | ratio between the size of the data and the amount of |
|  |  | storage actually consumed. For example, 1TB of data |
|  |  | consuming 250GB would have a ration of 4:1. A 4:1 |
|  |  | data reduction ratio is equivalent to a 75% data |
|  |  | reduction percentage. |
| flashPercentage | unsigned Integer[16(percent)] | Pool flash tier percentage |
| sizeSubscribed | unsigned Integer[64(bytes)] | Size of space requested by the storage resources |
|  |  | allocated in the pool for possible future allocations. If |
|  |  | this value is greater than the total size of the pool, the |
|  |  | pool is considered oversubscribed. |
| alertThreshold | unsigned Integer[32(percent)] | Threshold at which the system generates notifications |
|  | [50..84] | about the size of free space in the pool, specified as a |
|  |  | percentage. |
|  |  | storage in the pool compared to the total pool size. |
| hasDataReductionEnabledLuns | Boolean | (Applies if Data Reduction is supported on the system |
|  |  | and the corresponding license is installed.) Indicates |
|  |  | whether the pool has any Lun that has data reduction |
|  |  | ever turned on: Values are: |
|  | ● | true - Lun(s) in this pool have had or currently |
|  |  | have data reduction enabled. |
|  |  | reduction enabled. |
| hasDataReductionEnabledFs | Boolean | (Applies if Data Reduction is supported on the system |
|  |  | and the corresponding license is installed.) Indicates |
|  |  | whether the pool has any File System that has data |
|  |  | reduction ever turned on; Values are. |
|  | . | true - File system(s) in this pool have had or |
|  |  | currently have data reduction enabled. |
|  | . |  |
|  |  | data reduction enabled. |
| isFASTCacheEnabled | Boolean | (Applies if FAST Cache is supported on the system |
|  |  | and the corresponding license is installed.) Indicates |
|  |  | whether the FAST Cache is enabled for the pool. |
|  |  | Values are: |
|  | . | true - FAST Cache is enabled for the pool. |
|  |  | FAST Cache is created from Flash SAS drives and |
|  |  | applied only to RAID groups created of SAS and NL-SAS hard drives. If the pool is populated by |
|  |  | purely Flash drives the FAST Cache is not enabled. |
|  |  | type. |
| creationTime | DateTime | Date and time when the pool was created. |
| isEmpty | Boolean |  |
|  |  | Indicates whether the pool is unused; that is, whether |
|  |  | are: |
|  | . | true - Pool is unused. |
|  | . | false - Pool is used .. |
| poolFastVP | poolFASTVP | (Applies if FAST VP is supported on the system and |
|  |  | the corresponding license is installed.) FAST VP |
|  |  | resource type. Pool is not eligible to be a multi-tier pool |
|  |  | This threshold is based on the percentage of allocated |
|  | . | false - No lun(s) in this pool have ever had data |
|  |  | false - No file system(s) in this pool have ever had |
|  | . | false - FAST Cache is disabled for the pool. |
| tiers | List< poolTier> | Tiers in the pool, as defined by the poolTier resource |
|  |  | it has no storage resources provisioned from it. Values |
|  |  | information for the pool, as defined by the poolFastVP |

|  |  | until FAST VP license installed. |
| --- | --- | --- |
| isHarvestEnabled | Boolean | Indicates whether the automatic deletion of snapshots |
|  |  | through pool space harvesting is enabled for the pool. |
|  |  | See properties poolSpaceHarvestHighThreshold and |
|  |  | poolSpaceHarvestLowThreshold. Values are: |
|  |  | ● true - Automatic deletion of snapshots through |
|  |  | pool harvesting is enabled for the pool. |
|  |  | . false - Automatic deletion of snapshots through |
|  |  | pool harvesting is disabled for the pool. |
| harvestState | UsageHarvestStateEnum | Current state of pool space harvesting. |
| isSnapHarvestEnabled | Boolean | Indicates whether the automatic deletion of snapshots through snapshot harvesting is enabled for the pool. |
|  |  | See properties snapSpaceHarvestHighThreshold and |
|  |  | snapSpaceHarvestLowThreshold. Values are: |
|  |  | . true - Automatic deletion of snapshots through |
|  |  | snapshot harvesting is enabled for the pool. |
|  |  | ● false - Automatic deletion of snapshots through |
|  |  | snapshot harvesting is disabled for the pool. |
| poolSpaceHarvestHighThreshold | Float | (Applies when the automatic deletion of snapshots |
|  |  | based on pool space usage is enabled for the system |
|  |  | and pool.) |
|  |  | Pool used space high threshold at which the system |
|  |  | automatically starts to delete snapshot objects in the pool, specified as a percentage with .01% granularity. |
|  |  | This threshold is based on the percentage of space used in the pool by all types of objects compared to |
|  |  | the total pool size. When the percentage of used space reaches this threshold, the system starts to |
|  |  | automatically delete snapshot objects in the pool, until |
|  |  | a low threshold (see poolSpaceHarvestLowThreshold) |
|  |  | is reached. |
| poolSpaceHarvestLowThreshold | Float | (Applies when the automatic deletion of snapshots |
|  |  | based on pool space usage is enabled for the system and pool.) |
|  |  | Pool used space low threshold under which the system stops automatically deleting snapshots in the |
|  |  | pool, specified as a percentage with .01% granularity. |
|  |  | This threshold is based on the percentage of space |
|  |  | used in the pool by all types of objects compared to |
|  |  | the total pool size. When the percentage of used |
|  |  | space in the pool falls below this threshold, the system |
|  |  | stops the automatic deletion of snapshot objects in the |
|  |  | pool, until a high threshold (see |
|  |  | poolSpaceHarvestHighThreshold) is reached again. |
| snapSpaceHarvestHighThreshold | Float | (Applies when the automatic deletion of snapshots |
|  |  | based on snapshot space usage is enabled for the |
|  |  | system and pool.) |
|  |  | Space used by snapshot objects high threshold at |
|  |  | which the system automatically starts to delete |
|  |  | snapshot objects in the pool, specified as a |
|  |  | percentage with .01% granularity. |
|  |  | This threshold is based on the percentage of space |
|  |  | used in the pool by snapshot objects only compared to |
|  |  | the total pool size. When the percentage of space |
|  |  | used by snapshots reaches this threshold, the system |
|  |  | automatically starts to delete snapshots in the pool, |
|  |  | until a low threshold (see |
|  |  | snapSpaceHarvestLowThreshold) is reached. Note |
|  |  | that if Base LUN has Thin Clones its snapshot space doesn't affect this threshold. |
| snapSpaceHarvestLowThreshold | Float |  |
|  |  | (Applies when the automatic deletion of snapshots based on snapshot space usage is enabled for the |
|  |  | system and pool.) |
|  |  | Space used by snapshot objects low threshold under |
|  |  | which the system automatically stops deleting |
|  |  | snapshots in the pool, specified as a percentage with |
|  |  | .01% granularity. |
|  |  | This threshold is based on the percentage of space |
|  |  | used in the pool by snapshots only compared to the total pool size. When the percentage of pool space |
|  |  | used by snapshot objects falls below this threshold, |
|  |  | the system automatically stops deletion of snapshots |
|  |  | in the pool, until a high threshold (see |
|  |  | snapSpaceHarvestHighThreshold) is reached again. |
|  |  | Note that if Base LUN has Thin Clones its snapshot |
|  |  | space doesn't affect this threshold. |
| metadataSizeSubscribed | unsigned Integer[64(bytes)] | Size of pool space subscribed for metadata. |
| snapSizeSubscribed | unsigned Integer[64(bytes)] | Size of pool space subscribed for snapshots. |
| nonBaseSizeSubscribed | unsigned Integer[64(bytes)] | Size of pool space subscribed for thin clones and |
|  |  | snapshots |
| metadataSizeUsed | unsigned Integer[64(bytes)] | Size of pool space used by metadata. |
| snapSizeUsed | unsigned Integer[64(bytes)] | Size of pool space used by snapshots. |

| nonBaseSizeUsed | unsigned Integer[64(bytes)] | Size of pool space used for thin clones and snapshots |
| --- | --- | --- |
| rebalanceProgress | unsigned Integer[16(percent)] | (Applies if FAST VP is supported on the system and |
|  |  | the corresponding license is installed.) Percent of work |
|  |  | completed for data rebalancing. |
| type | StoragePoolTypeEnum | Indicates type of this pool. Values are: |
|  |  | . Dynamic - It is dynamic pool. |
|  |  | . Traditional - It is traditional pool. |
| isAllFlash | Boolean | Indicates whether this pool contains only Flash drives. |
|  |  | Values are: |
|  |  | . true - It is an all Flash pool. |
|  |  | . false - This pool contains drives other than Flash |
|  |  | drives. |

Attributes for poolConfiguration

System-recommended pool configuration settings. Instances of this resource type contain the output of the pool resource type's RecommendAutoConfiguration operation

| Attribute | Type | Description |
| --- | --- | --- |
| name | String | Pool name. |
| description | String |  |
|  |  | Pool description. |
| storageConfiguration | storageTierConfiguration | Recommended configuration of the storage tier in the |
|  |  | recommended pool, as defined by the |
|  |  | storageCapabilityEstimation resource type. |
| alertThreshold | unsigned Integer[32(percent)] | Threshold at which the system will generate |
|  |  | notifications about the amount of space remaining in |
|  |  | the pool, specified as a percentage with 1% |
|  |  | granularity. |
|  |  | This threshold is based on the percentage of allocated |
|  |  | storage in the pool compared to the total pool size. |
| poolSpaceHarvestHighThreshold | Float | (Applies when the automatic deletion of snapshots |
|  |  | based on pool space usage is enabled for the system |
|  |  | and pool.) |
|  |  | Pool used space high threshold at which the system |
|  |  | will automatically delete snapshots in the pool, specified as a percentage with .01% granularity. |
|  |  | This threshold is based on the percentage of used |
|  |  | space in the pool compared to the total pool size. |
|  |  | When the percentage of used space reaches this threshold, the system automatically deletes snapshots |
|  |  | in the pool, until a low threshold is reached. |
| poolSpaceHarvestLowThreshold | Float | (Applies when the automatic deletion of snapshots |
|  |  | based on pool space usage is enabled for the system |
|  |  | and pool.) |
|  |  | Pool used space low threshold under which the |
|  |  | system will stop automatically deleting snapshots in |
|  |  | the pool, specified as a percentage with .01% |
|  |  | granularity. |
|  |  | This threshold is based on the percentage of used |
|  |  | pool space compared to the total pool size. When the |
|  |  | percentage of used space in the pool falls below this |
|  |  | threshold, the system stops the automatic deletion of |
|  |  | snapshots in the pool, until a high threshold is |
|  |  | reached. |
| snapSpaceHarvestHighThreshold | Float | (Applies when the automatic deletion of snapshots |
|  |  | based on snapshot space usage is enabled for the |
|  |  | system and the pool.) |
|  |  | Snapshot used space high threshold at which the |
|  |  | system will automatically delete snapshots in the pool, |
|  |  | specified as a percentage with .01% granularity. |
|  |  | This threshold is based on the percentage of space |
|  |  | used by pool snapshots compared to the total pool |
|  |  | size. When the percentage of space used by |
|  |  | snapshots reaches this threshold, the system |
|  |  | automatically deletes snapshots in the pool, until a low |
|  |  | threshold is reached. |
| snapSpaceHarvestLowThreshold | Float | (Applies when the automatic deletion of snapshots |
|  |  | based on snapshot space usage is enabled for the |
|  |  | system and the pool.) |
|  |  | Snapshot used space low threshold under which the |
|  |  | system will stop automatically delete snapshots in the |
|  |  | pool, specified as a percentage with .01% granularity. |
|  |  | This threshold is based on the percentage of space |
|  |  | used by pool snapshots compared to the total pool |
|  |  | size. When the percentage of space used by pool |
|  |  | snapshots falls below this threshold, the system stops |
|  |  | the automatic deletion of snapshots in the pool, until a |
|  |  | high threshold is reached. |
| isFastCacheEnabled | Boolean | (Applies if a FAST Cache license is installed on the |
|  |  | system.) Indicates whether the pool will be used in the |
|  |  | FAST Cache. Values are: |

|  |  | . true - FAST Cache will be enabled for this pool. |
| --- | --- | --- |
|  |  | . false - FAST Cache will be disabled for this pool. |
| isFASTVpScheduleEnabled | Boolean | (Applies if a FAST VP license is installed on the |
|  |  | storage system.) Indicates whether to enable |
|  |  | scheduled data relocations for the pool. Values are: |
|  |  | . true - Enable scheduled data relocations for the |
|  |  | pool. |
|  |  | ● false - Disable scheduled data relocations for the |
|  |  | pool. |
| isDiskTechnologyMixed | Boolean | Indicates whether the pool contains drives with |
|  |  | different drive technologies, such as FLASH, SAS and |
|  |  | NL-SAS. Values are: |
|  |  | . true - Pool contains drives with different drive |
|  |  | technologies. |
|  |  | . false - Pool does not contain drives with different |
|  |  | drive technologies. |
| maxSizeLimit | unsigned Integer[64(bytes)] | Maximum pool capacity recommended for the storage |
|  |  | system. |
| maxDiskNumberLimit | unsigned Integer[32] | Maximum number of drives recommended for the |
|  |  | storage system. |
| isMaxSizeLimitExceeded | Boolean | Indicates whether the total size of all recommended |
|  |  | pools exceeds that allowed by the storage system. |
|  |  | Values are: |
|  |  | . true - Total size of all recommended pools |
|  |  | exceeds that allowed by the storage system. |
|  |  | . false - Total size of all recommended pools does |
|  |  | not exceed that alllowed by the storage system. |
| isMaxDiskNumberLimitExceeded | Boolean | Indicates whether the total number of drives in the |
|  |  | recommended pools exceeds that allowed by the |
|  |  | storage system. Values are: |
|  |  | . true - Total size of all recommended pools |
|  |  | exceeds that allowed by the storage system. |
|  |  | . false - Total size of all recommended pools does |
|  |  | not exceed that alllowed by the storage system. |
| isRPMMixed | Boolean | Indicates whether the pool contains drives with |
|  |  | different rotational speeds. Values are: |
|  |  | . true - Pool contains drives with different rotational |
|  |  | speeds. |
|  |  | . false - Pool does not contain drives with different |
|  |  | rotational speeds. |

# Attributes for poolFASTVP

(Applies it FAST VP is supported on the system and the corresponding license is installed) EAST VP settings for the pool associated with this embedied type

| Attribute | Type | Description |
| --- | --- | --- |
| status | FastVPStatusEnum | Data relocation status. |
| relocationRate | FastVPRelocationRateEnum | Data relocation rate. |
| isScheduleEnabled | Boolean | Indicates if scheduled data relocations are enabled: |
|  |  | . true - Scheduled data relocations are enabled. |
|  |  | . false - Scheduled data relocations are disabled. |
| relocationDurationEstimate | Date Time[Interval] | Estimated time required for the data relocation. |
| sizeMovingDown | unsigned Integer[64(bytes)] | Size of data to move to a lower tier. This value is 0 for a |
|  |  | single tier pool. |
| sizeMovingUp | unsigned Integer[64(bytes)] | Size of data to move to higher tier. This value is 0 for a |
|  |  | single tier pool. |
| sizeMovingWithin | unsigned Integer[64(bytes)] | Size of data to move within a tier. |
| percentComplete | unsigned Integer[16] | Percent of data relocated so far in the relocation process. |
| type | PoolDataRelocationTypeEnum | Data relocation type. |
| dataRelocated | unsigned Integer[64(bytes)] | Size of data relocated. For a completed data relocation, |
|  |  | this is the total size of data relocated since the last data |
|  |  | relocation session. |
| lastStartTime | Date Time | Time of day to start scheduled data relocations. |
| lastEndTime | Date Time | Time of day at which scheduled data relocations should |
|  |  | end. |

#### Attributes for poolRaidStripeWidthInfo

(Applies to dynamic pools only) Information about the stripe width info in the pool

| Attribute | Type | Description |
| --- | --- | --- |
| rpm | unsigned Integer[32(rpm)] | Revolutions Per Minute (RPMs). |
| stripeWidth | RaidStripeWidthEnum | RAID stripe width of the drives in the raid stripe info. |
| driveTechnology | DiskTechnologyEnum | Drive technology in the raid stripe info. |

| driveCount | unsigned Integer[32] | The number of physical drives in the raid stripe info. |
| --- | --- | --- |
| parityDrives | unsigned Integer[32] | The number of parity drives in the raid stripe info. |

# Attributes for poolTier

Information about the tiers in the pool

| Attribute | Type | Description |
| --- | --- | --- |
| tierType | TierTypeEnum | Tier type. |
| stripeWidth | RaidStripeWidthEnum | RAID stripe width of the drives in the tier. |
| raidType | RaidTypeEnum | RAID type of the drives in the tier. |
| sizeTotal | unsigned Integer[64(bytes)] | Total size of space in the tier. |
| sizeUsed | unsigned Integer[64(bytes)] | Size of used space in the tier. |
| sizeFree | unsigned Integer[64(bytes)] | Size of free space in the tier. |
| sizeMovingDown | unsigned Integer[64(bytes)] | Size of data scheduled to be moved to a lower tier. This value is 0 |
|  |  | for a single-tier pool. |
| sizeMovingUp | unsigned Integer[64(bytes)] | Amount of data scheduled to be moved to a higher tier. This |
|  |  | value is 0 for a single tier pool. |
| sizeMovingWithin | unsigned Integer[64(bytes)] | Amount of data to be rebalanced within the tier. |
| name | String | Name of the pool. |
| poolUnits | List < poolUnit> | List of Pool Units, i.e. raidGroup and virtualDisk objects, in the |
|  |  | tier. |
| diskCount | unsigned Integer[32] | The number of physical drives in the tier. |
| spareDriveCount | unsigned Integer[32] | The drive number of hot spare space for dynamic pool. |
| raidStripeWidthInfo | List<poolRaidStripeWidthInfo> | (Applies to dynamic pools only and the corresponding license is installed.) Raid Stripe Width Info in the pool, as defined by the |
|  |  | poolRaidStripeWidthInfo resource type. |

#### Querv all members of the pool collection

| Header | Accept: application/json |
| --- | --- |
|  | Content - Type: application/json |
| Method and URI | GET /api/types/pool/instances |
| Request body arguments | None |
| Successful return status | 200 OK |
| Successful response body | JSON representation of all members of the pool collection. |

# Query a specific pool instance

| Header | Accept: application/json |
| --- | --- |
|  | Content - Type: application/json |
| Method and URI | GET /api/instances/pool/<id> |
|  | where <id> is the unique identifier of the pool instance to query. |
| Or |  |
|  | GET /api/instances/pool/name: < value> |
|  | where <value> is the name of the pool instance to query. |
| Request body arguments | None |
| Successful return status | 200 OK |
| Successful response body | JSON representation of a specific pool instance. |

### Create operation

Create a new pool

| Header | Accept: application/json |
| --- | --- |
|  | Content - Type: application/json |
| Method and URI | POST /api/types/pool/instances |
| Request body arguments | See the arquments table below. |
| Successful return status | 201 Created, 202 Accepted (async response) |
| Successful response body | JSON representation of the <id> attribute |

#### Arquments for the Create operation

| Argument | In/ | Type | Required? | Description |
| --- | --- | --- | --- | --- |
|  | out |  |  |  |
| name | In | String[1.85] | Required | Pool name. |

| description | in | String[0 .. 170] | Optional | Pool description. |
| --- | --- | --- | --- | --- |
| addRaidGroupParameters | in | List < raidGroupParameters> | Optional | Parameters to add RAID |
|  |  |  |  | groups to the pool (disk group, |
|  |  |  |  | number of drives, RAID level, |
|  |  |  |  | stripe length: see object |
|  |  |  |  | raidGroupParameters). To |
|  |  |  |  | create a pool with drives of |
|  |  |  |  | different type (SAS Flash, SAS, NL-SAS) FAST VP license is |
|  |  |  |  | required. |
| addPoolUnitParameters | in | List<poolUnitParameters> | Optional | Pool capacity units (now Virtual |
|  |  |  |  | Disks only, see virtualDisk |
|  |  |  |  | object) with associated |
|  |  |  |  | parameters to add to the pool |
|  |  |  |  | without RAID protection. |
| alertThreshold | in | unsigned | Optional | Threshold at which the system |
|  |  | Integer[32(percent)][50.84] |  | will generate alerts about the |
|  |  |  |  | free space in the pool, specified |
|  |  |  |  | as a percentage. |
|  |  |  |  | This threshold is based on the |
|  |  |  |  | percentage of allocated storage |
|  |  |  |  | in the pool compared to the |
|  |  |  |  | total pool size. |
| poolSpaceHarvestHighThreshold | in | Float[32] | Optional | (Applies when the automatic |
|  |  |  |  | deletion of snapshots based on |
|  |  |  |  | pool space usage is enabled for the system and pool.) |
|  |  |  |  | Pool used space high threshold |
|  |  |  |  | at which the system will |
|  |  |  |  | automatically starts to delete snapshots in the pool, specified |
|  |  |  |  | as a percentage with .01% |
|  |  |  |  | granularity. |
|  |  |  |  | This threshold is based on the |
|  |  |  |  | percentage of space used in |
|  |  |  |  | the pool by all types of objects |
|  |  |  |  | compared to the total pool size. |
|  |  |  |  | When the percentage of used |
|  |  |  |  | space reaches this threshold, |
|  |  |  |  | the system automatically starts |
|  |  |  |  | to delete snapshots in the pool, |
|  |  |  |  | until a low threshold is reached. |
| poolSpaceHarvestLowThreshold | in | Float[32] | Optional | (Applies when the automatic |
|  |  |  |  | deletion of snapshots based on |
|  |  |  |  | pool space usage is enabled for |
|  |  |  |  | the system and pool.) |
|  |  |  |  | Pool used space low threshold |
|  |  |  |  | under which the system will |
|  |  |  |  | automatically stop deletion of |
|  |  |  |  | snapshots in the pool, specified |
|  |  |  |  | as a percentage with .01% |
|  |  |  |  | granularity. |
|  |  |  |  | This threshold is based on the |
|  |  |  |  | percentage of space in the pool used by all types of obejcts |
|  |  |  |  | compared to the total pool size. |
|  |  |  |  | When the percentage of used |
|  |  |  |  | space in the pool falls below |
|  |  |  |  | this threshold, the system stops |
|  |  |  |  | the automatic deletion of |
|  |  |  |  | snapshots in the pool, until a |
|  |  |  |  | high threshold is reached |
|  |  |  |  | again. |
| snapSpaceHarvestHighThreshold | in | Float[32] | Optional | (Applies when the automatic |
|  |  |  |  | deletion of snapshots based on |
|  |  |  |  | snapshot space usage is |
|  |  |  |  | enabled for the system and |
|  |  |  |  | pool.) |
|  |  |  |  | Snapshot used space high threshold at which the system |
|  |  |  |  | automatically starts to delete |
|  |  |  |  | snapshots in the pool, specified |
|  |  |  |  | as a percentage with .01% granularity. |
|  |  |  |  | This threshold is based on the |
|  |  |  |  | percentage of pool space used |
|  |  |  |  | by snapshot objects only |
|  |  |  |  | compared with the total pool |
|  |  |  |  | size. When the percentage of |
|  |  |  |  | space used by snapshots |
|  |  |  |  | reaches this threshold, the |
|  |  |  |  | system automatically starts to |
|  |  |  |  | delete snapshots in the pool, until a low threshold is reached. |
| snapSpaceHarvestLowThreshold | in | Float[32] | Optional | (Applies when the automatic |
|  |  |  |  | deletion of snapshots based on snapshot space usage is |
|  |  |  |  | enabled for the system and the |
|  |  |  |  | pool.) |

|  |  |  |  | Snapshot used space low |
| --- | --- | --- | --- | --- |
|  |  |  |  | threshold below which the |
|  |  |  |  | system will stop automatically deleting snapshots in the pool, |
|  |  |  |  | specified as a percentage with |
|  |  |  |  | .01% granularity. |
|  |  |  |  | This threshold is based on the percentage of space used by |
|  |  |  |  | snapshot objects only as |
|  |  |  |  | compared to the total pool size. |
|  |  |  |  | When the percentage of space used by snapshots falls below |
|  |  |  |  | this threshold, the system stops |
|  |  |  |  | automatically deleting |
|  |  |  |  | snapshots in the pool, until a |
|  |  |  |  | high threshold is reached |
|  |  |  |  | again. |
| isHarvestEnabled | in | Boolean | Optional | Indicates whether to enable |
|  |  |  |  | pool space harvesting (the |
|  |  |  |  | automatic deletion of snapshots |
|  |  |  |  | based on pool space usage) for |
|  |  |  |  | the pool. Values are: |
|  |  |  |  | . true - Enable pool harvesting for the pool. |
|  |  |  |  | . false - Disable pool |
|  |  |  |  | harvesting for the pool. |
| isSnapHarvestEnabled | in | Boolean | Optional | Indicates whether to enable |
|  |  |  |  | snapshot harvesting (the |
|  |  |  |  | automatic deletion of snapshots |
|  |  |  |  | based on snapshot space |
|  |  |  |  | usage) for the pool. Values are: |
|  |  |  |  | . true - Enable snapshot |
|  |  |  |  | harvesting for the pool. |
|  |  |  |  | . false - Disable snapshot |
|  |  |  |  | harvesting for the pool. |
| isFASTCacheEnabled | in |  | Optional |  |
|  |  | Boolean |  | (Applies if a FAST Cache |
|  |  |  |  | license is installed on the |
|  |  |  |  | system.) Indicates whether to |
|  |  |  |  | enable the FAST Cache for the |
|  |  |  |  | pool. Values are: |
|  |  |  |  | . |
|  |  |  |  | true - FAST Cache will be |
|  |  |  |  | enabled for this pool. |
|  |  |  |  | . false - FAST Cache will be |
|  |  |  |  | disabled for this pool. |
|  |  |  |  | Only RAID groups created of |
|  |  |  |  | SAS and NL-SAS hard drives |
|  |  |  |  | are eligible for FAST Cache. If |
|  |  |  |  | the pool is populated by only Flash drives this option is not |
|  |  |  |  | allowed. |
| isFASTVpScheduleEnabled | in | Boolean | Optional | (Applies when a FAST VP |
|  |  |  |  | license is installed on the |
|  |  |  |  | system.) Indicates whether to |
|  |  |  |  | enable scheduled data |
|  |  |  |  | relocations for the pool. Values |
|  |  |  |  | are: |
|  |  |  |  | . true - Enable scheduled |
|  |  |  |  | data relocations for the |
|  |  |  |  | pool. |
|  |  |  |  | . false - Disable scheduled |
|  |  |  |  | data relocations for the |
|  |  |  |  | pool. |
| type | in | StoragePoolTypeEnum | Optional | Indicates whether to create |
|  |  |  |  | traditional pool or dynamic |
|  |  |  |  | pool. |
|  |  |  |  | . traditional - Create |
|  |  |  |  | traditional pool. |
|  |  |  |  | . dynamic - Create dynamic |
|  |  |  |  | pool. (default) |
| id | out | pool | N/A | Output parameter for the |
|  |  |  |  | created pool id. The pool object |
|  |  |  |  | with this id may not exist at the |
|  |  |  |  | moment of this method |
|  |  |  |  | complete because this method |
|  |  |  |  | only launches background |
|  |  |  |  | process called Job which is |
|  |  |  |  | actually creating the pool. |

# Delete operation

# Delete a pool.

| Header | Accept: application/json |
| --- | --- |
|  | Content - Type: application/json |
| Method and URI | DELETE /api/instances/pool/<id> |
|  | where <id> is the unique identifier of the pool instance to delete. |
| Or |  |
|  | DELETE /api/instances/pool/name: < value> |

|  | where <value> is the name of the pool instance to delete. |
| --- | --- |
| Request body arguments | None |
| Successful return status | 204 No Content, 202 Accepted (async response) |
| Successful response body | No body content. |

#### Modify operation

Modifies the existing pool: allows to expand pool capacity and/or modify different parameters of the pool.

| Header | Accept: application/json |
| --- | --- |
|  | Content - Type: application/json |
| Method and URI | POST /api/instances/pool/<id>/action/modify |
|  | where <id> is the unique identifier of the pool instance. |
|  | Or |
|  | POST /api/instances/pool/name: < value>/action/modify |
|  | where < value> is the name of the pool instance. |
| Request body arguments | See the arquments table below. |
| Successful return status | 204 No Content, 202 Accepted (async response) |
|  | No body content. |
| Successful response body |  |

## Arguments for the Modify operation

| Argument | In/ | Type | Required? | Description |
| --- | --- | --- | --- | --- |
|  | out |  |  |  |
| name | in | String[1.. 85] | Optional | Pool new name. |
| description | in | String[0 .. 170] | Optional | Pool new description. |
| addRaidGroupParameters | in | List<raidGroupParameters> | Optional | Parameters to add RAID |
|  |  |  |  | groups to the pool (disk group, |
|  |  |  |  | number of drives, RAID level, |
|  |  |  |  | stripe length). If the expansion |
|  |  |  |  | of the single-tier pool makes it multi-tier pool then FAST VP |
|  |  |  |  | license is required to be |
|  |  |  |  | installed on the system. |
| addPoolUnitParameters | in | List<poolUnitParameters> | Optional | Pool capacity units (now Virtual |
|  |  |  |  | Disks only) with associated |
|  |  |  |  | parameters to add to the pool |
|  |  |  |  | without RAID protection. |
| alertThreshold | in | unsigned | Optional |  |
|  |  | Integer[32(percent)][50.84] |  |  |
| poolSpaceHarvestHighThreshold | in | Float[32] | Optional | (Applies when the automatic |
|  |  |  |  | deletion of snapshots based on |
|  |  |  |  | pool space usage is enabled for |
|  |  |  |  | the system and pool.) |
|  |  |  |  | Pool used space high threshold |
|  |  |  |  | at which the system will |
|  |  |  |  | automatically starts to delete |
|  |  |  |  | snapshots in the pool, specified |
|  |  |  |  | as a percentage with .01% |
|  |  |  |  | granularity. |
|  |  |  |  | This threshold is based on the |
|  |  |  |  | percentage of space used in |
|  |  |  |  | the pool by all types of objects |
|  |  |  |  | compared to the total pool size. |
|  |  |  |  | When the percentage of used |
|  |  |  |  | space reaches this threshold, |
|  |  |  |  | the system automatically starts |
|  |  |  |  | to delete snapshots in the pool, |
|  |  |  |  | until a low threshold is reached. |
| poolSpaceHarvestLowThreshold | in | Float[32] | Optional | (Applies when the automatic |
|  |  |  |  | deletion of snapshots based on |
|  |  |  |  | pool space usage is enabled for |
|  |  |  |  | the system and pool.) |
|  |  |  |  | Pool used space low threshold |
|  |  |  |  | under which the system will |
|  |  |  |  | automatically stop deletion of |
|  |  |  |  | snapshots in the pool, specified |
|  |  |  |  | as a percentage with .01% granularity. |
|  |  |  |  | This threshold is based on the |
|  |  |  |  | percentage of space in the pool |
|  |  |  |  | used by all types of obejcts |
|  |  |  |  | compared to the total pool size. |
|  |  |  |  | When the percentage of used |
|  |  |  |  | space in the pool falls below |
|  |  |  |  | this threshold, the system stops |
|  |  |  |  | the automatic deletion of |
|  |  |  |  | snapshots in the pool, until a |
|  |  |  |  | high threshold is reached |
|  |  |  |  | again. |

| snapSpaceHarvestHighThreshold | in | Float[32] | Optional | (Applies when the automatic |
| --- | --- | --- | --- | --- |
|  |  |  |  | snapshot space usage is |
|  |  |  |  | deletion of snapshots based on |
|  |  |  |  | enabled for the system and |
|  |  |  |  | pool.) |
|  |  |  |  | Snapshot used space high |
|  |  |  |  | threshold at which the system |
|  |  |  |  | automatically starts to delete snapshots in the pool, specified |
|  |  |  |  | as a percentage with .01% |
|  |  |  |  | granularity. |
|  |  |  |  | This threshold is based on the |
|  |  |  |  | percentage of pool space used |
|  |  |  |  | by snapshot objects only compared with the total pool |
|  |  |  |  | size. When the percentage of |
|  |  |  |  | space used by snapshots reaches this threshold, the |
|  |  |  |  | system automatically starts to |
|  |  |  |  | delete snapshots in the pool, |
|  |  |  |  | until a low threshold is reached. |
| snapSpaceHarvestLowThreshold | in | Float[32] | Optional | (Applies when the automatic |
|  |  |  |  | deletion of snapshots based on |
|  |  |  |  | snapshot space usage is |
|  |  |  |  | enabled for the system and the |
|  |  |  |  | pool.) |
|  |  |  |  | Snapshot used space low |
|  |  |  |  | threshold below which the system will stop automatically |
|  |  |  |  | deleting snapshots in the pool, |
|  |  |  |  | specified as a percentage with |
|  |  |  |  | .01% granularity. |
|  |  |  |  | This threshold is based on the |
|  |  |  |  | percentage of space used by |
|  |  |  |  | snapshot objects only as compared to the total pool size. |
|  |  |  |  | When the percentage of space |
|  |  |  |  | used by snapshots falls below |
|  |  |  |  | this threshold, the system stops |
|  |  |  |  | automatically deleting |
|  |  |  |  | snapshots in the pool, until a |
|  |  |  |  | high threshold is reached |
|  |  |  |  | again. |
| isHarvestEnabled | in | Boolean | Optional | Indicates whether to enable |
|  |  |  |  | pool space harvesting (the automatic deletion of snapshots |
|  |  |  |  | based on pool space usage) for |
|  |  |  |  | the pool. Values are: |
|  |  |  |  | . true - Enable pool |
|  |  |  |  | harvesting for the pool. |
|  |  |  |  | . false - Disable pool |
|  |  |  |  | harvesting for the pool. |
| isSnapHarvestEnabled | in | Boolean | Optional | Indicates whether to enable |
|  |  |  |  | snapshot harvesting (the |
|  |  |  |  | automatic deletion of snapshots |
|  |  |  |  | based on snapshot space |
|  |  |  |  | usage) for the pool. Values are: |
|  |  |  |  | . true - Enable snapshot |
|  |  |  |  | harvesting for the pool. |
|  |  |  |  | . false - Disable snapshot |
|  |  |  |  | harvesting for the pool. |
| isFASTCacheEnabled | in | Boolean | Optional | (Applies if a FAST Cache |
|  |  |  |  | license is installed on the |
|  |  |  |  | system.) Indicates whether to |
|  |  |  |  | enable the FAST Cache for the |
|  |  |  |  | pool. Values are: |
| isFASTVpScheduleEnabled | in | Boolean | Optional | (Applies when a FAST VP |
|  |  |  |  | license is installed on the |
|  |  |  |  | system.) Indicates whether to |
|  |  |  |  | enable scheduled data |
|  |  |  |  | relocations for the pool. Values |
|  |  |  |  | are: |
|  |  |  |  | . true - Enable scheduled |
|  |  |  |  | data relocations for the |
|  |  |  |  | pool. |
|  |  |  |  | . false - Disable scheduled |
|  |  |  |  | data relocations for the |
|  |  |  |  | pool. |

# RecommendAutoConfiguration operation

Recommend a list of pool configurations for the storage system.

| Header | Accept: application/json |
| --- | --- |
|  | Content - Type: application/json |
| Method and URI | POST /api/types/pool/action/recommendAutoConfiguration |
| Request body arguments | See the arquments table below. |
| Successful return status | 200 OK |

# Arguments for the RecommendAutoConfiguration operation

| Arqument | In/ | Type | Required? | Description |
| --- | --- | --- | --- | --- |
|  | out |  |  |  |
| poolConfigurations | out | List< poolConfiguration> | N/A | The list of recommended pool configurations, as |
|  |  |  |  | defined by the poolSetting type. |

### StartRelocation operation

(Applies if FAST VP is supported on the system and the corresponding license is installed.) Initiate data relocation on the pool.

| Header | Accept: application/json |
| --- | --- |
|  | Content - Type: application/json |
| Method and URI | POST /api/instances/pool/ <id> /action/startRelocation |
|  | where <id> is the unique identifier of the pool instance. |
|  | Or |
|  | POST /api/instances/pool/name : < value>/action/startRelocation |
|  | where < value> is the name of the pool instance. |
| Request body arguments | See the arquments table below. |
| Successful return status | 204 No Content, 202 Accepted (async response) |
| Successful response body | No body content. |

#### Arguments for the StartRelocation operation

| Arqument | In/ | Type | Required? | Description |
| --- | --- | --- | --- | --- |
|  | out |  |  |  |
| endTime | in | DateTime[Interval - h+:mm:ss[.sss]] | Optional | Date and time at which to stop the data relocation operation. |
|  |  |  |  | [The value of interval will be |
|  |  |  |  | rounded down to minutes.] |
| relocationRate | in | FastVPRelocationRateEnum | Optional | Data relocation rate. |

### StopRelocation operation

(Applies if FAST VP is supported on the system and the corresponding license is installed.) Stop data relocation on the pool.

| Header | Accept: application/json |
| --- | --- |
|  | Content - Type: application/json |
| Method and URI | POST /api/instances/pool/<id>/action/stopRelocation |
|  | where <id> is the unique identifier of the pool instance. |
|  | Or |
|  | POST /api/instances/pool/name:<value>/action/stopRelocation |
|  | where < value> is the name of the pool instance. |
| Request body arguments | None |
| Successful return status | 204 No Content, 202 Accepted (async response) |
| Successful response body | No body content. |

### GetStorageTierConfiguration operation

Return all possible RAID configurations for the specified tier type, RAID type, stripe width, for a specific pool. Applied to traditional pools only

| Header | Accept: application/json |
| --- | --- |
|  | Content - Type: application/json |
| Method and URI | POST /api/instances/pool/<id>/action/getStorageTierConfiguration |
|  | where <id> is the unique identifier of the pool instance. |
|  | Or |
|  | POST /api/instances/pool/name: |
|  | <value>/action/getStorageTierConfiguration |
|  | where < value> is the name of the pool instance. |
| Request body arguments | See the arquments table below. |
| Successful return status | 200 OK |
| Successful response body | JSON representation of the returned attributes. |

Arguments for the GetStorageTierConfiguration operation

| Argument | In/ | Type | Required? | Description |
| --- | --- | --- | --- | --- |
|  | out |  |  |  |
| tierType | in | TierTypeEnum | Required | Type of the tier. |
| raidType | in | RaidTypeEnum | Required | Preferred RAID type (RAID level) for the |

|  |  |  |  | storage tier. |
| --- | --- | --- | --- | --- |
| stripeWidth | in | RaidStripeWidthEnum | Required | Preferred RAID stripe width (RAID modulus) for |
|  |  |  |  | the tier. |
| storageConfiguration | out | storageTierConfiguration | N/A | All possible configurations for the tier, as |
|  |  |  |  | defined by the storageTierConfiguration |
|  |  |  |  | embedded object. |

# GetStorageTierConfigurationsForDynamicPool operation

Return all oossible RAID configurations for the parameters which specify tier type, RAID type, stripe width, for a specific pool. Applied to dynamic pools only,

| Header | Accept: application/json |
| --- | --- |
|  | Content - Type: application/json |
| Method and URI | POST |
|  | /api/instances/pool/<id>/action/getStorageTierConfigurationsForDynamicPool |
|  | where <id> is the unique identifier of the pool instance. |
|  | Or |
|  | POST /api/instances/pool/name: |
|  | <value>/action/getStorageTierConfigurationsForDynamicPool |
|  | where < value> is the name of the pool instance. |
| Request body | See the arguments table below. |
| arguments |  |
| Successful return | 200 OK |
| status |  |
| Successful | JSON representation of the returned attributes. |
| response body |  |

Arguments for the GetStorageTierConfigurationsForDynamicPool operation

| Arqument | In/ out | Type | Required? | Description |
| --- | --- | --- | --- | --- |
| storageTierParameters | in | List< storageTierConfigurationParameters> | Required | List of sepcified |
|  |  |  |  | pamameters. |
| storage Tier Configurations | out | List< storageTierConfiguration> | N/A | All possible |
|  |  |  |  | configurations for the list |
|  |  |  |  | of specified parameters, |
|  |  |  |  | as defined by the |
|  |  |  |  | storageTierConfiguration |
|  |  |  |  | embedded object. |
