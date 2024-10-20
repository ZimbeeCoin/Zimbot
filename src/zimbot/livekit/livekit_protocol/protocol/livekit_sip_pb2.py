# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: livekit_sip.proto
# Protobuf Python Version: 5.27.2
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    27,
    2,
    '',
    'livekit_sip.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import duration_pb2 as google_dot_protobuf_dot_duration__pb2
from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
from . import livekit_models_pb2 as livekit__models__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x11livekit_sip.proto\x12\x07livekit\x1a\x1egoogle/protobuf/duration.proto\x1a\x1bgoogle/protobuf/empty.proto\x1a\x14livekit_models.proto\"\xaf\x02\n\x15\x43reateSIPTrunkRequest\x12\x19\n\x11inbound_addresses\x18\x01 \x03(\t\x12\x18\n\x10outbound_address\x18\x02 \x01(\t\x12\x17\n\x0foutbound_number\x18\x03 \x01(\t\x12!\n\x15inbound_numbers_regex\x18\x04 \x03(\tB\x02\x18\x01\x12\x17\n\x0finbound_numbers\x18\t \x03(\t\x12\x18\n\x10inbound_username\x18\x05 \x01(\t\x12\x18\n\x10inbound_password\x18\x06 \x01(\t\x12\x19\n\x11outbound_username\x18\x07 \x01(\t\x12\x19\n\x11outbound_password\x18\x08 \x01(\t\x12\x0c\n\x04name\x18\n \x01(\t\x12\x10\n\x08metadata\x18\x0b \x01(\t:\x02\x18\x01\"\xdb\x03\n\x0cSIPTrunkInfo\x12\x14\n\x0csip_trunk_id\x18\x01 \x01(\t\x12-\n\x04kind\x18\x0e \x01(\x0e\x32\x1f.livekit.SIPTrunkInfo.TrunkKind\x12\x19\n\x11inbound_addresses\x18\x02 \x03(\t\x12\x18\n\x10outbound_address\x18\x03 \x01(\t\x12\x17\n\x0foutbound_number\x18\x04 \x01(\t\x12(\n\ttransport\x18\r \x01(\x0e\x32\x15.livekit.SIPTransport\x12!\n\x15inbound_numbers_regex\x18\x05 \x03(\tB\x02\x18\x01\x12\x17\n\x0finbound_numbers\x18\n \x03(\t\x12\x18\n\x10inbound_username\x18\x06 \x01(\t\x12\x18\n\x10inbound_password\x18\x07 \x01(\t\x12\x19\n\x11outbound_username\x18\x08 \x01(\t\x12\x19\n\x11outbound_password\x18\t \x01(\t\x12\x0c\n\x04name\x18\x0b \x01(\t\x12\x10\n\x08metadata\x18\x0c \x01(\t\"D\n\tTrunkKind\x12\x10\n\x0cTRUNK_LEGACY\x10\x00\x12\x11\n\rTRUNK_INBOUND\x10\x01\x12\x12\n\x0eTRUNK_OUTBOUND\x10\x02:\x02\x18\x01\"K\n\x1c\x43reateSIPInboundTrunkRequest\x12+\n\x05trunk\x18\x01 \x01(\x0b\x32\x1c.livekit.SIPInboundTrunkInfo\"\xa6\x04\n\x13SIPInboundTrunkInfo\x12\x14\n\x0csip_trunk_id\x18\x01 \x01(\t\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\x10\n\x08metadata\x18\x03 \x01(\t\x12\x0f\n\x07numbers\x18\x04 \x03(\t\x12\x19\n\x11\x61llowed_addresses\x18\x05 \x03(\t\x12\x17\n\x0f\x61llowed_numbers\x18\x06 \x03(\t\x12\x15\n\rauth_username\x18\x07 \x01(\t\x12\x15\n\rauth_password\x18\x08 \x01(\t\x12:\n\x07headers\x18\t \x03(\x0b\x32).livekit.SIPInboundTrunkInfo.HeadersEntry\x12T\n\x15headers_to_attributes\x18\n \x03(\x0b\x32\x35.livekit.SIPInboundTrunkInfo.HeadersToAttributesEntry\x12\x32\n\x0fringing_timeout\x18\x0b \x01(\x0b\x32\x19.google.protobuf.Duration\x12\x34\n\x11max_call_duration\x18\x0c \x01(\x0b\x32\x19.google.protobuf.Duration\x1a.\n\x0cHeadersEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t:\x02\x38\x01\x1a:\n\x18HeadersToAttributesEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t:\x02\x38\x01\"M\n\x1d\x43reateSIPOutboundTrunkRequest\x12,\n\x05trunk\x18\x01 \x01(\x0b\x32\x1d.livekit.SIPOutboundTrunkInfo\"\xc6\x03\n\x14SIPOutboundTrunkInfo\x12\x14\n\x0csip_trunk_id\x18\x01 \x01(\t\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\x10\n\x08metadata\x18\x03 \x01(\t\x12\x0f\n\x07\x61\x64\x64ress\x18\x04 \x01(\t\x12(\n\ttransport\x18\x05 \x01(\x0e\x32\x15.livekit.SIPTransport\x12\x0f\n\x07numbers\x18\x06 \x03(\t\x12\x15\n\rauth_username\x18\x07 \x01(\t\x12\x15\n\rauth_password\x18\x08 \x01(\t\x12;\n\x07headers\x18\t \x03(\x0b\x32*.livekit.SIPOutboundTrunkInfo.HeadersEntry\x12U\n\x15headers_to_attributes\x18\n \x03(\x0b\x32\x36.livekit.SIPOutboundTrunkInfo.HeadersToAttributesEntry\x1a.\n\x0cHeadersEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t:\x02\x38\x01\x1a:\n\x18HeadersToAttributesEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t:\x02\x38\x01\"1\n\x19GetSIPInboundTrunkRequest\x12\x14\n\x0csip_trunk_id\x18\x01 \x01(\t\"I\n\x1aGetSIPInboundTrunkResponse\x12+\n\x05trunk\x18\x01 \x01(\x0b\x32\x1c.livekit.SIPInboundTrunkInfo\"2\n\x1aGetSIPOutboundTrunkRequest\x12\x14\n\x0csip_trunk_id\x18\x01 \x01(\t\"K\n\x1bGetSIPOutboundTrunkResponse\x12,\n\x05trunk\x18\x01 \x01(\x0b\x32\x1d.livekit.SIPOutboundTrunkInfo\"\x19\n\x13ListSIPTrunkRequest:\x02\x18\x01\"@\n\x14ListSIPTrunkResponse\x12$\n\x05items\x18\x01 \x03(\x0b\x32\x15.livekit.SIPTrunkInfo:\x02\x18\x01\"\x1c\n\x1aListSIPInboundTrunkRequest\"J\n\x1bListSIPInboundTrunkResponse\x12+\n\x05items\x18\x01 \x03(\x0b\x32\x1c.livekit.SIPInboundTrunkInfo\"\x1d\n\x1bListSIPOutboundTrunkRequest\"L\n\x1cListSIPOutboundTrunkResponse\x12,\n\x05items\x18\x01 \x03(\x0b\x32\x1d.livekit.SIPOutboundTrunkInfo\"-\n\x15\x44\x65leteSIPTrunkRequest\x12\x14\n\x0csip_trunk_id\x18\x01 \x01(\t\"7\n\x15SIPDispatchRuleDirect\x12\x11\n\troom_name\x18\x01 \x01(\t\x12\x0b\n\x03pin\x18\x02 \x01(\t\"=\n\x19SIPDispatchRuleIndividual\x12\x13\n\x0broom_prefix\x18\x01 \x01(\t\x12\x0b\n\x03pin\x18\x02 \x01(\t\"L\n\x15SIPDispatchRuleCallee\x12\x13\n\x0broom_prefix\x18\x01 \x01(\t\x12\x0b\n\x03pin\x18\x02 \x01(\t\x12\x11\n\trandomize\x18\x03 \x01(\x08\"\xe1\x01\n\x0fSIPDispatchRule\x12>\n\x14\x64ispatch_rule_direct\x18\x01 \x01(\x0b\x32\x1e.livekit.SIPDispatchRuleDirectH\x00\x12\x46\n\x18\x64ispatch_rule_individual\x18\x02 \x01(\x0b\x32\".livekit.SIPDispatchRuleIndividualH\x00\x12>\n\x14\x64ispatch_rule_callee\x18\x03 \x01(\x0b\x32\x1e.livekit.SIPDispatchRuleCalleeH\x00\x42\x06\n\x04rule\"\xab\x02\n\x1c\x43reateSIPDispatchRuleRequest\x12&\n\x04rule\x18\x01 \x01(\x0b\x32\x18.livekit.SIPDispatchRule\x12\x11\n\ttrunk_ids\x18\x02 \x03(\t\x12\x19\n\x11hide_phone_number\x18\x03 \x01(\x08\x12\x17\n\x0finbound_numbers\x18\x06 \x03(\t\x12\x0c\n\x04name\x18\x04 \x01(\t\x12\x10\n\x08metadata\x18\x05 \x01(\t\x12I\n\nattributes\x18\x07 \x03(\x0b\x32\x35.livekit.CreateSIPDispatchRuleRequest.AttributesEntry\x1a\x31\n\x0f\x41ttributesEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t:\x02\x38\x01\"\xb7\x02\n\x13SIPDispatchRuleInfo\x12\x1c\n\x14sip_dispatch_rule_id\x18\x01 \x01(\t\x12&\n\x04rule\x18\x02 \x01(\x0b\x32\x18.livekit.SIPDispatchRule\x12\x11\n\ttrunk_ids\x18\x03 \x03(\t\x12\x19\n\x11hide_phone_number\x18\x04 \x01(\x08\x12\x17\n\x0finbound_numbers\x18\x07 \x03(\t\x12\x0c\n\x04name\x18\x05 \x01(\t\x12\x10\n\x08metadata\x18\x06 \x01(\t\x12@\n\nattributes\x18\x08 \x03(\x0b\x32,.livekit.SIPDispatchRuleInfo.AttributesEntry\x1a\x31\n\x0f\x41ttributesEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t:\x02\x38\x01\"\x1c\n\x1aListSIPDispatchRuleRequest\"J\n\x1bListSIPDispatchRuleResponse\x12+\n\x05items\x18\x01 \x03(\x0b\x32\x1c.livekit.SIPDispatchRuleInfo\"<\n\x1c\x44\x65leteSIPDispatchRuleRequest\x12\x1c\n\x14sip_dispatch_rule_id\x18\x01 \x01(\t\"\xfa\x03\n\x1b\x43reateSIPParticipantRequest\x12\x14\n\x0csip_trunk_id\x18\x01 \x01(\t\x12\x13\n\x0bsip_call_to\x18\x02 \x01(\t\x12\x11\n\troom_name\x18\x03 \x01(\t\x12\x1c\n\x14participant_identity\x18\x04 \x01(\t\x12\x18\n\x10participant_name\x18\x07 \x01(\t\x12\x1c\n\x14participant_metadata\x18\x08 \x01(\t\x12_\n\x16participant_attributes\x18\t \x03(\x0b\x32?.livekit.CreateSIPParticipantRequest.ParticipantAttributesEntry\x12\x0c\n\x04\x64tmf\x18\x05 \x01(\t\x12\x15\n\rplay_ringtone\x18\x06 \x01(\x08\x12\x19\n\x11hide_phone_number\x18\n \x01(\x08\x12\x32\n\x0fringing_timeout\x18\x0b \x01(\x0b\x32\x19.google.protobuf.Duration\x12\x34\n\x11max_call_duration\x18\x0c \x01(\x0b\x32\x19.google.protobuf.Duration\x1a<\n\x1aParticipantAttributesEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t:\x02\x38\x01\"r\n\x12SIPParticipantInfo\x12\x16\n\x0eparticipant_id\x18\x01 \x01(\t\x12\x1c\n\x14participant_identity\x18\x02 \x01(\t\x12\x11\n\troom_name\x18\x03 \x01(\t\x12\x13\n\x0bsip_call_id\x18\x04 \x01(\t\"e\n\x1dTransferSIPParticipantRequest\x12\x1c\n\x14participant_identity\x18\x01 \x01(\t\x12\x11\n\troom_name\x18\x02 \x01(\t\x12\x13\n\x0btransfer_to\x18\x03 \x01(\t\"\xbf\x02\n\x0bSIPCallInfo\x12\x0f\n\x07\x63\x61ll_id\x18\x01 \x01(\t\x12\x10\n\x08trunk_id\x18\x02 \x01(\t\x12\x11\n\troom_name\x18\x03 \x01(\t\x12\x0f\n\x07room_id\x18\x04 \x01(\t\x12\x1c\n\x14participant_identity\x18\x05 \x01(\t\x12!\n\x08\x66rom_uri\x18\x06 \x01(\x0b\x32\x0f.livekit.SIPUri\x12\x1f\n\x06to_uri\x18\x07 \x01(\x0b\x32\x0f.livekit.SIPUri\x12+\n\x0b\x63\x61ll_status\x18\x08 \x01(\x0e\x32\x16.livekit.SIPCallStatus\x12\x12\n\nstarted_at\x18\t \x01(\x03\x12\x10\n\x08\x65nded_at\x18\n \x01(\x03\x12\x34\n\x11\x64isconnect_reason\x18\x0b \x01(\x0e\x32\x19.livekit.DisconnectReason\"h\n\x06SIPUri\x12\x0c\n\x04user\x18\x01 \x01(\t\x12\x0c\n\x04host\x18\x02 \x01(\t\x12\n\n\x02ip\x18\x03 \x01(\t\x12\x0c\n\x04port\x18\x04 \x01(\t\x12(\n\ttransport\x18\x05 \x01(\x0e\x32\x15.livekit.SIPTransport*k\n\x0cSIPTransport\x12\x16\n\x12SIP_TRANSPORT_AUTO\x10\x00\x12\x15\n\x11SIP_TRANSPORT_UDP\x10\x01\x12\x15\n\x11SIP_TRANSPORT_TCP\x10\x02\x12\x15\n\x11SIP_TRANSPORT_TLS\x10\x03*h\n\rSIPCallStatus\x12\x15\n\x11SCS_CALL_INCOMING\x10\x00\x12\x1a\n\x16SCS_PARTICIPANT_JOINED\x10\x01\x12\x0e\n\nSCS_ACTIVE\x10\x02\x12\x14\n\x10SCS_DISCONNECTED\x10\x03\x32\xba\t\n\x03SIP\x12P\n\x0cListSIPTrunk\x12\x1c.livekit.ListSIPTrunkRequest\x1a\x1d.livekit.ListSIPTrunkResponse\"\x03\x88\x02\x01\x12\\\n\x15\x43reateSIPInboundTrunk\x12%.livekit.CreateSIPInboundTrunkRequest\x1a\x1c.livekit.SIPInboundTrunkInfo\x12_\n\x16\x43reateSIPOutboundTrunk\x12&.livekit.CreateSIPOutboundTrunkRequest\x1a\x1d.livekit.SIPOutboundTrunkInfo\x12]\n\x12GetSIPInboundTrunk\x12\".livekit.GetSIPInboundTrunkRequest\x1a#.livekit.GetSIPInboundTrunkResponse\x12`\n\x13GetSIPOutboundTrunk\x12#.livekit.GetSIPOutboundTrunkRequest\x1a$.livekit.GetSIPOutboundTrunkResponse\x12`\n\x13ListSIPInboundTrunk\x12#.livekit.ListSIPInboundTrunkRequest\x1a$.livekit.ListSIPInboundTrunkResponse\x12\x63\n\x14ListSIPOutboundTrunk\x12$.livekit.ListSIPOutboundTrunkRequest\x1a%.livekit.ListSIPOutboundTrunkResponse\x12G\n\x0e\x44\x65leteSIPTrunk\x12\x1e.livekit.DeleteSIPTrunkRequest\x1a\x15.livekit.SIPTrunkInfo\x12\\\n\x15\x43reateSIPDispatchRule\x12%.livekit.CreateSIPDispatchRuleRequest\x1a\x1c.livekit.SIPDispatchRuleInfo\x12`\n\x13ListSIPDispatchRule\x12#.livekit.ListSIPDispatchRuleRequest\x1a$.livekit.ListSIPDispatchRuleResponse\x12\\\n\x15\x44\x65leteSIPDispatchRule\x12%.livekit.DeleteSIPDispatchRuleRequest\x1a\x1c.livekit.SIPDispatchRuleInfo\x12Y\n\x14\x43reateSIPParticipant\x12$.livekit.CreateSIPParticipantRequest\x1a\x1b.livekit.SIPParticipantInfo\x12X\n\x16TransferSIPParticipant\x12&.livekit.TransferSIPParticipantRequest\x1a\x16.google.protobuf.EmptyBFZ#github.com/livekit/protocol/livekit\xaa\x02\rLiveKit.Proto\xea\x02\x0eLiveKit::Protob\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'livekit_sip_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  _globals['DESCRIPTOR']._loaded_options = None
  _globals['DESCRIPTOR']._serialized_options = b'Z#github.com/livekit/protocol/livekit\252\002\rLiveKit.Proto\352\002\016LiveKit::Proto'
  _globals['_CREATESIPTRUNKREQUEST'].fields_by_name['inbound_numbers_regex']._loaded_options = None
  _globals['_CREATESIPTRUNKREQUEST'].fields_by_name['inbound_numbers_regex']._serialized_options = b'\030\001'
  _globals['_CREATESIPTRUNKREQUEST']._loaded_options = None
  _globals['_CREATESIPTRUNKREQUEST']._serialized_options = b'\030\001'
  _globals['_SIPTRUNKINFO'].fields_by_name['inbound_numbers_regex']._loaded_options = None
  _globals['_SIPTRUNKINFO'].fields_by_name['inbound_numbers_regex']._serialized_options = b'\030\001'
  _globals['_SIPTRUNKINFO']._loaded_options = None
  _globals['_SIPTRUNKINFO']._serialized_options = b'\030\001'
  _globals['_SIPINBOUNDTRUNKINFO_HEADERSENTRY']._loaded_options = None
  _globals['_SIPINBOUNDTRUNKINFO_HEADERSENTRY']._serialized_options = b'8\001'
  _globals['_SIPINBOUNDTRUNKINFO_HEADERSTOATTRIBUTESENTRY']._loaded_options = None
  _globals['_SIPINBOUNDTRUNKINFO_HEADERSTOATTRIBUTESENTRY']._serialized_options = b'8\001'
  _globals['_SIPOUTBOUNDTRUNKINFO_HEADERSENTRY']._loaded_options = None
  _globals['_SIPOUTBOUNDTRUNKINFO_HEADERSENTRY']._serialized_options = b'8\001'
  _globals['_SIPOUTBOUNDTRUNKINFO_HEADERSTOATTRIBUTESENTRY']._loaded_options = None
  _globals['_SIPOUTBOUNDTRUNKINFO_HEADERSTOATTRIBUTESENTRY']._serialized_options = b'8\001'
  _globals['_LISTSIPTRUNKREQUEST']._loaded_options = None
  _globals['_LISTSIPTRUNKREQUEST']._serialized_options = b'\030\001'
  _globals['_LISTSIPTRUNKRESPONSE']._loaded_options = None
  _globals['_LISTSIPTRUNKRESPONSE']._serialized_options = b'\030\001'
  _globals['_CREATESIPDISPATCHRULEREQUEST_ATTRIBUTESENTRY']._loaded_options = None
  _globals['_CREATESIPDISPATCHRULEREQUEST_ATTRIBUTESENTRY']._serialized_options = b'8\001'
  _globals['_SIPDISPATCHRULEINFO_ATTRIBUTESENTRY']._loaded_options = None
  _globals['_SIPDISPATCHRULEINFO_ATTRIBUTESENTRY']._serialized_options = b'8\001'
  _globals['_CREATESIPPARTICIPANTREQUEST_PARTICIPANTATTRIBUTESENTRY']._loaded_options = None
  _globals['_CREATESIPPARTICIPANTREQUEST_PARTICIPANTATTRIBUTESENTRY']._serialized_options = b'8\001'
  _globals['_SIP'].methods_by_name['ListSIPTrunk']._loaded_options = None
  _globals['_SIP'].methods_by_name['ListSIPTrunk']._serialized_options = b'\210\002\001'
  _globals['_SIPTRANSPORT']._serialized_start=5039
  _globals['_SIPTRANSPORT']._serialized_end=5146
  _globals['_SIPCALLSTATUS']._serialized_start=5148
  _globals['_SIPCALLSTATUS']._serialized_end=5252
  _globals['_CREATESIPTRUNKREQUEST']._serialized_start=114
  _globals['_CREATESIPTRUNKREQUEST']._serialized_end=417
  _globals['_SIPTRUNKINFO']._serialized_start=420
  _globals['_SIPTRUNKINFO']._serialized_end=895
  _globals['_SIPTRUNKINFO_TRUNKKIND']._serialized_start=823
  _globals['_SIPTRUNKINFO_TRUNKKIND']._serialized_end=891
  _globals['_CREATESIPINBOUNDTRUNKREQUEST']._serialized_start=897
  _globals['_CREATESIPINBOUNDTRUNKREQUEST']._serialized_end=972
  _globals['_SIPINBOUNDTRUNKINFO']._serialized_start=975
  _globals['_SIPINBOUNDTRUNKINFO']._serialized_end=1525
  _globals['_SIPINBOUNDTRUNKINFO_HEADERSENTRY']._serialized_start=1419
  _globals['_SIPINBOUNDTRUNKINFO_HEADERSENTRY']._serialized_end=1465
  _globals['_SIPINBOUNDTRUNKINFO_HEADERSTOATTRIBUTESENTRY']._serialized_start=1467
  _globals['_SIPINBOUNDTRUNKINFO_HEADERSTOATTRIBUTESENTRY']._serialized_end=1525
  _globals['_CREATESIPOUTBOUNDTRUNKREQUEST']._serialized_start=1527
  _globals['_CREATESIPOUTBOUNDTRUNKREQUEST']._serialized_end=1604
  _globals['_SIPOUTBOUNDTRUNKINFO']._serialized_start=1607
  _globals['_SIPOUTBOUNDTRUNKINFO']._serialized_end=2061
  _globals['_SIPOUTBOUNDTRUNKINFO_HEADERSENTRY']._serialized_start=1419
  _globals['_SIPOUTBOUNDTRUNKINFO_HEADERSENTRY']._serialized_end=1465
  _globals['_SIPOUTBOUNDTRUNKINFO_HEADERSTOATTRIBUTESENTRY']._serialized_start=1467
  _globals['_SIPOUTBOUNDTRUNKINFO_HEADERSTOATTRIBUTESENTRY']._serialized_end=1525
  _globals['_GETSIPINBOUNDTRUNKREQUEST']._serialized_start=2063
  _globals['_GETSIPINBOUNDTRUNKREQUEST']._serialized_end=2112
  _globals['_GETSIPINBOUNDTRUNKRESPONSE']._serialized_start=2114
  _globals['_GETSIPINBOUNDTRUNKRESPONSE']._serialized_end=2187
  _globals['_GETSIPOUTBOUNDTRUNKREQUEST']._serialized_start=2189
  _globals['_GETSIPOUTBOUNDTRUNKREQUEST']._serialized_end=2239
  _globals['_GETSIPOUTBOUNDTRUNKRESPONSE']._serialized_start=2241
  _globals['_GETSIPOUTBOUNDTRUNKRESPONSE']._serialized_end=2316
  _globals['_LISTSIPTRUNKREQUEST']._serialized_start=2318
  _globals['_LISTSIPTRUNKREQUEST']._serialized_end=2343
  _globals['_LISTSIPTRUNKRESPONSE']._serialized_start=2345
  _globals['_LISTSIPTRUNKRESPONSE']._serialized_end=2409
  _globals['_LISTSIPINBOUNDTRUNKREQUEST']._serialized_start=2411
  _globals['_LISTSIPINBOUNDTRUNKREQUEST']._serialized_end=2439
  _globals['_LISTSIPINBOUNDTRUNKRESPONSE']._serialized_start=2441
  _globals['_LISTSIPINBOUNDTRUNKRESPONSE']._serialized_end=2515
  _globals['_LISTSIPOUTBOUNDTRUNKREQUEST']._serialized_start=2517
  _globals['_LISTSIPOUTBOUNDTRUNKREQUEST']._serialized_end=2546
  _globals['_LISTSIPOUTBOUNDTRUNKRESPONSE']._serialized_start=2548
  _globals['_LISTSIPOUTBOUNDTRUNKRESPONSE']._serialized_end=2624
  _globals['_DELETESIPTRUNKREQUEST']._serialized_start=2626
  _globals['_DELETESIPTRUNKREQUEST']._serialized_end=2671
  _globals['_SIPDISPATCHRULEDIRECT']._serialized_start=2673
  _globals['_SIPDISPATCHRULEDIRECT']._serialized_end=2728
  _globals['_SIPDISPATCHRULEINDIVIDUAL']._serialized_start=2730
  _globals['_SIPDISPATCHRULEINDIVIDUAL']._serialized_end=2791
  _globals['_SIPDISPATCHRULECALLEE']._serialized_start=2793
  _globals['_SIPDISPATCHRULECALLEE']._serialized_end=2869
  _globals['_SIPDISPATCHRULE']._serialized_start=2872
  _globals['_SIPDISPATCHRULE']._serialized_end=3097
  _globals['_CREATESIPDISPATCHRULEREQUEST']._serialized_start=3100
  _globals['_CREATESIPDISPATCHRULEREQUEST']._serialized_end=3399
  _globals['_CREATESIPDISPATCHRULEREQUEST_ATTRIBUTESENTRY']._serialized_start=3350
  _globals['_CREATESIPDISPATCHRULEREQUEST_ATTRIBUTESENTRY']._serialized_end=3399
  _globals['_SIPDISPATCHRULEINFO']._serialized_start=3402
  _globals['_SIPDISPATCHRULEINFO']._serialized_end=3713
  _globals['_SIPDISPATCHRULEINFO_ATTRIBUTESENTRY']._serialized_start=3350
  _globals['_SIPDISPATCHRULEINFO_ATTRIBUTESENTRY']._serialized_end=3399
  _globals['_LISTSIPDISPATCHRULEREQUEST']._serialized_start=3715
  _globals['_LISTSIPDISPATCHRULEREQUEST']._serialized_end=3743
  _globals['_LISTSIPDISPATCHRULERESPONSE']._serialized_start=3745
  _globals['_LISTSIPDISPATCHRULERESPONSE']._serialized_end=3819
  _globals['_DELETESIPDISPATCHRULEREQUEST']._serialized_start=3821
  _globals['_DELETESIPDISPATCHRULEREQUEST']._serialized_end=3881
  _globals['_CREATESIPPARTICIPANTREQUEST']._serialized_start=3884
  _globals['_CREATESIPPARTICIPANTREQUEST']._serialized_end=4390
  _globals['_CREATESIPPARTICIPANTREQUEST_PARTICIPANTATTRIBUTESENTRY']._serialized_start=4330
  _globals['_CREATESIPPARTICIPANTREQUEST_PARTICIPANTATTRIBUTESENTRY']._serialized_end=4390
  _globals['_SIPPARTICIPANTINFO']._serialized_start=4392
  _globals['_SIPPARTICIPANTINFO']._serialized_end=4506
  _globals['_TRANSFERSIPPARTICIPANTREQUEST']._serialized_start=4508
  _globals['_TRANSFERSIPPARTICIPANTREQUEST']._serialized_end=4609
  _globals['_SIPCALLINFO']._serialized_start=4612
  _globals['_SIPCALLINFO']._serialized_end=4931
  _globals['_SIPURI']._serialized_start=4933
  _globals['_SIPURI']._serialized_end=5037
  _globals['_SIP']._serialized_start=5255
  _globals['_SIP']._serialized_end=6465
# @@protoc_insertion_point(module_scope)
