import dash_bootstrap_components as dbc
from dash import html

# Sidebar
sidebar = html.Div(
    [   
        # dbc.Button([
        #     html.I(className="fas fa-align-left")],
        #     id="open-canvas",
        #     n_clicks=0),

        # dbc.Offcanvas(
        #     dbc.ListGroup(),
        #     id="offcanvas-scrollable",
        #     scrollable=True,
        #     title="",
        #     is_open=True,
        # ),
    ],
    style = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}, className='sidebar'
)


# Navbar
navbar = dbc.NavbarSimple(
    children=[sidebar],
    brand="Qlab Dashboard",
    brand_style={"font-size": "26px"},
    color="#495057",
    links_left=True,
    fixed="top",
    sticky="top",
    class_name="customNavBar")


# 

from dotenv import load_dotenv
import os
from ..analysis import HerokuDB

# Load dot env file
load_dotenv(dotenv_path=os.getcwd()+'/qlab/.env')

# Connect to Heroku PostgreSQL
db = HerokuDB(os.environ.get("HERO_URI"))