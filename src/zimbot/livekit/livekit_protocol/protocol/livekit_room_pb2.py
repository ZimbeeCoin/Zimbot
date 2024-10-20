# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: livekit_room.proto
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
    'livekit_room.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from . import livekit_models_pb2 as livekit__models__pb2
from . import livekit_egress_pb2 as livekit__egress__pb2
from . import livekit_agent_dispatch_pb2 as livekit__agent__dispatch__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x12livekit_room.proto\x12\x07livekit\x1a\x14livekit_models.proto\x1a\x14livekit_egress.proto\x1a\x1clivekit_agent_dispatch.proto\"\xd1\x02\n\x11\x43reateRoomRequest\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x13\n\x0b\x63onfig_name\x18\x0c \x01(\t\x12\x15\n\rempty_timeout\x18\x02 \x01(\r\x12\x19\n\x11\x64\x65parture_timeout\x18\n \x01(\r\x12\x18\n\x10max_participants\x18\x03 \x01(\r\x12\x0f\n\x07node_id\x18\x04 \x01(\t\x12\x10\n\x08metadata\x18\x05 \x01(\t\x12#\n\x06\x65gress\x18\x06 \x01(\x0b\x32\x13.livekit.RoomEgress\x12!\n\x05\x61gent\x18\x0b \x01(\x0b\x32\x12.livekit.RoomAgent\x12\x19\n\x11min_playout_delay\x18\x07 \x01(\r\x12\x19\n\x11max_playout_delay\x18\x08 \x01(\r\x12\x14\n\x0csync_streams\x18\t \x01(\x08\x12\x16\n\x0ereplay_enabled\x18\r \x01(\x08\"\x9e\x01\n\nRoomEgress\x12\x31\n\x04room\x18\x01 \x01(\x0b\x32#.livekit.RoomCompositeEgressRequest\x12\x33\n\x0bparticipant\x18\x03 \x01(\x0b\x32\x1e.livekit.AutoParticipantEgress\x12(\n\x06tracks\x18\x02 \x01(\x0b\x32\x18.livekit.AutoTrackEgress\";\n\tRoomAgent\x12.\n\ndispatches\x18\x01 \x03(\x0b\x32\x1a.livekit.RoomAgentDispatch\"!\n\x10ListRoomsRequest\x12\r\n\x05names\x18\x01 \x03(\t\"1\n\x11ListRoomsResponse\x12\x1c\n\x05rooms\x18\x01 \x03(\x0b\x32\r.livekit.Room\"!\n\x11\x44\x65leteRoomRequest\x12\x0c\n\x04room\x18\x01 \x01(\t\"\x14\n\x12\x44\x65leteRoomResponse\"\'\n\x17ListParticipantsRequest\x12\x0c\n\x04room\x18\x01 \x01(\t\"J\n\x18ListParticipantsResponse\x12.\n\x0cparticipants\x18\x01 \x03(\x0b\x32\x18.livekit.ParticipantInfo\"9\n\x17RoomParticipantIdentity\x12\x0c\n\x04room\x18\x01 \x01(\t\x12\x10\n\x08identity\x18\x02 \x01(\t\"\x1b\n\x19RemoveParticipantResponse\"X\n\x14MuteRoomTrackRequest\x12\x0c\n\x04room\x18\x01 \x01(\t\x12\x10\n\x08identity\x18\x02 \x01(\t\x12\x11\n\ttrack_sid\x18\x03 \x01(\t\x12\r\n\x05muted\x18\x04 \x01(\x08\":\n\x15MuteRoomTrackResponse\x12!\n\x05track\x18\x01 \x01(\x0b\x32\x12.livekit.TrackInfo\"\x88\x02\n\x18UpdateParticipantRequest\x12\x0c\n\x04room\x18\x01 \x01(\t\x12\x10\n\x08identity\x18\x02 \x01(\t\x12\x10\n\x08metadata\x18\x03 \x01(\t\x12\x32\n\npermission\x18\x04 \x01(\x0b\x32\x1e.livekit.ParticipantPermission\x12\x0c\n\x04name\x18\x05 \x01(\t\x12\x45\n\nattributes\x18\x06 \x03(\x0b\x32\x31.livekit.UpdateParticipantRequest.AttributesEntry\x1a\x31\n\x0f\x41ttributesEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t:\x02\x38\x01\"\x9b\x01\n\x1aUpdateSubscriptionsRequest\x12\x0c\n\x04room\x18\x01 \x01(\t\x12\x10\n\x08identity\x18\x02 \x01(\t\x12\x12\n\ntrack_sids\x18\x03 \x03(\t\x12\x11\n\tsubscribe\x18\x04 \x01(\x08\x12\x36\n\x12participant_tracks\x18\x05 \x03(\x0b\x32\x1a.livekit.ParticipantTracks\"\x1d\n\x1bUpdateSubscriptionsResponse\"\xb1\x01\n\x0fSendDataRequest\x12\x0c\n\x04room\x18\x01 \x01(\t\x12\x0c\n\x04\x64\x61ta\x18\x02 \x01(\x0c\x12&\n\x04kind\x18\x03 \x01(\x0e\x32\x18.livekit.DataPacket.Kind\x12\x1c\n\x10\x64\x65stination_sids\x18\x04 \x03(\tB\x02\x18\x01\x12\x1e\n\x16\x64\x65stination_identities\x18\x06 \x03(\t\x12\x12\n\x05topic\x18\x05 \x01(\tH\x00\x88\x01\x01\x42\x08\n\x06_topic\"\x12\n\x10SendDataResponse\";\n\x19UpdateRoomMetadataRequest\x12\x0c\n\x04room\x18\x01 \x01(\t\x12\x10\n\x08metadata\x18\x02 \x01(\t\"\x81\x02\n\x11RoomConfiguration\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x15\n\rempty_timeout\x18\x02 \x01(\r\x12\x19\n\x11\x64\x65parture_timeout\x18\x03 \x01(\r\x12\x18\n\x10max_participants\x18\x04 \x01(\r\x12#\n\x06\x65gress\x18\x05 \x01(\x0b\x32\x13.livekit.RoomEgress\x12!\n\x05\x61gent\x18\x06 \x01(\x0b\x32\x12.livekit.RoomAgent\x12\x19\n\x11min_playout_delay\x18\x07 \x01(\r\x12\x19\n\x11max_playout_delay\x18\x08 \x01(\r\x12\x14\n\x0csync_streams\x18\t \x01(\x08\x32\xe6\x06\n\x0bRoomService\x12\x37\n\nCreateRoom\x12\x1a.livekit.CreateRoomRequest\x1a\r.livekit.Room\x12\x42\n\tListRooms\x12\x19.livekit.ListRoomsRequest\x1a\x1a.livekit.ListRoomsResponse\x12\x45\n\nDeleteRoom\x12\x1a.livekit.DeleteRoomRequest\x1a\x1b.livekit.DeleteRoomResponse\x12W\n\x10ListParticipants\x12 .livekit.ListParticipantsRequest\x1a!.livekit.ListParticipantsResponse\x12L\n\x0eGetParticipant\x12 .livekit.RoomParticipantIdentity\x1a\x18.livekit.ParticipantInfo\x12Y\n\x11RemoveParticipant\x12 .livekit.RoomParticipantIdentity\x1a\".livekit.RemoveParticipantResponse\x12S\n\x12MutePublishedTrack\x12\x1d.livekit.MuteRoomTrackRequest\x1a\x1e.livekit.MuteRoomTrackResponse\x12P\n\x11UpdateParticipant\x12!.livekit.UpdateParticipantRequest\x1a\x18.livekit.ParticipantInfo\x12`\n\x13UpdateSubscriptions\x12#.livekit.UpdateSubscriptionsRequest\x1a$.livekit.UpdateSubscriptionsResponse\x12?\n\x08SendData\x12\x18.livekit.SendDataRequest\x1a\x19.livekit.SendDataResponse\x12G\n\x12UpdateRoomMetadata\x12\".livekit.UpdateRoomMetadataRequest\x1a\r.livekit.RoomBFZ#github.com/livekit/protocol/livekit\xaa\x02\rLiveKit.Proto\xea\x02\x0eLiveKit::Protob\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'livekit_room_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  _globals['DESCRIPTOR']._loaded_options = None
  _globals['DESCRIPTOR']._serialized_options = b'Z#github.com/livekit/protocol/livekit\252\002\rLiveKit.Proto\352\002\016LiveKit::Proto'
  _globals['_UPDATEPARTICIPANTREQUEST_ATTRIBUTESENTRY']._loaded_options = None
  _globals['_UPDATEPARTICIPANTREQUEST_ATTRIBUTESENTRY']._serialized_options = b'8\001'
  _globals['_SENDDATAREQUEST'].fields_by_name['destination_sids']._loaded_options = None
  _globals['_SENDDATAREQUEST'].fields_by_name['destination_sids']._serialized_options = b'\030\001'
  _globals['_CREATEROOMREQUEST']._serialized_start=106
  _globals['_CREATEROOMREQUEST']._serialized_end=443
  _globals['_ROOMEGRESS']._serialized_start=446
  _globals['_ROOMEGRESS']._serialized_end=604
  _globals['_ROOMAGENT']._serialized_start=606
  _globals['_ROOMAGENT']._serialized_end=665
  _globals['_LISTROOMSREQUEST']._serialized_start=667
  _globals['_LISTROOMSREQUEST']._serialized_end=700
  _globals['_LISTROOMSRESPONSE']._serialized_start=702
  _globals['_LISTROOMSRESPONSE']._serialized_end=751
  _globals['_DELETEROOMREQUEST']._serialized_start=753
  _globals['_DELETEROOMREQUEST']._serialized_end=786
  _globals['_DELETEROOMRESPONSE']._serialized_start=788
  _globals['_DELETEROOMRESPONSE']._serialized_end=808
  _globals['_LISTPARTICIPANTSREQUEST']._serialized_start=810
  _globals['_LISTPARTICIPANTSREQUEST']._serialized_end=849
  _globals['_LISTPARTICIPANTSRESPONSE']._serialized_start=851
  _globals['_LISTPARTICIPANTSRESPONSE']._serialized_end=925
  _globals['_ROOMPARTICIPANTIDENTITY']._serialized_start=927
  _globals['_ROOMPARTICIPANTIDENTITY']._serialized_end=984
  _globals['_REMOVEPARTICIPANTRESPONSE']._serialized_start=986
  _globals['_REMOVEPARTICIPANTRESPONSE']._serialized_end=1013
  _globals['_MUTEROOMTRACKREQUEST']._serialized_start=1015
  _globals['_MUTEROOMTRACKREQUEST']._serialized_end=1103
  _globals['_MUTEROOMTRACKRESPONSE']._serialized_start=1105
  _globals['_MUTEROOMTRACKRESPONSE']._serialized_end=1163
  _globals['_UPDATEPARTICIPANTREQUEST']._serialized_start=1166
  _globals['_UPDATEPARTICIPANTREQUEST']._serialized_end=1430
  _globals['_UPDATEPARTICIPANTREQUEST_ATTRIBUTESENTRY']._serialized_start=1381
  _globals['_UPDATEPARTICIPANTREQUEST_ATTRIBUTESENTRY']._serialized_end=1430
  _globals['_UPDATESUBSCRIPTIONSREQUEST']._serialized_start=1433
  _globals['_UPDATESUBSCRIPTIONSREQUEST']._serialized_end=1588
  _globals['_UPDATESUBSCRIPTIONSRESPONSE']._serialized_start=1590
  _globals['_UPDATESUBSCRIPTIONSRESPONSE']._serialized_end=1619
  _globals['_SENDDATAREQUEST']._serialized_start=1622
  _globals['_SENDDATAREQUEST']._serialized_end=1799
  _globals['_SENDDATARESPONSE']._serialized_start=1801
  _globals['_SENDDATARESPONSE']._serialized_end=1819
  _globals['_UPDATEROOMMETADATAREQUEST']._serialized_start=1821
  _globals['_UPDATEROOMMETADATAREQUEST']._serialized_end=1880
  _globals['_ROOMCONFIGURATION']._serialized_start=1883
  _globals['_ROOMCONFIGURATION']._serialized_end=2140
  _globals['_ROOMSERVICE']._serialized_start=2143
  _globals['_ROOMSERVICE']._serialized_end=3013
# @@protoc_insertion_point(module_scope)
