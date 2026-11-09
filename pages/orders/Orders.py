from datetime import datetime

import flet as ft

from db import (
    active_queue,
    add_order_items,
    get_connection,
    get_menu,
    insert_total,
    new_order,
    update_order,
    update_status,
    get_orders_by_specific_month,
    get_orders_by_specific_day
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

MONTHS = [
    "JAN",
    "FEB",
    "MAR",
    "APR",
    "MAY",
    "JUNE",
    "JULY",
    "AUG",
    "SEPT",
    "OCT",
    "NOV",
    "DEC",
]

now = datetime.now()

def build(app):
    queue = []
    month = {"active": MONTHS[datetime.now().month - 1]}
    mode = {"range": "active", "date": None}
    

    def product_names():
        conn = get_connection()
        try:
            return [row["p_name"] for row in get_menu(conn)]
        finally:
            conn.close()

    def load_queue(update=True):
        conn = get_connection()
        try:
            if mode["range"] == "active":
                queue[:] = active_queue(conn)
                print(item["c_name"] for item in queue)
            elif mode["range"] == "month":
                queue[:] = get_orders_by_specific_month(conn, MONTHS.index(month["active"])+1)
            elif mode["range"] == "specific":
                queue[:] = get_orders_by_specific_day(conn, mode["date"])
                
        finally:
            conn.close()
        orders_column.controls = [
            order_card(order, i, edit_order, change_status)
            for i, order in enumerate(queue)
        ]
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
            menu = get_menu(conn)
            items = [
                item
                for item in data["items"]
                if item["quantity"] > 0
            ]

            if not items:
                return "Add at least one product"
                
            total = 0
            for item in items:
                for product in menu:
                    if product['p_name'] == item["p_name"]:
                        total += product['price'] * item["quantity"]

            if index is None:
                order_id = new_order(
                    conn,
                    data["c_name"],
                    "PENDING",
                    data["order_type"],
                    data["address"],
                    now.strftime("%H:%M"),
                    now.strftime("%Y-%m-%d"),
                    data["type_date"],
                    data["type_time"]
                )
                if not isinstance(order_id, int):
                    return order_id or "Could not save the order"
                add_order_items(conn, order_id, items, menu)
                insert_total(conn, order_id, total)
            else:
                order = queue[index]
                error = update_order(
                    conn,
                    order["id"],
                    data["c_name"],
                    data["order_type"],
                    data["address"],
                    order["order_time"],
                    order["order_date"],
                    data["type_date"],
                    data["type_time"],
                    total,
                    items,
                    menu
                )
                print(name for name in order["c_name"] )
                if error:
                    return error
        finally:
            conn.close()
        load_queue()

    overlay, open_popup, close_popup = create_popup(app.page, product_names, save_order)

    def month_buttons():
        return [
            ft.Container(
                padding=ft.Padding.only(left=5),
                content=ft.TextButton(
                    key=name,
                    content=name,
                    on_click=month_selected,
                    style=ft.ButtonStyle(
                        color="White",
                        bgcolor=(
                            "white,0.40" if name == month["active"] else BROWN
                        ),
                        text_style={
                            ft.ControlState.DEFAULT: ft.TextStyle(
                                font_family=FONT
                            ),
                            ft.ControlState.HOVERED: ft.TextStyle(
                                font_family=FONT, weight=ft.FontWeight.BOLD
                            ),
                        },
                    ),
                ),
            )
            for name in MONTHS
        ]

    def month_selected(e):
        month["active"] = e.control.content
        months_row.controls = month_buttons()
        mode["range"] = "month"
        
        load_queue()
        months_row.update()

    def handle_change(e: ft.Event[ft.DatePicker]):
        print("handled")
        local_date = e.control.value + datetime.now().astimezone().utcoffset()
        mode["date"] = local_date.strftime("%Y-%m-%d")
        mode["range"] = "specific"
        load_queue()
    
    months_row = ft.Row(scroll=ft.ScrollMode.AUTO, controls=month_buttons())
    orders_column = ft.Column(
        spacing=5,
        scroll=ft.ScrollMode.AUTO,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    picker = ft.DatePicker(
        first_date=datetime(year=now.year - 1, month=1, day=1),
        last_date=datetime(year=now.year + 1, month=now.month, day=20),
        current_date=now,
        on_change=handle_change, 
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
                            "QUEUE ORDERS",
                            size=40,
                            weight=ft.FontWeight.W_600,
                            font_family=FONT_TITLE,
                            color=BROWN,
                        ),
                    ),
                    ft.Container(
                        height=40,
                        padding=ft.Padding.only(left=10, right=10),
                        bgcolor=BROWN,
                        content=months_row,
                    ),
                    ft.Container(
                        height=50,
                        content=ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_AROUND,
                            controls=[
                                ft.Container(
                                    bgcolor=GREEN,
                                    height=40,
                                    width=130,
                                    border_radius=10,
                                    shadow=ft.BoxShadow(
                                        spread_radius=0.5,
                                        blur_radius=2,
                                        color=ft.Colors.BLACK_45,
                                    ),
                                    content=ft.TextButton(
                                        content="New order",
                                        style=ft.ButtonStyle(
                                            color=BG,
                                            shape=ft.RoundedRectangleBorder(radius=10),
                                            bgcolor={
                                                ft.ControlState.DEFAULT: GREEN,
                                                ft.ControlState.HOVERED: GREEN_HOVER,
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
                                        icon=ft.Icons.ADD_BOX_OUTLINED,
                                        icon_color=BG,
                                        on_click=lambda e: open_popup(),
                                    ),
                                ),
                                ft.Container(
                                    bgcolor=ROSE,
                                    height=40,
                                    width=150,
                                    border_radius=10,
                                    shadow=ft.BoxShadow(
                                        spread_radius=0.5,
                                        blur_radius=2,
                                        color=ft.Colors.BLACK_45,
                                    ),
                                    content=ft.TextButton(
                                        content="Choose date",
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
        offset = MONTHS.index(month["active"]) * 70
        app.page.run_task(months_row.scroll_to, offset=offset, duration=500)

    return view, on_show