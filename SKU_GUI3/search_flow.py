from dependencies import * 
from data import catalog

def get_basic_data(ref_val):
    # Creates a ref on the catalog and gets always present data
    item = catalog.get_or_create(ref_val)
    print(item)
    update_weight(item)

def update_weight(item):
    item.mechanical.weight = 999