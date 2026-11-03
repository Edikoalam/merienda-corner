import flet as ft

BG = "#fff8e5"
DARK = "#3b2a22"
FONT_BOLD = "Poppins-Bold"


def chevron():
    return ft.Container(
        content=ft.Icon(ft.Icons.KEYBOARD_ARROW_DOWN, size=12, color=BG),
        bgcolor=DARK,
        border_radius=20,
        width=14,
        height=14,
        alignment=ft.Alignment.CENTER,
    )


def popup_menu(
    label,
    options,
    on_pick,
    width=None,
    outlined=True,
    arrow=True,
    height=24,
    extra_items=None,
):
    label_text = ft.Text(
        label,
        size=10,
        weight=ft.FontWeight.BOLD,
        color=DARK if outlined else BG,
        font_family=FONT_BOLD,
        max_lines=1,
        overflow=ft.TextOverflow.ELLIPSIS,
    )
    row_controls = [ft.Container(content=label_text, expand=True)]
    if arrow:
        row_controls.append(chevron())

    face = ft.Container(
        content=ft.Row(
            controls=row_controls,
            spacing=4,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        width=width,
        height=height,
        padding=ft.Padding.symmetric(horizontal=8),
        border=ft.Border.all(1.5, DARK) if outlined else None,
        border_radius=10 if outlined else 8,
        bgcolor=None if outlined else DARK,
        alignment=ft.Alignment.CENTER_LEFT,
    )
    items = [
        ft.PopupMenuItem(
            content=ft.Text(option, size=12),
            on_click=lambda e, option=option: on_pick(option),
        )
        for option in options
    ]
    menu = ft.PopupMenuButton(content=face, items=items + (extra_items or []))
    return menu, label_text