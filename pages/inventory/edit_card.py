import flet as ft
from datetime import datetime
from pages.inventory.confirmations import add_confirmation_tabs
from db import (get_connection,
                update_qty,
                add_batch)

def date_format(date):
    if date == '':
        return ''
    else:
        date_dt = datetime.strptime(date, "%Y-%m-%d")
        return str(date_dt.strftime("%m/%d/%Y"))

def date_db_format(date):
    if date == '':
            return ''
    else:
        date_dt = datetime.strptime(date, "%m/%d/%Y" )
        return str(date_dt.strftime("%Y-%m-%d"))

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

def pill_button(text, width,height, size, color, round, on_click):
    return ft.Container(
        width=width,
        height=height,
        bgcolor=color,
        border_radius=round,
        alignment=ft.Alignment.CENTER,
        shadow=ft.BoxShadow(blur_radius=2, color=ft.Colors.BLACK_45),
        on_click=on_click,
        ink=True,
        content=ft.Text(
            text,
            color="#fff8e5",
            size=size,
            font_family="Poppins-Bold",
            weight=ft.FontWeight.BOLD,
        ),
    )

confirm_overlay, delete_confirmation = add_confirmation_tabs()

def create_edit_card(snack, page, get_inventory, show_rows):

    callbacks = {} 

    def close_edit_card(e=None):
        overlay.content.controls.clear()
        overlay.visible = False
        overlay.update()
        show_rows()

    def open_edit_card(item, on_consume,on_restock, e=None):
        print("open")
        overlay.content.controls.append(card(item, on_consume, on_restock))
        overlay.visible = True
        overlay.update()

    def card(item, on_consume, on_restock):
        print(item)
        callbacks["on_consume"] = on_consume
        callbacks["on_restock"] = on_restock
        selected_batch = 0

        def update_selected_batch(e, batch):
            nonlocal selected_batch
            selected_batch = batch
            batches.content.content.controls[0].value = batch
            batches.content.content.update()
        
        batches = ft.PopupMenuButton(
            content=ft.Container(
                margin=ft.Margin.only(top=2),
                content=ft.Row(
                    controls=[
                        ft.Text(
                            value=f"BATCH {selected_batch}",
                            size=7,
                            color="#894e3f",
                            weight=ft.FontWeight.BOLD,
                            font_family="Poppins-Bold",
                        ),
                        ft.Icon(ft.Icons.ARROW_DROP_DOWN, size=14, color="#894e3f"),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    spacing=2,
                ),
                bgcolor="#efd7a6",
                width=80,
                height=14,
                border_radius=15,
                padding=ft.Padding.symmetric(horizontal=10),
                shadow=ft.BoxShadow(
                    spread_radius=0,
                    blur_radius=4,
                    color="#50000000",
                    offset=ft.Offset(0, 1),
                ),
            ),
            items=[
                ft.PopupMenuItem(
                    content=ft.Text(batch),
                    on_click=lambda e, batch=f"BATCH {batch}" : update_selected_batch(e, batch),
                )
                for batch in range (len(item["batches"]))
            ],
        )

        batch_info = ft.Container(
            width=140,
            height=33,
            border_radius=4,
            bgcolor="#fff8e5",
            border=ft.Border.all(1, "#c37960"),
            margin=ft.Margin.only(top=5),
            content=ft.Column(
                spacing=0,
                tight=True,
                controls=[
                    ft.Row(
                        tight=True,
                        spacing=0,
                        controls= [
                            ft.Text(
                                "Date added: ",
                                size=9,
                                color="#894e3f",
                                font_family="Poppins",
                                margin=ft.Margin.only(left=4, top=2),
                            ),
                            ft.Text(
                                date_format(item['batches'][selected_batch]['purchase_date']),
                                size=9,
                                color="#894e3f",
                                font_family="Poppins-Bold",
                                weight=ft.FontWeight.BOLD,
                                margin=ft.Margin.only(top=2),
                            )
                        ]
                    ),
                    ft.Row(
                        tight=True,
                        spacing=0,
                        controls= [
                            ft.Text(
                                "Expiry: ",
                                size=9,
                                color="#894e3f",
                                font_family="Poppins",
                                margin=ft.Margin.only(left=4),
                            ),
                            ft.Text(
                                date_format(item['batches'][selected_batch]['expiration_date']),
                                size=9,
                                color="#dd433f",
                                font_family="Poppins-Bold",
                                weight=ft.FontWeight.BOLD,
                            )
                        ]
                    )
                ]
            )
        )
        
        
        qty_text = ft.Text(
            str(item["quantity"]),
            size=9,
            color="#894e3f",
            weight=ft.FontWeight.BOLD,
            font_family="Poppins-Bold",
        )

        def refresh():
            qty_text.value = str(item["quantity"])
            qty_text.update()

        def handle_consume(e):
            on_consume(item)
            refresh()

        def handle_restock(e):
            on_restock(item)
            refresh()

        def save_qty(e, item):
            conn = get_connection()
            update_qty(conn, item["ingredient_id"], item["quantity"])
            conn.close()
            snack("Quantity updated successfully")
            refresh()

        def handle_delete(e):
            item["quantity"] = 1
            on_consume(item)

        return ft.Container(
            width=280,
            bgcolor="#fff8e5",
            border=ft.Border.all(1.5, "#c37960"),
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
                                item["name"].upper(),
                                size=16,
                                font_family="Poppins-Bold",
                                weight=ft.FontWeight.BOLD,
                                color="#894e3f",
                            ),
                            ft.IconButton(
                                ft.Icons.CLOSE,
                                icon_size=16,
                                icon_color="#894e3f",
                                padding=0,
                                width=22,
                                height=22,
                                on_click=close_edit_card,
                            ),
                        ],
                    ),
                    ft.Row(
                        spacing=8,
                        vertical_alignment=ft.CrossAxisAlignment.START,
                        controls=[
                            ft.Column(
                                spacing=4,
                                tight=True,
                                controls=[
                                    ft.Container(
                                        width=90,
                                        height=90,
                                        border=ft.Border.all(1, "#c37960"),
                                        border_radius=6,
                                        bgcolor="#fdeccb",
                                        alignment=ft.Alignment.CENTER,
                                        content=ft.Icon(
                                            ft.Icons.ADD_PHOTO_ALTERNATE, size=26, color="#894e3f"
                                        ),
                                        on_click=lambda e: snack("Image upload coming soon"),
                                        ink=True,
                                    ),
                                    pill_button("DELETE ITEM", 90, 20, 10, "#8f0000", 3, lambda e: handle_delete(e)),
                                ]
                            ),
                            ft.Column(
                                spacing=1,
                                tight=True,
                                controls=[
                                    ft.Row(
                                        tight=True,
                                        spacing=0,
                                        controls=[
                                            ft.Text(
                                                "TOTAL STOCKS LEFT: ",
                                                font_family="Poppins-Bold",
                                                weight=ft.FontWeight.BOLD,
                                                size=11,
                                                color="#894e3f",
                                            ),
                                            ft.Text(
                                                str(item["quantity"]),
                                                font_family="Poppins-Bold",
                                                weight=ft.FontWeight.BOLD,
                                                size=11,
                                                color="#7c994d",
                                            ),
                                        ],
                                    ),
                                    ft.Row(
                                        tight=True,
                                        spacing=0,
                                        controls=[
                                            ft.Text(
                                                "LATEST EXPIRY:",
                                                font_family="Poppins-Bold",
                                                weight=ft.FontWeight.BOLD,
                                                size=11,
                                                color="#894e3f",
                                            ),
                                            ft.Text(
                                                date_format(item["expiry"]),
                                                font_family="Poppins",
                                                size=10,
                                                color="#dd433f",
                                            ),
                                        ],
                                    ),
                                    ft.Row(
                                        spacing=1,
                                        controls=[
                                            round_button(
                                                ft.Icons.REMOVE,
                                                lambda e: handle_consume(e),
                                                True,
                                            ),
                                            ft.Container(
                                                width=20,
                                                alignment=ft.Alignment.CENTER,
                                                border=ft.Border.all(1, "#c37960"),
                                                border_radius=3,
                                                content=qty_text
                                            ),
                                            round_button(
                                                ft.Icons.ADD,
                                                lambda e: handle_restock(e),
                                                False,
                                            ),
                                            ft.Container(
                                                width=5
                                            ),
                                            pill_button("SAVE QUANTITY", 80, 15,7, "#c37960", 8,  lambda e: save_qty(e, item)),
                                        ]
                                    ),
                                    ft.Text(
                                        "Select Batch to Edit:",
                                        font_family="Poppins-Bold",
                                        color="#894e3f",
                                        size=10,
                                    ),
                                    batches,
                                    batch_info
                                ]
                            )
                        ]
                    ),
                    ft.Divider(height=1, color="#894e3f"),
                    ft.Container(
                        height=30,
                        width=256,
                        bgcolor="#894e3f",
                        alignment=ft.Alignment.CENTER,
                        border_radius=6,
                        content=(
                            ft.Row(
                                alignment=ft.MainAxisAlignment.CENTER,
                                spacing=2,
                                controls=[
                                    ft.Icon(ft.Icons.ADD, size=10, color="white"),
                                    ft.Text(
                                        "Add New Batch",
                                        size=10,
                                        font_family="Poppins-Bold",
                                        weight=ft.FontWeight.BOLD,
                                        color="white",
                                    ),
                                ]
                            )
                        ),
                        on_click=lambda e: open_new_batch_card(item, e),
                        ink=True,
                    ),
                ],
            )
        )


    def open_new_batch_card(item, e=None):
        expiry_text.value = "Select date"
        expiry_text.value = None
        overlay.content.controls.append(new_batch_card(item))
        overlay.visible = True
        overlay.update()

    def close_new_batch_card(e=None):
        overlay.content.controls.pop()
        overlay.update()

    expiry_text = ft.Text(
        "Select date", 
        size=9, 
        color="#894e3f", 
        font_family="Poppins",
        margin=ft.Margin.only(left=4)
        )

    expiry_field = ft.Container(
        width=100,
        height=18,
        border_radius=4,
        bgcolor="#fff8e5",
        border=ft.Border.all(1, "#c37960"),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            spacing=0,
            controls=[
                expiry_text,
                ft.Icon(
                    ft.Icons.CALENDAR_MONTH,
                    size=11,
                    color="#894e3f",
                    width=18,
                    height=18,
                ),
            ]
        ),
        on_click=lambda e: pick_date(e),
        ink=True,
    )

    new_batch_quantity = ft.TextField(
        text_align=ft.TextAlign.LEFT,
        height=15,
        border=ft.NoInputBorder(),
        width=100,
        dense=True,
        text_size=9,
        content_padding=ft.Padding.only(left=5),
        color="#894e3f",
        keyboard_type=ft.KeyboardType.NUMBER,
        input_filter=ft.NumbersOnlyInputFilter(),
        hint_text="Enter quantity",
        hint_style=ft.TextStyle(
            font_family="Poppins",
            size=7,
            color="#894e3f"
        )
    )

    def pick_date(e):
        def on_change(ev):
            if ev.control.value:
                expiry_text.value = ev.control.value.strftime("%m/%d/%Y")
                expiry_text.update()
    
        page.show_dialog(
            ft.DatePicker(
                first_date=datetime(2020, 1, 1),
                last_date=datetime(2100, 12, 31),
                on_change=on_change,
            )
        )

    def add_batch_db(item):
        batch = {
            "expiration_date" : date_db_format(expiry_text.value),
            "qty" : new_batch_quantity.value
        }

        conn = get_connection()

        id = add_batch(conn, item["ingredient_id"], batch["expiration_date"], batch["qty"], item["quantity"])

        conn.close()

        items = get_inventory()

        new_items = {}
        for i in items:
            if i["ingredient_id"] == item["ingredient_id"]:
                new_items = i
                break

        overlay.content.controls.clear()
        open_edit_card(new_items, callbacks["on_consume"], callbacks["on_restock"])

    
    def new_batch_card(item):
        return ft.Container(
            width=280,
            bgcolor="#fff8e5",
            border=ft.Border.all(1.5, "#c37960"),
            border_radius=12,
            padding=ft.Padding.only(left=12, right=12, top=6, bottom=12),
            shadow=ft.BoxShadow(
                blur_radius=10, color="#40000000", offset=ft.Offset(0, 2)
            ),
            content=ft.Column(
                alignment=ft.Alignment(0, -0.5),
                spacing=1,
                tight=True,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Text(
                                "ADD NEW BATCH",
                                size=16,
                                font_family="Poppins-Bold",
                                weight=ft.FontWeight.BOLD,
                                color="#894e3f",
                            ),
                            ft.IconButton(
                                ft.Icons.CLOSE,
                                icon_size=16,
                                icon_color="#894e3f",
                                padding=0,
                                width=22,
                                height=22,
                                on_click=close_new_batch_card,
                            ),
                        ],
                    ),
                    ft.Divider(height=1, color="#894e3f",),
                    ft.Container(
                        alignment=ft.Alignment.CENTER,
                        margin=ft.Margin.only(top=7),
                        border_radius=6,
                        width=256,
                        padding=ft.Padding.only(left=10, right=10),
                        border=ft.Border.all(1, "#c37960"),
                        content=ft.Column(
                            spacing=0,
                            tight=True,
                            controls=[
                                ft.Text(
                                    f"BATCH ({len(item["batches"]) + 1})",
                                    text_align=ft.TextAlign.LEFT,
                                    size=10,
                                    font_family="Poppins-Bold",
                                    weight=ft.FontWeight.BOLD,
                                    color="#894e3f",
                                    margin=ft.Margin.only(top=4, bottom=2),
                                ),
                                ft.Divider(height=1, color="#894e3f"),
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    spacing=0,
                                    controls=[
                                        ft.Column(
                                            spacing=0,
                                            tight=True,
                                            controls=[
                                                ft.Text(
                                                    "Expiration Date:",
                                                    size=7,
                                                    font_family="Poppins",
                                                    color="#894e3f",
                                                    margin=ft.Margin.only(top=3),
                                                ),
                                                expiry_field,
                                            ]
                                        ),
                                        ft.Column(
                                            spacing=0,
                                            tight=True,
                                            controls=[
                                                ft.Text(
                                                    "Quantity:",
                                                    size=7,
                                                    font_family="Poppins",
                                                    color="#894e3f",
                                                    margin=ft.Margin.only(top=3),
                                                ),
                                                ft.Container(
                                                    width=100,
                                                    height=18,
                                                    border_radius=4,
                                                    bgcolor="#fff8e5",
                                                    border=ft.Border.all(1, "#c37960"),
                                                    content=new_batch_quantity
                                                )
                                            ]
                                        )
                                    ]
                                ),
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.END,
                                    spacing=5,
                                    controls=[
                                        ft.Container(
                                            width=70,
                                            height=15,
                                            bgcolor="transparent",
                                            alignment=ft.Alignment.CENTER,
                                            on_click=close_new_batch_card,
                                            ink=True,
                                            margin=ft.Margin.only(top=5, bottom= 5),
                                            content=ft.Text(
                                                "CANCEL",
                                                color="#894e3f",
                                                size=10,
                                                font_family="Poppins-Bold",
                                                weight=ft.FontWeight.BOLD,
                                            ),
                                        ),
                                        ft.Container(
                                            width=100,
                                            height=17,
                                            bgcolor="#894e3f",
                                            border_radius=5,
                                            alignment=ft.Alignment.CENTER,
                                            shadow=ft.BoxShadow(blur_radius=2, color=ft.Colors.BLACK_45),
                                            on_click=lambda e :add_batch_db(item),
                                            ink=True,
                                            margin=ft.Margin.only(top=6, bottom= 5),
                                            content=ft.Text(
                                                "SAVE NEW BATCH",
                                                color="#fff8e5",
                                                size=9,
                                                font_family="Poppins-Bold",
                                                weight=ft.FontWeight.BOLD,
                                            ),
                                        )
                                    ]
                                )
                            
                            ]
                        )
                    )      
                
                ]
            )
        )
    
    overlay = ft.Container(
            visible=False,
            expand=True,
            alignment=ft.Alignment(0, 0),
            content=ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[]
            )
        )

    return overlay, open_edit_card, close_edit_card