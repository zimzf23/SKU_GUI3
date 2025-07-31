# -*- coding: utf-8 -*-
#Import Modules
from dependencies import *
from ui_components import header_and_search, main_layout
from Catalog import build_section_classes

@ui.page('/home')
def page_layout():
    # Build Header
    header_and_search(None)

    # Build Body
    main_layout()


@ui.page('/new')
def page_layout():
    # Build Header
    header_and_search(None)
    ui.button('Create New Item', on_click=lambda: test_config()).props('color=primary')
    # Build Body
    main_layout()
    

def test_config():
    # Test if config file is loaded correctly
    sections, FullItem = build_section_classes("data.toml")

    # instantiate one item
    item = FullItem()
    print(item)  # you get nested dataclasses like item.basic, item.decoded, etc.

    # access and mutate
    item.basic.ref = "REF001"
    item.basic.name = 'Hello!'
    item.mechanical.weight = 42.0
    print(item)  # you get nested dataclasses like item.basic, item.decoded, etc.


# Navigate to the home page when the application starts
ui.navigate.to('/home')

# Run the application    
ui.run(title='Warak UI', native=False, favicon='assets/logo.ico')
