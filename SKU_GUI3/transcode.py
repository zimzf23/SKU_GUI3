from dependencies import *
from state import state
from data import catalog

def decode_ref(ref_value):
    target = catalog.get_or_create(ref_value)
    # Cut the string
    parts   = target.basic.ref.split('-')
    header  = parts[0]
    data    = parts[1]
    uid     = parts[2]

    #Split the data
    target.decoded.level   = data[0]
    target.decoded.type    = data[1]
    target.decoded.cat     = data[2]
    target.decoded.subcat  = data[3]

def decode_cls_wear(ref_value):
    target = catalog.get_or_create(ref_value)
    class_cfg = config["data"]["classes"]
    if target.basic.cls == 4 :
        target.strings.cls_str = 'Externa'
    if target.basic.wear == 0 :
        target.strings.wear_str = 'Recambio'