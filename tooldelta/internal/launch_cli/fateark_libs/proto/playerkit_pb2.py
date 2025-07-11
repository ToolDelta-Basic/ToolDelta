# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: proto/playerkit.proto
# Protobuf Python Version: 6.31.0
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    6,
    31,
    0,
    '',
    'proto/playerkit.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from . import response_pb2 as proto_dot_response__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x15proto/playerkit.proto\x12\x17\x66\x61teark.proto.playerkit\x1a\x14proto/response.proto\"\x1c\n\x1aGetAllOnlinePlayersRequest\"&\n\x16GetPlayerByNameRequest\x12\x0c\n\x04name\x18\x01 \x01(\t\"&\n\x16GetPlayerByUUIDRequest\x12\x0c\n\x04uuid\x18\x01 \x01(\t\",\n\x18ReleaseBindPlayerRequest\x12\x10\n\x08uuid_str\x18\x01 \x01(\t\"(\n\x14GetPlayerNameRequest\x12\x10\n\x08uuid_str\x18\x01 \x01(\t\"2\n\x1eGetPlayerEntityUniqueIDRequest\x12\x10\n\x08uuid_str\x18\x01 \x01(\t\"-\n\x19GetPlayerLoginTimeRequest\x12\x10\n\x08uuid_str\x18\x01 \x01(\t\"2\n\x1eGetPlayerPlatformChatIDRequest\x12\x10\n\x08uuid_str\x18\x01 \x01(\t\"1\n\x1dGetPlayerBuildPlatformRequest\x12\x10\n\x08uuid_str\x18\x01 \x01(\t\"*\n\x16GetPlayerSkinIDRequest\x12\x10\n\x08uuid_str\x18\x01 \x01(\t\",\n\x18GetPlayerCanBuildRequest\x12\x10\n\x08uuid_str\x18\x01 \x01(\t\";\n\x18SetPlayerCanBuildRequest\x12\x10\n\x08uuid_str\x18\x01 \x01(\t\x12\r\n\x05\x61llow\x18\x02 \x01(\x08\"*\n\x16GetPlayerCanDigRequest\x12\x10\n\x08uuid_str\x18\x01 \x01(\t\"9\n\x16SetPlayerCanDigRequest\x12\x10\n\x08uuid_str\x18\x01 \x01(\t\x12\r\n\x05\x61llow\x18\x02 \x01(\x08\"7\n#GetPlayerCanDoorsAndSwitchesRequest\x12\x10\n\x08uuid_str\x18\x01 \x01(\t\"F\n#SetPlayerCanDoorsAndSwitchesRequest\x12\x10\n\x08uuid_str\x18\x01 \x01(\t\x12\r\n\x05\x61llow\x18\x02 \x01(\x08\"5\n!GetPlayerCanOpenContainersRequest\x12\x10\n\x08uuid_str\x18\x01 \x01(\t\"D\n!SetPlayerCanOpenContainersRequest\x12\x10\n\x08uuid_str\x18\x01 \x01(\t\x12\r\n\x05\x61llow\x18\x02 \x01(\x08\"4\n GetPlayerCanAttackPlayersRequest\x12\x10\n\x08uuid_str\x18\x01 \x01(\t\"C\n SetPlayerCanAttackPlayersRequest\x12\x10\n\x08uuid_str\x18\x01 \x01(\t\x12\r\n\x05\x61llow\x18\x02 \x01(\x08\"1\n\x1dGetPlayerCanAttackMobsRequest\x12\x10\n\x08uuid_str\x18\x01 \x01(\t\"@\n\x1dSetPlayerCanAttackMobsRequest\x12\x10\n\x08uuid_str\x18\x01 \x01(\t\x12\r\n\x05\x61llow\x18\x02 \x01(\x08\"7\n#GetPlayerCanOperatorCommandsRequest\x12\x10\n\x08uuid_str\x18\x01 \x01(\t\"F\n#SetPlayerCanOperatorCommandsRequest\x12\x10\n\x08uuid_str\x18\x01 \x01(\t\x12\r\n\x05\x61llow\x18\x02 \x01(\x08\"/\n\x1bGetPlayerCanTeleportRequest\x12\x10\n\x08uuid_str\x18\x01 \x01(\t\">\n\x1bSetPlayerCanTeleportRequest\x12\x10\n\x08uuid_str\x18\x01 \x01(\t\x12\r\n\x05\x61llow\x18\x02 \x01(\x08\"6\n\"GetPlayerStatusInvulnerableRequest\x12\x10\n\x08uuid_str\x18\x01 \x01(\t\"0\n\x1cGetPlayerStatusFlyingRequest\x12\x10\n\x08uuid_str\x18\x01 \x01(\t\"0\n\x1cGetPlayerStatusMayFlyRequest\x12\x10\n\x08uuid_str\x18\x01 \x01(\t\",\n\x18GetPlayerDeviceIDRequest\x12\x10\n\x08uuid_str\x18\x01 \x01(\t\"3\n\x1fGetPlayerEntityRuntimeIDRequest\x12\x10\n\x08uuid_str\x18\x01 \x01(\t\"2\n\x1eGetPlayerEntityMetadataRequest\x12\x10\n\x08uuid_str\x18\x01 \x01(\t\"(\n\x14GetPlayerIsOPRequest\x12\x10\n\x08uuid_str\x18\x01 \x01(\t\"*\n\x16GetPlayerOnlineRequest\x12\x10\n\x08uuid_str\x18\x01 \x01(\t\"6\n\x15SendPlayerChatRequest\x12\x10\n\x08uuid_str\x18\x01 \x01(\t\x12\x0b\n\x03msg\x18\x02 \x01(\t\"9\n\x18SendPlayerRawChatRequest\x12\x10\n\x08uuid_str\x18\x01 \x01(\t\x12\x0b\n\x03msg\x18\x02 \x01(\t\"L\n\x16SendPlayerTitleRequest\x12\x10\n\x08uuid_str\x18\x01 \x01(\t\x12\r\n\x05title\x18\x02 \x01(\t\x12\x11\n\tsub_title\x18\x03 \x01(\t\"B\n\x1aSendPlayerActionBarRequest\x12\x10\n\x08uuid_str\x18\x01 \x01(\t\x12\x12\n\naction_bar\x18\x02 \x01(\t\"M\n#InterceptPlayerJustNextInputRequest\x12\x10\n\x08uuid_str\x18\x01 \x01(\t\x12\x14\n\x0cretriever_id\x18\x02 \x01(\t2\xab%\n\x10PlayerKitService\x12s\n\x13GetAllOnlinePlayers\x12\x33.fateark.proto.playerkit.GetAllOnlinePlayersRequest\x1a\'.fateark.proto.response.GeneralResponse\x12k\n\x0fGetPlayerByName\x12/.fateark.proto.playerkit.GetPlayerByNameRequest\x1a\'.fateark.proto.response.GeneralResponse\x12k\n\x0fGetPlayerByUUID\x12/.fateark.proto.playerkit.GetPlayerByUUIDRequest\x1a\'.fateark.proto.response.GeneralResponse\x12o\n\x11ReleaseBindPlayer\x12\x31.fateark.proto.playerkit.ReleaseBindPlayerRequest\x1a\'.fateark.proto.response.GeneralResponse\x12g\n\rGetPlayerName\x12-.fateark.proto.playerkit.GetPlayerNameRequest\x1a\'.fateark.proto.response.GeneralResponse\x12\x80\x01\n\x17GetPlayerEntityUniqueID\x12\x37.fateark.proto.playerkit.GetPlayerEntityUniqueIDRequest\x1a,.fateark.proto.response.GeneralInt64Response\x12v\n\x12GetPlayerLoginTime\x12\x32.fateark.proto.playerkit.GetPlayerLoginTimeRequest\x1a,.fateark.proto.response.GeneralInt64Response\x12{\n\x17GetPlayerPlatformChatID\x12\x37.fateark.proto.playerkit.GetPlayerPlatformChatIDRequest\x1a\'.fateark.proto.response.GeneralResponse\x12~\n\x16GetPlayerBuildPlatform\x12\x36.fateark.proto.playerkit.GetPlayerBuildPlatformRequest\x1a,.fateark.proto.response.GeneralInt32Response\x12k\n\x0fGetPlayerSkinID\x12/.fateark.proto.playerkit.GetPlayerSkinIDRequest\x1a\'.fateark.proto.response.GeneralResponse\x12s\n\x11GetPlayerCanBuild\x12\x31.fateark.proto.playerkit.GetPlayerCanBuildRequest\x1a+.fateark.proto.response.GeneralBoolResponse\x12o\n\x11SetPlayerCanBuild\x12\x31.fateark.proto.playerkit.SetPlayerCanBuildRequest\x1a\'.fateark.proto.response.GeneralResponse\x12o\n\x0fGetPlayerCanDig\x12/.fateark.proto.playerkit.GetPlayerCanDigRequest\x1a+.fateark.proto.response.GeneralBoolResponse\x12k\n\x0fSetPlayerCanDig\x12/.fateark.proto.playerkit.SetPlayerCanDigRequest\x1a\'.fateark.proto.response.GeneralResponse\x12\x89\x01\n\x1cGetPlayerCanDoorsAndSwitches\x12<.fateark.proto.playerkit.GetPlayerCanDoorsAndSwitchesRequest\x1a+.fateark.proto.response.GeneralBoolResponse\x12\x85\x01\n\x1cSetPlayerCanDoorsAndSwitches\x12<.fateark.proto.playerkit.SetPlayerCanDoorsAndSwitchesRequest\x1a\'.fateark.proto.response.GeneralResponse\x12\x85\x01\n\x1aGetPlayerCanOpenContainers\x12:.fateark.proto.playerkit.GetPlayerCanOpenContainersRequest\x1a+.fateark.proto.response.GeneralBoolResponse\x12\x81\x01\n\x1aSetPlayerCanOpenContainers\x12:.fateark.proto.playerkit.SetPlayerCanOpenContainersRequest\x1a\'.fateark.proto.response.GeneralResponse\x12\x83\x01\n\x19GetPlayerCanAttackPlayers\x12\x39.fateark.proto.playerkit.GetPlayerCanAttackPlayersRequest\x1a+.fateark.proto.response.GeneralBoolResponse\x12\x7f\n\x19SetPlayerCanAttackPlayers\x12\x39.fateark.proto.playerkit.SetPlayerCanAttackPlayersRequest\x1a\'.fateark.proto.response.GeneralResponse\x12}\n\x16GetPlayerCanAttackMobs\x12\x36.fateark.proto.playerkit.GetPlayerCanAttackMobsRequest\x1a+.fateark.proto.response.GeneralBoolResponse\x12y\n\x16SetPlayerCanAttackMobs\x12\x36.fateark.proto.playerkit.SetPlayerCanAttackMobsRequest\x1a\'.fateark.proto.response.GeneralResponse\x12\x89\x01\n\x1cGetPlayerCanOperatorCommands\x12<.fateark.proto.playerkit.GetPlayerCanOperatorCommandsRequest\x1a+.fateark.proto.response.GeneralBoolResponse\x12\x85\x01\n\x1cSetPlayerCanOperatorCommands\x12<.fateark.proto.playerkit.SetPlayerCanOperatorCommandsRequest\x1a\'.fateark.proto.response.GeneralResponse\x12y\n\x14GetPlayerCanTeleport\x12\x34.fateark.proto.playerkit.GetPlayerCanTeleportRequest\x1a+.fateark.proto.response.GeneralBoolResponse\x12y\n\x14SetPlayerCanTeleport\x12\x34.fateark.proto.playerkit.SetPlayerCanTeleportRequest\x1a+.fateark.proto.response.GeneralBoolResponse\x12\x87\x01\n\x1bGetPlayerStatusInvulnerable\x12;.fateark.proto.playerkit.GetPlayerStatusInvulnerableRequest\x1a+.fateark.proto.response.GeneralBoolResponse\x12{\n\x15GetPlayerStatusFlying\x12\x35.fateark.proto.playerkit.GetPlayerStatusFlyingRequest\x1a+.fateark.proto.response.GeneralBoolResponse\x12{\n\x15GetPlayerStatusMayFly\x12\x35.fateark.proto.playerkit.GetPlayerStatusMayFlyRequest\x1a+.fateark.proto.response.GeneralBoolResponse\x12o\n\x11GetPlayerDeviceID\x12\x31.fateark.proto.playerkit.GetPlayerDeviceIDRequest\x1a\'.fateark.proto.response.GeneralResponse\x12\x83\x01\n\x18GetPlayerEntityRuntimeID\x12\x38.fateark.proto.playerkit.GetPlayerEntityRuntimeIDRequest\x1a-.fateark.proto.response.GeneralUint64Response\x12{\n\x17GetPlayerEntityMetadata\x12\x37.fateark.proto.playerkit.GetPlayerEntityMetadataRequest\x1a\'.fateark.proto.response.GeneralResponse\x12k\n\rGetPlayerIsOP\x12-.fateark.proto.playerkit.GetPlayerIsOPRequest\x1a+.fateark.proto.response.GeneralBoolResponse\x12o\n\x0fGetPlayerOnline\x12/.fateark.proto.playerkit.GetPlayerOnlineRequest\x1a+.fateark.proto.response.GeneralBoolResponse\x12i\n\x0eSendPlayerChat\x12..fateark.proto.playerkit.SendPlayerChatRequest\x1a\'.fateark.proto.response.GeneralResponse\x12o\n\x11SendPlayerRawChat\x12\x31.fateark.proto.playerkit.SendPlayerRawChatRequest\x1a\'.fateark.proto.response.GeneralResponse\x12k\n\x0fSendPlayerTitle\x12/.fateark.proto.playerkit.SendPlayerTitleRequest\x1a\'.fateark.proto.response.GeneralResponse\x12s\n\x13SendPlayerActionBar\x12\x33.fateark.proto.playerkit.SendPlayerActionBarRequest\x1a\'.fateark.proto.response.GeneralResponse\x12\x85\x01\n\x1cInterceptPlayerJustNextInput\x12<.fateark.proto.playerkit.InterceptPlayerJustNextInputRequest\x1a\'.fateark.proto.response.GeneralResponseB#Z!network_api/playerkit;playerkitpbb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'proto.playerkit_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  _globals['DESCRIPTOR']._loaded_options = None
  _globals['DESCRIPTOR']._serialized_options = b'Z!network_api/playerkit;playerkitpb'
  _globals['_GETALLONLINEPLAYERSREQUEST']._serialized_start=72
  _globals['_GETALLONLINEPLAYERSREQUEST']._serialized_end=100
  _globals['_GETPLAYERBYNAMEREQUEST']._serialized_start=102
  _globals['_GETPLAYERBYNAMEREQUEST']._serialized_end=140
  _globals['_GETPLAYERBYUUIDREQUEST']._serialized_start=142
  _globals['_GETPLAYERBYUUIDREQUEST']._serialized_end=180
  _globals['_RELEASEBINDPLAYERREQUEST']._serialized_start=182
  _globals['_RELEASEBINDPLAYERREQUEST']._serialized_end=226
  _globals['_GETPLAYERNAMEREQUEST']._serialized_start=228
  _globals['_GETPLAYERNAMEREQUEST']._serialized_end=268
  _globals['_GETPLAYERENTITYUNIQUEIDREQUEST']._serialized_start=270
  _globals['_GETPLAYERENTITYUNIQUEIDREQUEST']._serialized_end=320
  _globals['_GETPLAYERLOGINTIMEREQUEST']._serialized_start=322
  _globals['_GETPLAYERLOGINTIMEREQUEST']._serialized_end=367
  _globals['_GETPLAYERPLATFORMCHATIDREQUEST']._serialized_start=369
  _globals['_GETPLAYERPLATFORMCHATIDREQUEST']._serialized_end=419
  _globals['_GETPLAYERBUILDPLATFORMREQUEST']._serialized_start=421
  _globals['_GETPLAYERBUILDPLATFORMREQUEST']._serialized_end=470
  _globals['_GETPLAYERSKINIDREQUEST']._serialized_start=472
  _globals['_GETPLAYERSKINIDREQUEST']._serialized_end=514
  _globals['_GETPLAYERCANBUILDREQUEST']._serialized_start=516
  _globals['_GETPLAYERCANBUILDREQUEST']._serialized_end=560
  _globals['_SETPLAYERCANBUILDREQUEST']._serialized_start=562
  _globals['_SETPLAYERCANBUILDREQUEST']._serialized_end=621
  _globals['_GETPLAYERCANDIGREQUEST']._serialized_start=623
  _globals['_GETPLAYERCANDIGREQUEST']._serialized_end=665
  _globals['_SETPLAYERCANDIGREQUEST']._serialized_start=667
  _globals['_SETPLAYERCANDIGREQUEST']._serialized_end=724
  _globals['_GETPLAYERCANDOORSANDSWITCHESREQUEST']._serialized_start=726
  _globals['_GETPLAYERCANDOORSANDSWITCHESREQUEST']._serialized_end=781
  _globals['_SETPLAYERCANDOORSANDSWITCHESREQUEST']._serialized_start=783
  _globals['_SETPLAYERCANDOORSANDSWITCHESREQUEST']._serialized_end=853
  _globals['_GETPLAYERCANOPENCONTAINERSREQUEST']._serialized_start=855
  _globals['_GETPLAYERCANOPENCONTAINERSREQUEST']._serialized_end=908
  _globals['_SETPLAYERCANOPENCONTAINERSREQUEST']._serialized_start=910
  _globals['_SETPLAYERCANOPENCONTAINERSREQUEST']._serialized_end=978
  _globals['_GETPLAYERCANATTACKPLAYERSREQUEST']._serialized_start=980
  _globals['_GETPLAYERCANATTACKPLAYERSREQUEST']._serialized_end=1032
  _globals['_SETPLAYERCANATTACKPLAYERSREQUEST']._serialized_start=1034
  _globals['_SETPLAYERCANATTACKPLAYERSREQUEST']._serialized_end=1101
  _globals['_GETPLAYERCANATTACKMOBSREQUEST']._serialized_start=1103
  _globals['_GETPLAYERCANATTACKMOBSREQUEST']._serialized_end=1152
  _globals['_SETPLAYERCANATTACKMOBSREQUEST']._serialized_start=1154
  _globals['_SETPLAYERCANATTACKMOBSREQUEST']._serialized_end=1218
  _globals['_GETPLAYERCANOPERATORCOMMANDSREQUEST']._serialized_start=1220
  _globals['_GETPLAYERCANOPERATORCOMMANDSREQUEST']._serialized_end=1275
  _globals['_SETPLAYERCANOPERATORCOMMANDSREQUEST']._serialized_start=1277
  _globals['_SETPLAYERCANOPERATORCOMMANDSREQUEST']._serialized_end=1347
  _globals['_GETPLAYERCANTELEPORTREQUEST']._serialized_start=1349
  _globals['_GETPLAYERCANTELEPORTREQUEST']._serialized_end=1396
  _globals['_SETPLAYERCANTELEPORTREQUEST']._serialized_start=1398
  _globals['_SETPLAYERCANTELEPORTREQUEST']._serialized_end=1460
  _globals['_GETPLAYERSTATUSINVULNERABLEREQUEST']._serialized_start=1462
  _globals['_GETPLAYERSTATUSINVULNERABLEREQUEST']._serialized_end=1516
  _globals['_GETPLAYERSTATUSFLYINGREQUEST']._serialized_start=1518
  _globals['_GETPLAYERSTATUSFLYINGREQUEST']._serialized_end=1566
  _globals['_GETPLAYERSTATUSMAYFLYREQUEST']._serialized_start=1568
  _globals['_GETPLAYERSTATUSMAYFLYREQUEST']._serialized_end=1616
  _globals['_GETPLAYERDEVICEIDREQUEST']._serialized_start=1618
  _globals['_GETPLAYERDEVICEIDREQUEST']._serialized_end=1662
  _globals['_GETPLAYERENTITYRUNTIMEIDREQUEST']._serialized_start=1664
  _globals['_GETPLAYERENTITYRUNTIMEIDREQUEST']._serialized_end=1715
  _globals['_GETPLAYERENTITYMETADATAREQUEST']._serialized_start=1717
  _globals['_GETPLAYERENTITYMETADATAREQUEST']._serialized_end=1767
  _globals['_GETPLAYERISOPREQUEST']._serialized_start=1769
  _globals['_GETPLAYERISOPREQUEST']._serialized_end=1809
  _globals['_GETPLAYERONLINEREQUEST']._serialized_start=1811
  _globals['_GETPLAYERONLINEREQUEST']._serialized_end=1853
  _globals['_SENDPLAYERCHATREQUEST']._serialized_start=1855
  _globals['_SENDPLAYERCHATREQUEST']._serialized_end=1909
  _globals['_SENDPLAYERRAWCHATREQUEST']._serialized_start=1911
  _globals['_SENDPLAYERRAWCHATREQUEST']._serialized_end=1968
  _globals['_SENDPLAYERTITLEREQUEST']._serialized_start=1970
  _globals['_SENDPLAYERTITLEREQUEST']._serialized_end=2046
  _globals['_SENDPLAYERACTIONBARREQUEST']._serialized_start=2048
  _globals['_SENDPLAYERACTIONBARREQUEST']._serialized_end=2114
  _globals['_INTERCEPTPLAYERJUSTNEXTINPUTREQUEST']._serialized_start=2116
  _globals['_INTERCEPTPLAYERJUSTNEXTINPUTREQUEST']._serialized_end=2193
  _globals['_PLAYERKITSERVICE']._serialized_start=2196
  _globals['_PLAYERKITSERVICE']._serialized_end=6975
# @@protoc_insertion_point(module_scope)
