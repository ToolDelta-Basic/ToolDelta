# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

from . import command_pb2 as proto_dot_command__pb2
from . import response_pb2 as proto_dot_response__pb2

GRPC_GENERATED_VERSION = '1.71.0'
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
        + f' but the generated code in proto/command_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class CommandServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.SendWOCommand = channel.unary_unary(
                '/fateark.proto.command.CommandService/SendWOCommand',
                request_serializer=proto_dot_command__pb2.SendWOCommandRequest.SerializeToString,
                response_deserializer=proto_dot_response__pb2.GeneralResponse.FromString,
                _registered_method=True)
        self.SendWSCommand = channel.unary_unary(
                '/fateark.proto.command.CommandService/SendWSCommand',
                request_serializer=proto_dot_command__pb2.SendWSCommandRequest.SerializeToString,
                response_deserializer=proto_dot_response__pb2.GeneralResponse.FromString,
                _registered_method=True)
        self.SendPlayerCommand = channel.unary_unary(
                '/fateark.proto.command.CommandService/SendPlayerCommand',
                request_serializer=proto_dot_command__pb2.SendPlayerCommandRequest.SerializeToString,
                response_deserializer=proto_dot_response__pb2.GeneralResponse.FromString,
                _registered_method=True)
        self.SendAICommand = channel.unary_unary(
                '/fateark.proto.command.CommandService/SendAICommand',
                request_serializer=proto_dot_command__pb2.SendAICommandRequest.SerializeToString,
                response_deserializer=proto_dot_response__pb2.GeneralResponse.FromString,
                _registered_method=True)
        self.SendWSCommandWithResponse = channel.unary_unary(
                '/fateark.proto.command.CommandService/SendWSCommandWithResponse',
                request_serializer=proto_dot_command__pb2.SendWSCommandWithResponseRequest.SerializeToString,
                response_deserializer=proto_dot_response__pb2.GeneralResponse.FromString,
                _registered_method=True)
        self.SendPlayerCommandWithResponse = channel.unary_unary(
                '/fateark.proto.command.CommandService/SendPlayerCommandWithResponse',
                request_serializer=proto_dot_command__pb2.SendPlayerCommandWithResponseRequest.SerializeToString,
                response_deserializer=proto_dot_response__pb2.GeneralResponse.FromString,
                _registered_method=True)
        self.SendAICommandWithResponse = channel.unary_unary(
                '/fateark.proto.command.CommandService/SendAICommandWithResponse',
                request_serializer=proto_dot_command__pb2.SendAICommandWithResponseRequest.SerializeToString,
                response_deserializer=proto_dot_response__pb2.GeneralResponse.FromString,
                _registered_method=True)


class CommandServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def SendWOCommand(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SendWSCommand(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SendPlayerCommand(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SendAICommand(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SendWSCommandWithResponse(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SendPlayerCommandWithResponse(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SendAICommandWithResponse(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_CommandServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'SendWOCommand': grpc.unary_unary_rpc_method_handler(
                    servicer.SendWOCommand,
                    request_deserializer=proto_dot_command__pb2.SendWOCommandRequest.FromString,
                    response_serializer=proto_dot_response__pb2.GeneralResponse.SerializeToString,
            ),
            'SendWSCommand': grpc.unary_unary_rpc_method_handler(
                    servicer.SendWSCommand,
                    request_deserializer=proto_dot_command__pb2.SendWSCommandRequest.FromString,
                    response_serializer=proto_dot_response__pb2.GeneralResponse.SerializeToString,
            ),
            'SendPlayerCommand': grpc.unary_unary_rpc_method_handler(
                    servicer.SendPlayerCommand,
                    request_deserializer=proto_dot_command__pb2.SendPlayerCommandRequest.FromString,
                    response_serializer=proto_dot_response__pb2.GeneralResponse.SerializeToString,
            ),
            'SendAICommand': grpc.unary_unary_rpc_method_handler(
                    servicer.SendAICommand,
                    request_deserializer=proto_dot_command__pb2.SendAICommandRequest.FromString,
                    response_serializer=proto_dot_response__pb2.GeneralResponse.SerializeToString,
            ),
            'SendWSCommandWithResponse': grpc.unary_unary_rpc_method_handler(
                    servicer.SendWSCommandWithResponse,
                    request_deserializer=proto_dot_command__pb2.SendWSCommandWithResponseRequest.FromString,
                    response_serializer=proto_dot_response__pb2.GeneralResponse.SerializeToString,
            ),
            'SendPlayerCommandWithResponse': grpc.unary_unary_rpc_method_handler(
                    servicer.SendPlayerCommandWithResponse,
                    request_deserializer=proto_dot_command__pb2.SendPlayerCommandWithResponseRequest.FromString,
                    response_serializer=proto_dot_response__pb2.GeneralResponse.SerializeToString,
            ),
            'SendAICommandWithResponse': grpc.unary_unary_rpc_method_handler(
                    servicer.SendAICommandWithResponse,
                    request_deserializer=proto_dot_command__pb2.SendAICommandWithResponseRequest.FromString,
                    response_serializer=proto_dot_response__pb2.GeneralResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'fateark.proto.command.CommandService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('fateark.proto.command.CommandService', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class CommandService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def SendWOCommand(request,
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
            '/fateark.proto.command.CommandService/SendWOCommand',
            proto_dot_command__pb2.SendWOCommandRequest.SerializeToString,
            proto_dot_response__pb2.GeneralResponse.FromString,
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
    def SendWSCommand(request,
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
            '/fateark.proto.command.CommandService/SendWSCommand',
            proto_dot_command__pb2.SendWSCommandRequest.SerializeToString,
            proto_dot_response__pb2.GeneralResponse.FromString,
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
    def SendPlayerCommand(request,
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
            '/fateark.proto.command.CommandService/SendPlayerCommand',
            proto_dot_command__pb2.SendPlayerCommandRequest.SerializeToString,
            proto_dot_response__pb2.GeneralResponse.FromString,
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
    def SendAICommand(request,
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
            '/fateark.proto.command.CommandService/SendAICommand',
            proto_dot_command__pb2.SendAICommandRequest.SerializeToString,
            proto_dot_response__pb2.GeneralResponse.FromString,
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
    def SendWSCommandWithResponse(request,
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
            '/fateark.proto.command.CommandService/SendWSCommandWithResponse',
            proto_dot_command__pb2.SendWSCommandWithResponseRequest.SerializeToString,
            proto_dot_response__pb2.GeneralResponse.FromString,
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
    def SendPlayerCommandWithResponse(request,
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
            '/fateark.proto.command.CommandService/SendPlayerCommandWithResponse',
            proto_dot_command__pb2.SendPlayerCommandWithResponseRequest.SerializeToString,
            proto_dot_response__pb2.GeneralResponse.FromString,
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
    def SendAICommandWithResponse(request,
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
            '/fateark.proto.command.CommandService/SendAICommandWithResponse',
            proto_dot_command__pb2.SendAICommandWithResponseRequest.SerializeToString,
            proto_dot_response__pb2.GeneralResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)
