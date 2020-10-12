from graphene.relay import Node
from graphene_mongo import MongoengineObjectType

from ..fields import EnhancedConnection
from ...db.schema import MapLayer as MapLayerModel
from ...db.schema import MapFile as MapFileModel


class MapLayerNode(MongoengineObjectType):
    class Meta:
        model = MapLayerModel
        interfaces = (Node,)
        connection_class = EnhancedConnection


class MapFileNode(MongoengineObjectType):
    class Meta:
        model = MapFileModel
        interfaces = (Node,)
        connection_class = EnhancedConnection

'''
from ..mutations import create_delete_mutation, \
    EnhancedClientIDMutation


class DeleteMapFileMutation(EnhancedClientIDMutation):
    @classmethod
    def __custom__(cls):
        create_delete_mutation(cls, MapFileModel)
'''
