# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

import livekit_models_pb2 as livekit__models__pb2
import livekit_room_pb2 as livekit__room__pb2

GRPC_GENERATED_VERSION = '1.67.0'
GRPC_VERSION = grpc.__version__
_version_not_supported = False

try:
    from grpc._utilities import first_version_is_lower
    _version_not_supported = first_version_is_lower(GRPC_VERSION, GRPC_GENERATED_VERSION)
except ImportError:
    _version_not_supported = True

if _version_not_supported:
    raise RuntimeError(
        f'The grpc package installed is at version {GRPC_VERSION},'
        + f' but the generated code in livekit_room_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class RoomServiceStub(object):
    """Room service that can be performed on any node
    they are Twirp-based HTTP req/responses
    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.CreateRoom = channel.unary_unary(
                '/livekit.RoomService/CreateRoom',
                request_serializer=livekit__room__pb2.CreateRoomRequest.SerializeToString,
                response_deserializer=livekit__models__pb2.Room.FromString,
                _registered_method=True)
        self.ListRooms = channel.unary_unary(
                '/livekit.RoomService/ListRooms',
                request_serializer=livekit__room__pb2.ListRoomsRequest.SerializeToString,
                response_deserializer=livekit__room__pb2.ListRoomsResponse.FromString,
                _registered_method=True)
        self.DeleteRoom = channel.unary_unary(
                '/livekit.RoomService/DeleteRoom',
                request_serializer=livekit__room__pb2.DeleteRoomRequest.SerializeToString,
                response_deserializer=livekit__room__pb2.DeleteRoomResponse.FromString,
                _registered_method=True)
        self.ListParticipants = channel.unary_unary(
                '/livekit.RoomService/ListParticipants',
                request_serializer=livekit__room__pb2.ListParticipantsRequest.SerializeToString,
                response_deserializer=livekit__room__pb2.ListParticipantsResponse.FromString,
                _registered_method=True)
        self.GetParticipant = channel.unary_unary(
                '/livekit.RoomService/GetParticipant',
                request_serializer=livekit__room__pb2.RoomParticipantIdentity.SerializeToString,
                response_deserializer=livekit__models__pb2.ParticipantInfo.FromString,
                _registered_method=True)
        self.RemoveParticipant = channel.unary_unary(
                '/livekit.RoomService/RemoveParticipant',
                request_serializer=livekit__room__pb2.RoomParticipantIdentity.SerializeToString,
                response_deserializer=livekit__room__pb2.RemoveParticipantResponse.FromString,
                _registered_method=True)
        self.MutePublishedTrack = channel.unary_unary(
                '/livekit.RoomService/MutePublishedTrack',
                request_serializer=livekit__room__pb2.MuteRoomTrackRequest.SerializeToString,
                response_deserializer=livekit__room__pb2.MuteRoomTrackResponse.FromString,
                _registered_method=True)
        self.UpdateParticipant = channel.unary_unary(
                '/livekit.RoomService/UpdateParticipant',
                request_serializer=livekit__room__pb2.UpdateParticipantRequest.SerializeToString,
                response_deserializer=livekit__models__pb2.ParticipantInfo.FromString,
                _registered_method=True)
        self.UpdateSubscriptions = channel.unary_unary(
                '/livekit.RoomService/UpdateSubscriptions',
                request_serializer=livekit__room__pb2.UpdateSubscriptionsRequest.SerializeToString,
                response_deserializer=livekit__room__pb2.UpdateSubscriptionsResponse.FromString,
                _registered_method=True)
        self.SendData = channel.unary_unary(
                '/livekit.RoomService/SendData',
                request_serializer=livekit__room__pb2.SendDataRequest.SerializeToString,
                response_deserializer=livekit__room__pb2.SendDataResponse.FromString,
                _registered_method=True)
        self.UpdateRoomMetadata = channel.unary_unary(
                '/livekit.RoomService/UpdateRoomMetadata',
                request_serializer=livekit__room__pb2.UpdateRoomMetadataRequest.SerializeToString,
                response_deserializer=livekit__models__pb2.Room.FromString,
                _registered_method=True)


class RoomServiceServicer(object):
    """Room service that can be performed on any node
    they are Twirp-based HTTP req/responses
    """

    def CreateRoom(self, request, context):
        """Creates a room with settings. Requires `roomCreate` permission.
        This method is optional; rooms are automatically created when clients connect to them for the first time.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ListRooms(self, request, context):
        """List rooms that are active on the server. Requires `roomList` permission.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def DeleteRoom(self, request, context):
        """Deletes an existing room by name or id. Requires `roomCreate` permission.
        DeleteRoom will disconnect all participants that are currently in the room.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ListParticipants(self, request, context):
        """Lists participants in a room, Requires `roomAdmin`
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetParticipant(self, request, context):
        """Get information on a specific participant, Requires `roomAdmin`
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def RemoveParticipant(self, request, context):
        """Removes a participant from room. Requires `roomAdmin`
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def MutePublishedTrack(self, request, context):
        """Mute/unmute a participant's track, Requires `roomAdmin`
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def UpdateParticipant(self, request, context):
        """Update participant metadata, will cause updates to be broadcasted to everyone in the room. Requires `roomAdmin`
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def UpdateSubscriptions(self, request, context):
        """Subscribes or unsubscribe a participant from tracks. Requires `roomAdmin`
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SendData(self, request, context):
        """Send data over data channel to participants in a room, Requires `roomAdmin`
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def UpdateRoomMetadata(self, request, context):
        """Update room metadata, will cause updates to be broadcasted to everyone in the room, Requires `roomAdmin`
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_RoomServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'CreateRoom': grpc.unary_unary_rpc_method_handler(
                    servicer.CreateRoom,
                    request_deserializer=livekit__room__pb2.CreateRoomRequest.FromString,
                    response_serializer=livekit__models__pb2.Room.SerializeToString,
            ),
            'ListRooms': grpc.unary_unary_rpc_method_handler(
                    servicer.ListRooms,
                    request_deserializer=livekit__room__pb2.ListRoomsRequest.FromString,
                    response_serializer=livekit__room__pb2.ListRoomsResponse.SerializeToString,
            ),
            'DeleteRoom': grpc.unary_unary_rpc_method_handler(
                    servicer.DeleteRoom,
                    request_deserializer=livekit__room__pb2.DeleteRoomRequest.FromString,
                    response_serializer=livekit__room__pb2.DeleteRoomResponse.SerializeToString,
            ),
            'ListParticipants': grpc.unary_unary_rpc_method_handler(
                    servicer.ListParticipants,
                    request_deserializer=livekit__room__pb2.ListParticipantsRequest.FromString,
                    response_serializer=livekit__room__pb2.ListParticipantsResponse.SerializeToString,
            ),
            'GetParticipant': grpc.unary_unary_rpc_method_handler(
                    servicer.GetParticipant,
                    request_deserializer=livekit__room__pb2.RoomParticipantIdentity.FromString,
                    response_serializer=livekit__models__pb2.ParticipantInfo.SerializeToString,
            ),
            'RemoveParticipant': grpc.unary_unary_rpc_method_handler(
                    servicer.RemoveParticipant,
                    request_deserializer=livekit__room__pb2.RoomParticipantIdentity.FromString,
                    response_serializer=livekit__room__pb2.RemoveParticipantResponse.SerializeToString,
            ),
            'MutePublishedTrack': grpc.unary_unary_rpc_method_handler(
                    servicer.MutePublishedTrack,
                    request_deserializer=livekit__room__pb2.MuteRoomTrackRequest.FromString,
                    response_serializer=livekit__room__pb2.MuteRoomTrackResponse.SerializeToString,
            ),
            'UpdateParticipant': grpc.unary_unary_rpc_method_handler(
                    servicer.UpdateParticipant,
                    request_deserializer=livekit__room__pb2.UpdateParticipantRequest.FromString,
                    response_serializer=livekit__models__pb2.ParticipantInfo.SerializeToString,
            ),
            'UpdateSubscriptions': grpc.unary_unary_rpc_method_handler(
                    servicer.UpdateSubscriptions,
                    request_deserializer=livekit__room__pb2.UpdateSubscriptionsRequest.FromString,
                    response_serializer=livekit__room__pb2.UpdateSubscriptionsResponse.SerializeToString,
            ),
            'SendData': grpc.unary_unary_rpc_method_handler(
                    servicer.SendData,
                    request_deserializer=livekit__room__pb2.SendDataRequest.FromString,
                    response_serializer=livekit__room__pb2.SendDataResponse.SerializeToString,
            ),
            'UpdateRoomMetadata': grpc.unary_unary_rpc_method_handler(
                    servicer.UpdateRoomMetadata,
                    request_deserializer=livekit__room__pb2.UpdateRoomMetadataRequest.FromString,
                    response_serializer=livekit__models__pb2.Room.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'livekit.RoomService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('livekit.RoomService', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class RoomService(object):
    """Room service that can be performed on any node
    they are Twirp-based HTTP req/responses
    """

    @staticmethod
    def CreateRoom(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/livekit.RoomService/CreateRoom',
            livekit__room__pb2.CreateRoomRequest.SerializeToString,
            livekit__models__pb2.Room.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def ListRooms(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/livekit.RoomService/ListRooms',
            livekit__room__pb2.ListRoomsRequest.SerializeToString,
            livekit__room__pb2.ListRoomsResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def DeleteRoom(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/livekit.RoomService/DeleteRoom',
            livekit__room__pb2.DeleteRoomRequest.SerializeToString,
            livekit__room__pb2.DeleteRoomResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def ListParticipants(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/livekit.RoomService/ListParticipants',
            livekit__room__pb2.ListParticipantsRequest.SerializeToString,
            livekit__room__pb2.ListParticipantsResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def GetParticipant(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/livekit.RoomService/GetParticipant',
            livekit__room__pb2.RoomParticipantIdentity.SerializeToString,
            livekit__models__pb2.ParticipantInfo.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def RemoveParticipant(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/livekit.RoomService/RemoveParticipant',
            livekit__room__pb2.RoomParticipantIdentity.SerializeToString,
            livekit__room__pb2.RemoveParticipantResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def MutePublishedTrack(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/livekit.RoomService/MutePublishedTrack',
            livekit__room__pb2.MuteRoomTrackRequest.SerializeToString,
            livekit__room__pb2.MuteRoomTrackResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def UpdateParticipant(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/livekit.RoomService/UpdateParticipant',
            livekit__room__pb2.UpdateParticipantRequest.SerializeToString,
            livekit__models__pb2.ParticipantInfo.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def UpdateSubscriptions(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/livekit.RoomService/UpdateSubscriptions',
            livekit__room__pb2.UpdateSubscriptionsRequest.SerializeToString,
            livekit__room__pb2.UpdateSubscriptionsResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def SendData(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/livekit.RoomService/SendData',
            livekit__room__pb2.SendDataRequest.SerializeToString,
            livekit__room__pb2.SendDataResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def UpdateRoomMetadata(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/livekit.RoomService/UpdateRoomMetadata',
            livekit__room__pb2.UpdateRoomMetadataRequest.SerializeToString,
            livekit__models__pb2.Room.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)
