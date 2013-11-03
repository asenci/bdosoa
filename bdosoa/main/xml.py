"""
XML schema validator
"""

from lxml import etree, objectify


LNP_NS = '{urn:brazil:lnp:1.0}'

XSDSchema = etree.XMLSchema(
    etree.XML(
        '''<?xml version="1.0" encoding="UTF-8"?>
<!-- edited with XMLSpy v2008 (http://www.altova.com) by Ed Barker (NeuStar, Inc.) -->
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns="urn:brazil:lnp:1.0" targetNamespace="urn:brazil:lnp:1.0" elementFormDefault="qualified" attributeFormDefault="unqualified">
  <!--
  Filename: Brazil LNP Schema v1.9.xsd
    Updated to include:
  -->
  <xs:simpleType name="AuditName">
    <xs:restriction base="xs:string">
      <xs:maxLength value="40"/>
    </xs:restriction>
  </xs:simpleType>
  <xs:simpleType name="AuditResultStatus">
    <xs:restriction base="xs:token">
      <xs:enumeration value="success"/>
      <xs:enumeration value="failed_due_to_discrepancies"/>
      <xs:enumeration value="failed_on_bdo"/>
      <xs:enumeration value="no_audit_performed"/>
    </xs:restriction>
  </xs:simpleType>
  <xs:simpleType name="AuditStatus">
    <xs:restriction base="xs:token">
      <xs:enumeration value="in_progress"/>
      <xs:enumeration value="suspended"/>
      <xs:enumeration value="complete"/>
    </xs:restriction>
  </xs:simpleType>
  <xs:complexType name="MismatchAttributes">
    <xs:sequence>
      <xs:element name="recipient_SP" minOccurs="0">
        <xs:complexType>
          <xs:sequence>
            <xs:element name="bdo_subscriptionRecipientCurrentSP" type="ServiceProvId" nillable="true"/>
            <xs:element name="bdr_subscriptionRecipientCurrentSP" type="ServiceProvId" nillable="true"/>
          </xs:sequence>
        </xs:complexType>
      </xs:element>
      <xs:element name="recipient_EOT" minOccurs="0">
        <xs:complexType>
          <xs:sequence>
            <xs:element name="bdo_subscriptionRecipientCurrentEOT" type="EOT" nillable="true"/>
            <xs:element name="bdr_subscriptionRecipientCurrentEOT" type="EOT" nillable="true"/>
          </xs:sequence>
        </xs:complexType>
      </xs:element>
      <xs:element name="activation_time_stamp" minOccurs="0">
        <xs:complexType>
          <xs:sequence>
            <xs:element name="bdo_subscriptionActivationTimeStamp" type="xs:dateTime" nillable="true"/>
            <xs:element name="bdr_subscriptionActivationTimeStamp" type="xs:dateTime" nillable="true"/>
          </xs:sequence>
        </xs:complexType>
      </xs:element>
      <xs:element name="rn1" minOccurs="0">
        <xs:complexType>
          <xs:sequence>
            <xs:element name="bdo_subscription_rn1" type="RN1" nillable="true"/>
            <xs:element name="bdr_subscription_rn1" type="RN1" nillable="true"/>
          </xs:sequence>
        </xs:complexType>
      </xs:element>
      <xs:element name="cnl" minOccurs="0">
        <xs:complexType>
          <xs:sequence>
            <xs:element name="bdo_subscription_cnl" type="CNL" nillable="true"/>
            <xs:element name="bdr_subscription_cnl" type="CNL" nillable="true"/>
          </xs:sequence>
        </xs:complexType>
      </xs:element>
      <xs:element name="lnp_type" minOccurs="0">
        <xs:complexType>
          <xs:sequence>
            <xs:element name="bdo_subscriptionLNPType" type="LNPType" nillable="true"/>
            <xs:element name="bdr_subscriptionLNPType" type="LNPType" nillable="true"/>
          </xs:sequence>
        </xs:complexType>
      </xs:element>
      <xs:element name="line_type" minOccurs="0">
        <xs:complexType>
          <xs:sequence>
            <xs:element name="bdo_subscription_line_type" type="LineType"/>
            <xs:element name="bdr_subscription_line_type" type="LineType"/>
          </xs:sequence>
        </xs:complexType>
      </xs:element>
      <xs:element name="optional_data" minOccurs="0">
        <xs:complexType>
          <xs:sequence>
            <xs:element name="bdo_subscription_optional_data" type="OptionalData"/>
            <xs:element name="bdr_subscription_optional_data" type="OptionalData"/>
          </xs:sequence>
        </xs:complexType>
      </xs:element>
    </xs:sequence>
  </xs:complexType>
  <xs:complexType name="AuditFailureData">
    <xs:choice>
      <xs:element name="tn_version_missing_BDR"/>
      <xs:element name="tn_version_missing_BDO"/>
      <xs:element name="mismatch_data" type="MismatchAttributes"/>
    </xs:choice>
  </xs:complexType>
  <xs:complexType name="AuditServiceProvIdCriteria">
    <xs:choice>
      <xs:element name="allServiceProvs"/>
      <xs:element name="service_prov_id" type="ServiceProvId"/>
    </xs:choice>
  </xs:complexType>
  <xs:simpleType name="DownloadStatus">
    <xs:restriction base="xs:token">
      <xs:enumeration value="success"/>
      <xs:enumeration value="failed"/>
      <xs:enumeration value="time-range-invalid"/>
      <xs:enumeration value="criteria-to-large"/>
      <xs:enumeration value="no-data-selected"/>
      <xs:enumeration value="swim-more-data"/>
    </xs:restriction>
  </xs:simpleType>
  <xs:complexType name="ReleaseSessionData">
    <xs:sequence>
      <xs:element name="release_reason" type="ErrorReason" minOccurs="0"/>
    </xs:sequence>
  </xs:complexType>
  <xs:complexType name="ClientReleaseSessionData">
    <xs:sequence>
      <xs:element name="release_reason" type="xs:string" minOccurs="0"/>
    </xs:sequence>
  </xs:complexType>
  <xs:simpleType name="RN1">
    <xs:restriction base="NumberString">
      <xs:length value="5"/>
    </xs:restriction>
  </xs:simpleType>
  <xs:simpleType name="DownloadReason">
    <xs:restriction base="xs:token">
      <xs:enumeration value="new"/>
      <xs:enumeration value="delete"/>
      <xs:enumeration value="modified"/>
    </xs:restriction>
  </xs:simpleType>
  <xs:simpleType name="CancelType">
    <xs:restriction base="xs:token">
      <xs:enumeration value="port_request"/>
      <xs:enumeration value="disconnect_request"/>
    </xs:restriction>
  </xs:simpleType>
  <xs:complexType name="ErrorData">
    <xs:sequence>
      <xs:element name="error_status" type="ErrorStatus"/>
      <xs:element name="error_reason" type="ErrorReason" minOccurs="0"/>
    </xs:sequence>
  </xs:complexType>
  <xs:complexType name="ClientErrorData">
    <xs:sequence>
      <xs:element name="error_status" type="ErrorStatus"/>
      <xs:element name="error_info" type="xs:string" minOccurs="0"/>
    </xs:sequence>
  </xs:complexType>
  <xs:simpleType name="ErrorNumber">
    <xs:restriction base="xs:integer"/>
  </xs:simpleType>
  <xs:complexType name="ErrorReason">
    <xs:sequence>
      <xs:element name="error_number" type="ErrorNumber"/>
      <xs:element name="error_info" type="xs:string" minOccurs="0"/>
    </xs:sequence>
  </xs:complexType>
  <xs:complexType name="Failed_SP_List">
    <xs:sequence minOccurs="0" maxOccurs="unbounded">
      <xs:element name="service_prov_id" type="ServiceProvId"/>
      <xs:element name="service_prov_name" type="ServiceProvName"/>
    </xs:sequence>
  </xs:complexType>
  <xs:simpleType name="AdditionalInfo">
    <xs:restriction base="xs:string">
      <xs:maxLength value="255"/>
    </xs:restriction>
  </xs:simpleType>
  <xs:complexType name="ID_Range">
    <xs:sequence>
      <xs:element name="start_id" type="SubscriptionVersionId"/>
      <xs:element name="end_id" type="SubscriptionVersionId"/>
    </xs:sequence>
  </xs:complexType>
  <xs:simpleType name="AuditId">
    <xs:restriction base="xs:integer"/>
  </xs:simpleType>
  <xs:simpleType name="LNPType">
    <xs:restriction base="xs:token">
      <xs:enumeration value="lspp"/>
      <xs:enumeration value="lisp"/>
    </xs:restriction>
  </xs:simpleType>
  <xs:simpleType name="NotificationRecoveryStatus">
    <xs:restriction base="xs:token">
      <xs:enumeration value="success"/>
      <xs:enumeration value="failed"/>
      <xs:enumeration value="time-range-invalid"/>
      <xs:enumeration value="criteria-to-large"/>
      <xs:enumeration value="no-data-selected"/>
      <xs:enumeration value="swim-more-data"/>
    </xs:restriction>
  </xs:simpleType>
  <xs:simpleType name="NumberString">
    <xs:restriction base="xs:string">
      <xs:pattern value="[0123456789]{0,}"/>
    </xs:restriction>
  </xs:simpleType>
  <xs:simpleType name="OptionalData">
    <xs:restriction base="xs:string"/>
  </xs:simpleType>
  <xs:simpleType name="PhoneNumber">
    <xs:restriction base="NumberString">
      <xs:minLength value="10"/>
      <xs:maxLength value="11"/>
    </xs:restriction>
  </xs:simpleType>
  <xs:complexType name="Final" final="#all"/>
  <!--
    For QueryBdoSVs audit operation from BDR to BDO, this parameter represents the regular expression used to define SVs satisfying a certain criteria.
    The possible operands are:
      <= (lessOrEqual)
      >= (greaterOrEqual)
      = (equal)
      AND (and)
      OR (or)
      NOT (not)
    The possible parameters are:
      subscription_version_tn
      subscription_activation_timestamp
      subscription_broadcast_timestamp
      subscription_recipient_sp
      subscription_lnp_type
    The execution order is defined by using parenthesis.
    Examples:
      For QueryBDOSVs operation:
        "((subscription_version_tn >= '1111119000' AND subscription_version_tn <= '1111119049') AND (subscription_activation_timestamp >= '2007-01-27T00:00:00Z' AND subscription_activation_timestamp <= '2007-01-28T00:00:00Z'))"

    For some SOA/BDO SV query request operations, this parameter represents the regular expression that defines the criteria to query/modify/delete entries in BDR database.
      <= (lessOrEqual)
      < (lessThan)
      >= (greaterOrEqual)
      > (greaterThan)
      = (equal)
      != (notEqual)
      AND (and)
      OR (or)
      NOT (not)

    The possible query parameters are:
    Subscription Version QUERY
    ==========================
      subscription_group_id
      subscription_version_id
      subscription_version_tn
      subscription_rn1
      subscription_new_cnl
      subscription_old_cnl
      subscription_donor_sp
      subscription_due_date
      subscription_recipient_sp
      subscription_recipient_eot
      subscription_creation_timestamp
      subscription_activation_timestamp
      subscription_broadcast_timestamp
      subscription_version_status (do not send this parameter alone)
      subscription_lnp_type (do not send this parameter alone)
      subscription_line_type (do not send this parameter alone)
      subscription_porting_to_original_sp (do not send this parameter alone)
      subscription_precancellation_status (do not send this parameter alone)
      e.g.:
        (subscription_recipient_sp='1111' AND (subscription_version_tn>='1111110000' AND subscription_version_tn<='1111119999'))

  -->
  <xs:simpleType name="QueryExpression">
    <xs:restriction base="xs:string"/>
  </xs:simpleType>
  <xs:simpleType name="ResultsStatus">
    <xs:restriction base="xs:token">
      <xs:enumeration value="success"/>
      <xs:enumeration value="failure"/>
    </xs:restriction>
  </xs:simpleType>
  <xs:simpleType name="ServiceProvAuthorization">
    <xs:restriction base="xs:boolean"/>
  </xs:simpleType>
  <xs:simpleType name="ServiceProvId">
    <xs:restriction base="xs:string">
      <xs:length value="4"/>
    </xs:restriction>
  </xs:simpleType>
  <xs:simpleType name="EOT">
    <xs:restriction base="xs:string">
      <xs:length value="3"/>
    </xs:restriction>
  </xs:simpleType>
  <xs:simpleType name="ServiceProvName">
    <xs:restriction base="xs:string">
      <xs:maxLength value="40"/>
    </xs:restriction>
  </xs:simpleType>
  <xs:simpleType name="CustomerName">
    <xs:restriction base="xs:string">
      <xs:maxLength value="40"/>
    </xs:restriction>
  </xs:simpleType>
  <xs:simpleType name="CustomerType">
    <xs:restriction base="xs:token">
      <xs:enumeration value="legal_entity"/>
      <xs:enumeration value="individual"/>
    </xs:restriction>
  </xs:simpleType>
  <xs:simpleType name="FraudErrorJustification">
    <xs:restriction base="xs:string">
      <xs:maxLength value="255"/>
    </xs:restriction>
  </xs:simpleType>
  <xs:simpleType name="FraudErrorType">
    <xs:restriction base="xs:token">
      <xs:enumeration value="fraud"/>
      <xs:enumeration value="error"/>
    </xs:restriction>
  </xs:simpleType>
  <xs:complexType name="FraudInformation">
    <xs:sequence>
      <xs:element name="subscription_fraud_error_version_id" type="SubscriptionVersionId"/>
      <xs:element name="subscription_recipient_fraud_error_type" type="FraudErrorType"/>
      <xs:element name="subscription_recipient_fraud_error_justification" type="FraudErrorJustification" minOccurs="0"/>
      <xs:element name="subscription_adjust_fraud_error_duedate" type="xs:boolean" minOccurs="0"/>
    </xs:sequence>
  </xs:complexType>
  <xs:complexType name="FraudSuspicionInformation">
    <xs:sequence>
      <xs:element name="subscription_donor_fraud_error_type" type="FraudErrorType"/>
      <xs:element name="subscription_donor_fraud_error_justification" type="FraudErrorJustification" minOccurs="0"/>
    </xs:sequence>
  </xs:complexType>
  <xs:simpleType name="SessionID">
    <xs:restriction base="xs:integer"/>
  </xs:simpleType>
  <xs:simpleType name="CNL">
    <xs:restriction base="NumberString">
      <xs:length value="5"/>
    </xs:restriction>
  </xs:simpleType>
  <xs:simpleType name="CPF">
    <xs:restriction base="xs:string">
      <xs:maxLength value="11"/>
    </xs:restriction>
  </xs:simpleType>
  <xs:simpleType name="CNPJ">
    <xs:restriction base="xs:string">
      <xs:maxLength value="14"/>
    </xs:restriction>
  </xs:simpleType>
  <xs:simpleType name="GenericID">
    <xs:restriction base="xs:string">
      <xs:maxLength value="20"/>
    </xs:restriction>
  </xs:simpleType>
  <xs:simpleType name="SubscriptionStatusChangeCauseCode">
    <xs:restriction base="xs:integer"/>
  </xs:simpleType>
  <xs:simpleType name="SubscriptionVersionId">
    <xs:restriction base="xs:integer"/>
  </xs:simpleType>
  <xs:complexType name="TNandStatus">
    <xs:sequence>
      <xs:element name="subscription_tn" type="PhoneNumber"/>
      <xs:element name="version_status" type="VersionStatus" minOccurs="0"/>
    </xs:sequence>
  </xs:complexType>
  <xs:complexType name="SubscriptionVersionModifyRequestKey">
    <xs:choice>
      <xs:element name="version_id" type="SubscriptionVersionId"/>
      <xs:element name="tn_and_status" type="TNandStatus"/>
    </xs:choice>
  </xs:complexType>
  <xs:complexType name="SubscriptionVersionRequestKey">
    <xs:choice>
      <xs:element name="version_id" type="SubscriptionVersionId"/>
      <xs:element name="subscription_tn" type="PhoneNumber"/>
    </xs:choice>
  </xs:complexType>
  <xs:complexType name="DonorCancelAckRequest">
    <xs:sequence>
      <xs:element name="subscription_version_key" type="SubscriptionVersionRequestKey"/>
    </xs:sequence>
  </xs:complexType>
  <xs:simpleType name="LineType">
    <xs:restriction base="xs:token">
      <xs:enumeration value="Basic"/>
      <xs:enumeration value="DDR"/>
      <xs:enumeration value="CNG"/>
    </xs:restriction>
  </xs:simpleType>
  <xs:complexType name="PrePortData">
    <xs:sequence>
      <xs:element name="customer_id" type="CustomerID"/>
      <xs:element name="customer_name" type="CustomerName" minOccurs="0"/>
      <xs:element name="customer_type" type="CustomerType"/>
    </xs:sequence>
  </xs:complexType>
  <xs:complexType name="IndividualId">
    <xs:sequence>
      <xs:element name="CPF" type="CPF" minOccurs="0"/>
      <xs:element name="generic_id" type="GenericID" minOccurs="0"/>
    </xs:sequence>
  </xs:complexType>
  <xs:complexType name="LegalEntityId">
    <xs:choice>
      <xs:element name="CNPJ" type="CNPJ" minOccurs="0"/>
      <xs:element name="generic_id" type="GenericID" minOccurs="0"/>
    </xs:choice>
  </xs:complexType>
  <xs:complexType name="CustomerID">
    <xs:choice>
      <xs:element name="individual" type="IndividualId"/>
      <xs:element name="legal_entity" type="LegalEntityId"/>
    </xs:choice>
  </xs:complexType>
  <xs:complexType name="BdoCompletionTSReplyData">
    <xs:sequence>
      <xs:element name="status" type="NotificationReplyStatus"/>
      <xs:element name="error_reason" type="ErrorReason" minOccurs="0"/>
    </xs:sequence>
  </xs:complexType>
  <xs:complexType name="BdoCompletionTS">
    <xs:sequence>
      <xs:element name="version_id" type="SubscriptionVersionId"/>
      <xs:element name="completion_ts" type="xs:dateTime"/>
      <xs:element name="download_reason" type="DownloadReason"/>
    </xs:sequence>
  </xs:complexType>
  <xs:complexType name="SwimDownloadCriteria">
    <xs:sequence>
      <xs:element name="action_id" type="xs:integer" minOccurs="0"/>
    </xs:sequence>
  </xs:complexType>
  <xs:simpleType name="SwimResultsStatus">
    <xs:restriction base="ResultsStatus"/>
  </xs:simpleType>
  <xs:complexType name="TimeRange">
    <xs:sequence>
      <xs:element name="start_time" type="xs:dateTime"/>
      <xs:element name="stop_time" type="xs:dateTime"/>
    </xs:sequence>
  </xs:complexType>
  <xs:complexType name="TN_Range">
    <xs:sequence>
      <xs:element name="tn_start" type="PhoneNumber"/>
      <xs:element name="tn_stop">
        <xs:simpleType>
          <xs:restriction base="NumberString">
            <xs:length value="4"/>
          </xs:restriction>
        </xs:simpleType>
      </xs:element>
    </xs:sequence>
  </xs:complexType>
  <xs:complexType name="TN_VersionId">
    <xs:sequence>
      <xs:element name="tn" type="PhoneNumber"/>
      <xs:element name="version_id" type="SubscriptionVersionId"/>
    </xs:sequence>
  </xs:complexType>
  <xs:complexType name="TN_AssignedVersionId">
    <xs:sequence>
      <xs:element name="tn" type="PhoneNumber"/>
      <xs:element name="version_id" type="SubscriptionVersionId" minOccurs="0"/>
    </xs:sequence>
  </xs:complexType>
  <xs:simpleType name="VersionStatus">
    <xs:restriction base="xs:token">
      <xs:enumeration value="conflict"/>
      <xs:enumeration value="active"/>
      <xs:enumeration value="pending"/>
      <xs:enumeration value="sending"/>
      <xs:enumeration value="download-failed"/>
      <xs:enumeration value="download-failed-partial"/>
      <xs:enumeration value="disconnect-pending"/>
      <xs:enumeration value="old"/>
      <xs:enumeration value="cancelled"/>
      <xs:enumeration value="cancel-pending"/>
      <xs:enumeration value="suspended"/>
    </xs:restriction>
  </xs:simpleType>
  <xs:simpleType name="SubscriptionPreCancellationStatus">
    <xs:restriction base="xs:token">
      <xs:enumeration value="conflict"/>
      <xs:enumeration value="pending"/>
      <xs:enumeration value="disconnect_pending"/>
    </xs:restriction>
  </xs:simpleType>
  <xs:complexType name="NotificationReply">
    <xs:sequence>
      <xs:element name="status" type="NotificationReplyStatus"/>
      <xs:element name="error_info" type="xs:string" minOccurs="0"/>
    </xs:sequence>
  </xs:complexType>
  <xs:simpleType name="NotificationReplyStatus">
    <xs:restriction base="xs:token">
      <xs:enumeration value="success"/>
      <xs:enumeration value="failed"/>
    </xs:restriction>
  </xs:simpleType>
  <xs:complexType name="DownloadReply">
    <xs:sequence>
      <xs:element name="status" type="DownloadReplyStatus"/>
      <xs:element name="error_info" type="xs:string" minOccurs="0"/>
      <xs:element name="bdo_completion_ts" type="BdoCompletionTS" minOccurs="0"/>
    </xs:sequence>
  </xs:complexType>
  <xs:simpleType name="DownloadReplyStatus">
    <xs:restriction base="xs:token">
      <xs:enumeration value="success"/>
      <xs:enumeration value="failed"/>
    </xs:restriction>
  </xs:simpleType>
  <xs:simpleType name="ConfirmationStatus">
    <xs:restriction base="xs:token">
      <xs:enumeration value="success"/>
      <xs:enumeration value="failed"/>
    </xs:restriction>
  </xs:simpleType>
  <xs:simpleType name="ErrorStatus">
    <xs:restriction base="xs:token">
      <xs:enumeration value="success"/>
      <xs:enumeration value="session-invalid"/>
      <xs:enumeration value="failed"/>
    </xs:restriction>
  </xs:simpleType>
  <xs:simpleType name="SessionStatus">
    <xs:restriction base="xs:token">
      <xs:enumeration value="success"/>
      <xs:enumeration value="try_other_host"/>
      <xs:enumeration value="retry_same_host"/>
      <xs:enumeration value="failed"/>
    </xs:restriction>
  </xs:simpleType>
  <xs:complexType name="OperationReplyStatus">
    <xs:sequence>
      <xs:element name="status" type="ConfirmationStatus"/>
      <xs:element name="error_reason" type="ErrorReason" minOccurs="0"/>
    </xs:sequence>
  </xs:complexType>
  <xs:complexType name="NewSessionData">
    <xs:sequence>
      <xs:element name="recovery_mode" type="xs:boolean"/>
      <xs:element name="reuse_existing_session" minOccurs="0"/>
    </xs:sequence>
  </xs:complexType>
  <xs:complexType name="NewSessionReplyData">
    <xs:sequence>
      <xs:element name="session_status" type="SessionStatus"/>
      <xs:element name="session_id" type="SessionID" minOccurs="0"/>
      <xs:element name="recovery_mode" type="xs:boolean" minOccurs="0"/>
    </xs:sequence>
  </xs:complexType>
  <xs:complexType name="AuditDiscrepancyRpt">
    <xs:sequence>
      <xs:element name="audit_id" type="AuditId"/>
      <xs:element name="tn" type="PhoneNumber"/>
      <xs:element name="version_id" type="SubscriptionVersionId"/>
      <xs:element name="bdo_service_prov_id" type="ServiceProvId"/>
      <xs:element name="failure_reason" type="AuditFailureData"/>
    </xs:sequence>
  </xs:complexType>
  <xs:complexType name="AuditResult">
    <xs:sequence>
      <xs:element name="audit_id" type="AuditId"/>
      <xs:element name="audit_result_status" type="AuditResultStatus"/>
      <xs:element name="failed_service_prov_list" type="Failed_SP_List" minOccurs="0"/>
      <xs:element name="number_of_discrepancies" type="xs:integer"/>
      <xs:element name="time_of_completion" type="xs:dateTime"/>
    </xs:sequence>
  </xs:complexType>
  <xs:complexType name="AuditCreateReplyData">
    <xs:sequence>
      <xs:element name="create_status" type="OperationReplyStatus"/>
      <xs:element name="audit_id" type="AuditId" minOccurs="0"/>
    </xs:sequence>
  </xs:complexType>
  <xs:complexType name="AuditCreateRequestData">
    <xs:sequence>
      <xs:element name="audit_name" type="AuditName"/>
      <xs:element name="audit_TN_range" type="TN_Range"/>
      <xs:element name="audit_TN_activation_range" type="TimeRange" minOccurs="0"/>
      <xs:element name="audit_service_prov_id_criteria" type="AuditServiceProvIdCriteria"/>
      <xs:element name="audit_requesting_service_prov_id" type="ServiceProvId"/>
    </xs:sequence>
  </xs:complexType>
  <xs:complexType name="AuditRequestData">
    <xs:sequence>
      <xs:element name="audit_id" type="AuditId"/>
    </xs:sequence>
  </xs:complexType>
  <xs:complexType name="AuditObjectData">
    <xs:sequence>
      <xs:element name="audit_id" type="AuditId"/>
      <xs:element name="audit_name" type="AuditName"/>
      <xs:element name="audit_status" type="AuditStatus"/>
      <xs:element name="audit_TN_range" type="TN_Range"/>
      <xs:element name="audit_TN_activation_range" type="TimeRange" minOccurs="0"/>
      <xs:element name="audit_service_prov_id_criteria" type="AuditServiceProvIdCriteria"/>
      <xs:element name="audit_number_of_TNs" type="xs:integer"/>
      <xs:element name="audit_number_of_TNs_complete" type="xs:integer"/>
      <xs:element name="audit_requesting_service_prov_id" type="ServiceProvId"/>
    </xs:sequence>
  </xs:complexType>
  <xs:complexType name="AuditObjectCreationData">
    <xs:sequence>
      <xs:element name="audit_id" type="AuditId"/>
    </xs:sequence>
  </xs:complexType>
  <xs:complexType name="AuditObjectDeletionData">
    <xs:sequence>
      <xs:element name="audit_id" type="AuditId"/>
    </xs:sequence>
  </xs:complexType>
  <xs:complexType name="AuditCancelReplyData">
    <xs:sequence>
      <xs:element name="cancel_status" type="OperationReplyStatus"/>
    </xs:sequence>
  </xs:complexType>
  <xs:complexType name="AuditQueryReplyData">
    <xs:sequence>
      <xs:element name="query_status" type="OperationReplyStatus"/>
      <xs:element name="audit_info" type="AuditObjectData" minOccurs="0"/>
    </xs:sequence>
  </xs:complexType>
  <xs:simpleType name="BWBNotificationType">
    <xs:restriction base="xs:token">
      <xs:enumeration value="create"/>
      <xs:enumeration value="delete"/>
    </xs:restriction>
  </xs:simpleType>
  <xs:simpleType name="BWBScheduledAction">
    <xs:restriction base="xs:token">
      <xs:enumeration value="activate"/>
      <xs:enumeration value="disconnect"/>
    </xs:restriction>
  </xs:simpleType>
  <xs:complexType name="BWBVersionInfo">
    <xs:sequence>
      <xs:element name="subscription_version_id" type="SubscriptionVersionId"/>
      <xs:element name="subscription_version_tn" type="PhoneNumber"/>
      <xs:element name="subscription_version_status" type="VersionStatus"/>
      <xs:element name="subscription_recipient_sp" type="ServiceProvId"/>
      <xs:element name="subscription_donor_sp" type="ServiceProvId"/>
      <xs:element name="subscription_scheduled_action" type="BWBScheduledAction"/>
    </xs:sequence>
  </xs:complexType>
  <xs:complexType name="BroadcastWindowBlockData">
    <xs:sequence>
      <xs:element name="broadcast_window_start_timestamp" type="xs:dateTime"/>
      <xs:element name="notification_type" type="BWBNotificationType"/>
      <xs:element name="total_number_of_svs_in_BWB" type="xs:integer" minOccurs="0"/>
      <xs:element name="version_list" minOccurs="0">
        <xs:complexType>
          <xs:sequence maxOccurs="unbounded">
            <xs:element name="data" type="BWBVersionInfo"/>
          </xs:sequence>
        </xs:complexType>
      </xs:element>
    </xs:sequence>
  </xs:complexType>
  <xs:complexType name="SubscriptionVersionQueryRequestData">
    <xs:sequence>
      <xs:choice>
        <xs:element name="version_id" type="SubscriptionVersionId"/>
        <xs:element name="query_expression" type="QueryExpression"/>
      </xs:choice>
    </xs:sequence>
  </xs:complexType>
  <xs:complexType name="SubscriptionVersionQueryReplyData">
    <xs:sequence>
      <xs:element name="query_status" type="OperationReplyStatus"/>
      <xs:element name="version_list" minOccurs="0">
        <xs:complexType>
          <xs:sequence minOccurs="0" maxOccurs="unbounded">
            <xs:element name="data" type="SubscriptionVersionObjectData"/>
          </xs:sequence>
        </xs:complexType>
      </xs:element>
    </xs:sequence>
  </xs:complexType>
  <xs:complexType name="SubscriptionVersionObjectData">
    <xs:sequence>
      <xs:element name="subscription_version_id" type="SubscriptionVersionId"/>
      <xs:element name="subscription_version_tn" type="PhoneNumber"/>
      <xs:element name="subscription_recipient_sp" type="ServiceProvId"/>
      <xs:element name="subscription_recipient_eot" type="EOT" minOccurs="0"/>
      <xs:element name="subscription_donor_sp" type="ServiceProvId"/>
      <xs:element name="subscription_pre_port_data" type="PrePortData" minOccurs="0"/>
      <xs:element name="subscription_fraud_error_data" type="FraudInformation" minOccurs="0"/>
      <xs:element name="subscription_customer_extended_port_date" type="xs:boolean" minOccurs="0"/>
      <xs:element name="subscription_fixed_special" type="xs:boolean" minOccurs="0"/>
      <xs:element name="subscription_documentation_receipt_confirmation" type="xs:boolean" minOccurs="0"/>
      <xs:element name="subscription_group_id" type="xs:integer" minOccurs="0"/>
      <xs:element name="subscription_donor_sp_authorization_due_date" type="xs:dateTime" minOccurs="0"/>
      <xs:element name="subscription_activation_timestamp" type="xs:dateTime" minOccurs="0"/>
      <xs:element name="subscription_rn1" type="RN1" minOccurs="0"/>
      <xs:element name="subscription_new_cnl" type="CNL" minOccurs="0"/>
      <xs:element name="subscription_old_cnl" type="CNL" minOccurs="0"/>
      <xs:element name="subscription_lnp_type" type="LNPType"/>
      <xs:element name="subscription_download_reason" type="DownloadReason"/>
      <xs:element name="subscription_version_status" type="VersionStatus"/>
      <xs:element name="subscription_due_date" type="xs:dateTime" minOccurs="0"/>
      <xs:element name="subscription_recipient_sp_creation_ts" type="xs:dateTime" minOccurs="0"/>
      <xs:element name="subscription_recipient_completion_ts" type="xs:dateTime" minOccurs="0"/>
      <xs:element name="subscription_donor_completion_ts" type="xs:dateTime" minOccurs="0"/>
      <xs:element name="subscription_donor_sp_authorization" type="ServiceProvAuthorization" minOccurs="0"/>
      <xs:element name="subscription_fraud_error_suspicion_data" type="FraudSuspicionInformation" minOccurs="0"/>
      <xs:element name="subscription_status_change_cause_code" type="SubscriptionStatusChangeCauseCode" minOccurs="0"/>
      <xs:element name="subscription_cancellation_cause_code" type="xs:integer" minOccurs="0"/>
      <xs:element name="subscription_donor_sp_authorization_ts" type="xs:dateTime" minOccurs="0"/>
      <xs:element name="subscription_broadcast_timestamp" type="xs:dateTime" minOccurs="0"/>
      <xs:element name="subscription_conflict_timestamp" type="xs:dateTime" minOccurs="0"/>
      <xs:element name="subscription_customer_disconnect_date" type="xs:dateTime" minOccurs="0"/>
      <xs:element name="subscription_effective_release_date" type="xs:dateTime" minOccurs="0"/>
      <xs:element name="subscription_disconnect_complete_timestamp" type="xs:dateTime" minOccurs="0"/>
      <xs:element name="subscription_cancellation_timestamp" type="xs:dateTime" minOccurs="0"/>
      <xs:element name="subscription_creation_timestamp" type="xs:dateTime" minOccurs="0"/>
      <xs:element name="failed_service_provs" type="Failed_SP_List" minOccurs="0"/>
      <xs:element name="subscription_modified_timestamp" type="xs:dateTime" minOccurs="0"/>
      <xs:element name="subscription_old_timestamp" type="xs:dateTime" minOccurs="0"/>
      <xs:element name="subscription_recipient_sp_cancellation_timestamp" type="xs:dateTime" minOccurs="0"/>
      <xs:element name="subscription_recipient_sp_conflict_resolution_timestamp" type="xs:dateTime" minOccurs="0"/>
      <xs:element name="subscription_porting_to_original_sp" type="xs:boolean"/>
      <xs:element name="subscription_precancellation_status" type="SubscriptionPreCancellationStatus" minOccurs="0"/>
      <xs:element name="subscription_timer_type" type="xs:integer" minOccurs="0"/>
      <xs:element name="subscription_business_type" type="xs:integer" minOccurs="0"/>
      <xs:element name="subscription_line_type" type="LineType"/>
      <xs:element name="subscription_optional_data" type="OptionalData" minOccurs="0"/>
    </xs:sequence>
  </xs:complexType>
  <xs:complexType name="TNListData">
    <xs:sequence maxOccurs="unbounded">
      <xs:element name="data" type="TNChoice"/>
    </xs:sequence>
  </xs:complexType>
  <xs:complexType name="TNChoice">
    <xs:choice>
      <xs:element name="tn" type="PhoneNumber"/>
      <xs:element name="tn_range" type="TN_Range"/>
    </xs:choice>
  </xs:complexType>
  <xs:complexType name="DateRange">
    <xs:sequence>
      <xs:element name="starting_date" type="xs:dateTime"/>
      <xs:element name="duration_days" type="xs:integer"/>
    </xs:sequence>
  </xs:complexType>
  <xs:complexType name="SPDueDate">
    <xs:choice>
      <xs:element name="specific_date" type="xs:dateTime"/>
      <xs:element name="date_range" type="DateRange"/>
      <xs:element name="next_available_date" type="Final"/>
    </xs:choice>
  </xs:complexType>
  <xs:complexType name="RecipientPortRequestData">
    <xs:sequence>
      <xs:element name="subscription_identifier" type="TNListData"/>
      <xs:element name="subscription_pre_port_data" type="PrePortData" minOccurs="0"/>
      <xs:element name="subscription_fraud_error_data" type="FraudInformation" minOccurs="0"/>
      <xs:element name="subscription_generate_group_id" type="xs:boolean" minOccurs="0"/>
      <xs:element name="subscription_group_id" type="xs:integer" minOccurs="0"/>
      <xs:element name="subscription_fixed_special" type="xs:boolean" minOccurs="0"/>
      <xs:element name="subscription_customer_extended_port_date" type="xs:boolean" minOccurs="0"/>
      <xs:element name="subscription_documentation_receipt_confirmation" type="xs:boolean" minOccurs="0"/>
      <xs:element name="subscription_recipient_sp" type="ServiceProvId"/>
      <xs:element name="subscription_recipient_eot" type="EOT" minOccurs="0"/>
      <xs:element name="subscription_donor_sp" type="ServiceProvId" minOccurs="0"/>
      <xs:element name="subscription_due_date_criteria" type="SPDueDate"/>
      <xs:element name="subscription_rn1" type="RN1" minOccurs="0"/>
      <xs:element name="subscription_new_cnl" type="CNL" minOccurs="0"/>
      <xs:element name="subscription_old_cnl" type="CNL" minOccurs="0"/>
      <xs:element name="subscription_lnp_type" type="LNPType"/>
      <xs:element name="subscription_porting_to_original_sp" type="xs:boolean"/>
      <xs:element name="subscription_line_type" type="LineType"/>
      <xs:element name="subscription_optional_data" type="OptionalData" minOccurs="0"/>
      <xs:element name="portability_continuation_indicator" type="xs:boolean" minOccurs="0"/>
    </xs:sequence>
  </xs:complexType>
  <xs:complexType name="ExistingSVData">
    <xs:sequence>
      <xs:element name="existing_version_id" type="SubscriptionVersionId"/>
      <xs:element name="existing_service_prov" type="ServiceProvId"/>
    </xs:sequence>
  </xs:complexType>
  <xs:complexType name="RecipientPortReply">
    <xs:sequence>
      <xs:element name="status" type="SubscriptionVersionReplyStatus"/>
      <xs:element name="tn_version_list" type="RecipientTNPortResultListData" minOccurs="0"/>
      <xs:element name="error_result" type="RecipientTNPortErrorResult" minOccurs="0"/>
      <xs:element name="group_id" type="xs:integer" minOccurs="0"/>
    </xs:sequence>
  </xs:complexType>
  <xs:complexType name="DonorInitialConcurrenceRequestInfo">
    <xs:sequence>
      <xs:element name="tn_version_id" type="NotifyTN_ID_Info"/>
      <xs:element name="subscription_recipient_sp" type="ServiceProvId"/>
      <xs:element name="subscription_due_date" type="xs:dateTime"/>
      <xs:element name="subscription_recipient_sp_creation_timestamp" type="xs:dateTime"/>
      <xs:element name="subscription_donor_sp_authorization_due_date" type="xs:dateTime"/>
      <xs:element name="subscription_timer_type" type="xs:integer" minOccurs="0"/>
      <xs:element name="subscription_business_type" type="xs:integer" minOccurs="0"/>
      <xs:element name="subscription_donor_action_id" type="xs:integer"/>
    </xs:sequence>
  </xs:complexType>
  <xs:complexType name="NotifyTN_ID_Info">
    <xs:choice>
      <xs:element name="single_version" type="TN_VersionId"/>
    </xs:choice>
  </xs:complexType>
  <xs:complexType name="SVOperationReplyData">
    <xs:sequence>
      <xs:element name="status" type="SubscriptionVersionReplyStatus"/>
      <xs:element name="error_reason" type="ErrorReason" minOccurs="0"/>
    </xs:sequence>
  </xs:complexType>
  <xs:complexType name="DonorPortReplyData">
    <xs:sequence>
      <xs:element name="status" type="SubscriptionVersionReplyStatus"/>
      <xs:element name="error_reason" type="ErrorReason" minOccurs="0"/>
      <xs:element name="subscription_donor_action_id" type="xs:integer" minOccurs="0"/>
    </xs:sequence>
  </xs:complexType>
  <xs:complexType name="ModifyReplyData">
    <xs:sequence>
      <xs:element name="status" type="SubscriptionVersionReplyStatus"/>
      <xs:element name="error_reason" type="ErrorReason" minOccurs="0"/>
      <xs:element name="subscription_due_date" type="xs:dateTime" minOccurs="0"/>
    </xs:sequence>
  </xs:complexType>
  <xs:complexType name="RecipientTNPortErrorResult">
    <xs:sequence>
      <xs:element name="error_reason" type="ErrorReason"/>
      <xs:element name="error_tn" type="PhoneNumber" minOccurs="0"/>
      <xs:element name="existing_version_data" type="ExistingSVData" minOccurs="0"/>
    </xs:sequence>
  </xs:complexType>
  <xs:complexType name="RecipientTNPortDueDate">
    <xs:sequence>
      <xs:element name="tn_version_id" type="TN_VersionId"/>
      <xs:element name="subscription_due_date" type="xs:dateTime"/>
    </xs:sequence>
  </xs:complexType>
  <xs:complexType name="RecipientTNPortResultListData">
    <xs:sequence maxOccurs="unbounded">
      <xs:element name="data" type="RecipientTNPortDueDate"/>
    </xs:sequence>
  </xs:complexType>
  <xs:complexType name="VersionAttributeValueChange">
    <xs:sequence>
      <xs:element name="tn_version_id" type="NotifyTN_ID_Info"/>
      <xs:element name="ObjectInfo" type="VersionObjectAttributeInfo"/>
    </xs:sequence>
  </xs:complexType>
  <xs:complexType name="VersionCancellationAcknowledgeRequest">
    <xs:sequence>
      <xs:element name="tn_version_id" type="NotifyTN_ID_Info"/>
      <xs:element name="subscription_cancellation_cause_code" type="xs:integer" minOccurs="0"/>
    </xs:sequence>
  </xs:complexType>
  <xs:complexType name="DisconnectDates">
    <xs:sequence>
      <xs:element name="subscription_customer_disconnect_date" type="xs:dateTime"/>
      <xs:element name="subscription_effective_release_date" type="xs:dateTime"/>
    </xs:sequence>
  </xs:complexType>
  <xs:simpleType name="DisconnectNotificationReason">
    <xs:restriction base="xs:token">
      <xs:enumeration value="created"/>
      <xs:enumeration value="modified"/>
      <xs:enumeration value="cancelled"/>
      <xs:enumeration value="disconnected"/>
    </xs:restriction>
  </xs:simpleType>
  <xs:complexType name="DisconnectInfo">
    <xs:sequence>
      <xs:element name="disconnect_dates" type="DisconnectDates" minOccurs="0"/>
      <xs:element name="notification_reason" type="DisconnectNotificationReason"/>
    </xs:sequence>
  </xs:complexType>
  <xs:complexType name="CustomerDisconnectInfo">
    <xs:sequence>
      <xs:element name="tn_version_id" type="NotifyTN_ID_Info"/>
      <xs:element name="disconnect_info" type="DisconnectInfo"/>
    </xs:sequence>
  </xs:complexType>
  <xs:complexType name="DonorPortRequestKey">
    <xs:choice>
      <xs:element name="subscription_tn" type="PhoneNumber"/>
      <xs:element name="subscription_version_id" type="SubscriptionVersionId"/>
    </xs:choice>
  </xs:complexType>
  <xs:complexType name="DonorPortRequestData">
    <xs:sequence>
      <xs:element name="subscription_tn" type="PhoneNumber"/>
      <xs:element name="subscription_recipient_sp" type="ServiceProvId"/>
      <xs:element name="subscription_donor_sp" type="ServiceProvId"/>
      <xs:element name="subscription_donor_sp_authorization" type="ServiceProvAuthorization"/>
      <xs:element name="subscription_fraud_error_suspicion_data" type="FraudSuspicionInformation" minOccurs="0"/>
      <xs:element name="subscription_status_change_cause_code" type="SubscriptionStatusChangeCauseCode" minOccurs="0"/>
      <xs:element name="subscription_old_cnl" type="CNL" minOccurs="0"/>
      <xs:element name="subscription_donor_action_id" type="xs:integer"/>
    </xs:sequence>
  </xs:complexType>
  <xs:simpleType name="SubscriptionVersionReplyStatus">
    <xs:restriction base="xs:token">
      <xs:enumeration value="success"/>
      <xs:enumeration value="failed"/>
      <xs:enumeration value="soa-not-authorized"/>
      <xs:enumeration value="no-version-found"/>
      <xs:enumeration value="invalid-data-values"/>
    </xs:restriction>
  </xs:simpleType>
  <xs:complexType name="ModifyAction">
    <xs:choice>
      <xs:element name="suspend_port" type="Final"/>
      <xs:element name="remove_suspension" type="Final"/>
      <xs:element name="remove_conflict" type="Final"/>
    </xs:choice>
  </xs:complexType>
  <xs:complexType name="RecipientPendingSuspendedOrConflictModifyData">
    <xs:sequence>
      <xs:element name="customer_CPF" type="CPF" nillable="true" minOccurs="0"/>
      <xs:element name="customer_CNPJ" type="CNPJ" nillable="true" minOccurs="0"/>
      <xs:element name="customer_generic_id" type="GenericID" nillable="true" minOccurs="0"/>
      <xs:element name="customer_name" type="CustomerName" minOccurs="0"/>
      <xs:element name="customer_type" type="CustomerType" minOccurs="0"/>
      <xs:element name="subscription_fraud_error_version_id" type="SubscriptionVersionId" minOccurs="0"/>
      <xs:element name="subscription_recipient_fraud_error_type" type="FraudErrorType" minOccurs="0"/>
      <xs:element name="subscription_recipient_fraud_error_justification" type="FraudErrorJustification" minOccurs="0"/>
      <xs:element name="subscription_adjust_fraud_error_duedate" type="xs:boolean" minOccurs="0"/>
      <xs:element name="subscription_group_id" type="xs:integer" nillable="true" minOccurs="0"/>
      <xs:element name="subscription_fixed_special" type="xs:boolean" minOccurs="0"/>
      <xs:element name="subscription_customer_extended_port_date" type="xs:boolean" minOccurs="0"/>
      <xs:element name="subscription_recipient_eot" type="EOT" minOccurs="0"/>
      <xs:element name="subscription_documentation_receipt_confirmation" type="xs:boolean" minOccurs="0"/>
      <xs:element name="subscription_due_date_criteria" type="SPDueDate" minOccurs="0"/>
      <xs:element name="subscription_rn1" type="RN1" minOccurs="0"/>
      <xs:element name="subscription_new_cnl" type="CNL" minOccurs="0"/>
      <xs:element name="subscription_old_cnl" type="CNL" minOccurs="0"/>
      <xs:element name="subscription_line_type" type="LineType" minOccurs="0"/>
      <xs:element name="subscription_optional_data" type="OptionalData" nillable="true" minOccurs="0"/>
      <xs:element name="modify_action" type="ModifyAction" minOccurs="0"/>
    </xs:sequence>
  </xs:complexType>
  <xs:complexType name="RecipientDisconnectPendingModifyData">
    <xs:sequence>
      <xs:element name="subscription_customer_disconnect_date" type="xs:dateTime" minOccurs="0"/>
      <xs:element name="subscription_effective_release_date" type="xs:dateTime" minOccurs="0"/>
    </xs:sequence>
  </xs:complexType>
  <xs:complexType name="RecipientCancelPendingModifyData">
    <xs:sequence>
      <xs:element name="subscription_cancellation_cause_code" type="xs:integer" minOccurs="0"/>
      <xs:element name="undo_cancel" type="Final" minOccurs="0"/>
    </xs:sequence>
  </xs:complexType>
  <xs:complexType name="RecipientDonorCompletionTSModifyData">
    <xs:choice>
      <xs:element name="subscription_recipient_completion_ts" type="xs:dateTime"/>
      <xs:element name="subscription_donor_completion_ts" type="xs:dateTime"/>
    </xs:choice>
  </xs:complexType>
  <xs:complexType name="SubscriptionModifyData">
    <xs:choice>
      <xs:element name="recipient_pending_suspended_or_conflict" type="RecipientPendingSuspendedOrConflictModifyData"/>
      <xs:element name="recipient_disconnect_pending" type="RecipientDisconnectPendingModifyData"/>
      <xs:element name="recipient_cancel_pending" type="RecipientCancelPendingModifyData"/>
      <xs:element name="recipient_or_donor_completion_ts" type="RecipientDonorCompletionTSModifyData"/>
    </xs:choice>
  </xs:complexType>
  <xs:complexType name="DisconnectRequest">
    <xs:sequence>
      <xs:element name="subscription_version_key" type="SubscriptionVersionRequestKey"/>
      <xs:element name="subscription_customer_disconnect_date" type="xs:dateTime" minOccurs="0"/>
      <xs:element name="subscription_effective_release_date" type="xs:dateTime" minOccurs="0"/>
    </xs:sequence>
  </xs:complexType>
  <xs:complexType name="ModifyRequest">
    <xs:sequence>
      <xs:element name="subscription_version_key" type="SubscriptionVersionModifyRequestKey"/>
      <xs:element name="data_to_modify" type="SubscriptionModifyData"/>
    </xs:sequence>
  </xs:complexType>
  <xs:complexType name="CancelRequest">
    <xs:sequence>
      <xs:element name="subscription_version_key" type="SubscriptionVersionRequestKey"/>
      <xs:element name="cancel_type" type="CancelType"/>
      <xs:element name="subscription_cancellation_cause_code" type="xs:integer" minOccurs="0"/>
    </xs:sequence>
  </xs:complexType>
  <xs:complexType name="VersionObjectInfo">
    <xs:sequence>
      <xs:element name="subscription_pre_port_data" type="PrePortData" minOccurs="0"/>
      <xs:element name="subscription_fraud_error_data" type="FraudInformation" minOccurs="0"/>
      <xs:element name="subscription_group_id" type="xs:integer" minOccurs="0"/>
      <xs:element name="subscription_fixed_special" type="xs:boolean" minOccurs="0"/>
      <xs:element name="subscription_customer_extended_port_date" type="xs:boolean" minOccurs="0"/>
      <xs:element name="subscription_documentation_receipt_confirmation" type="xs:boolean" minOccurs="0"/>
      <xs:element name="subscription_recipient_sp" type="ServiceProvId"/>
      <xs:element name="subscription_donor_sp" type="ServiceProvId"/>
      <xs:element name="subscription_due_date" type="xs:dateTime"/>
      <xs:element name="subscription_recipient_sp_creation_timestamp" type="xs:dateTime" minOccurs="0"/>
      <xs:element name="subscription_donor_sp_authorization_due_date" type="xs:dateTime" minOccurs="0"/>
      <xs:element name="subscription_line_type" type="LineType"/>
      <xs:element name="subscription_new_cnl" type="CNL" minOccurs="0"/>
      <xs:element name="subscription_old_cnl" type="CNL" minOccurs="0"/>
      <xs:element name="subscription_timer_type" type="xs:integer" minOccurs="0"/>
      <xs:element name="subscription_business_type" type="xs:integer" minOccurs="0"/>
      <xs:element name="subscription_donor_action_id" type="xs:integer" minOccurs="0"/>
    </xs:sequence>
  </xs:complexType>
  <xs:complexType name="VersionObjectCreation">
    <xs:sequence>
      <xs:element name="tn_version_id" type="NotifyTN_ID_Info"/>
      <xs:element name="object_info" type="VersionObjectInfo"/>
    </xs:sequence>
  </xs:complexType>
  <xs:complexType name="VersionObjectAttributeInfo">
    <xs:sequence>
      <xs:element name="customer_CPF" type="CPF" nillable="true" minOccurs="0"/>
      <xs:element name="customer_CNPJ" type="CNPJ" nillable="true" minOccurs="0"/>
      <xs:element name="customer_generic_id" type="GenericID" nillable="true" minOccurs="0"/>
      <xs:element name="customer_name" type="CustomerName" minOccurs="0"/>
      <xs:element name="customer_type" type="CustomerType" minOccurs="0"/>
      <xs:element name="subscription_fraud_error_version_id" type="SubscriptionVersionId" minOccurs="0"/>
      <xs:element name="subscription_recipient_fraud_error_type" type="FraudErrorType" minOccurs="0"/>
      <xs:element name="subscription_recipient_fraud_error_justification" type="FraudErrorJustification" minOccurs="0"/>
      <xs:element name="subscription_group_id" type="xs:integer" nillable="true" minOccurs="0"/>
      <xs:element name="subscription_fixed_special" type="xs:boolean" nillable="true" minOccurs="0"/>
      <xs:element name="subscription_customer_extended_port_date" type="xs:boolean" nillable="true" minOccurs="0"/>
      <xs:element name="subscription_documentation_receipt_confirmation" type="xs:boolean" nillable="true" minOccurs="0"/>
      <xs:element name="subscription_due_date" type="xs:dateTime" minOccurs="0"/>
      <xs:element name="subscription_donor_sp_authorization_due_date" type="xs:dateTime" minOccurs="0"/>
      <xs:element name="subscription_donor_sp_authorization_timestamp" type="xs:dateTime" minOccurs="0"/>
      <xs:element name="subscription_donor_sp_authorization" type="ServiceProvAuthorization" minOccurs="0"/>
      <xs:element name="subscription_donor_response_timeout" type="Final" minOccurs="0"/>
      <xs:element name="subscription_fraud_error_suspicion_data" type="FraudSuspicionInformation" minOccurs="0"/>
      <xs:element name="subscription_conflict_timestamp" type="xs:dateTime" minOccurs="0"/>
      <xs:element name="subscription_version_status" type="VersionStatus" minOccurs="0"/>
      <xs:element name="failed_service_provs" type="Failed_SP_List" minOccurs="0"/>
      <xs:element name="subscription_status_change_cause_code" type="SubscriptionStatusChangeCauseCode" minOccurs="0"/>
      <xs:element name="subscription_cancellation_cause_code" type="xs:integer" minOccurs="0"/>
      <xs:element name="subscription_new_cnl" type="CNL" minOccurs="0"/>
      <xs:element name="subscription_old_cnl" type="CNL" minOccurs="0"/>
      <xs:element name="subscription_line_type" type="LineType" minOccurs="0"/>
      <xs:element name="subscription_donor_action_id" type="xs:integer" minOccurs="0"/>
    </xs:sequence>
  </xs:complexType>
  <xs:complexType name="NotificationRecoveryRequestData">
    <xs:choice>
      <xs:element name="time_range" type="TimeRange"/>
      <xs:element name="swim" type="SwimDownloadCriteria"/>
    </xs:choice>
  </xs:complexType>
  <xs:complexType name="NotificationRecoveryReplyData">
    <xs:sequence>
      <xs:element name="recovery_reply_status" type="NotificationRecoveryStatus" minOccurs="0"/>
      <xs:element name="error_reason" type="ErrorReason" minOccurs="0"/>
      <xs:sequence minOccurs="0" maxOccurs="unbounded">
        <xs:element name="notification">
          <xs:complexType>
            <xs:sequence>
              <xs:element name="notification_invoke_id" type="xs:integer"/>
              <xs:choice>
                <xs:element name="VersionObjectCreationRecovery" type="VersionObjectCreation"/>
                <xs:element name="DonorInitialConcurRequestRecovery" type="DonorInitialConcurrenceRequestInfo"/>
                <xs:element name="AttributeValueChangeRecovery" type="VersionAttributeValueChange"/>
                <xs:element name="CustomerDisconnectRecovery" type="CustomerDisconnectInfo"/>
                <xs:element name="CancelAckRequestRecovery" type="VersionCancellationAcknowledgeRequest"/>
                <xs:element name="AuditCreationRecovery" type="AuditObjectCreationData"/>
                <xs:element name="AuditDeletionRecovery" type="AuditObjectDeletionData"/>
                <xs:element name="AuditDiscrepancyRptRecovery" type="AuditDiscrepancyRpt"/>
                <xs:element name="AuditResultRecovery" type="AuditResult"/>
                <xs:element name="BroadcastWindowBlockRecovery" type="BroadcastWindowBlockData"/>
              </xs:choice>
            </xs:sequence>
          </xs:complexType>
        </xs:element>
      </xs:sequence>
      <xs:element name="action_id" type="xs:integer" minOccurs="0"/>
    </xs:sequence>
  </xs:complexType>
  <xs:complexType name="MessageHeader">
    <xs:sequence>
      <xs:element name="service_prov_id" type="ServiceProvId"/>
      <xs:element name="invoke_id" type="xs:integer"/>
      <xs:element name="message_date_time" type="xs:dateTime"/>
    </xs:sequence>
  </xs:complexType>
  <xs:element name="SOAMessage">
    <xs:complexType>
      <xs:sequence>
        <xs:element name="messageHeader" type="MessageHeader"/>
        <xs:element name="messageContent" type="SOAContent"/>
      </xs:sequence>
    </xs:complexType>
  </xs:element>
  <xs:complexType name="SOAContent">
    <xs:choice>
      <xs:element name="SOAtoBDR" type="SOAtoBDR"/>
      <xs:element name="BDRtoSOA" type="BDRtoSOA"/>
    </xs:choice>
  </xs:complexType>
  <xs:complexType name="SOAtoBDR">
    <xs:choice>
      <xs:element name="NewSession" type="NewSessionData"/>
      <xs:element name="RecipientPortRequest" type="RecipientPortRequestData"/>
      <xs:element name="DonorPortRequest" type="DonorPortRequestData"/>
      <xs:element name="CancelRequest" type="CancelRequest"/>
      <xs:element name="DonorCancelAck" type="DonorCancelAckRequest"/>
      <xs:element name="DisconnectRequest" type="DisconnectRequest"/>
      <xs:element name="ModifyRequest" type="ModifyRequest"/>
      <xs:element name="AuditCreateRequest" type="AuditCreateRequestData"/>
      <xs:element name="AuditCancelRequest" type="AuditRequestData"/>
      <xs:element name="AuditQueryRequest" type="AuditRequestData"/>
      <xs:element name="SVQueryRequest" type="SubscriptionVersionQueryRequestData"/>
      <xs:element name="NotificationRecoveryRequest" type="NotificationRecoveryRequestData"/>
      <xs:element name="SwimRecoveryComplete" type="SwimRecoveryCompleteData"/>
      <xs:element name="RecoveryCompleteRequest" type="Final"/>
      <xs:element name="NotificationReply" type="NotificationReply"/>
      <xs:element name="ClientKeepAlive" type="Final"/>
      <xs:element name="ClientError" type="ClientErrorData"/>
      <xs:element name="ClientReleaseSession" type="ClientReleaseSessionData"/>
    </xs:choice>
  </xs:complexType>
  <xs:complexType name="BDRtoSOA">
    <xs:choice>
      <xs:element name="NewSessionReply" type="NewSessionReplyData"/>
      <xs:element name="RecipientPortReply" type="RecipientPortReply"/>
      <xs:element name="DonorPortReply" type="DonorPortReplyData"/>
      <xs:element name="CancelReply" type="SVOperationReplyData"/>
      <xs:element name="DonorCancelAckReply" type="SVOperationReplyData"/>
      <xs:element name="DisconnectReply" type="SVOperationReplyData"/>
      <xs:element name="ModifyReply" type="ModifyReplyData"/>
      <xs:element name="AuditCreateReply" type="AuditCreateReplyData"/>
      <xs:element name="AuditCancelReply" type="AuditCancelReplyData"/>
      <xs:element name="AuditQueryReply" type="AuditQueryReplyData"/>
      <xs:element name="SVQueryReply" type="SubscriptionVersionQueryReplyData"/>
      <xs:element name="VersionObjectCreationNotification" type="VersionObjectCreation"/>
      <xs:element name="DonorInitialConcurRequestNotification" type="DonorInitialConcurrenceRequestInfo"/>
      <xs:element name="AttributeValueChangeNotification" type="VersionAttributeValueChange"/>
      <xs:element name="CustomerDisconnectNotification" type="CustomerDisconnectInfo"/>
      <xs:element name="CancelAckRequestNotification" type="VersionCancellationAcknowledgeRequest"/>
      <xs:element name="AuditCreationNotification" type="AuditObjectCreationData"/>
      <xs:element name="AuditDeletionNotification" type="AuditObjectDeletionData"/>
      <xs:element name="AuditDiscrepancyRptNotification" type="AuditDiscrepancyRpt"/>
      <xs:element name="AuditResultNotification" type="AuditResult"/>
      <xs:element name="BroadcastWindowBlockNotification" type="BroadcastWindowBlockData"/>
      <xs:element name="NotificationRecoveryReply" type="NotificationRecoveryReplyData"/>
      <xs:element name="SwimRecoveryCompleteReply" type="SwimRecoveryCompleteReplyData"/>
      <xs:element name="RecoveryCompleteReply" type="Final"/>
      <xs:element name="BDRKeepAlive" type="Final"/>
      <xs:element name="BDRError" type="ErrorData"/>
      <xs:element name="BDRReleaseSession" type="ReleaseSessionData"/>
    </xs:choice>
  </xs:complexType>
  <xs:complexType name="FailedTN_List">
    <xs:sequence minOccurs="0" maxOccurs="unbounded">
      <xs:element name="failed_tn">
        <xs:complexType>
          <xs:sequence>
            <xs:element name="subscriptionVersionId" type="SubscriptionVersionId"/>
            <xs:element name="tn" type="PhoneNumber"/>
            <xs:element name="error_reason" type="ErrorReason"/>
          </xs:sequence>
        </xs:complexType>
      </xs:element>
    </xs:sequence>
  </xs:complexType>
  <xs:complexType name="SubscriptionVersionData">
    <xs:sequence>
      <xs:element name="subscription_tn_version_id" type="TN_VersionId"/>
      <xs:element name="subscription_data" type="SubscriptionData"/>
    </xs:sequence>
  </xs:complexType>
  <xs:complexType name="SubscriptionVersionDeleteData">
    <xs:sequence>
      <xs:element name="subscription_version_id" type="SubscriptionVersionId"/>
      <xs:element name="subscription_delete_data" type="SubscriptionDownloadDeleteData"/>
    </xs:sequence>
  </xs:complexType>
  <xs:complexType name="QueryBdoSVsReplyData">
    <xs:sequence minOccurs="0" maxOccurs="unbounded">
      <xs:element name="subscription_version" type="SubscriptionVersionData"/>
    </xs:sequence>
  </xs:complexType>
  <xs:complexType name="SubscriptionDownloadDeleteData">
    <xs:sequence>
      <xs:element name="subscription_download_reason" type="DownloadReason"/>
      <xs:element name="broadcast_window_start_timestamp" type="xs:dateTime" minOccurs="0"/>
    </xs:sequence>
  </xs:complexType>
  <xs:complexType name="SubscriptionData">
    <xs:sequence>
      <xs:element name="subscription_recipient_sp" type="ServiceProvId"/>
      <xs:element name="subscription_recipient_eot" type="EOT"/>
      <xs:element name="subscription_activation_timestamp" type="xs:dateTime"/>
      <xs:element name="broadcast_window_start_timestamp" type="xs:dateTime" minOccurs="0"/>
      <xs:element name="subscription_rn1" type="RN1"/>
      <xs:element name="subscription_new_cnl" type="CNL" minOccurs="0"/>
      <xs:element name="subscription_lnp_type" type="LNPType"/>
      <xs:element name="subscription_download_reason" type="DownloadReason"/>
      <xs:element name="subscription_line_type" type="LineType"/>
      <xs:element name="subscription_optional_data" type="OptionalData" minOccurs="0"/>
    </xs:sequence>
  </xs:complexType>
  <xs:complexType name="SubscriptionDownloadData">
    <xs:sequence minOccurs="0" maxOccurs="unbounded">
      <xs:element name="data" type="SubscriptionDownloadDataDetail"/>
    </xs:sequence>
  </xs:complexType>
  <xs:complexType name="SubscriptionDownloadDataDetail">
    <xs:sequence>
      <xs:element name="download_invoke_id" type="xs:integer"/>
      <xs:element name="subscription_version_id" type="SubscriptionVersionId"/>
      <xs:element name="subscription_version_tn" type="PhoneNumber" minOccurs="0"/>
      <xs:choice>
        <xs:element name="subscription_data" type="SubscriptionData"/>
        <xs:element name="subscription_delete_data" type="SubscriptionDownloadDeleteData"/>
      </xs:choice>
    </xs:sequence>
  </xs:complexType>
  <xs:complexType name="QueryBdoSVsData">
    <xs:sequence>
      <xs:element name="query_expression" type="QueryExpression"/>
    </xs:sequence>
  </xs:complexType>
  <xs:complexType name="DownloadAction">
    <xs:choice>
      <xs:element name="subscriber_download" type="SubscriptionDownloadCriteria"/>
    </xs:choice>
  </xs:complexType>
  <xs:complexType name="SubscriptionDownloadCriteria">
    <xs:choice>
      <xs:element name="time_range" type="TimeRange"/>
      <xs:element name="tn" type="PhoneNumber"/>
      <xs:element name="tn_range" type="TN_Range"/>
      <xs:element name="swim" type="SwimDownloadCriteria"/>
    </xs:choice>
  </xs:complexType>
  <xs:complexType name="DownloadRecoveryReply">
    <xs:sequence>
      <xs:element name="status" type="DownloadStatus"/>
      <xs:element name="error_reason" type="ErrorReason" minOccurs="0"/>
      <xs:element name="download_data" minOccurs="0">
        <xs:complexType>
          <xs:choice>
            <xs:element name="subscriber_data" type="SubscriptionDownloadData"/>
          </xs:choice>
        </xs:complexType>
      </xs:element>
      <xs:element name="action_id" type="xs:integer" minOccurs="0"/>
    </xs:sequence>
  </xs:complexType>
  <xs:element name="BDOMessage">
    <xs:complexType>
      <xs:sequence>
        <xs:element name="messageHeader" type="MessageHeader"/>
        <xs:element name="messageContent" type="BDOContent"/>
      </xs:sequence>
    </xs:complexType>
  </xs:element>
  <xs:complexType name="SwimRecoveryCompleteData">
    <xs:sequence>
      <xs:element name="action_id" type="xs:integer"/>
      <xs:element name="status" type="SwimResultsStatus"/>
      <xs:element name="time_of_completion" type="xs:dateTime"/>
    </xs:sequence>
  </xs:complexType>
  <xs:complexType name="SwimRecoveryCompleteReplyData">
    <xs:sequence>
      <xs:element name="status" type="SwimResultsStatus"/>
      <xs:element name="error_reason" type="ErrorReason" minOccurs="0"/>
      <xs:element name="stop_date" type="xs:dateTime" minOccurs="0"/>
    </xs:sequence>
  </xs:complexType>
  <xs:complexType name="BDOContent">
    <xs:choice>
      <xs:element name="BDOtoBDR" type="BDOtoBDR"/>
      <xs:element name="BDRtoBDO" type="BDRtoBDO"/>
    </xs:choice>
  </xs:complexType>
  <xs:complexType name="BDOtoBDR">
    <xs:choice>
      <xs:element name="NewSession" type="NewSessionData"/>
      <xs:element name="SVQueryRequest" type="SubscriptionVersionQueryRequestData"/>
      <xs:element name="QueryBdoSVsReply" type="QueryBdoSVsReplyData"/>
      <xs:element name="BdoCompletionTSRequest" type="BdoCompletionTS"/>
      <xs:element name="DownloadRecoveryRequest" type="DownloadAction"/>
      <xs:element name="SwimRecoveryComplete" type="SwimRecoveryCompleteData"/>
      <xs:element name="RecoveryCompleteRequest" type="Final"/>
      <xs:element name="DownloadReply" type="DownloadReply"/>
      <xs:element name="ClientKeepAlive" type="Final"/>
      <xs:element name="ClientError" type="ClientErrorData"/>
      <xs:element name="ClientReleaseSession" type="ClientReleaseSessionData"/>
    </xs:choice>
  </xs:complexType>
  <xs:complexType name="BDRtoBDO">
    <xs:choice>
      <xs:element name="NewSessionReply" type="NewSessionReplyData"/>
      <xs:element name="SVQueryReply" type="SubscriptionVersionQueryReplyData"/>
      <xs:element name="SVCreateDownload" type="SubscriptionVersionData"/>
      <xs:element name="SVDeleteDownload" type="SubscriptionVersionDeleteData"/>
      <xs:element name="QueryBdoSVs" type="QueryBdoSVsData"/>
      <xs:element name="BdoCompletionTSReply" type="BdoCompletionTSReplyData"/>
      <xs:element name="RecoveryCompleteReply" type="Final"/>
      <xs:element name="DownloadRecoveryReply" type="DownloadRecoveryReply"/>
      <xs:element name="SwimRecoveryCompleteReply" type="SwimRecoveryCompleteReplyData"/>
      <xs:element name="BDRKeepAlive" type="Final"/>
      <xs:element name="BDRError" type="ErrorData"/>
      <xs:element name="BDRReleaseSession" type="ReleaseSessionData"/>
    </xs:choice>
  </xs:complexType>
</xs:schema>'''))

XMLParser = objectify.makeparser(encoding='utf-8', schema=XSDSchema)


def from_string(xml_str):
    """Create an Element object from a string"""

    # Parse the XML string and validate the document
    try:
        xml = objectify.fromstring(xml_str.encode('utf-8'), parser=XMLParser)
    except Exception as e:
        raise Exception('Error processing XML:\n{0}\n{1}\n'.format(
            xml_str, e))

    return xml
