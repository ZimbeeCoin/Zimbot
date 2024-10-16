# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

import livekit_ingress_pb2 as livekit__ingress__pb2

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
        + f' but the generated code in livekit_ingress_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class IngressStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.CreateIngress = channel.unary_unary(
                '/livekit.Ingress/CreateIngress',
                request_serializer=livekit__ingress__pb2.CreateIngressRequest.SerializeToString,
                response_deserializer=livekit__ingress__pb2.IngressInfo.FromString,
                _registered_method=True)
        self.UpdateIngress = channel.unary_unary(
                '/livekit.Ingress/UpdateIngress',
                request_serializer=livekit__ingress__pb2.UpdateIngressRequest.SerializeToString,
                response_deserializer=livekit__ingress__pb2.IngressInfo.FromString,
                _registered_method=True)
        self.ListIngress = channel.unary_unary(
                '/livekit.Ingress/ListIngress',
                request_serializer=livekit__ingress__pb2.ListIngressRequest.SerializeToString,
                response_deserializer=livekit__ingress__pb2.ListIngressResponse.FromString,
                _registered_method=True)
        self.DeleteIngress = channel.unary_unary(
                '/livekit.Ingress/DeleteIngress',
                request_serializer=livekit__ingress__pb2.DeleteIngressRequest.SerializeToString,
                response_deserializer=livekit__ingress__pb2.IngressInfo.FromString,
                _registered_method=True)


class IngressServicer(object):
    """Missing associated documentation comment in .proto file."""

    def CreateIngress(self, request, context):
        """Create a new Ingress
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def UpdateIngress(self, request, context):
        """Update an existing Ingress. Ingress can only be updated when it's in ENDPOINT_WAITING state.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ListIngress(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def DeleteIngress(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_IngressServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'CreateIngress': grpc.unary_unary_rpc_method_handler(
                    servicer.CreateIngress,
                    request_deserializer=livekit__ingress__pb2.CreateIngressRequest.FromString,
                    response_serializer=livekit__ingress__pb2.IngressInfo.SerializeToString,
            ),
            'UpdateIngress': grpc.unary_unary_rpc_method_handler(
                    servicer.UpdateIngress,
                    request_deserializer=livekit__ingress__pb2.UpdateIngressRequest.FromString,
                    response_serializer=livekit__ingress__pb2.IngressInfo.SerializeToString,
            ),
            'ListIngress': grpc.unary_unary_rpc_method_handler(
                    servicer.ListIngress,
                    request_deserializer=livekit__ingress__pb2.ListIngressRequest.FromString,
                    response_serializer=livekit__ingress__pb2.ListIngressResponse.SerializeToString,
            ),
            'DeleteIngress': grpc.unary_unary_rpc_method_handler(
                    servicer.DeleteIngress,
                    request_deserializer=livekit__ingress__pb2.DeleteIngressRequest.FromString,
                    response_serializer=livekit__ingress__pb2.IngressInfo.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'livekit.Ingress', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('livekit.Ingress', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class Ingress(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def CreateIngress(request,
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
            '/livekit.Ingress/CreateIngress',
            livekit__ingress__pb2.CreateIngressRequest.SerializeToString,
            livekit__ingress__pb2.IngressInfo.FromString,
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
    def UpdateIngress(request,
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
            '/livekit.Ingress/UpdateIngress',
            livekit__ingress__pb2.UpdateIngressRequest.SerializeToString,
            livekit__ingress__pb2.IngressInfo.FromString,
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
    def ListIngress(request,
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
            '/livekit.Ingress/ListIngress',
            livekit__ingress__pb2.ListIngressRequest.SerializeToString,
            livekit__ingress__pb2.ListIngressResponse.FromString,
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
    def DeleteIngress(request,
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
            '/livekit.Ingress/DeleteIngress',
            livekit__ingress__pb2.DeleteIngressRequest.SerializeToString,
            livekit__ingress__pb2.IngressInfo.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)