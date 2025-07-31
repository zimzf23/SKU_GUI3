# -*- coding: utf-8 -*-
#Import Modules
from dependencies import *
from ui_components import header_and_search, main_layout

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

    # Build Body
    main_layout()

# Navigate to the home page when the application starts
ui.navigate.to('/home')

# Run the application    
ui.run(title='Warak UI', native=False, favicon='assets/logo.ico')
