from dependencies import *
from state import state
from data import catalog

def get_current_item():
    ref = (state.current_ref or "").strip()
    if not ref:
        return None
    return catalog.get_or_create(ref)

@ui.refreshable
def main_card():
    # Main Card
    item = get_current_item()

    with ui.card().classes('w-full mx-auto  p-4'):
        with ui.grid(columns='1fr 0.3fr').classes('w-full'):
            # Data column
            with ui.column().classes('w-full mx-auto  p-4 gap-1'):
                ui.label("Ref").classes('w-full').style('font-family: Magistral; font-size:3rem;').bind_text(item.basic, "ref")
                ui.label().classes('w-full').style('font-family: Muli; font-size:2rem;').bind_text(item.basic, "name")
                with ui.row().classes('space-x-10'):
                    ui.label().style('font-weight: bold;').bind_text(item.decoded, "level")
                    ui.label().style('font-weight: bold;').bind_text(item.decoded, "type")
                    ui.label().style('font-weight: bold;').bind_text(item.decoded, "cat") 
                    ui.label().style('font-weight: bold;').bind_text(item.decoded, "subcat") 
                    ui.label().style(f'font-weight: bold; color: blue')  
                ui.input(label='Descripción').classes('w-full').style('font-family: Muli; font-size:1rem;').bind_value(item.basic, "description")
            # Media Column
            with ui.column().classes('w-full mx-auto p-4'):
                state.image_view = ui.image(img_loading).style('width:12rem; height:12rem; object-fit: contain;')

# Subscribe to state changes to refresh the card
state.subscribe(lambda ref: main_card.refresh())

