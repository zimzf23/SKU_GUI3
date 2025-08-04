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
                    ui.label().style('font-weight: bold;').bind_text(item.strings, "level_str")
                    ui.label().style('font-weight: bold;').bind_text(item.strings, "type_str")
                    ui.label().style('font-weight: bold;').bind_text(item.strings, "cat_str") 
                    ui.label().style('font-weight: bold;').bind_text(item.strings, "subcat_str") 
                    ui.label().style(f'font-weight: bold; color: blue').bind_text(item.strings, "cls_str")
                    ui.label().style(f'font-weight: bold; color: red').bind_text(item.strings, "wear_str")
                ui.input(label='Descripción').classes('w-full').style('font-family: Muli; font-size:1rem;').bind_value(item.basic, "description")
            # Media Column
            with ui.column().classes('w-full mx-auto p-4'):
                thumb = ui.image().bind_source(item.thumbnail,"thumbnail").style("width:12rem; height:12rem; object-fit: contain;")

@ui.refreshable
def visibility_controls():
    item = get_current_item()
    if not item:
        return
    with ui.card().classes('w-full mx-auto p-4'):
        # Title 
        ui.label('Paginas').style('font-family: Magistral; font-size:1.6rem;')
        ui.separator()
        with ui.row().classes('w-full'):
            if item.available.external > 0:
                ui.checkbox('External').bind_value(state, 'external_visible')
            if item.available.mechanical > 0:
                ui.checkbox('Mechanical').bind_value(state, 'mechanical_visible')
            if item.available.electrical > 0:
                ui.checkbox('Electrical').bind_value(state, 'electrical_visible')
            if item.available.shipping > 0:
                ui.checkbox('Shipping').bind_value(state, 'shipping_visible')
            if item.available.supplier > 0:
                ui.checkbox('Supplier').bind_value(state, 'supplier_visible')
            if item.available.finance > 0:
                ui.checkbox('Finance').bind_value(state, 'finance_visible')
            if item.available.certs > 0:
                ui.checkbox('Certs').bind_value(state, 'certs_visible')
            if item.available.enviromental > 0:
                ui.checkbox('Enviromental').bind_value(state, 'enviromental_visible')

@ui.refreshable
def content_cards():
    item = get_current_item()
    with ui.column().classes('w-full'):
        # External Card
        if item.available.external > 0:
            with ui.card().classes('w-full mx-auto p-4').bind_visibility(state, 'external_visible'):
                # Title 
                ui.label('Datos fabricante').style('font-family: Magistral; font-size:1.6rem;')
                ui.separator()
                # Body
                with ui.row().classes('w-full justify-between items-start h-full'):
                    with ui.grid(columns='auto auto').classes('gap-3').style('max-width: 70%;'):
                        ui.input('Fabricante').bind_value(item.external_manufacturer, 'manufacturer').props('readonly, borderless')
                        ui.input('Nombre').bind_value(item.external_manufacturer, 'name').props('readonly, borderless')
                        ui.input('Referencia').bind_value(item.external_manufacturer, 'number').props('readonly, borderless')
                        ui.input('Descripción').bind_value(item.external_manufacturer, 'description').props('readonly, borderless')
                        ui.input('EAN').bind_value(item.external_manufacturer, 'ean').props('readonly, borderless')
                    with ui.column().classes('tems-end h-full').style('min-width: 8rem;'):
                        ui.button('Hoja de datos', icon='file_open').classes('w-full')

        # Mechanical Card
        if item.available.mechanical > 0:
            with ui.card().classes('w-full mx-auto p-4').bind_visibility(state, 'mechanical_visible'):
                # Title 
                ui.label('Datos Mecanicos').style('font-family: Magistral; font-size:1.6rem;')
                ui.separator()
                # Body
                with ui.row().classes('w-full justify-between items-start h-full'):
                    with ui.grid(columns='auto auto').classes('gap-3').style('max-width: 70%;'):
                        ui.input('Weight').bind_value(item.mechanical, 'weight').props('readonly, borderless')
                        ui.input('Dimensions').bind_value(item.mechanical, 'dimensions').props('readonly, borderless')
                        ui.input('Material').bind_value(item.mechanical, 'material').props('readonly, borderless')
                        ui.input('Color').bind_value(item.mechanical, 'color').props('readonly, borderless')
                        ui.input('Finish').bind_value(item.mechanical, 'finish').props('readonly, borderless')
                        ui.input('Shape').bind_value(item.mechanical, 'shape').props('readonly, borderless')
                        ui.input('Size').bind_value(item.mechanical, 'size').props('readonly, borderless')
                    with ui.column().classes('tems-end h-full').style('min-width: 8rem;'):
                        ui.button('Drawings', icon='file_open').classes('w-full')

        # Electrical Card
        if item.available.electrical > 0:
            with ui.card().classes('w-full mx-auto p-4').bind_visibility(state, 'electrical_visible'):
                # Title 
                ui.label('Datos Electricos').style('font-family: Magistral; font-size:1.6rem;')
                ui.separator()
                # Body
                with ui.row().classes('w-full justify-between items-start h-full'):
                    with ui.grid(columns='auto auto').classes('gap-3').style('max-width: 70%;'):
                        ui.input('Voltage').bind_value(item.electrical, 'voltage').props('readonly, borderless')
                        ui.input('Current').bind_value(item.electrical, 'current').props('readonly, borderless')
                        ui.input('Frequency').bind_value(item.electrical, 'frequency').props('readonly, borderless')
                        ui.input('Efficiency').props('readonly, borderless')
                    with ui.column().classes('tems-end h-full').style('min-width: 8rem;'):
                        ui.button('Drawings', icon='file_open').classes('w-full')


        # Shipping Card
        if item.available.shipping > 0:
            with ui.card().classes('w-full mx-auto p-4').bind_visibility(state, 'shipping_visible'):
                # Title 
                ui.label('Logistica').style('font-family: Magistral; font-size:1.6rem;')
                ui.separator()
                # Body
                with ui.row().classes('w-full justify-between items-start h-full'):
                    with ui.grid(columns='auto auto').classes('gap-3').style('max-width: 70%;'):
                        ui.number('Shipping Weight').bind_value(item.shipping, 'shipping_weight')
                        ui.input('Shipping Dimensions').bind_value(item.shipping, 'shipping_dimensions')
                        ui.input('Shipping Method').bind_value(item.shipping, 'shipping_method')
                        ui.number('Shipping Cost').bind_value(item.shipping, 'shipping_cost')
                    with ui.column().classes('tems-end h-full').style('min-width: 8rem;'):
                        ui.button('SDS', icon='file_open').classes('w-full')

        # Supplier Card
        if item.available.supplier > 0:
            with ui.card().classes('w-full mx-auto p-4').bind_visibility(state, 'supplier_visible'):
                ui.label('Supplier').style('font-weight: bold;')
                ui.input('Supplier').bind_value(item.supplier, 'supplier')
                ui.input('Contact').bind_value(item.supplier, 'contact')
                ui.input('Phone').bind_value(item.supplier, 'phone')
                ui.input('Email').bind_value(item.supplier, 'email')
                ui.input('Address').bind_value(item.supplier, 'address')

        # Finance Card
        if item.available.finance > 0:
            with ui.card().classes('w-full mx-auto p-4').bind_visibility(state, 'finance_visible'):
                ui.label('Finance').style('font-weight: bold;')
                ui.input('Cost').bind_value(item.finance, 'cost')
                ui.input('Price').bind_value(item.finance, 'price')
                ui.input('Margin').bind_value(item.finance, 'margin')
                ui.input('Currency').bind_value(item.finance, 'currency')
                ui.input('Payment Terms').bind_value(item.finance, 'payment_terms')

        # Certs Card
        if item.available.certs > 0:
            with ui.card().classes('w-full mx-auto p-4').bind_visibility(state, 'certs_visible'):
                ui.label('Certifications').style('font-weight: bold;')
                ui.input('Certifications').bind_value(item.certs, 'certifications')
                ui.input('Compliance').bind_value(item.certs, 'compliance')
                ui.input('Standards').bind_value(item.certs, 'standards')

        # Enviromental Card
        if item.available.enviromental > 0:
            with ui.card().classes('w-full mx-auto p-4').bind_visibility(state, 'enviromental_visible'):
                ui.label('Enviromental').style('font-weight: bold;')
                ui.number('CO2').bind_value(item.enviromental, 'CO2')
                ui.checkbox('Recyclable').bind_value(item.enviromental, 'recyclable')
                ui.checkbox('Hazardous').bind_value(item.enviromental, 'hazardous')
                ui.input('Disposal Instructions').bind_value(item.enviromental, 'disposal_instructions')

# Subscribe to state changes to refresh the card
state.subscribe(lambda ref: main_card.refresh())
state.subscribe(lambda ref: visibility_controls.refresh())  
state.subscribe(lambda ref: content_cards.refresh())  
