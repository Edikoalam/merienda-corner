import flet as ft

from pages.orders.Popup_menu import popup_menu

BG = "#fff8e5"
CREAM = "#f4ead6"
CREAM_LIGHT = "#fffaf0"
DARK = "#3b2a22"
FIELD_LABEL = "#5f5f5f"
GREEN = "#3a7f2c"
RED = "#c0392b"
ADD_BUTTON = "#b0887e"
ADD_BUTTON_HOVER = "#95736a"

FONT = "Poppins"
FONT_BOLD = "Poppins-Bold"

ORDER_TYPES = ["DELIVERY", "PICKUP"]
ORDER_STATUSES = ["PENDING", "DONE", "CANCELLED"]


def create_popup(stack, get_products, on_save):
    items = []
    products = []
    state = {"index": None, "type": None, "status": None}

    def field(label, width=150):
        return ft.TextField(
            label=label,
            label_style=ft.TextStyle(
                size=12,
                weight=ft.FontWeight.BOLD,
                color=FIELD_LABEL,
                font_family=FONT_BOLD,
            ),
            text_size=10,
            width=width,
            height=35,
            filled=True,
            bgcolor=CREAM,
            border=ft.OutlineInputBorder(
                side=ft.BorderSide(color=ft.Colors.WHITE),
            ),
        )

    def pick_type(value):
        state["type"] = value
        type_label.value = value
        type_label.color = DARK
        type_label.update()

    def pick_status(value):
        state["status"] = value
        status_label.value = value
        status_label.update()

    name_field = field("NAME")
    address_field = field("ADDRESS")
    type_menu, type_label = popup_menu("TYPE", ORDER_TYPES, pick_type, width=105)
    status_menu, status_label = popup_menu(
        "STATUS",
        ORDER_STATUSES,
        pick_status,
        width=90,
        height=30,
        outlined=False,
        arrow=False,
    )
    items_column = ft.Column(spacing=6, scroll=ft.ScrollMode.AUTO, expand=True)
    error_text = ft.Text("", size=10, color=RED, text_align=ft.TextAlign.CENTER)

    def render_items(update=True):
        def pick_product(i, name):
            items[i]["p_name"] = name
            render_items()

        def remove_item(i):
            items.pop(i)
            render_items()

        def set_qty(i, value):
            try:
                items[i]["quantity"] = int(value or 0)
            except ValueError:
                pass

        rows = []
        for i, item in enumerate(items):
            product_menu, _ = popup_menu(
                item["p_name"] or "PRODUCT",
                products,
                lambda name, i=i: pick_product(i, name),
                width=125,
                extra_items=[
                    ft.PopupMenuItem(
                        content=ft.Text("REMOVE", size=12, color=RED),
                        on_click=lambda e, i=i: remove_item(i),
                    )
                ],
            )
            qty = ft.TextField(
                value=str(item["quantity"]),
                width=38,
                height=26,
                text_size=11,
                text_align=ft.TextAlign.CENTER,
                content_padding=ft.Padding.all(0),
                keyboard_type=ft.KeyboardType.NUMBER,
                input_filter=ft.NumbersOnlyInputFilter(),
                filled=True,
                bgcolor=CREAM_LIGHT,
                border=ft.OutlineInputBorder(
                    border_radius=8,
                    side=ft.BorderSide(1, DARK),
                ),
                on_change=lambda e, i=i: set_qty(i, e.control.value),
            )
            rows.append(
                ft.Container(
                    content=ft.Row(
                        controls=[
                            product_menu,
                            ft.Row(
                                controls=[
                                    ft.Text(
                                        "QUANTITY:",
                                        size=10,
                                        weight=ft.FontWeight.BOLD,
                                        color=DARK,
                                    ),
                                    qty,
                                ],
                                spacing=4,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    border=ft.Border.all(1, DARK),
                    border_radius=10,
                    bgcolor=CREAM_LIGHT,
                    padding=ft.Padding.symmetric(horizontal=6, vertical=4),
                )
            )
        items_column.controls = rows
        if update:
            items_column.update()

    def add_product(e):
        items.append({"p_name": "", "quantity": 0})
        render_items()

    def get_data():
        return {
            "c_name": name_field.value or "",
            "address": address_field.value or "",
            "order_type": state["type"],
            "status": state["status"],
            "items": [dict(it) for it in items if it["p_name"]],
        }

    def close_popup(e=None):
        if overlay in stack.controls:
            stack.controls.remove(overlay)
            stack.update()

    def save(e):
        data = get_data()
        error = on_save(state["index"], data)
        if error:
            error_text.value = error
            error_text.update()
            return
        close_popup()


    def open_popup(index=None, data=None):
        data = data or {}
        state["index"] = index

        name_field.value = data.get("c_name", "")
        address_field.value = data.get("address", "")

        state["type"] = (data.get("order_type") or "").upper() or None
        type_label.value = state["type"] or "TYPE"
        type_label.color = DARK

        state["status"] = (data.get("status") or "").upper() or None
        status_label.value = state["status"] or "STATUS"

        products[:] = get_products()
        items[:] = [
            {"p_name": it["p_name"], "quantity": it["quantity"]}
            for it in data.get("items", [])
        ]
        render_items(update=False)
        error_text.value = ""

        if overlay not in stack.controls:
            stack.controls.append(overlay)
        stack.update()

    card = ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        name_field,
                        ft.TextButton(
                            content="ADD PRODUCT",
                            on_click=add_product,
                            style=ft.ButtonStyle(
                                color=BG,
                                shape=ft.RoundedRectangleBorder(radius=10),
                                side=ft.BorderSide(width=1, color=ft.Colors.WHITE),
                                bgcolor={
                                    ft.ControlState.DEFAULT: ADD_BUTTON,
                                    ft.ControlState.HOVERED: ADD_BUTTON_HOVER,
                                },
                                text_style=ft.TextStyle(
                                    font_family=FONT,
                                    size=11,
                                    weight=ft.FontWeight.BOLD,
                                ),
                            ),
                            width=105,
                        ),
                    ],
                    spacing=4,
                ),
                ft.Row(controls=[address_field, type_menu], spacing=4),
                items_column,
                error_text,
                ft.Row(
                    controls=[
                        status_menu,
                        ft.Button(
                            content="DONE",
                            on_click=save,
                            width=85,
                            height=30,
                            style=ft.ButtonStyle(
                                bgcolor=GREEN,
                                color=BG,
                                shape=ft.RoundedRectangleBorder(radius=8),
                                text_style=ft.TextStyle(
                                    font_family=FONT_BOLD,
                                    size=12,
                                    weight=ft.FontWeight.BOLD,
                                ),
                            ),
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
            ],
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True,
            spacing=5,
        ),
        bgcolor=CREAM,
        border_radius=16,
        width=280,
        height=500,
        padding=ft.Padding.all(10),
        border=ft.Border.all(1, GREEN),
    )

    overlay = ft.Container(
        blur=10,
        bgcolor="#33000000",
        alignment=ft.Alignment.CENTER,
        expand=True,
        content=ft.Stack(
            alignment=ft.Alignment.CENTER,
            controls=[
                ft.Container(
                    on_click=close_popup
                ),
                card,
            ],
        ),
    )

    return open_popup, close_popup