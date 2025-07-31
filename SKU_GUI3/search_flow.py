from dependencies import * 
from data import catalog
from text_queries import search

def get_basic_data(ref_val):
    # Creates a ref on the catalog and gets always present data
    search(ref_val)
    item = catalog.items.get(ref_val)
    if item : print(item) 
    else: print(f"Item {ref_val} not found in catalog.")
    
