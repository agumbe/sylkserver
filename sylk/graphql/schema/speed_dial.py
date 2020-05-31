import graphene
from graphene import Field, String
from graphene.relay import Node
from graphene_mongo import MongoengineConnectionField, MongoengineObjectType

from ..fields import EnhancedConnection
from ..utiils import update_params_with_args
from ...db.schema import SpeedDial as SpeedDialModel
from ...db.schema import SpeedDialGroup as SpeedDialGroupModel
from ...db.schema import User as UserModel
from .user import UserNode

class SpeedDialNode(MongoengineObjectType):
    class Meta:
        model = SpeedDialModel
        interfaces = (Node,)
        connection_class = EnhancedConnection

    user = Field(UserNode)

    def resolve_user(parent, info, **args):
        return UserModel.objects.get(user_id = parent.user_id)


class SpeedDialGroupNode(MongoengineObjectType):
    class Meta:
        model = SpeedDialGroupModel
        interfaces = (Node,)
        connection_class = EnhancedConnection

    speed_dials = MongoengineConnectionField(SpeedDialNode)

    def resolve_speed_dials(parent, info, **args):
        return SpeedDialModel.objects(group_id = parent.group_id)


