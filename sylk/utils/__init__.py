import bson
import arrow
import datetime
from mongoengine import fields
from sylk.applications import ApplicationLogger

log = ApplicationLogger(__package__)


def dump_var(log, data):
    if isinstance(data, object):
        dump_object_member_vars(log, data)
        dump_object_member_funcs(log, data)
    else:
        log.info(u'    %r' % data)

def get_iso_format(datetime_obj):
    arrow_obj = arrow.get(datetime_obj)
    return arrow_obj.format("YYYY-MM-DDTHH:mm:ss.SSSZ")

def dump_object_member_vars(log, obj):
    log.info(u'member vars ')
    #for key in obj.__dict__.keys():
    #    log.info(u'    %r' % key)
    for key in [method_name for method_name in dir(obj) if not callable(getattr(obj, method_name))]:
        log.info(u'    %r' % key)


def dump_object_member_funcs(log, obj):
    log.info(u'member funcs ')
    for key in [method_name for method_name in dir(obj) if callable(getattr(obj, method_name))]:
        log.info(u'    %r' % key)

def format_db_obj_field(db_field, db_obj_dict):
    db_field_val = db_obj_dict[db_field]
    if isinstance(db_field_val, bson.objectid.ObjectId):
        return str(db_field_val)
    elif isinstance(db_field_val, datetime.datetime):
        return get_iso_format(db_field_val)
    return db_field_val

'''
 only one of ignore_fields or use_fields should be specified.
 give an array of fields to be ignored or added
'''
def get_json_from_db_obj(db_obj, ignore_fields=None, include_fields=None):
    db_obj_dict = db_obj.to_mongo(True).to_dict()
    if include_fields is None:
        all_fields = db_obj_dict.keys()
        if ignore_fields is None:
            ignore_fields = ['_id']
        else:
            if '_id' not in ignore_fields:
                ignore_fields.append('_id')
        include_fields = list(set(all_fields)-set(ignore_fields))
    json_data = {x:format_db_obj_field(x, db_obj) for x in include_fields}
    return json_data

'''
Cuidado - this only handles string or maybe int values for now

def set_db_obj_from_request(log, db_obj, request):
    log.info("set_db_obj_from_request request.content_type %r", request.content_type)
    if (request.content_type is not None) and request.content_type.startswith('application/json'):
        request_data = request.get_json()
        log.info("request_data is json is %r", request_data)
    else:
        log.info("request is %r", request)
        request_data = request.values
        log.info("request.values is %r", request.values)
    log.debug("set_db_obj_from_request request_data is %r", request_data)
    field_names = request_data.keys()
    db_obj_dict = db_obj.to_mongo(True).to_dict()
    for field_name in field_names:
        if field_name in db_obj_dict:
            setattr(db_obj, field_name, request_data[field_name])
            #db_obj_dict[field_name] = request_data[field_name]
            log.info("set_db_obj_from_request updating field %r, value %r ", field_name, request_data[field_name])
    log.info("set_db_obj_from_request end ")
'''

'''
big thx from https://stackoverflow.com/questions/19002469/update-a-mongoengine-document-using-a-python-dict
'''
def set_db_obj_from_request(document, request, ignore_fields=[]):
    def field_value(field, value):
        if field.__class__ in (fields.ListField, fields.SortedListField):
            return [
                field_value(field.field, item)
                for item in value
            ]
        if field.__class__ in (
            fields.EmbeddedDocumentField,
            fields.GenericEmbeddedDocumentField,
            fields.ReferenceField,
            fields.GenericReferenceField
        ):
            return field.document_type(**value)
        else:
            return value
    if (request.content_type is not None) and request.content_type.startswith('application/json'):
        request_data = request.get_json()
    else:
        request_data = request.values

    for key, value in request_data.items():
        if (key in document._fields) and (key not in ignore_fields):
            log.info("update key %r, value %r", key, value)
            setattr(document, key, field_value(document._fields[key], value))

    return document


def copy_request_data_to_object(request, dest_object):
    if (request.content_type is not None) and request.content_type.startswith('application/json'):
        request_data = request.get_json()
    else:
        request_data = request.values

    for key, value in request_data.items():
        setattr(dest_object, key, value)

    return dest_object
