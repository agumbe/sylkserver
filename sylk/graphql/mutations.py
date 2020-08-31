import logging
import traceback
import graphene
from mongoengine import *
from graphql_relay.node.node import from_global_id

log = logging.getLogger("emergent-ng911")

def get_id_from_node_id(node_id):
    from base64 import b64decode
    id_decoded = b64decode(node_id).decode('utf-8')
    _, _id = id_decoded.split(':', 1)
    return _id


def _get_graphene_fied_for_mongoengine(field):
    if isinstance(field, ObjectIdField) or isinstance(field, StringField):
        return graphene.String()
    if isinstance(field, BooleanField):
        return graphene.Boolean()
    if isinstance(field, IntField):
        return graphene.Int()
    # we only support string/objectid list fields for now
    if isinstance(field, ListField):
        return graphene.List(of_type=graphene.String)
    return None


def _create_input_class(model_class, add_id_field=False):
    input_class = type('Input', (object, ), {})
    fields = []
    if add_id_field:
        setattr(input_class, "id", graphene.ID)
        fields.append("id")
    for field, val in model_class._fields.items():
        #print(f"field {field} type {val.__class__.__name__} required {val.required}")
        graphene_field = _get_graphene_fied_for_mongoengine(val)
        if graphene_field != None:
            setattr(input_class, field, graphene_field)
            fields.append(field)
    return input_class, fields

def _create_input_class_delete():
    return type('Input', (object, ), {"id" : graphene.ID(required=True)})


def _mutate_and_get_payload_for_update(model_class, fields, key="id"):
    def mutate_and_get_payload(cls, root, info, **input):
        key_val = input.get(key)
        if key=="id":
            key_val = get_id_from_node_id(key_val)
        params = {
            key: key_val
        }
        db_obj = model_class.objects.get(**params)
        for field in fields:
            if field != key:
                val = input.get(field)
                if val != None:
                    setattr(db_obj, field, val)
        db_obj.save()
        prop_name = model_class._get_collection_name()
        params = {
            prop_name : db_obj
        }
        return cls(**params)
    return mutate_and_get_payload


def _mutate_and_get_payload_for_insert(model_class, fields):
    def mutate_and_get_payload(cls, root, info, **input):
        db_obj = model_class()
        for field in fields:
            val = input.get(field)
            if val != None:
                setattr(db_obj, field, val)
        db_obj.save()
        prop_name = model_class._get_collection_name()
        params = {
            prop_name : db_obj
        }
        return cls(**params)
    return mutate_and_get_payload

def _mutate_and_get_payload_for_delete(model_class):
    def mutate_and_get_payload(cls, root, info, **input):
        try:
            node_id = input.get("id")
            log.info("node_id is %r", node_id)
            id_ = get_id_from_node_id(node_id)
            log.info("id_ is %r", id_)
            try:
                db_obj = model_class.objects.get(pk=id_).delete()
                success = True
            except DoesNotExist:
                success = False
            return cls(success = success)
        except Exception as e:
            stacktrace = traceback.format_exc()
            log.error(stacktrace)
            log.error(str(e))
            return cls(success = False)

    return mutate_and_get_payload

def create_insert_mutation(cls, model_class, node_class):
    input_class, fields = _create_input_class(model_class)
    prop_name = model_class._get_collection_name()
    setattr(cls, "Input", input_class)
    setattr(cls, prop_name, graphene.Field(node_class))
    _create_mutate_method = _mutate_and_get_payload_for_insert(model_class, fields)
    setattr(cls, "mutate_and_get_payload", classmethod(_create_mutate_method))
    return cls

def create_update_mutation(cls, model_class, node_class, key="id"):
    input_class, fields = _create_input_class(model_class, add_id_field=True)
    prop_name = model_class._get_collection_name()
    setattr(cls, "Input", input_class)
    setattr(cls, prop_name, graphene.Field(node_class))
    _create_mutate_method = _mutate_and_get_payload_for_update(model_class, fields, key)
    setattr(cls, "mutate_and_get_payload", classmethod(_create_mutate_method))
    return cls

def create_delete_mutation(cls, model_class):
    input_class = _create_input_class_delete()
    setattr(cls, "Input", input_class)
    setattr(cls, "success", graphene.Boolean())
    _create_mutate_method = _mutate_and_get_payload_for_delete(model_class)
    setattr(cls, "mutate_and_get_payload", classmethod(_create_mutate_method))
    return cls

'''
class DeleteBikeMutation(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    success = graphene.Boolean()

    def mutate(self, info, id):
        try:
            Bike.objects.get(pk=id).delete()
            success = True
        except ObjectDoesNotExist:
            success = False

        return DeleteBikeMutation(success=success)
        
'''


class EnhancedClientIDMutation(graphene.relay.ClientIDMutation):
    class Meta:
        abstract = True

    @classmethod
    def __init_subclass_with_meta__(
        cls, output=None, input_fields=None, arguments=None, name=None, **options
    ):
        cls.__custom__()
        super(EnhancedClientIDMutation, cls).__init_subclass_with_meta__(
            output=output, arguments=arguments, name=name, **options
        )

    @classmethod
    def __custom__(cls):
        pass

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        pass

