Collection Resource Endpoints

 • /api/types/alert/instances
 • /api/types/disk/instances
 • /api/types/user/instances
 • /api/types/loginSessionInfo/instances
 • /api/types/basicSystemInfo/instances
 • /api/types/ethernetPort/instances
 • /api/types/pool/instances
 • /api/types/storageResource/instances

Instance Resource Endpoints (using ID)

 • /api/instances/alert/<id>
 • /api/instances/disk/<id>
 • /api/instances/user/<id>
 • /api/instances/ldapServer/<id>
 • /api/instances/pool/<id>
 • /api/instances/storageResource/<id>

Instance Resource Endpoints (using name)

 • /api/instances/user/name:<value>
 • /api/instances/pool/name:<value>
 • /api/instances/disk/name:<value>
 • /api/instances/ldapServer/name:<value>
 • /api/instances/storageResource/name:<value>

Instance Action Endpoints (using ID)

 • /api/instances/user/<id>/action/modify
 • /api/instances/ldapServer/<id>/action/verify
 • /api/instances/pool/<id>/action/startRelocation
 • /api/instances/pool/<id>/action/modify

Instance Action Endpoints (using name)

 • /api/instances/user/name:<value>/action/modify
 • /api/instances/pool/name:<value>/action/startRelocation
 • /api/instances/pool/name:<value>/action/modify

Class-Level Action Endpoints

 • /api/types/ethernetPort/action/RecommendForAggregation
 • /api/types/ipPort/action/RecommendForInterface
 • /api/types/loginSessionInfo/action/logout
 • /api/types/storageResource/action/createLun

Download Endpoints

 • /download/x509Certificate/<cert_id>
 • /download/<protocoltype>/nasServer/<nasserverid>
    • Where <protocoltype> can be 1 (Ldap_Configuration), 2 (Ldap_CA_Certificate), 3 (Username_Mappings), 4 (Virus_Checker_Configuration), 5 (Users), 6 (Groups), 7 (Hosts), 8
      (Netgroups), 9 (User_Mapping_Report), 10 (Kerberos_Key_Table), or 11 (Homedir)
 • /download/encryption/keystore
 • /download/encryption/auditLogAndChecksum
 • /download/encryption/checksum
 • /download/configCaptureResult/<cc_id>
 • /download/dataCollectionResult/<dc_id>
 • /download/importSession/<im_id>/<report_file_name>

Upload Endpoints

 • /upload/x509Certificate
 • /upload/<protocoltype>/nasServer/<nasserverid>
    • Where <protocoltype> can be 1 (Ldap_Configuration), 2 (Ldap_CA_Certificate), 3 (Username_Mappings), 4 (Virus_Checker_Configuration), 5 (Users), 6 (Groups), 7 (Hosts), 8
      (Netgroups), 10 (Kerberos_Key_Table), or 11 (Homedir)
 • /upload/files/types/candidateSoftwareVersion
 • /upload/license

Note:

 • <id>, <value>, <cert_id>, <nasserverid>, <cc_id>, <dc_id>, <im_id>, and <report_file_name> are placeholders for actual IDs, names, or file names.
 • Some endpoints have variations based on whether you are using an ID or a user-assigned name.
 • Some endpoints are for specific actions on a resource type or instance.

This list should provide a comprehensive overview of all the endpoints mentioned in the document.
