#!/usr/bin/env python3
import requests
import json
import logging
from pathlib import Path
from calendar import month_abbr
from datetime import datetime, date
import flet
from flet import (
    Page, View, Container, AppBar, Row, Column, ListView, Divider,
    Image, Text, Markdown, SnackBar, Icon, icons,
    TextField,  ElevatedButton, TextButton, Dropdown, IconButton, Checkbox, 
    AlertDialog, RadioGroup, Radio, Banner,
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
OK_COLOR = "#92bce2ff"
WARN_COLOR = "#ff9955"
DANGER_COLOR = "#c73440ff"
APPBAR_COLOR = "#f5c300"

def main(page: Page):
    logger.info("Setting up page")
    page.title = "MutualCake"
    page.vertical_alignment = "center"
    page.horizontal_alignment = "center"
    page.route = "/login"

    def handle_route(e):
        all_ingredients = get_all_ingredients()
        logger.info(f"Fetched all ingredients: {all_ingredients}")
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
                                            hint_text = "Enter your user ID",
                                            on_submit = lambda _: log_in(page)),
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
                                color = "#000000", bgcolor=APPBAR_COLOR),
                        Markdown("# Welcome to MutualCake ™️"),
                        Markdown("Please fill in your details to continue"),
                        
                        Container(
                            Markdown("## 1. Enter your name"),
                            margin = margin.only(top = 50)
                        ),
                        Container(
                            content = TextField(label = None,
                                                hint_text = "John Doe"),
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
                            content = Column(
                                wrap = True,
                                height = page.height//4,
                                spacing=5,
                                run_spacing=5,
                                controls = [
                                    Checkbox(label = x) for x in all_ingredients
                                ],
                            ),
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
        if page.route.startswith("/main"):
            user_name = json.loads(usr_cache.read_text())['name']
            birthday_person = get_assigned_employee()
            birthday_person_fmt = format_partner_w_birthday(birthday_person)
            cake_to_bake    = get_assigned_cake()
            cake_details_button_visible = (
                False if "You have not chosen any cake" in cake_to_bake
                else True
            )
            check_allergens_in_cake(page)
            page.views.append(
                View(
                    route = "/main",
                    controls = [
                        AppBar(title=Text(f"Hello, {user_name}"), 
                                color = "#000000", bgcolor=APPBAR_COLOR),
                        Container(
                            Row(
                                controls = [
                                    IconButton(
                                        icon = icons.ACCOUNT_CIRCLE_ROUNDED,
                                        icon_size = 50,
                                        tooltip = "View/modify profile",
                                        on_click=lambda _: page.go("/main/user")
                                    )
                                ],
                                alignment='end'    
                            ),
                            # margin = margin.only(bottom = 50, top = 5)
                        ),
                        Divider(height = 50, thickness = 1, opacity=0),
                        Row(
                            controls = [
                                Column(controls=[
                                    Container(
                                        Markdown("## Your cake will be for..."),
                                        margin = margin.only(bottom = 50)
                                    ),
                                    Text(birthday_person_fmt)
                                ], horizontal_alignment="center"),
                                Column(controls=[
                                    Container(
                                        Markdown("## And the cake will be..."),
                                        margin = margin.only(bottom = 50)
                                    ),
                                    Container(
                                        Text(cake_to_bake),
                                        margin = margin.only(bottom = 10)
                                    ),
                                    ElevatedButton(
                                        "Show cake details",
                                        visible = cake_details_button_visible,
                                        disabled = not cake_details_button_visible,
                                        on_click = lambda _: page.go("/main/cake")
                                    )
                                ], horizontal_alignment="center"),
                            ],
                            spacing = 150,
                            alignment = "center",
                            vertical_alignment = "start"
                        ),
                        Divider(height=75, thickness=1, opacity=0),
                        Row(
                            controls = [
                                ElevatedButton(
                                    "Change partner",
                                    on_click = lambda _: page.go("/main/change-partner")
                                ),
                                ElevatedButton(
                                    "Change cake",
                                    on_click = lambda _: page.go("/main/change-cake")
                                ),
                                ElevatedButton(
                                    "Add your own cake recipe!",
                                    on_click = lambda _: page.go("/main/newcake")
                                ),
                            ],
                            alignment="spaceEvenly"
                        )
                    ],
                    vertical_alignment = "start",
                    horizontal_alignment = "center"
                )
            )
        if page.route == "/main/cake":
            cake_data = get_assigned_cake(details=True)
            logging.info(f"Retrieved dake data: {cake_data}")
            ingredients_md_list = "\n".join(sorted({
                f"- {ingr['name'].capitalize()}" 
                for ingr in cake_data['ingredients']
            }))
            page.views.append(
                View(
                    route = "/main/cake",
                    controls = [
                        AppBar(
                            title = Text(f"Your cake: {cake_data['name']}",
                                        color = "#000000"),
                            bgcolor=APPBAR_COLOR
                        ),
                        Container(
                            Markdown(f"__{cake_data['previewDescription']}__"),
                            margin = margin.only(bottom = 50)
                        ),
                        Container(
                            Image(src="logo.png", width=150, height=150),
                            margin = margin.only(bottom = 50)
                        ),
                        Row(
                            controls = [
                                Container(Markdown("# Ingredients"), width = 250),
                                Markdown(ingredients_md_list),
                            ],
                            alignment = "center"
                        )
                    ],
                    vertical_alignment = "center",
                    horizontal_alignment = "center"
                )
            )
        if page.route == "/main/user":
            cached_user = json.loads(usr_cache.read_text())
            user_data = get_user_details(cached_user['id'])
            logger.info(f"Fetched data for user '{cached_user['id']}': {user_data}")
            user_allergies = [x['name'].capitalize() for x in user_data['allergies']]
            page.views.append(
                View(
                    route = "/main/user",
                    controls = [
                        AppBar(
                            title = Text("Your Profile"),
                            color = "#000000", bgcolor=APPBAR_COLOR
                        ),
                        Row(
                            controls = [
                                # Left side: User pic, user id, submit button
                                Column(controls = [
                                    Container(
                                        Icon(name=icons.ACCOUNT_CIRCLE_ROUNDED,
                                            size = 250),
                                        margin = margin.only(bottom = 10)
                                    ),
                                    Container(
                                        TextField(label = "User ID",
                                                value = user_data["id"],
                                                disabled = True),
                                        margin = margin.only(bottom = 10)
                                    ),
                                    ElevatedButton(
                                        "Update details",
                                        on_click=lambda _:
                                            update_user_details(page)
                                    ),
                                    ElevatedButton(
                                        "Delete profile",
                                        color = "#ffffff",
                                        bgcolor = DANGER_COLOR,
                                        on_click=lambda _: delete_user(page)
                                    )
                                    ],
                                    alignment = "start",
                                    horizontal_alignment="center"
                                ),
                                # Right side: Pic, user name, dob, allergies
                                Column(controls = [
                                    Container(
                                        TextField(label = "Full name",
                                                value = user_data["name"]),
                                        margin = margin.only(bottom=10, top=25)
                                    ),
                                    Container(
                                        TextField(label = "Date of birth",
                                                value = user_data["birthday"],
                                                hint_text = "YYYY-MM-DD"),
                                        margin = margin.only(bottom=10)
                                    ),
                                    Markdown("## Allergies"),
                                    Row(
                                        wrap = True,
                                        width = page.width//4,
                                        spacing=5,
                                        run_spacing=5,
                                        controls = [
                                            Checkbox(
                                                label = x,
                                                value = x in user_allergies
                                            )
                                            for x in all_ingredients
                                        ],
                                    )
                                ]),
                            ],
                            # spacing = 50,
                            alignment = "center",
                            vertical_alignment = "start"
                        )
                    ],
                    vertical_alignment = "center",
                    horizontal_alignment = "center",
                    scroll='auto'
                )
            )
        if page.route == "/main/newcake":
            page.views.append(
                View(
                    route = "/main/newcake",
                    controls = [
                        AppBar(title=Text("Submit new cake"), 
                                color = "#000000", bgcolor=APPBAR_COLOR),
                        Markdown("# Submit your own cake"),
                        
                        Container(
                            Markdown("## 1. Name of your cake"),
                            margin = margin.only(top = 50)
                        ),
                        Container(content = TextField(label = None,
                                                    hint_text = "Cake name"),
                                    width = 600
                        ),
                        
                        Container(
                            Markdown("## 2. Brief description"),
                            margin = margin.only(top = 50)
                        ),
                        Container(content = TextField(label = None,
                                                    hint_text = "Description"),
                                    width = 600
                        ),
                        
                        Container(
                            Markdown("## 3. Which ingredients does it have?"),
                            margin = margin.only(top = 50)
                        ),
                        Container(
                            content = Column(
                                wrap = True,
                                height = page.height//4,
                                spacing=5,
                                run_spacing=5,
                                controls = [
                                    Checkbox(label = x) for x in all_ingredients
                                ],
                            ),
                        ),
                        Divider(height = 30, thickness = 3),
                        ElevatedButton("Submit",
                                        on_click= lambda _: submit_cake(page)),
                    ],
                    vertical_alignment = "start",
                    horizontal_alignment = "start",
                    scroll='auto'
                )
            
            )
        if page.route == "/main/change-partner":
            this_user_id = json.loads(usr_cache.read_text())['id']
            all_employees = get_all_employees()
            for employee in all_employees:
                employee["allergies"] = [x['name'].capitalize() 
                                        for x in employee["allergies"] ]
            page.views.append(
                View(
                    route = "/main/change-partner",
                    vertical_alignment = "start",
                    horizontal_alignment = "start",
                    scroll='auto',
                    controls = [
                        AppBar(
                            title = Text("Choose a new partner"),
                            color = "#000000", bgcolor=APPBAR_COLOR
                        ),
                        Container(
                            Markdown("## Your colleagues:"),
                            margin = margin.only(top = 50, left = 50)
                        ),
                        Container(
                            RadioGroup(
                                content = Column(controls = [
                                    Radio(
                                        value=emp['id'],
                                        label= format_employee_label(emp)
                                    )
                                    for emp in all_employees
                                    if emp['id'] != this_user_id
                                ])
                            ),
                            margin = margin.only(top = 20, left = 75)
                        ),
                        Container(
                            ElevatedButton("Choose new partner", 
                                on_click=lambda _: choose_new_partner(page)),
                            margin = margin.only(top = 50),
                            alignment=alignment.center
                        ),
                    ]
                )
            )
        if page.route == "/main/change-cake":
            this_user_id = json.loads(usr_cache.read_text())['id']
            current_cake = (
                cake["name"] if (cake := get_assigned_cake(details=True)) 
                is not None else None
            )
            all_cakes = get_all_cakes()
            logger.info(f"All cakes: {all_cakes}")
            logger.info(f"Current cakes: {current_cake}")
            assigned_employee_details = get_user_details(
                get_assigned_employee(),
                id_type='name'
            )
            logger.info(f"Assigned partner: {assigned_employee_details}")
            partner_allergies = [
                ingredient['name'].lower() 
                for ingredient in assigned_employee_details['allergies']
            ]
            logger.info(f"Partner's allergies: {partner_allergies}")
            page.views.append(
                View(
                    route = "/main/change-cake",
                    vertical_alignment = "start",
                    horizontal_alignment = "start",
                    scroll='auto',
                    controls = [
                        AppBar(
                            title = Text("Choose a new cake"),
                            color = "#000000", bgcolor=APPBAR_COLOR
                        ),
                        Container(
                            Markdown("## Our cakes:"),
                            margin = margin.only(top = 50, left = 50)
                        ),
                        Container(
                            RadioGroup(
                                content = Column(controls = [
                                    Radio(
                                        value=cake['id'],
                                        label= format_cake_label(
                                            cake,
                                            current_cake,
                                            partner_allergies
                                        )
                                    )
                                    for cake in all_cakes
                                ]),
                            ),
                            margin = margin.only(top = 20, left = 75)
                        ),
                        Container(
                            ElevatedButton("Choose new cake",
                                on_click=lambda _: choose_new_cake(page)),
                            margin = margin.only(top = 50),
                            alignment=alignment.center
                        ),
                    ]
                )
            )

    def view_pop(e):
        logger.info(f"View pop @ {e.view.route}: {e.view}")
        logger.info("Current routes in page.views: "
                    f"{[v.route for v in page.views]}")
        page.views.pop()
        logger.info(f"Popped last view. Current routes in page.views: "
                    f"{[v.route for v in page.views]}")
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = handle_route
    page.on_view_pop = view_pop
    page.on_disconnect = clear_cache
    page.on_close = clear_cache
    page.go(page.route)


# region Send data to server ----------------------------------------

def log_in(page):
    # NOTE: seems more robust but may not be necessary
    # login_view = [view for view in page.views if view.route == '/login'][0]
    login_view = page.views[-1]
    user   = login_view.controls[1].content.value
    logger.info(f"User is '{user}'")
    user_data = get_user_details(user)
    if user_data is None:
        logger.info(f"User {user} not registered")
        page.snack_bar = SnackBar(
            Text("We cannot seem to find you...", color = "#000000",), 
            bgcolor = WARN_COLOR, action="Sign up",
            on_action = lambda _: page.go("/signup")
        )
        page.snack_bar.open = True
        page.update()
        return
    logger.info(f"Successfully retrieved details for user {user}, heading to main")
    usr_cache.write_text(json.dumps(user_data) + '\n')
    page.go("/main")

def sign_up_user(page):
    #Collect data
    user_name = page.views[-1].controls[4].content.value
    logger.debug(f"user_name = {user_name}")
    dmy_row = page.views[-1].controls[6]
    logger.debug(f"dmy_row = {dmy_row}")
    dob_str = "-".join([f"{ctrl.content.value!s}" for ctrl in dmy_row.controls])
    try:
        dob_str = datetime.strptime(dob_str, "%d-%b-%Y").strftime("%Y-%m-%d")
    except:
        page.snack_bar = SnackBar(
            Text("Invalid date, please chose one option in each box.", 
                    color = "#000000"),
            bgcolor = WARN_COLOR
        )
        page.snack_bar.open = True
        page.update()
        return
    logger.debug(f"dob_str = {dob_str}")
    allergies_row = page.views[-1].controls[8].content
    allergies = [box.label for box in allergies_row.controls if box.value]
    logger.info(f"Collected user data: Name='{user_name}'; DOB='{dob_str}'; "
                f"Allergies='{allergies}'")
    # Check user does not already exist
    potential_user = get_user_details(user_name, id_type='name')
    logger.info(f"Tried to fetch user {user_name}, found {potential_user}")
    user_exists = potential_user is not None
    if user_exists:
        page.snack_bar = SnackBar(
            Text("That username is already chosen", color = "#000000",),
            bgcolor = WARN_COLOR
        )
        page.snack_bar.open = True
        page.update()
        return
    #Budle and do POST request
    data = {
        "name": user_name,
        "birthday": dob_str,
        "allergies": allergies
    }
    requests.post(
        url = f"{SERVER_URL}/employees/",
        data = json.dumps(data),
        headers = {'Content-type': 'application/json'}
    )
    #Switch to main cake dashboard
    new_user = get_user_details(user_name, id_type='name')
    usr_cache.write_text(json.dumps(new_user) + '\n')

    def press_ok(e):
        page.dialog.open = False
        page.update()
        page.go("/main")

    page.dialog = AlertDialog(
        title = Text("Success"),
        content= Text(
            f"Your user name is: {new_user['id']} \nUse it for your next login"
        ),
        actions = [TextButton("OK", on_click = press_ok)],
        on_dismiss = press_ok
    )
    page.dialog.open = True
    page.update()

def update_user_details(page):
    cached_user = json.loads(usr_cache.read_text())['id']
    current_data = get_user_details(cached_user)
    # Fetch allergen names from allergen objects to allow comparisons
    user_allergies = sorted([
        ingredient["name"].lower() for ingredient in current_data["allergies"]
    ])
    current_data["allergies"] = user_allergies
    logger.info(f"Fetched current data: {current_data}")
    # Retrieve data from UI Controls
    updateable_user_data = page.views[-1].controls[1].controls[1].controls
    new_user_name = updateable_user_data[0].content.value
    new_user_dob  = updateable_user_data[1].content.value
    new_user_allergies = sorted([
        ingredient.label.lower() 
        for ingredient in updateable_user_data[3].controls
        if ingredient.value # i.e. if checkbox checked
    ])
    logger.info(f"Updated details: Name={new_user_name}; DOB={new_user_dob}; "
                f"Allergies={new_user_allergies}")
    # Bundle and send PUT request
    updated_user_data = {
        "name"     : new_user_name,
        "birthday" : new_user_dob,
        "allergies": new_user_allergies
    }
    user_data_to_put = {
        k:v for k,v in updated_user_data.items()
        if k != "id" and v != current_data[k]
    }
    logger.info(f"Submitting data: {user_data_to_put}")
    # Early skip is no new data
    if user_data_to_put == {}:
        banner_text = Text("You have not modified any detail", color="#000000")
        page.snack_bar = SnackBar(banner_text, bgcolor = WARN_COLOR)
        page.snack_bar.open = True
        page.update()
        page.go('/main/user')
        return

    response = requests.put(
        url = f"{SERVER_URL}/employees/{cached_user}/update",
        data = json.dumps(user_data_to_put), #updated_user_data),
        headers = {'Content-type': 'application/json'}
    )
    # Notify user
    if response.ok:
        banner_text = Text("User details updated successfully",
                            color = "#000000")
        banner_bg_color = OK_COLOR
    else:
        try:
            logger.error(f"PUT request failed: {response.content}")
            response_content = json.loads(response.content.decode())
            error_msg = response_content['detail'][0]['msg']
            error_msg = (error_msg if len(error_msg) < 50 
                        else f"{error_msg[:45]}...")
        except:
            error_msg = "Could not retrieve error msg"
        banner_text = Text(
            f"ERROR: Details could not be updated. Cause: '{error_msg}'", 
            color = "#000000"
        )
        banner_bg_color = WARN_COLOR
    page.snack_bar = SnackBar(banner_text, bgcolor = banner_bg_color)
    page.snack_bar.open = True
    page.update()
    page.go('/main/user')

def delete_user(page):

    def reply_no(e):
        alert_dialog.open = False
        page.update()

    def reply_yes(e):
        alert_dialog.open = False
        page.update()
        cached_user = json.loads(usr_cache.read_text())['id']
        response = requests.delete(f"{SERVER_URL}/employees/{cached_user}")
        if response.ok:
            logger.info("User has been deleted")
        else:
            logger.error(f"User could not be deleted: {response.content}")
        page.go("/login")
    
    alert_dialog = AlertDialog(
        title = Text("WARNING"),
        content= Text(
            "This profile will be deleted from MutualCake.\n"
            "Are you sure you want to proceed?"
        ),
        actions = [
            TextButton("Yes", on_click = reply_yes),
            TextButton("No", on_click = reply_no),
        ],
    )
    page.dialog = alert_dialog
    alert_dialog.open = True
    page.update()

def choose_new_partner(page):
    user_id = json.loads(usr_cache.read_text())['id']
    new_partner_id = page.views[-1].controls[2].content.value
    logger.info(f"New partner id: {new_partner_id}")
    new_partner = get_user_details(new_partner_id)
    logger.info(f"New partner info: {new_partner}")
    response = requests.put(
        f"{SERVER_URL}/employees/{user_id}/new_patner/{new_partner_id}"
    )
    if response.ok:
        logger.info("New partner has been selected")
        txt = Text("New partner chosen", color = "#000000")
        bg_color = OK_COLOR
    else:
        logger.error(f"New partner could not be set: {response.content}")
        txt = Text(f"Could not change partner: {response.content}",
                     color = "#000000")
        bg_color = WARN_COLOR
    page.snack_bar = SnackBar(txt, bgcolor = bg_color)
    page.snack_bar.open = True
    page.update()

def choose_new_cake(page):
    user_id = json.loads(usr_cache.read_text())['id']
    new_cake_id = page.views[-1].controls[2].content.value
    logger.info(f"New partner id: {new_cake_id}")
    response = requests.put(
        f"{SERVER_URL}/employees/{user_id}/new_cake/{new_cake_id}"
    )
    if response.ok:
        logger.info("New cake has been selected")
        txt = Text("New cake chosen", color = "#000000")
        bg_color = OK_COLOR
    else:
        logger.error(f"New cake could not be set: {response.content}")
        txt = Text(f"Could not change cake: {response.content}",
                     color = "#000000")
        bg_color = WARN_COLOR
    page.snack_bar = SnackBar(txt, bgcolor = bg_color)
    page.snack_bar.open = True
    page.update()

def submit_cake(page):
    # Read from GUI
    gui_cake_data = page.views[-1].controls
    cake_name   = gui_cake_data[3].content.value
    cake_descr  = gui_cake_data[5].content.value
    cake_ingredients = [
        ingredient.label for ingredient in gui_cake_data[7].content.controls
        if ingredient.value # i.e. if checkbox checked
    ]
    # Bundle
    new_cake_data = {
        "name"               : cake_name,
        "previewDescription" : cake_descr,
        "ingredients"        : cake_ingredients,
    }
    logger.info(f"Collected cake data: Name='{cake_name}'; Descr= "
                f"'{cake_descr}'; Ingredients='{cake_ingredients}'")
    # POST
    requests.post(
        url = f"{SERVER_URL}/cakes/",
        data = json.dumps(new_cake_data),
        headers = {'Content-type': 'application/json'}
    )
    # Notify
    page.snack_bar = SnackBar(
        Text("New cake recipe has been submitted!", color = "#000000"), 
        bgcolor = OK_COLOR,
    )
    page.snack_bar.open = True
    page.update()


# endregion

# region Request data from server -----------------------------------

def get_user_details(user_id, id_type='id'):
    if id_type == 'id':
        return requests.get(f"{SERVER_URL}/employees/{user_id}").json()
    if id_type == 'name':
        return requests.get(f"{SERVER_URL}/employees/name/{user_id}").json()

def get_assigned_employee(user_id=None):
    "Returns NAME of assigned employee"
    cached_user = json.loads(usr_cache.read_text())
    if user_id is None:
        user_id = cached_user['id']
    assigned_employee = requests.get(
        f"{SERVER_URL}/employees/{user_id}/assignments/employee"
    ).json()
    if assigned_employee is None:
        logger.info(f"User: {cached_user!s} has nobody to bake to!")
        return ("You have not been assigned to any employee.\n"
                "Click on 'Change partner' to choose one.")
    return assigned_employee

def format_partner_w_birthday(user_name:str):
    partner_details = get_user_details(user_name, id_type='name')
    next_bday, days_to_go = guess_next_birthday(partner_details['birthday'])
    next_bday_formatted = (
        f"{user_name}\n"
         "    on...\n"
        f"{next_bday}\n\n"
        f"({days_to_go} days to go!)"
    )
    return next_bday_formatted

def get_baker_for_employee(user_id=None):
    "Returns NAME of the employee who is baking a cake for `user_id`"
    cached_user = json.loads(usr_cache.read_text())
    if user_id is None:
        user_id = cached_user['id']
    baker_for_employee = requests.get(
        f"{SERVER_URL}/employees/{user_id}/assignments/baker"
    ).json()
    if baker_for_employee is None:
        logger.info(f"User: {cached_user!s} has nobody to bake to!")
    return baker_for_employee

def get_assigned_cake(details = False):
    cached_user = json.loads(usr_cache.read_text())
    url_base = f"{SERVER_URL}/employees/{cached_user['id']}/assignments/cake"
    url = f"{url_base}/details" if details else url_base
    assigned_cake = requests.get(url).json()
    if assigned_cake is None:
        logger.info(f"User: {cached_user!s} has nothing to bake!")
        if details:
            return
        return ("You have not chosen any cake.\n"
                "Click on 'Change cake' to choose one.")
    logger.info(f"User: {cached_user!s} is baking {assigned_cake}")
    return assigned_cake

def get_all_ingredients():
    return requests.get(url = f"{SERVER_URL}/ingredients/all").json()

def get_all_employees():
    return requests.get(url = f"{SERVER_URL}/employees/all").json()

def get_all_cakes():
    return requests.get(url = f"{SERVER_URL}/cakes/all").json()

# endregion

# region Utils ------------------------------------------------------

def clear_cache(e):
    usr_cache.unlink()

def check_allergens_in_cake(page):
    cake_to_bake    = get_assigned_cake(details=True)
    logging.info(f"The cake to bake is {cake_to_bake}")
    birthday_person = get_assigned_employee()
    bday_person_details = get_user_details(birthday_person, id_type='name')
    logging.info(f"The recipient is {bday_person_details}")
    if not (cake_to_bake or birthday_person or bday_person_details['allergies']):
        logging.info(f"No allergies to check")
        return
    allergies = {x['name'].lower() for x in bday_person_details['allergies']}
    ingredients = {x['name'].lower() for x in cake_to_bake['ingredients']}
    logging.info(f"allergies: {allergies} vs ingredients: {ingredients}")
    
    if len(allergies & ingredients) > 0:
        logger.warn(f"User {birthday_person} is allergic to {allergies & ingredients}")
        page.snack_bar = SnackBar(
            content=Text(
                "The cake you selected contains ingredient(s) to which "
                f"{birthday_person} is allergic: {allergies & ingredients}."
            ),
            action="Change cake", 
            on_action=lambda _: page.go("/main/change-cake"),
            bgcolor = DANGER_COLOR
        )
        page.snack_bar.open = True
        page.update()

def format_cake_label(cake, current_cake, partner_allergies):
    if cake['name'] == current_cake:
        return f"[Yours] {cake['name']}"
    if any([x['name'] in partner_allergies for x in cake['ingredients']]):
        return f"[ALLERGEN] {cake['name']}"
    return  cake['name']

def format_employee_label(emp):
    has_no_baker = get_baker_for_employee(emp['id']) is None
    button =   "🟢"  if has_no_baker else "🔴" 
    name = emp['name']
    allergies = (
        f"(Allergic to: "
        f"{emp['allergies'] if emp['allergies'] else 'Nothing'})"
    )
    return f"{button}    {name} {allergies}"

def guess_next_birthday(dob):
    """Use datetime's '%j' format to guess when the next birthday is
    
    %j: Day of the year as a zero-padded decimal number (001, 002, ... 365)"""
    this_year = date.today().year
    dob_dt = datetime.strptime(dob, "%Y-%m-%d")
    dob_day_of_year = int(dob_dt.strftime("%j"))
    today_day_of_year = int(datetime.now().strftime("%j"))
    next_bday_year = (this_year + 1
                      if today_day_of_year > dob_day_of_year 
                      else this_year)
    next_bday = date(year = next_bday_year, month = dob_dt.month, day=dob_dt.day)
    timedelta = (next_bday - date.today()).days
    return next_bday, timedelta

# endregion


flet.app(target=main, assets_dir = "assets")