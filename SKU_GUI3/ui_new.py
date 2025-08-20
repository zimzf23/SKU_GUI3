from dependencies import *
from new_sql import get_level_options, get_type_options, get_cat_options, get_subcat_options, get_next_code_number, insert_new
from state import state
from new_flow import get_next_ref, load_options, get_current_item
from data import catalog
from new_sql import upsert_external, create_folder
from fscache import UploadCache
from file_queries import get_thumbnail
from encoding import blob_to_data_uri

cache = UploadCache()

class NewPages:
    def __init__(self):
        self.main = False
        self.uri = None
        self.external = False
        self.mechanical = False
        self.electrical = False
        self.shipping = False
        self.supplier = False
        self.finance = False
        self.certs = False
        self.enviromental = False

new_pages = NewPages()

state.subscribe(lambda new_ref: create_main_card.refresh())

# Dropdown options for new reference assignment
@ui.refreshable
def check_available():
    def show_basic_data():
        if state.current_ref != 'W-':
            new_pages.main = True
        else:
            new_pages.main = False

    with ui.card().classes('w-full mx-auto p-4').bind_visibility_from(state, 'new_assign'):
        ui.label('Asignar referencia').style('font-family: Magistral; font-size:1.6rem;')
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
def create_main_card(owner, *, edit):
    item = get_current_item()
    # per-instance state (private to this call)
    st = SimpleNamespace(edit=edit)
    #Helpers
    def recompute_props():
        st.field_props = 'outlined stack-label ' if st.edit else 'readonly borderless '
    recompute_props()  # <-- respect initial edit
    def save_changes():
        try: 
            insert_new(state.current_ref, item.basic.name, item.basic.description, item.basic.cls, item.basic.wear)
        finally:
            commit_cached()
        lookup_get_thumbnail()
        toggle_edit()
        state.new_basic = True

    def discard_changes():
        cache.clear()
        lookup_get_thumbnail
        toggle_edit()
        state.new_basic = False
    def toggle_edit():
        st.edit = not st.edit
        st.field_props = 'outlined stack-label ' if st.edit else 'readonly borderless '
        print(item)
        render.refresh()
        print(item)
    def _to_jpeg_bytes(img: Image.Image, quality=90, bg=(255,255,255)) -> bytes:
        # Flatten alpha (transparency) because JPEG doesn’t support it
        if img.mode in ('RGBA','LA') or (img.mode == 'P' and 'transparency' in img.info):
            canvas = Image.new('RGB', img.size, bg)
            rgba = img.convert('RGBA')
            canvas.paste(rgba, mask=rgba.split()[-1])
            img = canvas
        else:
            img = img.convert('RGB')

        buf = io.BytesIO()
        img.save(buf, 'JPEG', quality=quality, optimize=True)
        return buf.getvalue()
    def lookup_get_thumbnail():
        blob, ext = get_thumbnail(item.basic.ref)
        if blob:
            new_pages.uri = blob_to_data_uri(blob, 'image/jpeg')  # always correct
        else:
            new_pages.uri = img_loading
    def handle_upload(e):
        raw = e.content.read() if hasattr(e.content, 'read') else e.content
        ext = os.path.splitext(e.name)[1].lower()

        if ext in ('.png', '.jpg', '.jpeg', '.webp', '.tif', '.tiff'):
            # Convert images to JPEG
            img = Image.open(io.BytesIO(raw))
            img = ImageOps.exif_transpose(img)   # respect EXIF rotation
            data = _to_jpeg_bytes(img, quality=85)
            final_name = "Thumbnail.jpg"
        else:
            # Non-image: store as-is
            data = raw
            final_name = e.name

        cache.add_file(code=state.current_ref,
                       file_name=final_name,
                       data=data,
                       folder=None)

        ui.notify(f'Cached {final_name} ({len(data)//1024} KB)', type='positive')
    def commit_cached():
        ok, failed = cache.flush(conn_string=state.sku_conn_string, overwrite=True)
        if ok:
            ui.notify(f'Uploaded: {", ".join(ok)}')
        if failed:
            for name, ex in failed:
                ui.notify(f'Failed {name}: {ex}', type='negative')
    #UI
    @ui.refreshable
    def render():
        with ui.card().classes('w-full mx-auto p-4').bind_visibility(*owner):
            # Title
            with ui.row().classes('w-full justify-between items-center'):
                ui.label('Datos fabricante').style('font-family: Magistral; font-size:1.6rem;')
                with ui.row():
                    if st.edit:
                        ui.button(icon='check', on_click=save_changes).props('flat round dense color=green')
                        ui.button(icon='close', on_click=toggle_edit).props('flat round dense color=red')
                    else:
                        ui.button(icon='edit', on_click=toggle_edit).props('flat round dense color=primary')
            ui.separator()
            # Body
            with ui.row().classes('w-full items-start h-full'):
                with ui.grid(columns='1fr 0.3fr').classes('w-full'):
                    with ui.column().classes('w-full mx-auto  p-4 gap-4'):
                        ui.label("Ref").classes('w-full').style('font-family: Magistral; font-size:2rem;').bind_text(item.basic, "ref")
                        title = ui.input(label='Titulo').classes('w-full').style('font-family: Muli; font-size:1rem;').props('outlined dense stack-label').bind_value(item.basic, "name")
                        desc = ui.input(label='Descripción').classes('w-full').style('font-family: Muli; font-size:1rem;').props('outlined stack-label').bind_value(item.basic, "description")
                        with ui.row():
                            tipo = ui.select(options={1:'Pieza', 2:'Kit', 4:'Externa'}, label='Tipo') .props('outlined  stack-label') .classes('w-40').bind_value(item.basic, "cls")
                            desgaste = ui.select(options={1:'Estándar', 2:'Recambio', 4:'Consumible'}, label='Desgaste') .props('outlined  stack-label') .classes('w-40').bind_value(item.basic, "wear")

                    if st.edit:
                        ui.upload(
                            label='Foto',
                            multiple=False,
                            auto_upload=True,
                            on_upload=lambda e: handle_upload(e)).props('accept="image/*"')
                    else:
                        with ui.column().classes('w-full mx-auto p-4'):
                            thumb = ui.image().bind_source(new_pages,"uri").style("width:12rem; height:12rem; object-fit: contain;")
    # build immediately and return the refresh handle in case you need it later
    render()
    return render

@ui.refreshable
def content_controls():

    item = get_current_item()
    if not item:
        return
    with ui.card().classes('w-full mx-auto p-4').bind_visibility_from(state, 'new_basic'):
        # Title 
        ui.label('Páginas').style('font-family: Magistral; font-size:1.6rem;')
        ui.separator()
        with ui.row().classes('w-full'):
            ui.checkbox('External').bind_value(new_pages, 'external')
            ui.checkbox('Mechanical').bind_value(new_pages, 'mechanical')
            ui.checkbox('Electrical').bind_value(new_pages, 'electrical')
            ui.checkbox('Shipping').bind_value(new_pages, 'shipping')
            ui.checkbox('Supplier').bind_value(new_pages, 'supplier')
            ui.checkbox('Finance').bind_value(new_pages, 'finance')
            ui.checkbox('Certs').bind_value(new_pages, 'certs')
            ui.checkbox('Enviromental').bind_value(new_pages, 'enviromental')



