from dependencies import *
from state import state
from new_sql import get_level_options, get_type_options, get_cat_options, get_subcat_options, get_next_code_number, insert_new
from sql_fs import create_folder, insert_to_folder, commit_uploads, cache_upload
from data import catalog

def get_current_item():
    ref = (state.current_ref or "").strip()
    if not ref:
        return None
    return catalog.get_or_create(ref)

def get_next_ref(s_level,s_type,s_cat,s_subcat,uuid):
    prefix = 'W-' + str(s_level) + str(s_type) + str(s_cat) + str(s_subcat) + '-'
    nextnum = get_next_code_number(prefix)
    state.current_ref = prefix + nextnum
    item = catalog.get_or_create(state.current_ref)
    return nextnum

def load_options(select_box, query_func, *args, **kwargs):
    try:
        opts = query_func(*args, **kwargs)
        select_box.set_options(opts)
    except Exception as ex:
        ui.notify(f'Error loading options: {ex}', type='negative')

def show_basic_data():
    if state.current_ref != 'W-':
        state.new_basic = True
    else:
        state.new_basic = True

def upload_data():
    item = get_current_item()
    insert_new(state.current_ref, item.basic.name, item.basic.description, item.basic.cls, item.basic.wear)
    create_folder("SKUs", state.current_ref)
    commit_uploads(kind="thumbnail",forced_name="Thumbnail",subfolder=None)  # root of SKU




