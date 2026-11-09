import flet as ft
from db import get_connection, get_menu, add_menu, update_menu, delete_menu
from sorting import insertionSort
import os
import shutil
import uuid
from pathlib import Path


TERRACOTTA = "#C47A62"
CREAM = "#fff8e5"
BROWN = "#8B4D3E"
WHITE = "#ffffff"
GREEN = "#7C994D"
RED = "#E04444"
GRAY = "#B0887E"


def storage_images_dir():
    root = os.getenv("FLET_APP_STORAGE_DATA") or str(
        Path(__file__).resolve().parent / "storage"
    )
    path = Path(root) / "images"
    path.mkdir(parents=True, exist_ok=True)
    return path


def product_image(value, width, height, **kwargs):
    if value and not value.startswith("images/"):
        path = storage_images_dir() / value
        if path.exists():
            return ft.Image(
                src=path.read_bytes(), width=width, height=height,
                fit=ft.BoxFit.COVER, **kwargs,
            )
    return ft.Image(
        src=value or "", width=width, height=height,
        fit=ft.BoxFit.COVER, **kwargs,
    )


def build(app):

    def snack(message):
            app.page.show_dialog(ft.SnackBar(ft.Text(message), bgcolor=BROWN))

    def round_btn(text, color, on_click, width=None, size=15):
        return ft.Container(
            width=width,
            height=38,
            bgcolor=color,
            border_radius=19,
            alignment=ft.Alignment.CENTER,
            padding=ft.Padding.symmetric(horizontal=14),
            ink=True,
            on_click=on_click,
            content=ft.Text(text, font_family="Poppins-Bold", size=size, color=WHITE, no_wrap=True),
        )

    menu = []

    def get_new_menu():
        conn = get_connection()
        try:
            menu[:] = get_menu(conn)
        finally:
            conn.close()
        return menu
        
    grid = ft.Row(wrap=True, spacing=8, run_spacing=8)

    def refresh():
        get_new_menu()
        grid.controls = [product_card(m) for m in menu]
        app.page.update()

    #TEMPLATE
    def product_card(p):
        card = ft.Container(
            left=6, top=8, width=100,
            padding=8,
            bgcolor=WHITE,
            border_radius=18,
            shadow=ft.BoxShadow(blur_radius=10, color="#A8515100", offset=ft.Offset(0, 2)),
            content=ft.Column(
                spacing=0,
                controls=[
                    ft.Container(
                        border_radius=12,
                        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                        content=product_image(p["img"], 84, 92),
                    ),
                    ft.Container(height=6),
                    ft.Text(p["p_name"], font_family="Poppins-Bold", size=11, color=BROWN, no_wrap=True),
                    ft.Text(f"Price: ₱{p['price']}", font_family="Poppins-Bold", size=10, color=BROWN),
                    ft.Text(f"{p['units_left']} units available", font_family="Poppins", size=10, color=BROWN),
                ],
            ),
        )
        edit_btn = ft.Container(
            right=0, top=0, width=26, height=26,
            bgcolor=BROWN,
            border_radius=13,
            alignment=ft.Alignment.CENTER,
            ink=True,
            on_click=lambda e: open_editor(p),
            content=ft.Icon(ft.Icons.EDIT_OUTLINED, size=14, color=WHITE),
        )
        return ft.Stack(width=109, height=180, clip_behavior=ft.ClipBehavior.NONE, controls=[card, edit_btn])

    
    def confirm_dialog(content_controls, border_color):
        app.page.show_dialog(
            ft.AlertDialog(
                bgcolor=CREAM,
                shape=ft.RoundedRectangleBorder(radius=16, side=ft.BorderSide(2, border_color)),
                content_padding=16,
                content=ft.Column(
                    tight=True, spacing=10,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=content_controls,
                ),
            )
        )

    def confirm_delete(p):
        def do_delete(e):
            conn = get_connection()
            try:    
                delete_menu(conn, p["id"])
            finally:
                conn.close()
            app.page.pop_dialog()  
            app.page.pop_dialog()  
            refresh()

        confirm_dialog(
            [
                ft.Text(
                    f"Are you sure you want to delete “{p['p_name']}”?",
                    font_family="Poppins", size=14, color=BROWN, text_align=ft.TextAlign.CENTER,
                ),
                ft.Text("This action cannot be undone.", font_family="Poppins", size=12, color=BROWN),
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        round_btn("CANCEL", GRAY, lambda e: app.page.pop_dialog(), width=100),
                        round_btn("DELETE", RED, do_delete, width=100),
                    ],
                ),
            ],
            RED,
        )

    def open_editor(product=None):
        is_new = product is None
        data = product or {"p_name": "", "price": 0, "units_sold": 0, "img": None}
        state = {"img": data["img"]}

        def field(value, width, hint=""):
            return ft.TextField(
                value=str(value), hint_text=hint, width=width, height=36,
                dense=True, bgcolor=WHITE, border=ft.NoInputBorder(),
                text_align=ft.TextAlign.CENTER,
                text_style=ft.TextStyle(font_family="Poppins", size=14, color=BROWN),
                content_padding=ft.Padding.symmetric(horizontal=6),
            )

        name_f = field(data["p_name"], 170, "DESSERT NAME")
        name_f.text_style = ft.TextStyle(font_family="Poppins-Bold", size=16, color=BROWN)
        price_f = field(data["price"], 110)
        units_f = field(data["units_left"], 110)
        price_f.keyboard_type = ft.KeyboardType.NUMBER
        units_f.keyboard_type = ft.KeyboardType.NUMBER


        placeholder = ft.Icon(ft.Icons.ADD_PHOTO_ALTERNATE, size=72, color=BROWN)
        image_box = ft.Container(
            width=180, height=180,
            border=ft.Border.all(1, TERRACOTTA),
            border_radius=12,
            alignment=ft.Alignment.CENTER,
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            bgcolor=WHITE,
            ink=True,
            content=(
                product_image(state["img"], 180, 180)
                if state["img"] else placeholder
            ),
        )

        def is_mobile():
            return app.page.platform in (ft.PagePlatform.ANDROID, ft.PagePlatform.IOS)

        def assets_images_dir():
            path = Path(__file__).resolve().parents[2] / "assets" / "images"
            path.mkdir(parents=True, exist_ok=True)
            return path

        def save_image(source_path, original_name):
            extension = os.path.splitext(original_name)[1] or ".jpg"
            filename = f"{uuid.uuid4().hex}{extension}"
            if not is_mobile():
                try:
                    shutil.copyfile(source_path, assets_images_dir() / filename)
                    return f"images/{filename}"
                except OSError as ex:
                    print("assets folder not writable, using app storage:", repr(ex))
            shutil.copyfile(source_path, storage_images_dir() / filename)
            return filename

        def show_image(value):
            image_box.content = product_image(value, 180, 180)
            image_box.update()

        async def pick_image(e):
            picker = ft.FilePicker()
            app.page.services.append(picker)
            app.page.update()
            try:
                files = await picker.pick_files(file_type=ft.FilePickerFileType.IMAGE)
                if not files:
                    return
                picked = files[0]
                if not picked.path:
                    snack("Could not read that image")
                    return
                state["img"] = save_image(picked.path, picked.name)
                show_image(state["img"])
            except Exception as ex:
                print("pick_image error:", repr(ex))
            finally:
                if picker in app.page.services:
                    app.page.services.remove(picker)
                    app.page.update()

        image_box.on_click = pick_image

        def to_int(tf):
            try:
                return int(float(tf.value))
            except ValueError:
                return 0

        def has_changes():
            """True if anything in the popup differs from the saved product."""
            return (
                name_f.value.strip() != data["p_name"]
                or to_int(price_f) != data["price"]
                or to_int(units_f) != data["units_sold"]
                or state["img"] != data["img"]
            )

        def save(e=None):
            if not name_f.value.strip():
                name_f.error_text = "Required"
                name_f.update()
                return
            values = {
                "name": name_f.value.strip(),
                "price": to_int(price_f),
                "units": to_int(units_f),
                "img": state["img"] or "images/placeholder.png",
            }
            conn = get_connection()
            if is_new:
                add_menu(conn, values["name"], values["price"], values["img"], values["units"])
                conn.close()
            else:
                update_menu(conn, data["id"], values["name"], values["price"], values["img"], values["units"])
                conn.close()
            app.page.pop_dialog()
            refresh()

        def request_close(e):
            if not has_changes():
                app.page.pop_dialog()
                return
            confirm_dialog(
                [
                    ft.Text("Do you want to save the changes made?", font_family="Poppins",
                            size=13, color=BROWN, text_align=ft.TextAlign.CENTER),
                    round_btn("SAVE", GREEN, lambda e: (app.page.pop_dialog(), save()), width=200, size=13),
                    round_btn("DON'T SAVE", RED, lambda e: (app.page.pop_dialog(), app.page.pop_dialog()), width=200, size=13),
                    round_btn("CANCEL", GRAY, lambda e: app.page.pop_dialog(), width=200, size=13),
                ],
                GREEN,
            )

        left_btn = (
            round_btn("CANCEL", GRAY, lambda e: app.page.pop_dialog(), width=110)
            if is_new else round_btn("DELETE", RED, lambda e: confirm_delete(product), width=110)
        )

        def label_row(text, tf, prefix=""):
            return ft.Row(
                alignment=ft.MainAxisAlignment.CENTER, spacing=6,
                controls=[
                    ft.Text(text, font_family="Poppins", size=15, color=BROWN, width=64),
                    ft.Text(prefix, font_family="Poppins", size=15, color=BROWN, width=14),
                    tf,
                ],
            )

        app.page.show_dialog(
            ft.AlertDialog(
                bgcolor=CREAM,
                shape=ft.RoundedRectangleBorder(radius=20, side=ft.BorderSide(2, TERRACOTTA)),
                content_padding=ft.Padding.all(14),
                content=ft.Column(
                    tight=True, spacing=10,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Icon(ft.Icons.EDIT, size=18, color=GRAY),
                                name_f,
                                ft.IconButton(ft.Icons.CLOSE, icon_size=20, icon_color=BROWN, on_click=request_close),
                            ],
                        ),
                        image_box,
                        label_row("PRICE:", price_f, "₱"),
                        label_row("UNITS:", units_f),
                        ft.Row(
                            alignment=ft.MainAxisAlignment.CENTER,
                            controls=[
                                left_btn, 
                                round_btn("SAVE", GREEN, save, width=110)
                            ],
                        ),
                    ],
                ),
            )
        )

    
    header = ft.Container(
        height=60,
        bgcolor=BROWN,
        alignment=ft.Alignment.CENTER,
        border_radius=ft.BorderRadius.only(bottom_left=30, bottom_right=30),
        content=ft.Text("DESSERT MENU", font_family="Poppins-Bold", size=40, color=CREAM),
    )

    title = ft.Container(
        padding=ft.Padding.symmetric(horizontal=26),
        content=ft.Column(
            spacing=5,
            controls=[
                ft.Stack(
                    height=95,
                    controls=[
                        ft.Text("Marinel’s Sari-Sari\nMerienda Corner", font_family="Poppins-Bold",
                                size=27, color=BROWN, top=16, left=0),
                        ft.Image(src="images/chef_hat.png", width=37, height=37, top=0, left=-8),
                    ],
                ),
                ft.Divider(height=3, thickness=3, color=BROWN),
            ],
        ),
    )

    add_btn = ft.Row(
        controls=[
            ft.Container(
                margin=ft.Margin.only(left=27),
                padding=ft.Padding.symmetric(horizontal=14, vertical=8),
                bgcolor=TERRACOTTA,
                border_radius=20,
                ink=True,
                on_click=lambda e: open_editor(None),
                content=ft.Text("+ ADD PRODUCT", font_family="Poppins-Bold", size=15, color=WHITE),
            )
        ]
    )

    grid_area = ft.Container(padding=ft.Padding.symmetric(horizontal=20), content=grid)
    grid.controls = [product_card(m) for m in menu]  #show cards kaopen ng app

    refresh()

    view = ft.Column(
        expand=True,
        spacing=14,
        scroll=ft.ScrollMode.AUTO,
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        controls=[
            header, 
            title, 
            add_btn, 
            grid_area, 
            ft.Container(height=8)
        ],
    )

    def on_show():
        refresh()

    return view, on_show