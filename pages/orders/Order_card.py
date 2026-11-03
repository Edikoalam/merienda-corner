from datetime import datetime

import flet as ft

BG = "#fff8e5"
BROWN = "#894e3f"
OLIVE = "#7c994d"
TEXT = "#4A3525"
TEXT_SOFT = "#8B5A2B"
GREY = "#4a4d52"
FONT_BOLD = "Poppins-Bold"

ORDER_STATUSES = ["PENDING", "DONE", "CANCELLED"]

STATUS_COLORS = {
    "PENDING": ft.Colors.ORANGE_700,
    "DONE": ft.Colors.GREEN_700,
    "CANCELLED": ft.Colors.RED_700,
}


def soft_shadow():
    return ft.BoxShadow(
        spread_radius=0,
        blur_radius=4,
        color="#50000000",
        offset=ft.Offset(0, 1),
    )


def fmt_date(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d").strftime("%b. %d, %Y").upper()
    except (TypeError, ValueError):
        return value or ""


def hover(e):
    is_hovered = e.data in ("true", True)
    e.control.bgcolor = "#f0f0f0" if is_hovered else "#ffffff"
    e.control.update()


def order_card(order, index, on_edit, on_status):
    status = (order["status"] or "PENDING").upper()

    status_menu = ft.PopupMenuButton(
        content=ft.Container(
            content=ft.Row(
                [
                    ft.Text(
                        value=status,
                        size=14,
                        color=STATUS_COLORS.get(status, GREY),
                        weight=ft.FontWeight.BOLD,
                        font_family=FONT_BOLD,
                    ),
                    ft.Icon(ft.Icons.ARROW_DROP_DOWN, size=23, color=GREY),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                spacing=2,
            ),
            bgcolor=ft.Colors.WHITE,
            width=100,
            height=24,
            border_radius=15,
            padding=ft.Padding.symmetric(horizontal=10),
            shadow=soft_shadow(),
        ),
        items=[
            ft.PopupMenuItem(
                content=ft.Text(option),
                on_click=lambda e, option=option: on_status(index, option),
            )
            for option in ORDER_STATUSES
        ],
    )

    header = ft.Row(
        controls=[
            ft.Text(
                f"ORDER {order['id']:03d}",
                weight=ft.FontWeight.BOLD,
                font_family=FONT_BOLD,
                size=22,
                color=BG,
            ),
            ft.Row(
                controls=[
                    ft.Container(
                        content=ft.Text(
                            "EDIT",
                            color=GREY,
                            weight=ft.FontWeight.BOLD,
                            font_family=FONT_BOLD,
                            size=15,
                        ),
                        alignment=ft.Alignment.CENTER,
                        height=25,
                        width=50,
                        bgcolor="#ffffff",
                        border_radius=ft.BorderRadius.all(20),
                        shadow=soft_shadow(),
                        on_hover=hover,
                        on_click=lambda e: on_edit(index),
                        animate=ft.Animation(150, ft.AnimationCurve.EASE_OUT),
                    ),
                    status_menu,
                ],
                spacing=5,
            ),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    )

    product_rows = [
        ft.Row(
            controls=[
                ft.Text(
                    item["p_name"],
                    color=BROWN,
                    size=15,
                    weight=ft.FontWeight.W_500,
                ),
                ft.Text(
                    str(item["quantity"]),
                    color=BROWN,
                    size=15,
                    weight=ft.FontWeight.BOLD,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )
        for item in order["items"]
    ]

    body = ft.Column(
        controls=[
            ft.Text(
                order["c_name"],
                weight=ft.FontWeight.BOLD,
                size=20,
                color=TEXT,
            ),
            ft.Column(controls=product_rows, spacing=0),
            ft.Text(order["address"], color=TEXT, size=14),
            ft.Row(
                controls=[
                    ft.Text(fmt_date(order["order_date"]), color=TEXT_SOFT, size=13),
                    ft.Text(order["order_time"], color=TEXT_SOFT, size=13),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            ft.Row(
                controls=[
                    ft.Text(
                        str(order["total"] or 0),
                        weight=ft.FontWeight.BOLD,
                        size=15,
                        color=TEXT_SOFT,
                    ),
                    ft.Text(
                        (order["order_type"] or "").upper(),
                        color=TEXT_SOFT,
                        size=13,
                        italic=True,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
        ],
        spacing=2,
    )

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Container(
                    content=header,
                    bgcolor=OLIVE,
                    padding=ft.Padding.symmetric(horizontal=12, vertical=7),
                    border_radius=0,
                ),
                ft.Container(
                    content=body,
                    bgcolor=ft.Colors.WHITE,
                    margin=ft.Margin.only(left=15),
                    padding=ft.Padding.only(left=10, right=10),
                    border_radius=ft.BorderRadius.only(
                        bottom_left=10, bottom_right=10
                    ),
                    border=ft.Border.only(
                        left=ft.BorderSide(2, OLIVE),
                        right=ft.BorderSide(2, OLIVE),
                        bottom=ft.BorderSide(2, OLIVE),
                    ),
                ),
            ],
            spacing=0,
        ),
        width=340,
    )