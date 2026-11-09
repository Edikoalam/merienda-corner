from datetime import datetime, timedelta

import flet as ft

from db import (
    get_connection,
    get_menu,
    update_order,
    update_status,
    get_history_by_date_range,
    order_history
)
from pages.orders.Order_card import order_card
from pages.orders.Order_popup import create_popup

BG = "#fff8e5"
BROWN = "#894e3f"
GREEN = "#3a7f2c"
GREEN_HOVER = "#1C750A"
ROSE = "#c37960"
ROSE_HOVER = "#ac5133"
FONT_TITLE = "Anton"
FONT = "Poppins"


now = datetime.now()
future_date = datetime.now() + timedelta(days=15)

def build(app):
    queue = []
    mode = {"start": now.strftime("%Y-%m-%d"), "end" : future_date.strftime("%Y-%m-%d")}
    

    def product_names():
        conn = get_connection()
        try:
            return [row["p_name"] for row in get_menu(conn)]
        finally:
            conn.close()

    def load_queue(daterange = None, update=True):
        conn = get_connection()
        if not daterange:
            try:
                queue[:] = order_history(conn)
                                            
            finally:
                conn.close()
                orders_column.controls = [
                    order_card(order, i, edit_order, change_status, True)
                    for i, order in enumerate(queue)
                ]
        else:
            try:
                print('bat history')
                queue[:] = get_history_by_date_range(conn, mode["start"], mode["end"])
                                
            finally:
                conn.close()
            orders_column.controls = [
                order_card(order, i, edit_order, change_status)
                for i, order in enumerate(queue)
            ]
        
        print(queue)
        if update:
            orders_column.update()

    def edit_order(index):
        open_popup(index, queue[index])

    def change_status(index, status):
        conn = get_connection()
        try:
            update_status(conn, queue[index]["id"], status)
        finally:
            conn.close()
        load_queue()

    def save_order(index, data):
        conn = get_connection()
        print("save_order:", index, data)
        try:
            menu = {row["p_name"]: row for row in get_menu(conn)}
            items = [
                item
                for item in data["items"]
                if item["quantity"] > 0 and item["p_name"] in menu
            ]
            if not items:
                return "Add at least one product"
            pairs = [(menu[i["p_name"]]["id"], i["quantity"]) for i in items]
            total = sum(
                menu[i["p_name"]]["price"] * i["quantity"] for i in items
            )

            order = queue[index]
            error = update_order(
                    conn,
                    order["id"],
                    data["c_name"],
                    data["status"] or order["status"],
                    data["order_type"],
                    data["address"],
                    order["order_time"],
                    order["order_date"],
                    total,
                    pairs,
            )
            print(name for name in order["c_name"] )
            if error:
                return error
        finally:
            conn.close()
        load_queue()

    overlay, open_popup, close_popup = create_popup(app.stack, product_names, save_order)

    def handle_change(e: ft.Event[ft.DatePicker]):
        print("handled")
        start_date = e.control.start_value + datetime.now().astimezone().utcoffset()
        end_date = e.control.end_value + datetime.now().astimezone().utcoffset()
        mode["start"] = start_date.strftime("%Y-%m-%d")
        mode["end"] = end_date.strftime("%Y-%m-%d")                
        load_queue("date")
    
    orders_column = ft.Column(
        spacing=5,
        scroll=ft.ScrollMode.AUTO,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    picker = ft.DateRangePicker(
        start_value=now,
        end_value=future_date,
        first_date=datetime(year=now.year - 1, month=1, day=1),
        last_date=datetime(year=now.year + 1, month=now.month, day=20),
        on_change=lambda e : handle_change(e), 
    )

    view = ft.Stack(
        expand=True,
        controls=[
            ft.Column(
                alignment=ft.MainAxisAlignment.START,
                expand=True,
                spacing=0,
                controls=[
                    ft.Container(
                        alignment=ft.Alignment.TOP_LEFT,
                        height=55,
                        padding=ft.Padding.only(left=10),
                        content=ft.Text(
                            "ORDER HISTORY",
                            size=40,
                            weight=ft.FontWeight.W_600,
                            font_family=FONT_TITLE,
                            color=BROWN,
                        ),
                    ),
                    ft.Container(
                        height=50,
                        content=ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_AROUND,
                            controls=[
                                ft.Container(
                                    bgcolor=ROSE,
                                    height=40,
                                    width=200,
                                    border_radius=10,
                                    shadow=ft.BoxShadow(
                                        spread_radius=0.5,
                                        blur_radius=2,
                                        color=ft.Colors.BLACK_45,
                                    ),
                                    content=ft.TextButton(
                                        content="CHOOSE DATE RANGE",
                                        style=ft.ButtonStyle(
                                            color=BG,
                                            shape=ft.RoundedRectangleBorder(radius=10),
                                            bgcolor={
                                                ft.ControlState.DEFAULT: ROSE,
                                                ft.ControlState.HOVERED: ROSE_HOVER,
                                            },
                                            text_style={
                                                ft.ControlState.DEFAULT: ft.TextStyle(
                                                    font_family=FONT,
                                                    size=14,
                                                    weight=ft.FontWeight.BOLD,
                                                ),
                                                ft.ControlState.HOVERED: ft.TextStyle(
                                                    font_family=FONT,
                                                    weight=ft.FontWeight.BOLD,
                                                ),
                                            },
                                        ),
                                        icon=ft.Icons.CALENDAR_MONTH,
                                        icon_color=BG,
                                        on_click=lambda _: app.page.show_dialog(picker),
                                    ),
                                ),
                            ],
                        ),
                    ),
                    ft.Container(
                        alignment=ft.Alignment.TOP_CENTER,
                        content=orders_column,
                        expand=True,
                        bgcolor=BG,
                    ),
                ],
            ),
            overlay
        ]
    )

    def on_show():
        mode["range"] = "active"
        load_queue()

    return view, on_show