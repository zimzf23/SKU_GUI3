# -*- coding: utf-8 -*-
from dependencies import *
from state import state
from ui_cards import external_card, main_card, visibility_controls, content_cards
from ui_new import new_pages, check_available, create_main_card, control_card, content_controls

def styles():
    ui.add_head_html('<style>body {background-color: GhostWhite; }</style>')
    ui.add_css('''
    @font-face{
        font-family: "Magistral";
        src: url('assets/Magistral-Medium.ttf') format('truetype');
    }
    @font-face{
        font-family: "Muli";
        src: url('assets/Muli-Regular.ttf') format('truetype');
    }
    @font-face{
        font-family: "Muli-SB";
        src: url('assets/Muli-SemiBold.ttf') format('truetype');
    }
    ''')

def main_layout():
    #Body
    # Left Column
    with ui.left_drawer(fixed=True).props('width=400').style('background-color: GhostWhite;'):
        ui.label('')
            
    # Main Body
    with ui.column().classes('w-full'):
        #Main Card
        main_card()
        #Ref Creator
            
        # Visibility Controls
        visibility_controls()
        # Content Cards
        content_cards()
        #Procedural content pages
                 
    # Right Column
    with ui.right_drawer(fixed=True).props('width=400').style('background-color: GhostWhite;'):
        ui.label('')

def header_and_search(on_search):
    mask = 'W-#A##-####'
    styles()
    # Header
    with ui.header(elevated=True).style('background-color: white').classes('items-center justify-between'):
        ui.html(content)
        # Settings Dialog
        with ui.dialog() as dialog, ui.card().classes(' mx-auto p-8 text-center').style('width:60rem;'):
            ui.label('Configuración').style('font-family: Magistral; font-size: 1.4rem')
            ui.separator()
            with ui.splitter().classes('w-full mx-auto p-4 text-center') as splitter:
                with splitter.before:
                    ui.checkbox("Tarjeta principal").style('font-family: Muli;')
                    ui.checkbox("Barra de campos").style('font-family: Muli;')
                    ui.checkbox("Creador de artículos").style('font-family: Muli;')
                with splitter.after:
                    ui.checkbox("Mostrar herramientas").style('font-family: Muli;')
                    ui.checkbox("Mostrar registro").style('font-family: Muli;')
                    ui.checkbox("Mostrar árbol").style('font-family: Muli;')
            
        # Item Bar
        with ui.row().classes('items-center'):
            ui.button(icon='add',on_click=lambda: ui.navigate.to('/new')).props('color=green')
            ui.button(icon='settings',on_click=dialog.open).props('color=grey')
            ref_input = ui.input(placeholder='W-1A23-4567') \
                .props(f'mask="{mask}" outlined dense') \
                .style('font-size: 20px; font-family: "Muli-SB";') \
                .style('width: 180px;')
            ui.button('Buscar', on_click=lambda: on_search(ref_input.value))

def header_new(on_save):
    styles()
    # Header
    with ui.header(elevated=True).style('background-color: white').classes('items-center justify-between'):
        ui.html(content)
        # Settings Dialog
        with ui.dialog() as dialog, ui.card().classes(' mx-auto p-8 text-center').style('width:60rem;'):
            ui.label('Configuración').style('font-family: Magistral; font-size: 1.4rem')
            ui.separator()
            with ui.splitter().classes('w-full mx-auto p-4 text-center') as splitter:
                with splitter.before:
                    ui.checkbox("Tarjeta principal").style('font-family: Muli;')
                    ui.checkbox("Barra de campos").style('font-family: Muli;')
                    ui.checkbox("Creador de artículos").style('font-family: Muli;')
                with splitter.after:
                    ui.checkbox("Mostrar herramientas").style('font-family: Muli;')
                    ui.checkbox("Mostrar registro").style('font-family: Muli;')
                    ui.checkbox("Mostrar árbol").style('font-family: Muli;')
            
        # Item Bar
        with ui.row().classes('items-center'):
            ui.button(icon='arrow_back',on_click=lambda: ui.navigate.to('/home')).props('color=green')
            ui.button(icon='settings',on_click=dialog.open).props('color=grey')
            #ui.button('Buscar', on_click=lambda: on_save())

def new_layout():
    #Body
    # Left Column
    with ui.left_drawer(fixed=True).props('width=400').style('background-color: GhostWhite;'):
        ui.label('')
            
    # Main Body
    with ui.column().classes('w-full'):
        check_available()
        create_main_card()
        content_controls()
        external_card((new_pages, 'external'), edit=True)
                 
    # Right Column
    with ui.right_drawer(fixed=True).props('width=400').style('background-color: GhostWhite;'):
        control_card()