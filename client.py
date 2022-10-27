#!/usr/bin/env python3
import requests
import json
import logging
from pathlib import Path
import flet
from flet import Page, Image, TextField, View, ElevatedButton, AppBar, Text

logging.basicConfig(
    format = "[{asctime}][{name:10}][{levelname:7}] {msg}",
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
                    Image(src = "logo.png", width = 150, height = 150),
                    TextField(label = None, hint_text = "Enter your user ID"),
                    ElevatedButton("Log in", on_click = lambda _: log_in(page)),
                ],
                vertical_alignment = "center",
                horizontal_alignment = "center"
            )
        )
        if page.route == "/signup":
            # TODO create sign-up form
            pass
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
    login_view = page.views[-1]
    user   = login_view.controls[1].value
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

flet.app(target=main, assets_dir = "assets")