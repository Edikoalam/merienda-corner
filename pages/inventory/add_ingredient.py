from datetime import datetime

import flet as ft

BROWN = "#894e3f"
LIGHT_BROWN = "#c37960"
CREAM = "#fff8e5"
ROW_BG = "#fdeccb"

UNITS = ["KG", "G", "L", "ML", "PCS"]


def box_field(hint, width, trailing=None, **kw):
    field = ft.TextField(
        hint_text=hint,
        hint_style=ft.TextStyle(size=6.5, color="#b9a58f", font_family="Poppins"),
        text_size=7,
        color="#4A3525",
        border=ft.InputBorder.NONE,
        dense=True,
        content_padding=ft.Padding.symmetric(horizontal=0, vertical=0),
        height=13,
        expand=True,
        **kw,
    )
    controls = [field] + ([trailing] if trailing else [])
    box = ft.Container(
        width=width,
        height=14,
        bgcolor="white",
        border=ft.Border.all(1, LIGHT_BROWN),
        border_radius=3,
        padding=ft.Padding.symmetric(horizontal=4),
        alignment=ft.Alignment.CENTER_LEFT,
        content=ft.Row(
            spacing=2,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=controls,
        ),
    )
    return field, box


def form_row(label, *controls):
    return ft.Row(
        spacing=3,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Text(
                label,
                size=7,
                color=BROWN,
                weight=ft.FontWeight.BOLD,
                font_family="Poppins-Bold",
            ),
            *controls,
        ],
    )


def create_add_ingredient(page, on_confirm, snack):
    def pick_date(e):
        def on_change(ev):
            if ev.control.value:
                expiry_field.value = ev.control.value.strftime("%m/%d/%Y")
                expiry_field.update()

        page.show_dialog(
            ft.DatePicker(
                first_date=datetime(2020, 1, 1),
                last_date=datetime(2100, 12, 31),
                on_change=on_change,
            )
        )

    name_field, name_box = box_field("Cocoa Powder", 110)
    unit_field, unit_box = box_field("0", 24)
    qty_field, qty_box = box_field("0", 24, keyboard_type=ft.KeyboardType.NUMBER)
    expiry_field, expiry_box = box_field(
        "mm/dd/yy",
        70,
        trailing=ft.Container(
            content=ft.Icon(ft.Icons.CALENDAR_MONTH, size=9, color=BROWN),
            on_click=pick_date,
        ),
        read_only=True,
    )

    unit_text = ft.Text(
        "KG",
        size=7,
        color=BROWN,
        weight=ft.FontWeight.BOLD,
        font_family="Poppins-Bold",
    )

    def set_unit(unit):
        unit_text.value = unit
        unit_text.update()

    unit_menu = ft.PopupMenuButton(
        content=ft.Row(
            spacing=1,
            tight=True,
            controls=[
                unit_text,
                ft.Icon(
                    ft.Icons.ARROW_DROP_DOWN_CIRCLE_OUTLINED, size=9, color=BROWN
                ),
            ],
        ),
        padding=0,
        items=[
            ft.PopupMenuItem(
                content=ft.Text(unit), on_click=lambda e, unit=unit: set_unit(unit)
            )
            for unit in UNITS
        ],
    )

    def close_card(e=None):
        overlay.visible = False
        overlay.update()

    def open_card(e=None):
        name_field.value = ""
        unit_field.value = ""
        qty_field.value = ""
        expiry_field.value = ""
        unit_text.value = "KG"
        name_box.border = ft.Border.all(1, LIGHT_BROWN)
        overlay.visible = True
        overlay.update()

    def date_db_format(date):
        if date == '':
                return ''
        else:
            date_dt = datetime.strptime(date, "%m/%d/%Y" )
            return str(date_dt.strftime("%Y-%m-%d"))
    
    def confirm_new(e):
        name = (name_field.value or "").strip().upper()
        if not name:
            name_box.border = ft.Border.all(1.5, ft.Colors.RED_700)
            name_box.update()
            return
        try:
            qty = int(qty_field.value or 0)
        except ValueError:
            qty = 0
        unit = (unit_field.value or "").strip()
        unit_value = f"{unit}{unit_text.value}" 
        on_confirm(
            {
                "name": name,
                "unit": unit_value,
                "quantity": qty,
                "expiration_date": date_db_format(expiry_field.value) or "--",
            }
        )
        close_card()

    card = ft.Container(
        width=262,
        bgcolor=CREAM,
        border=ft.Border.all(1.5, LIGHT_BROWN),
        border_radius=12,
        padding=ft.Padding.only(left=12, right=12, top=6, bottom=12),
        shadow=ft.BoxShadow(
            blur_radius=10, color="#40000000", offset=ft.Offset(0, 2)
        ),
        content=ft.Column(
            spacing=4,
            tight=True,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Text(
                            "ADD NEW INGREDIENT",
                            size=13,
                            font_family="Poppins-Bold",
                            weight=ft.FontWeight.BOLD,
                            color=BROWN,
                        ),
                        ft.IconButton(
                            ft.Icons.CLOSE,
                            icon_size=16,
                            icon_color=BROWN,
                            padding=0,
                            width=22,
                            height=22,
                            on_click=close_card,
                        ),
                    ],
                ),
                ft.Row(
                    spacing=8,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    controls=[
                        ft.Container(
                            width=58,
                            height=58,
                            border=ft.Border.all(1, LIGHT_BROWN),
                            border_radius=6,
                            bgcolor=ROW_BG,
                            alignment=ft.Alignment.CENTER,
                            content=ft.Icon(
                                ft.Icons.ADD_PHOTO_ALTERNATE, size=26, color=BROWN
                            ),
                            on_click=lambda e: snack("Image upload coming soon"),
                            ink=True,
                        ),
                        ft.Column(
                            spacing=2,
                            tight=True,
                            controls=[
                                ft.Text(
                                    "Ingredient Name:",
                                    size=7,
                                    color=BROWN,
                                    weight=ft.FontWeight.BOLD,
                                    font_family="Poppins-Bold",
                                ),
                                name_box,
                                form_row("Unit Measurement:", unit_box, unit_menu),
                                form_row("Initial Quantity:", qty_box),
                                form_row("Expiry Date:", expiry_box),
                            ],
                        ),
                    ],
                ),
                ft.Container(
                    height=1,
                    bgcolor=LIGHT_BROWN,
                    margin=ft.Margin.only(top=4, bottom=4),
                ),
                ft.Container(
                    alignment=ft.Alignment.CENTER,
                    content=ft.Container(
                        width=198,
                        height=24,
                        bgcolor=LIGHT_BROWN,
                        border_radius=6,
                        alignment=ft.Alignment.CENTER,
                        on_click=confirm_new,
                        ink=True,
                        content=ft.Text(
                            "CONFIRM NEW INGREDIENT",
                            color=CREAM,
                            size=9.5,
                            font_family="Poppins-Bold",
                            weight=ft.FontWeight.BOLD,
                        ),
                    ),
                ),
            ],
        ),
    )

    overlay = ft.Container(
        visible=False,
        expand=True,
        alignment=ft.Alignment(0, 0.27),
        content=card,
    )



    return overlay, open_card, close_card