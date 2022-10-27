#!/usr/bin/env python3
from xml.etree.ElementInclude import LimitedRecursiveIncludeError
from click import option
import requests
import json
import logging
from pathlib import Path
from calendar import month_abbr
from datetime import datetime
import flet
from flet import (
    Page, View, Container, AppBar, Row, Column, GridView, Divider,
    Image, Text, Markdown,
    TextField,  ElevatedButton, Dropdown, Slider, Checkbox,
    margin, dropdown
)

logging.basicConfig(
    format = "[{asctime}][{name:^10}][{levelname:^7}] {msg}",
    style = "{",
    force = True,
    level = logging.INFO
)
logger = logging.getLogger(__name__)

root = Path(__file__).parent
usr_cache = root / '.usr_cache'

def main(page: Page):
    logger.info("Setting up page")
    page.title = "MutualCake - login"
    page.vertical_alignment = "center"
    page.horizontal_alignment = "center"
    page.route = "/login"

    def handle_route(e):
        logger.info(f"Route change: {e.route}")
        page.views.clear()
        page.views.append(
            View(
                route = "/login",
                controls = [
                    Container(
                        content = Image(src = "logo.png", width = 150, height = 150),
                        margin = margin.only(top = 50, bottom = 50)
                    ),
                    Container(
                        content = TextField(label = None,
                        hint_text = "Enter your user ID"),
                        width = 600,
                    ),
                    ElevatedButton("Log in", on_click = lambda _: log_in(page)),
                ],
                vertical_alignment = "center",
                horizontal_alignment = "center"
            )
        )
        if page.route == "/signup":
            # def check_is_valid_day(e):
            #     day_is_valid = int(e) > 0 and int(e) <= 31 
            #     if
            page.views.append(
                View(
                    route = "/signup",
                    controls = [
                        Markdown("# Welcome to MutualCake ™️"),
                        Markdown("Please fill in your details to continue"),
                        
                        Container(
                            Markdown("## 1. Choose a User ID"),
                            margin = margin.only(top = 50)
                        ),
                        Container(
                            content = TextField(label = None,
                                                hint_text = "Choose a user ID"),
                            width = 600,
                        ),
                        
                        Container(
                            Markdown("## 2. Enter your date of birth"),
                            margin = margin.only(top = 50)
                        ),
                        Row(
                            controls = [
                                Container(
                                    Dropdown(label = "Day", options = [
                                        dropdown.Option(day) for day in range(1,32)
                                    ]),
                                    width = 180
                                ),
                                Container(
                                    Dropdown(label = "Month", options=[
                                        dropdown.Option(month) for month in
                                        month_abbr if month
                                    ]),
                                    width = 180
                                ),
                                Container(
                                    Dropdown(label = "Year", options=[
                                        dropdown.Option(year) 
                                        for year in range(datetime.now().year, 1900, -1)
                                    ]),
                                    width = 180
                                )
                            ],
                            width = 600,
                            alignment="center"
                        ),
                        
                        Container(
                            Markdown("## 3. Enter any allergies you may have"),
                            margin = margin.only(top = 50)
                        ),
                        Container(
                            content = Row(controls = [
                                Checkbox(label = "Eggs"),
                                Checkbox(label = "Milk"),
                                Checkbox(label = "Nuts"),
                                Checkbox(label = "Chocolate"),

                            ],
                            alignment="center"
                            # runs_count=2
                            )
                        ),
                        Divider(height = 30, thickness = 3),
                        ElevatedButton("Sign up", on_click= lambda _: sign_up_user(page)),
                    ],
                    vertical_alignment = "center",
                    horizontal_alignment = "center"
                )
            )
        if page.route == "/main":
            page.views.append(
                View(
                    route = "/main",
                    controls = [
                        AppBar(title=Text("Main dashboard"), bgcolor="#9accdaff"),
                        ElevatedButton("Do you like to bake cakes?"),
                    ],
                    vertical_alignment = "center",
                    horizontal_alignment = "center"
                )
            )

    def view_pop(e):
        logger.info(f"View pop: {e.view}")
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = handle_route
    page.on_view_pop = view_pop
    page.go(page.route)

def log_in(page):
    # NOTE: seems more robust but may not be necessary
    # login_view = [view for view in page.views if view.route == '/login'][0]
    login_view = page.views[-1]
    user   = login_view.controls[1].content.value
    logger.info(f"User is '{user}'")
    user_data_respose = requests.get(
        url = f"http://127.0.0.1:8000/employees/{user}"
    )
    user_data = user_data_respose.json() # TODO check status code, etc
    if user_data is None:
        logger.info(f"User {user} not registered, preparing sign-up sheet")
        page.go("/signup")
        return
    logger.info(f"Successfully retrieved details for user {user}, heading to main")
    usr_cache.write_text(json.dumps(user_data))
    page.go("/main")

def sign_up_user(page):
    pass

flet.app(target=main, assets_dir = "assets")