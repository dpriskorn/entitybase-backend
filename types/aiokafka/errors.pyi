from typing import Any

__all__ = [
    "ConsumerStoppedError",
    "NoOffsetForPartitionError",
    "RecordTooLargeError",
    "ProducerClosed",
    "KafkaError",
    "IllegalStateError",
    "IllegalArgumentError",
    "NoBrokersAvailable",
    "NodeNotReadyError",
    "KafkaProtocolError",
    "CorrelationIdError",
    "Cancelled",
    "TooManyInFlightRequests",
    "StaleMetadata",
    "UnrecognizedBrokerVersion",
    "IncompatibleBrokerVersion",
    "CommitFailedError",
    "AuthenticationMethodNotSupported",
    "AuthenticationFailedError",
    "BrokerResponseError",
    "NoError",
    "UnknownError",
    "OffsetOutOfRangeError",
    "CorruptRecordException",
    "UnknownTopicOrPartitionError",
    "InvalidFetchRequestError",
    "LeaderNotAvailableError",
    "NotLeaderForPartitionError",
    "RequestTimedOutError",
    "BrokerNotAvailableError",
    "ReplicaNotAvailableError",
    "MessageSizeTooLargeError",
    "StaleControllerEpochError",
    "OffsetMetadataTooLargeError",
    "StaleLeaderEpochCodeError",
    "GroupLoadInProgressError",
    "GroupCoordinatorNotAvailableError",
    "NotCoordinatorForGroupError",
    "InvalidTopicError",
    "RecordListTooLargeError",
    "NotEnoughReplicasError",
    "NotEnoughReplicasAfterAppendError",
    "InvalidRequiredAcksError",
    "IllegalGenerationError",
    "InconsistentGroupProtocolError",
    "InvalidGroupIdError",
    "UnknownMemberIdError",
    "InvalidSessionTimeoutError",
    "RebalanceInProgressError",
    "InvalidCommitOffsetSizeError",
    "TopicAuthorizationFailedError",
    "GroupAuthorizationFailedError",
    "ClusterAuthorizationFailedError",
    "InvalidTimestampError",
    "UnsupportedSaslMechanismError",
    "IllegalSaslStateError",
    "UnsupportedVersionError",
    "TopicAlreadyExistsError",
    "InvalidPartitionsError",
    "InvalidReplicationFactorError",
    "InvalidReplicationAssignmentError",
    "InvalidConfigurationError",
    "NotControllerError",
    "InvalidRequestError",
    "UnsupportedForMessageFormatError",
    "PolicyViolationError",
    "KafkaUnavailableError",
    "KafkaTimeoutError",
    "KafkaConnectionError",
    "UnsupportedCodecError",
]

class KafkaError(RuntimeError):
    retriable: bool
    invalid_metadata: bool

class IllegalStateError(KafkaError): ...
class IllegalArgumentError(KafkaError): ...

class NoBrokersAvailable(KafkaError):
    retriable: bool
    invalid_metadata: bool

class NodeNotReadyError(KafkaError):
    retriable: bool

class KafkaProtocolError(KafkaError):
    retriable: bool

class CorrelationIdError(KafkaProtocolError):
    retriable: bool

class Cancelled(KafkaError):
    retriable: bool

class TooManyInFlightRequests(KafkaError):
    retriable: bool

class StaleMetadata(KafkaError):
    retriable: bool
    invalid_metadata: bool

class MetadataEmptyBrokerList(KafkaError):
    retriable: bool

class UnrecognizedBrokerVersion(KafkaError): ...
class IncompatibleBrokerVersion(KafkaError): ...

class CommitFailedError(KafkaError):
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...

class AuthenticationMethodNotSupported(KafkaError): ...

class AuthenticationFailedError(KafkaError):
    retriable: bool

class KafkaUnavailableError(KafkaError): ...
class KafkaTimeoutError(KafkaError): ...

class KafkaConnectionError(KafkaError):
    retriable: bool
    invalid_metadata: bool

class UnsupportedCodecError(KafkaError): ...
class KafkaConfigurationError(KafkaError): ...
class QuotaViolationError(KafkaError): ...
class ConsumerStoppedError(Exception): ...
class IllegalOperation(Exception): ...
class NoOffsetForPartitionError(KafkaError): ...
class RecordTooLargeError(KafkaError): ...
class ProducerClosed(KafkaError): ...

class ProducerFenced(KafkaError):
    def __init__(
        self,
        msg: str = "There is a newer producer using the same transactional_id ortransaction timeout occurred (check that processing time is below transaction_timeout_ms)",
    ) -> None: ...

class BrokerResponseError(KafkaError):
    errno: int
    message: str
    description: str

class NoError(BrokerResponseError):
    errno: int
    message: str
    description: str

class UnknownError(BrokerResponseError):
    errno: int
    message: str
    description: str

class OffsetOutOfRangeError(BrokerResponseError):
    errno: int
    message: str
    description: str

class CorruptRecordException(BrokerResponseError):
    errno: int
    message: str
    description: str

InvalidMessageError = CorruptRecordException

class UnknownTopicOrPartitionError(BrokerResponseError):
    errno: int
    message: str
    description: str
    retriable: bool
    invalid_metadata: bool

class InvalidFetchRequestError(BrokerResponseError):
    errno: int
    message: str
    description: str

class LeaderNotAvailableError(BrokerResponseError):
    errno: int
    message: str
    description: str
    retriable: bool
    invalid_metadata: bool

class NotLeaderForPartitionError(BrokerResponseError):
    errno: int
    message: str
    description: str
    retriable: bool
    invalid_metadata: bool

class RequestTimedOutError(BrokerResponseError):
    errno: int
    message: str
    description: str
    retriable: bool

class BrokerNotAvailableError(BrokerResponseError):
    errno: int
    message: str
    description: str

class ReplicaNotAvailableError(BrokerResponseError):
    errno: int
    message: str
    description: str

class MessageSizeTooLargeError(BrokerResponseError):
    errno: int
    message: str
    description: str

class StaleControllerEpochError(BrokerResponseError):
    errno: int
    message: str
    description: str

class OffsetMetadataTooLargeError(BrokerResponseError):
    errno: int
    message: str
    description: str

class StaleLeaderEpochCodeError(BrokerResponseError):
    errno: int
    message: str

class GroupLoadInProgressError(BrokerResponseError):
    errno: int
    message: str
    description: str
    retriable: bool

CoordinatorLoadInProgressError = GroupLoadInProgressError

class GroupCoordinatorNotAvailableError(BrokerResponseError):
    errno: int
    message: str
    description: str
    retriable: bool

CoordinatorNotAvailableError = GroupCoordinatorNotAvailableError

class NotCoordinatorForGroupError(BrokerResponseError):
    errno: int
    message: str
    description: str
    retriable: bool

NotCoordinatorError = NotCoordinatorForGroupError

class InvalidTopicError(BrokerResponseError):
    errno: int
    message: str
    description: str

class RecordListTooLargeError(BrokerResponseError):
    errno: int
    message: str
    description: str

class NotEnoughReplicasError(BrokerResponseError):
    errno: int
    message: str
    description: str
    retriable: bool

class NotEnoughReplicasAfterAppendError(BrokerResponseError):
    errno: int
    message: str
    description: str
    retriable: bool

class InvalidRequiredAcksError(BrokerResponseError):
    errno: int
    message: str
    description: str

class IllegalGenerationError(BrokerResponseError):
    errno: int
    message: str
    description: str

class InconsistentGroupProtocolError(BrokerResponseError):
    errno: int
    message: str
    description: str

class InvalidGroupIdError(BrokerResponseError):
    errno: int
    message: str
    description: str

class UnknownMemberIdError(BrokerResponseError):
    errno: int
    message: str
    description: str

class InvalidSessionTimeoutError(BrokerResponseError):
    errno: int
    message: str
    description: str

class RebalanceInProgressError(BrokerResponseError):
    errno: int
    message: str
    description: str

class InvalidCommitOffsetSizeError(BrokerResponseError):
    errno: int
    message: str
    description: str

class TopicAuthorizationFailedError(BrokerResponseError):
    errno: int
    message: str
    description: str

class GroupAuthorizationFailedError(BrokerResponseError):
    errno: int
    message: str
    description: str

class ClusterAuthorizationFailedError(BrokerResponseError):
    errno: int
    message: str
    description: str

class InvalidTimestampError(BrokerResponseError):
    errno: int
    message: str
    description: str

class UnsupportedSaslMechanismError(BrokerResponseError):
    errno: int
    message: str
    description: str

class IllegalSaslStateError(BrokerResponseError):
    errno: int
    message: str
    description: str

class UnsupportedVersionError(BrokerResponseError):
    errno: int
    message: str
    description: str

class TopicAlreadyExistsError(BrokerResponseError):
    errno: int
    message: str
    description: str

class InvalidPartitionsError(BrokerResponseError):
    errno: int
    message: str
    description: str

class InvalidReplicationFactorError(BrokerResponseError):
    errno: int
    message: str
    description: str

class InvalidReplicationAssignmentError(BrokerResponseError):
    errno: int
    message: str
    description: str

class InvalidConfigurationError(BrokerResponseError):
    errno: int
    message: str
    description: str

class NotControllerError(BrokerResponseError):
    errno: int
    message: str
    description: str
    retriable: bool

class InvalidRequestError(BrokerResponseError):
    errno: int
    message: str
    description: str

class UnsupportedForMessageFormatError(BrokerResponseError):
    errno: int
    message: str
    description: str

class PolicyViolationError(BrokerResponseError):
    errno: int
    message: str
    description: str

class OutOfOrderSequenceNumber(BrokerResponseError):
    errno: int
    message: str
    description: str

class DuplicateSequenceNumber(BrokerResponseError):
    errno: int
    message: str
    description: str

class InvalidProducerEpoch(BrokerResponseError):
    errno: int
    message: str
    description: str

class InvalidTxnState(BrokerResponseError):
    errno: int
    message: str
    description: str

class InvalidProducerIdMapping(BrokerResponseError):
    errno: int
    message: str
    description: str

class InvalidTransactionTimeout(BrokerResponseError):
    errno: int
    message: str
    description: str

class ConcurrentTransactions(BrokerResponseError):
    errno: int
    message: str
    description: str

class TransactionCoordinatorFenced(BrokerResponseError):
    errno: int
    message: str
    description: str

class TransactionalIdAuthorizationFailed(BrokerResponseError):
    errno: int
    message: str
    description: str

class SecurityDisabled(BrokerResponseError):
    errno: int
    message: str
    description: str

class OperationNotAttempted(BrokerResponseError):
    errno: int
    message: str
    description: str

class KafkaStorageError(BrokerResponseError):
    errno: int
    message: str
    description: str
    retriable: bool
    invalid_metadata: bool

class LogDirNotFound(BrokerResponseError):
    errno: int
    message: str
    description: str

class SaslAuthenticationFailed(BrokerResponseError):
    errno: int
    message: str
    description: str

class UnknownProducerId(BrokerResponseError):
    errno: int
    message: str
    description: str

class ReassignmentInProgress(BrokerResponseError):
    errno: int
    message: str
    description: str

class DelegationTokenAuthDisabled(BrokerResponseError):
    errno: int
    message: str
    description: str

class DelegationTokenNotFound(BrokerResponseError):
    errno: int
    message: str
    description: str

class DelegationTokenOwnerMismatch(BrokerResponseError):
    errno: int
    message: str
    description: str

class DelegationTokenRequestNotAllowed(BrokerResponseError):
    errno: int
    message: str
    description: str

class DelegationTokenAuthorizationFailed(BrokerResponseError):
    errno: int
    message: str
    description: str

class DelegationTokenExpired(BrokerResponseError):
    errno: int
    message: str
    description: str

class InvalidPrincipalType(BrokerResponseError):
    errno: int
    message: str
    description: str

class NonEmptyGroup(BrokerResponseError):
    errno: int
    message: str
    description: str

class GroupIdNotFound(BrokerResponseError):
    errno: int
    message: str
    description: str

class FetchSessionIdNotFound(BrokerResponseError):
    errno: int
    message: str
    description: str

class InvalidFetchSessionEpoch(BrokerResponseError):
    errno: int
    message: str
    description: str

class ListenerNotFound(BrokerResponseError):
    errno: int
    message: str
    description: str

class MemberIdRequired(BrokerResponseError):
    errno: int
    message: str
    description: str
