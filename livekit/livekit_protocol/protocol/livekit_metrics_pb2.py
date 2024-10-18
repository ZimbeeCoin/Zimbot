# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: livekit_metrics.proto
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
    'livekit_metrics.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x15livekit_metrics.proto\x12\x07livekit\x1a\x1fgoogle/protobuf/timestamp.proto\"\xc6\x01\n\x0cMetricsBatch\x12\x14\n\x0ctimestamp_ms\x18\x01 \x01(\x03\x12\x38\n\x14normalized_timestamp\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12\x10\n\x08str_data\x18\x03 \x03(\t\x12.\n\x0btime_series\x18\x04 \x03(\x0b\x32\x19.livekit.TimeSeriesMetric\x12$\n\x06\x65vents\x18\x05 \x03(\x0b\x32\x14.livekit.EventMetric\"\x87\x01\n\x10TimeSeriesMetric\x12\r\n\x05label\x18\x01 \x01(\r\x12\x1c\n\x14participant_identity\x18\x02 \x01(\r\x12\x11\n\ttrack_sid\x18\x03 \x01(\r\x12&\n\x07samples\x18\x04 \x03(\x0b\x32\x15.livekit.MetricSample\x12\x0b\n\x03rid\x18\x05 \x01(\r\"m\n\x0cMetricSample\x12\x14\n\x0ctimestamp_ms\x18\x01 \x01(\x03\x12\x38\n\x14normalized_timestamp\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12\r\n\x05value\x18\x03 \x01(\x02\"\xdc\x02\n\x0b\x45ventMetric\x12\r\n\x05label\x18\x01 \x01(\r\x12\x1c\n\x14participant_identity\x18\x02 \x01(\r\x12\x11\n\ttrack_sid\x18\x03 \x01(\r\x12\x1a\n\x12start_timestamp_ms\x18\x04 \x01(\x03\x12\x1d\n\x10\x65nd_timestamp_ms\x18\x05 \x01(\x03H\x00\x88\x01\x01\x12>\n\x1anormalized_start_timestamp\x18\x06 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12\x41\n\x18normalized_end_timestamp\x18\x07 \x01(\x0b\x32\x1a.google.protobuf.TimestampH\x01\x88\x01\x01\x12\x10\n\x08metadata\x18\x08 \x01(\t\x12\x0b\n\x03rid\x18\t \x01(\rB\x13\n\x11_end_timestamp_msB\x1b\n\x19_normalized_end_timestamp*\xc5\x06\n\x0bMetricLabel\x12\x13\n\x0f\x41GENTS_LLM_TTFT\x10\x00\x12\x13\n\x0f\x41GENTS_STT_TTFT\x10\x01\x12\x13\n\x0f\x41GENTS_TTS_TTFB\x10\x02\x12(\n$CLIENT_VIDEO_SUBSCRIBER_FREEZE_COUNT\x10\x03\x12\x31\n-CLIENT_VIDEO_SUBSCRIBER_TOTAL_FREEZE_DURATION\x10\x04\x12\'\n#CLIENT_VIDEO_SUBSCRIBER_PAUSE_COUNT\x10\x05\x12\x31\n-CLIENT_VIDEO_SUBSCRIBER_TOTAL_PAUSES_DURATION\x10\x06\x12-\n)CLIENT_AUDIO_SUBSCRIBER_CONCEALED_SAMPLES\x10\x07\x12\x34\n0CLIENT_AUDIO_SUBSCRIBER_SILENT_CONCEALED_SAMPLES\x10\x08\x12.\n*CLIENT_AUDIO_SUBSCRIBER_CONCEALMENT_EVENTS\x10\t\x12.\n*CLIENT_AUDIO_SUBSCRIBER_INTERRUPTION_COUNT\x10\n\x12\x37\n3CLIENT_AUDIO_SUBSCRIBER_TOTAL_INTERRUPTION_DURATION\x10\x0b\x12)\n%CLIENT_SUBSCRIBER_JITTER_BUFFER_DELAY\x10\x0c\x12\x31\n-CLIENT_SUBSCRIBER_JITTER_BUFFER_EMITTED_COUNT\x10\r\x12@\n<CLIENT_VIDEO_PUBLISHER_QUALITY_LIMITATION_DURATION_BANDWIDTH\x10\x0e\x12:\n6CLIENT_VIDEO_PUBLISHER_QUALITY_LIMITATION_DURATION_CPU\x10\x0f\x12<\n8CLIENT_VIDEO_PUBLISHER_QUALITY_LIMITATION_DURATION_OTHER\x10\x10\x12&\n!METRIC_LABEL_PREDEFINED_MAX_VALUE\x10\x80 BFZ#github.com/livekit/protocol/livekit\xaa\x02\rLiveKit.Proto\xea\x02\x0eLiveKit::Protob\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'livekit_metrics_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  _globals['DESCRIPTOR']._loaded_options = None
  _globals['DESCRIPTOR']._serialized_options = b'Z#github.com/livekit/protocol/livekit\252\002\rLiveKit.Proto\352\002\016LiveKit::Proto'
  _globals['_METRICLABEL']._serialized_start=869
  _globals['_METRICLABEL']._serialized_end=1706
  _globals['_METRICSBATCH']._serialized_start=68
  _globals['_METRICSBATCH']._serialized_end=266
  _globals['_TIMESERIESMETRIC']._serialized_start=269
  _globals['_TIMESERIESMETRIC']._serialized_end=404
  _globals['_METRICSAMPLE']._serialized_start=406
  _globals['_METRICSAMPLE']._serialized_end=515
  _globals['_EVENTMETRIC']._serialized_start=518
  _globals['_EVENTMETRIC']._serialized_end=866
# @@protoc_insertion_point(module_scope)
