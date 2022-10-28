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
    Image, Text, Markdown, SnackBar,
    TextField,  ElevatedButton, TextButton, Dropdown, Slider, Checkbox,
    margin, dropdown, alignment
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
SERVER_URL = "http://127.0.0.1:8000"

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
                        content = Image(src="logo.png", width=150, height=150),
                        margin = margin.only(top = 50, bottom = 50)
                    ),
                    Container(
                        content = TextField(label = None,
                        hint_text = "Enter your user ID"),
                        width = 400,
                    ),
                    ElevatedButton("Log in", on_click = lambda _: log_in(page)),
                    Divider(height = 50, thickness = 0),
                    Container(
                        Row(controls = [
                            Markdown("Not a member yet?"),
                            TextButton(content = Markdown("**Sign up**"),
                                        on_click = lambda _: page.go("/signup")),
                        ]),
                        margin = margin.only(top = 50),
                    ),
                ],
                vertical_alignment = "center",
                horizontal_alignment = "center"
            )
        )
        if page.route == "/signup":
            page.views.append(
                View(
                    route = "/signup",
                    controls = [
                        AppBar(title=Text("Sign up"), 
                                color = "#000000", bgcolor="#f5c300"),
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
                                        dropdown.Option(day)
                                        for day in range(1,32)
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
                                        for year in \
                                        range(datetime.now().year, 1900, -1)
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
                        ElevatedButton("Sign up",
                                        on_click= lambda _: sign_up_user(page)),
                    ],
                    vertical_alignment = "center",
                    horizontal_alignment = "center",
                    scroll='auto'
                )
            )
        if page.route == "/main":
            birthday_person = get_assigned_employee()
            cake_to_bake    = get_assigned_cake()
            page.views.append(
                View(
                    route = "/main",
                    controls = [
                        AppBar(title=Text("Main dashboard"), 
                                color = "#000000", bgcolor="#f5c300"),
                        Row(
                            controls = [
                                Column(controls=[
                                    Container(
                                        Markdown("## Your cake will be for..."),
                                        margin = margin.only(bottom = 100)
                                    ),
                                    Text(birthday_person)
                                ], horizontal_alignment="center"),
                                Column(controls=[
                                    Container(
                                        Markdown("## And the cake will be..."),
                                        margin = margin.only(bottom = 100)
                                    ),
                                    Text(cake_to_bake)
                                ], horizontal_alignment="center"),
                            ],
                            spacing = 150,
                            alignment = "center",
                            vertical_alignment = "center"
                        )
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
    page.on_disconnect = clear_cache
    page.on_close = clear_cache
    page.go(page.route)

def log_in(page):
    # NOTE: seems more robust but may not be necessary
    # login_view = [view for view in page.views if view.route == '/login'][0]
    login_view = page.views[-1]
    user   = login_view.controls[1].content.value
    logger.info(f"User is '{user}'")
    user_data_response = requests.get(
        url = f"{SERVER_URL}/employees/{user}"
    )
    user_data = user_data_response.json() # TODO check status code, etc
    if user_data is None:
        logger.info(f"User {user} not registered")
        page.snack_bar = SnackBar(Text("We cannot seem to find you..."), 
                                    action="Sign up",
                                    on_action = lambda _: page.go("/signup"))
        page.snack_bar.open = True
        page.update()
        return
    logger.info(f"Successfully retrieved details for user {user}, heading to main")
    usr_cache.write_text(json.dumps(user_data) + '\n')
    page.go("/main")

def sign_up_user(page):
    #Collect data
    user_id = page.views[-1].controls[4].content.value
    logger.debug(f"user_id = {user_id}")
    dmy_row = page.views[-1].controls[6]
    logger.debug(f"dmy_row = {dmy_row}")
    dob_str = "-".join([f"{ctrl.content.value!s}" for ctrl in dmy_row.controls])
    dob_str = datetime.strptime(dob_str, "%d-%b-%Y").strftime("%Y-%m-%d")
    logger.debug(f"dob_str = {dob_str}")
    allergies_row = page.views[-1].controls[8].content
    allergies = [box.label for box in allergies_row.controls if box.value]
    logger.info(f"Collected user data: Name='{user_id}'; DOB='{dob_str}'; "
                f"Allergies='{allergies}'")
    #TODO Check user does not already exist!
    #Budle and do POST request
    data = {
        "name": user_id,
        "birthday": dob_str,
        "allergies": allergies
    }
    requests.post(
        url = f"{SERVER_URL}/employees/",
        data = json.dumps(data),
        headers = {'Content-type': 'application/json'}
    )
    #Switch to main cake dashboard
    page.go("/main")

def get_assigned_employee():
    cached_user = json.loads(usr_cache.read_text())
    assigned_employee = requests.get(
        f"{SERVER_URL}/employees/{cached_user['id']}/assignments/employee"
    ).json()
    if assigned_employee is None:
        logger.info(f"User: {cached_user!s} has nobody to bake to!")
        return
    return assigned_employee

def get_assigned_cake():
    cached_user = json.loads(usr_cache.read_text())
    assigned_employee = requests.get(
        f"{SERVER_URL}/employees/{cached_user['id']}/assignments/cake"
    ).json()
    if assigned_employee is None:
        logger.info(f"User: {cached_user!s} has nothing to bake!")
        return
    return assigned_employee


def clear_cache():
    usr_cache.unlink()

flet.app(target=main, assets_dir = "assets")