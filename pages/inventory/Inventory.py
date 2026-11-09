import flet as ft

from pages.inventory.add_ingredient import create_add_ingredient
from pages.inventory.inventory_card import inventory_card, inventory_header
from pages.inventory.confirmations import add_confirmation_tabs
from pages.inventory.edit_card import create_edit_card
from db import (get_connection, 
                get_inventory_list, 
                update_qty, 
                delete_ingredient, 
                add_ingredient)

BROWN = "#894e3f"
LIGHT_BROWN = "#c37960"
CREAM = "#fff8e5"
TEXT_DARK = "#4a4d52"

TITLE_FONT = "Anton"


def pill_button(text, width, on_click):
    return ft.Container(
        width=width,
        height=50,
        bgcolor=LIGHT_BROWN,
        border_radius=8,
        alignment=ft.Alignment.CENTER,
        shadow=ft.BoxShadow(blur_radius=2, color=ft.Colors.BLACK_45),
        on_click=on_click,
        ink=True,
        content=ft.Text(
            text,
            color=CREAM,
            size=10,
            font_family="Poppins-Bold",
            weight=ft.FontWeight.BOLD,
        ),
    )


def build(app):
    inventory = []

    def get_latest_expiry(batch):
            latest = batch[0]["expiration_date"]
            for i in range(len(batch)-1):
                if batch[i]["expiration_date"] > batch[i+1]["expiration_date"]:
                    latest= batch[i+1]["expiration_date"]
            return latest

    def get_inventory():
        conn = get_connection()
        
        inventory[:] = get_inventory_list(conn)
        for inv in inventory:
            inv["expiry"] = get_latest_expiry(inv["batches"])
        
        conn.close()
        return inventory

    def snack(message):
        app.page.show_dialog(ft.SnackBar(ft.Text(message), bgcolor=BROWN))

    rows_column = ft.Column(spacing=2, scroll=ft.ScrollMode.AUTO, expand=True)

    def show_rows(update=True):
        query = (search_field.value or "").lower()

        rows_column.controls = [
            inventory_card(item, consume, restock, open_edit_card)
            for item in inventory
            if query in item["name"].lower()
        ]
        if update:
            rows_column.update()


    confirm_overlay, delete_confirmation = add_confirmation_tabs()

    def consume(item):
        print("consume")
        if item["quantity"] <= 0:
            return
        if item["quantity"] == 1:
            delete_confirmation(
                "delete this ingredient?",
                lambda: remove_ingredient(item),
            )
            return
        item["quantity"] -= 1
        show_rows()
        

    def remove_ingredient(item):
        con = get_connection()
        try:
            delete_ingredient(con, item["ingredient_id"])
        finally:
            con.close()
        close_edit_card()
        get_inventory()
        show_rows()

    def restock(item):
        item["quantity"] += 1
        show_rows()

    def delete_item(item):
        inventory.remove(item)
        show_rows()
        snack(f"{item['name']} removed")

    def add_item(item):
        con = get_connection()
        name, unit, quantity, expiry, img = item["name"], item["unit"], item["quantity"], item["expiration_date"], item["img"]
        try:
            add_ingredient(con, name, unit, quantity, expiry, img)
        finally:
            con.close()
        get_inventory()
        show_rows()

    add_ingre_overlay, open_card, close_card = create_add_ingredient(
        app.page, add_item, snack
    )

    add_edit_overlay, open_edit_card, close_edit_card = create_edit_card(snack, app.page, get_inventory, show_rows)


    search_field = ft.TextField(
        hint_text="Search Ingredients...",
        hint_style=ft.TextStyle(size=8, color="#3b2a22", font_family="Poppins", weight=ft.FontWeight.BOLD),
        text_size=9,
        text_style=ft.TextStyle(
            weight=ft.FontWeight.BOLD,
            size=11,
        ),
        border=ft.InputBorder.NONE,
        dense=True,
        content_padding=ft.Padding.symmetric(horizontal=0, vertical=0),
        height=14,
        expand=True,
        on_change=lambda e: show_rows(),
    )

    search_box = ft.Container(
        width=118,
        height=20,
        bgcolor="white",
        border_radius=9,
        padding=ft.Padding.symmetric(horizontal=7),
        shadow=ft.BoxShadow(
            blur_radius=3, color="#30000000", offset=ft.Offset(0, 1)
        ),
        content=ft.Row(
            spacing=4,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Icon(ft.Icons.SEARCH, size=10, color=TEXT_DARK),
                search_field,
            ],
        ),
    )

    title_block = ft.Container(
        height=110,
        padding=ft.Padding.only(left=32, right=30, top=26),
        content=ft.Stack(
            controls=[
                ft.Text(
                    "Ingredients",
                    size=18,
                    font_family="Poppins-Bold",
                    weight=ft.FontWeight.BOLD,
                    color=BROWN,
                    top=0,
                    left=0,
                ),
                ft.Text(
                    "INVENTORY",
                    size=56,
                    font_family=TITLE_FONT,
                    weight=ft.FontWeight.BOLD,
                    color=BROWN,
                    style=ft.TextStyle(height=1.0),
                    top=17,
                    left=0,
                ),
                ft.Container(
                    top=68,
                    left=2,
                    content=ft.Text(
                        "Manage inventory and consumption.",
                        size=10,
                        color=BROWN,
                        font_family="Poppins",
                    ),
                ),
                ft.Container(top=65, right=0, content=search_box),
            ],
        ),
    )

    title_divider = ft.Container(
        height=1, bgcolor="#eadcb8", margin=ft.Margin.only(top=-1)
    )

    def save_qty(inventory):
        conn = get_connection()
        for inv in inventory:
            update_qty(conn, inv["ingredient_id"], inv["quantity"])
        conn.close()
        snack("Changes saved")
        show_rows()

    action_row = ft.Container(
        height=20,
        margin=ft.Margin.only(top=6, bottom=4),
        padding=ft.Padding.symmetric(horizontal=30),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                pill_button("+ ADD INGREDIENT", 116, open_card),
                pill_button("SAVE CHANGES", 100, lambda e: save_qty(inventory)),
            ],
        ),
    )

    bottom_line = ft.Container(
        height=58,
        alignment=ft.Alignment.CENTER,
        content=ft.Container(width=230, height=1, bgcolor="#e5d6b0"),
    )

    main_content = ft.Column(
        spacing=0,
        expand=True,
        controls=[
            title_block,
            title_divider,
            action_row,
            ft.Container(
                expand=True,
                padding=ft.Padding.symmetric(horizontal=20),
                content=ft.Column(
                    spacing=3,
                    expand=True,
                    controls=[inventory_header(), rows_column],
                ),
            ),
            bottom_line,
        ],
    )

    view = ft.Stack(expand=True, controls=[main_content, add_ingre_overlay, add_edit_overlay,confirm_overlay,])

    show_rows(update=False)

    def on_show():
        close_card()
        get_inventory()
        show_rows()

    return view, on_show