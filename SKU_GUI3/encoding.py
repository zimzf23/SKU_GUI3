from dependencies import *
import base64

def blob_to_data_uri(blob: bytes, mime_type: str) -> str:
    """
    Convert a binary image blob into a Data URI suitable for <img src="...">.
    :param blob: raw image bytes
    :param mime_type: the MIME type, e.g. 'image/jpeg' or 'image/png'
    :return: a string like 'data:image/jpeg;base64,/9j/4AAQ...'
    """
    b64 = base64.b64encode(blob).decode('ascii')
    return f'data:{mime_type};base64,{b64}'

