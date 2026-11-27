import flet as ft


def round_button(icon, on_click, filled):
    return ft.Container(
        width=11,
        height=11,
        border_radius=6,
        bgcolor="#e0b84a" if filled else "#fff8e5",
        border=None if filled else ft.Border.all(1, "#c9b57a"),
        alignment=ft.Alignment.CENTER,
        content=ft.Icon(icon, size=8, color="#fff8e5" if filled else "#c9b57a"),
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
            color="#c37960",
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
                ft.Container(expand=True, content=header_cell("INGREDIENTS", None)),
                header_cell("QTY.", 108, ft.Alignment.CENTER),
                header_cell("EXP. DATE", 65, ft.Alignment.CENTER),
                ft.Container(width=28),
            ],
        ),
    )


def inventory_card(item, on_consume, on_restock, open_card):
    return ft.Container(
        bgcolor="#fdeccb",
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
                    expand=True,
                    content=ft.Text(
                        item["name"] + " " + item["unit"],
                        size=9,
                        color="#894e3f",
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
                                    color="#894e3f",
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