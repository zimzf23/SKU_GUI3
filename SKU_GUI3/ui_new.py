from dependencies import *
from new_sql import get_level_options, get_type_options, get_cat_options, get_subcat_options, get_next_code_number, insert_new
from state import state
from new_flow import get_next_ref, load_options, show_basic_data, upload_data, get_current_item, upload_file
from data import catalog

# Dropdown options for new reference assignment
@ui.refreshable
def check_available():
    with ui.card().classes('w-full mx-auto p-4').bind_visibility_from(state, 'new_assign'):
        ui.label('Asignar Referencia').style('font-family: Magistral; font-size:1.6rem;')
        ui.separator()
        with ui.row().classes('w-full justify-center').style('align-items: flex-end; font-family: Muli;'):
            s_level = ui.select(options={}, label='Nivel') .props('outlined dense stack-label') .classes('w-40')
            s_level.on('focus', lambda e: load_options(s_level, get_level_options))

            s_type = ui.select(options={}, label='Tipo') .props('outlined dense stack-label') .classes('w-40')
            s_type.on('focus', lambda e: load_options(s_type, get_type_options))

            s_cat = ui.select(options={}, label='Categoría') .props('outlined dense stack-label') .classes('w-40')
            s_cat.on('focus', lambda e: load_options(s_cat, get_cat_options, s_type.value))

            s_subcat = ui.select(options={}, label='Subcategoría') .props('outlined dense stack-label') .classes('w-40')
            s_subcat.on('focus', lambda e: load_options(s_subcat, get_subcat_options, s_type.value, s_cat.value ))

            with ui.input(label='ID Único') .props('outlined dense stack-label').classes('w-40') as i:
                ui.button(color='primary', on_click=lambda e: i.set_value(get_next_ref(s_level.value,s_type.value,s_cat.value,s_subcat.value,i.value)), icon='search').props('flat dense')

            #ui.button(icon='add', on_click=lambda e: show_basic_data()).props('color=green').classes('w-10')
            #ui.button(icon='edit' ).props('color=orange').classes('w-10')
            #ui.button(icon='delete' ).props('color=red').classes('w-10')
            ui.button(icon='open_in_new', on_click=lambda e: show_basic_data()).props('color=primary').classes(' h-10')

# Main card for basic data entry
@ui.refreshable
def create_main_card():
    # Main Card
    item = get_current_item()

    with ui.card().classes('w-full mx-auto  p-4').bind_visibility_from(state, 'new_basic'):
        ui.label('Datos Básicos').style('font-family: Magistral; font-size:1.6rem;')
        ui.separator()
        with ui.grid(columns='1fr 0.3fr').classes('w-full'):
      
            # Data column
            with ui.column().classes('w-full mx-auto  p-4 gap-4'):
                ui.label("Ref").classes('w-full').style('font-family: Magistral; font-size:2rem;').bind_text(item.basic, "ref")
                title = ui.input(label='Titulo').classes('w-full').style('font-family: Muli; font-size:1rem;').props('outlined dense stack-label').bind_value(item.basic, "name")
                desc = ui.input(label='Descripción').classes('w-full').style('font-family: Muli; font-size:1rem;').props('outlined stack-label').bind_value(item.basic, "description")
                with ui.row():
                    tipo = ui.select(options={1:'Pieza', 2:'Kit', 4:'Externa'}, label='Tipo') .props('outlined  stack-label') .classes('w-40').bind_value(item.basic, "cls")
                    desgaste = ui.select(options={1:'Estándar', 2:'Recambio', 4:'Consumible'}, label='Desgaste') .props('outlined  stack-label') .classes('w-40').bind_value(item.basic, "wear")
            # Media Column
            with ui.column().classes('w-full mx-auto p-4'):
                ui.upload(on_upload=upload_file, auto_upload=True, label="Upload Thumbnail")

# Control card for save and discard actions
@ui.refreshable
def control_card():
    #Save and discard changes
    with ui.card().classes('w-full justify-center').style('align-items: center; font-family: Muli;'):
        with ui.row():
            ui.button('Guardar',icon="edit", on_click=upload_data).props('color=green')
            ui.button('Descartar',icon='delete').props('color=red')


state.subscribe(lambda new_ref: create_main_card.refresh())