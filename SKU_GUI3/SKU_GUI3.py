# -*- coding: utf-8 -*-
#Import Modules
from logging import PlaceHolder
from dependencies import *
from ui_components import header_and_search,header_new, main_layout, new_layout
from data import catalog
from search_flow import get_basic_data

@ui.page('/home')
def page_layout():
    # Build Header
    header_and_search(get_basic_data)

    # Build Body
    main_layout()


@ui.page('/new')
def page_layout():
    # Build Header
    header_new(None)

    # Build Body
    new_layout()


# Navigate to the home page when the application starts
ui.navigate.to('/home')

# Run the application    
ui.run(title='Warak UI', native=False, favicon='assets/logo.ico')
