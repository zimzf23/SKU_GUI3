from dependencies import *
from state import state
from data import catalog


def main_card():
    # Main Card
    item = catalog.get_or_create(state.current_ref)
    print('')
    print(item)
    with ui.card().classes('w-full mx-auto  p-4'):
        with ui.grid(columns='1fr 0.3fr').classes('w-full'):
            # Data column
            with ui.column().classes('w-full mx-auto  p-4 gap-1'):
                ref_input = ui.input(label='Name', placeholder='Enter name').bind_value(item.basic, 'ref')

                ui.label().classes('w-full').style('font-family: Muli; font-size:2rem;')
                with ui.row().classes('space-x-10'):
                    ui.label().style('font-weight: bold;')
                    ui.label().style('font-weight: bold;') 
                    ui.label().style('font-weight: bold;')  
                    ui.label().style('font-weight: bold;') 
                    ui.label().style(f'font-weight: bold; color: blue')  
                ui.input(label='Descripción').classes('w-full').style('font-family: Muli; font-size:1rem;')
            # Media Column
            with ui.column().classes('w-full mx-auto p-4'):
                state.image_view = ui.image(img_loading).style('width:12rem; height:12rem; object-fit: contain;')

