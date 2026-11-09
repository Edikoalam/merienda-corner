import flet as ft

BROWN = "#894e3f"
LIGHT_BROWN = "#c37960"
CREAM = "#fff8e5"
ROW_BG = "#fdeccb"
TEXT_DARK = "#4a4d52"
TAN = "#c9b57a"

W_NAME, W_QTY, W_LEFT, W_DATE, W_EXP, W_MENU = 100, 29, 42, 58, 75, 28


def round_button(icon, on_click, filled):
    return ft.Container(
        width=11,
        height=11,
        border_radius=6,
        bgcolor="#e0b84a" if filled else CREAM,
        border=None if filled else ft.Border.all(1, TAN),
        alignment=ft.Alignment.CENTER,
        content=ft.Icon(icon, size=8, color=CREAM if filled else TAN),
        on_click=on_click,
        ink=True,
    )


def header_cell(text, width, alignment=ft.Alignment.CENTER_LEFT, left=0):
    return ft.Container(
        width=width,
        alignment=alignment,
        padding=ft.Padding.only(left=left),
        content=ft.Text(
            text,
            size=9,
            color=LIGHT_BROWN,
            weight=ft.FontWeight.BOLD,
            font_family="Poppins-Bold",
        ),
    )


def inventory_header():
    return ft.Container(
        height=12,
        padding=ft.Padding.symmetric(horizontal=4),
        content=ft.Row(
            spacing=0,
            controls=[
                header_cell("INGREDIENTS", 147),
                header_cell("QTY.", 32),
                header_cell("LEFT", 55),
                header_cell("EXP. DATE", 65, ft.Alignment.CENTER),
                ft.Container(width=28),
            ],
        ),
    )


def inventory_card(item, on_consume, on_restock, open_card):
    return ft.Container(
        bgcolor=ROW_BG,
        border_radius=3,
        height=24,
        padding=ft.Padding.symmetric(horizontal=4),
        shadow=ft.BoxShadow(
            blur_radius=2, color="#20000000", offset=ft.Offset(0, 1)
        ),
        content=ft.Row(
            spacing=0,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    width=130,
                    content=ft.Text(
                        item["name"] + " " + item["unit"],
                        size=9,
                        color=BROWN,
                        weight=ft.FontWeight.BOLD,
                        font_family="Poppins-Bold",
                        overflow=ft.TextOverflow.ELLIPSIS,
                        max_lines=1,
                    ),
                ),
                ft.Container(
                    width=108,
                    content=ft.Row(
                        spacing=3,
                        alignment=ft.MainAxisAlignment.CENTER,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Container(
                                width=20,
                                alignment=ft.Alignment.CENTER,
                                content=round_button(
                                    ft.Icons.REMOVE,
                                    lambda e: on_consume(item),
                                    True,
                                ),
                            ),
                            ft.Container(
                                width=30,
                                alignment=ft.Alignment.CENTER,
                                content=ft.Text(
                                    str(item["quantity"]),
                                    size=10,
                                    color=BROWN,
                                    weight=ft.FontWeight.BOLD,
                                    font_family="Poppins-Bold",
                                ),
                            ),
                            ft.Container(
                                width=20,
                                alignment=ft.Alignment.CENTER,
                                content=round_button(
                                    ft.Icons.ADD, lambda e: on_restock(item), False
                                ),
                            ),
                        ],
                    ),
                ),
                
                ft.Container(
                    width=65,
                    alignment=ft.Alignment.CENTER,
                    content=ft.Text(
                        item["expiry"],
                        size=9,
                        color="#8B5A2B",
                        font_family="Poppins",
                    ),
                ),
                ft.Container(
                    width=28,
                    alignment=ft.Alignment.CENTER,
                    content=ft.IconButton(
                        icon=ft.Icons.MORE_HORIZ, 
                        scale=0.8, 
                        padding=0,
                        on_click=lambda e: open_card(item, on_consume, on_restock), 
                    ),
                ),
            ],
        ),
    )