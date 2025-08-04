from base64 import decode
from dependencies import * 
from data import catalog
from text_queries import search, get_cat_text, get_level_text
from state import state
from transcode import decode_ref, decode_cls_wear

def get_basic_data(ref_val):
    # Creates a ref on the catalog and gets always present data
    state.current_ref = ref_val
    search(ref_val)
    item = catalog.items.get(ref_val)
    if not item : print(f"Item {ref_val} not found in catalog.")
    # Decode the SKU
    decode_ref(ref_val)
    item.strings.level_str =  get_level_text({'Level': item.decoded.level,'Type': item.decoded.type,'Cat': 0,'Subcat': 0,'Class': 0})
    item.strings.type_str =  get_cat_text({'Level': 0,'Type': item.decoded.type,'Cat': 0,'Subcat': 0,'Class': 0})
    item.strings.cat_str =  get_cat_text({'Level': 0,'Type': item.decoded.type,'Cat': item.decoded.cat,'Subcat': 0,'Class': 0})
    item.strings.subcat_str =  get_cat_text({'Level': 0,'Type': item.decoded.type,'Cat': item.decoded.cat,'Subcat': item.decoded.subcat,'Class': 0})
    # Decode class and wear
    decode_cls_wear(ref_val)

    #move to file query

def get_thumbnail(ref_val):
    # Get the thumbnail image for the item
    # Query the thumbnail
    fcat = config['documents']['cats']['images']
    fsubcat = config['documents']['images']['thumbnails']
    # Get streamid
    streamid = find_files(ref_value,fcat,fsubcat)