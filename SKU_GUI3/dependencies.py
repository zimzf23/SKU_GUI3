import csv
import os
import time
import threading
import subprocess
import sys
import toml
import json
import tomllib
from dataclasses import make_dataclass, field, asdict
from typing import Any
from pathlib import Path
from types import SimpleNamespace

from nicegui import app,ui, events, binding
from nicegui.events import ValueChangeEventArguments
import pyodbc

with open("config.toml", "rb") as f:
    config = tomllib.load(f)

# Determine where the bundled assets actually live:
if getattr(sys, "_MEIPASS", None):
    # Running as a bundled exe
    assets_path = os.path.join(sys._MEIPASS, "assets")
else:
    # Running from source
    assets_path = os.path.join(os.path.dirname(__file__), "assets")

# Serve everything under that folder at /assets
app.add_static_files("/assets", assets_path)

img_loading = '''data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI2ODAuNzY0IiBoZWlnaHQ9IjUyOC4zNTQiIHZpZXdCb3g9IjAgMCAxODAuMTE5IDEzOS43OTQiPjxnIHRyYW5zZm9ybT0idHJhbnNsYXRlKC0xMy41OSAtNjYuNjM5KSIgcGFpbnQtb3JkZXI9ImZpbGwgbWFya2VycyBzdHJva2UiPjxwYXRoIGZpbGw9IiNkMGQwZDAiIGQ9Ik0xMy41OTEgNjYuNjM5SDE5My43MXYxMzkuNzk0SDEzLjU5MXoiLz48cGF0aCBkPSJtMTE4LjUwNyAxMzMuNTE0LTM0LjI0OSAzNC4yNDktMTUuOTY4LTE1Ljk2OC00MS45MzggNDEuOTM3SDE3OC43MjZ6IiBvcGFjaXR5PSIuNjc1IiBmaWxsPSIjZmZmIi8+PGNpcmNsZSBjeD0iNTguMjE3IiBjeT0iMTA4LjU1NSIgcj0iMTEuNzczIiBvcGFjaXR5PSIuNjc1IiBmaWxsPSIjZmZmIi8+PHBhdGggZmlsbD0ibm9uZSIgZD0iTTI2LjExMSA3Ny42MzRoMTUyLjYxNHYxMTYuMDk5SDI2LjExMXoiLz48L2c+PC9zdmc+'''
content = '''<svg width="50%" height="50%" viewBox="0 0 1418 485" version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" xml:space="preserve" xmlns:serif="http://www.serif.com/" style="fill-rule:evenodd;clip-rule:evenodd;stroke-linejoin:round;stroke-miterlimit:2;"><g id="imagotipo"><path d="M551.646,176.583c1.567,-6.05 4.933,-16.133 21.737,-16.133c15.242,-0 19.946,9.187 21.738,16.133l29.133,107.342c0.45,1.57 1.792,3.808 3.363,3.808c2.016,-0 3.133,-2.908 3.583,-4.704l31.15,-120.788l30.029,0l-37.871,136.7c-3.362,12.325 -7.395,21.959 -25.325,21.959c-17.925,-0 -22.183,-9.634 -25.1,-20.167l-27.562,-101.513c-0.671,-2.916 -1.567,-4.262 -2.913,-4.262c-1.566,-0 -2.241,1.346 -3.137,4.262l-27.788,101.513c-2.912,10.533 -6.945,20.167 -24.875,20.167c-17.929,-0 -22.187,-9.634 -25.545,-21.959l-37.65,-136.7l30.029,0l31.15,120.788c0.446,1.566 0.896,4.704 3.362,4.704c1.567,-0 2.688,-2.238 3.359,-3.808l29.133,-107.342Z" style="fill:#0053a1;fill-rule:nonzero;"/><path d="M734.753,258.38l60.288,0l-25.55,-63.871c-0.896,-2.462 -2.467,-6.496 -4.483,-6.496c-2.017,0 -3.588,4.034 -4.48,6.496l-25.775,63.871Zm4.484,-80.225c5.604,-13.225 11.654,-17.704 25.77,-17.704c13.446,-0 20.171,4.479 25.771,17.704l59.163,140.954l-31.15,0l-16.134,-39.662l-75.52,-0l-15.913,39.662l-31.15,0l59.163,-140.954Z" style="fill:#0053a1;fill-rule:nonzero;"/><path d="M856.974,319.11l0,-133.338c0,-17.929 9.408,-23.529 22.854,-23.529l79.109,0c29.133,0 39.216,18.15 39.216,49.525c0,32.267 -10.083,52.438 -36.304,52.438l-15.687,-0l-0,1.121l55.129,53.783l-38.096,0l-50.646,-50.871c-3.362,-3.583 -7.396,-8.742 -7.396,-13.221l0,-3.587c0,-6.275 4.484,-10.754 13.221,-10.754l30.479,-0c16.359,-0 18.821,-10.98 18.821,-28.909c0,-17.929 -3.358,-25.996 -22.183,-25.996l-47.734,0c-8.962,0 -11.204,2.242 -11.204,11.205l0,122.133l-29.579,-0Z" style="fill:#0053a1;fill-rule:nonzero;"/><path d="M1063.36,258.38l60.283,0l-25.55,-63.871c-0.896,-2.462 -2.467,-6.496 -4.479,-6.496c-2.021,0 -3.592,4.034 -4.484,6.496l-25.77,63.871Zm4.479,-80.225c5.604,-13.225 11.654,-17.704 25.775,-17.704c13.441,-0 20.166,4.479 25.766,17.704l59.163,140.954l-31.15,0l-16.133,-39.662l-75.521,-0l-15.909,39.662l-31.15,0l59.159,-140.954Z" style="fill:#0053a1;fill-rule:nonzero;"/><path d="M1299.03,319.11l-65.659,-59.833c-6.725,-6.055 -8.066,-13.221 -8.066,-20.842c-0,-6.05 3.358,-13.225 7.616,-17.479l59.388,-58.713l36.75,0l-67.9,64.317c-3.583,3.583 -7.396,6.271 -7.396,11.65c0,6.5 4.708,10.529 9.188,14.342l74.179,66.558l-38.1,-0Zm-112.05,-156.867l29.583,0l0,156.867l-29.583,-0l-0,-156.867Z" style="fill:#0053a1;fill-rule:nonzero;"/><path d="M215.987,197.461c5.813,-9.833 14.813,-15.475 24.688,-15.475c9.879,-0 18.879,5.642 24.691,15.475l37.867,64.083l24.3,-111.075l-58.5,-58.5c-15.658,-15.662 -41.05,-15.662 -56.708,0l-58.5,58.5l24.295,111.075l37.867,-64.083Z" style="fill:#4da32f;"/><path d="M389.384,212.321l-34.904,-34.909l-24.055,109.959c-3.808,17.417 -14.941,21.017 -19.554,21.758c-4.608,0.742 -16.308,0.8 -25.375,-14.546l-44.816,-75.841l-44.821,75.841c-7.409,12.538 -16.575,14.792 -22.196,14.792c-1.258,0 -2.338,-0.112 -3.179,-0.246c-4.613,-0.741 -15.742,-4.341 -19.554,-21.758l-24.05,-109.954l-34.909,34.904c-15.662,15.658 -15.662,41.05 0,56.708l120.35,120.354c15.663,15.659 41.05,15.659 56.713,0l120.35,-120.354c15.658,-15.658 15.658,-41.05 -0,-56.708" style="fill:#0053a1;"/></g></svg>'''