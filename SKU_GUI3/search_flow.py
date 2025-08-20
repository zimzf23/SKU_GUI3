from dependencies import * 
from data import catalog
from text_queries import search, get_cat_text, get_level_text, get_available_data
from state import state
from transcode import decode_ref, decode_cls_wear
from file_queries import get_thumbnail
from encoding import blob_to_data_uri
from ui_cards import main_card, visibility_controls, content_cards

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
    lookup_get_thumbnail(ref_val,item)

def lookup_get_thumbnail(ref_val, item):
    # Directly query the FILETABLE for SKUs/<ref>/Thumbnail.<ext>
    blob, ext = get_thumbnail(ref_val)
    if blob:
        thumb_uri = blob_to_data_uri(blob, f'image/{ext}')
    else:
        thumb_uri = img_loading   # fallback image
    item.thumbnail.thumbnail = thumb_uri
    # move to content
    look_content(ref_val, item)

    
def look_content(ref_val,item):
    #Check content
    get_available_data(ref_val,item)
    # In search_flow.py, inside look_content(ref_val, item):
    # Don't auto-enable; only turn OFF flags for unavailable sections
    state.external_visible     = state.external_visible     and (item.available.external > 0)
    state.mechanical_visible   = state.mechanical_visible   and (item.available.mechanical > 0)
    state.electrical_visible   = state.electrical_visible   and (item.available.electrical > 0)
    state.shipping_visible     = state.shipping_visible     and (item.available.shipping > 0)
    state.supplier_visible     = state.supplier_visible     and (item.available.supplier > 0)
    state.finance_visible      = state.finance_visible      and (item.available.finance > 0)
    state.certs_visible        = state.certs_visible        and (item.available.certs > 0)
    state.enviromental_visible = state.enviromental_visible and (item.available.enviromental > 0)

    main_card.refresh()
    visibility_controls.refresh()
    content_cards.refresh()
    print(item)
