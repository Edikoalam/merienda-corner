import flet as ft

def add_confirmation_tabs():

    message = ""
    state= {"on_yes" : None}

    confirm = ft.Container(
            width=150,
            bgcolor="#ffffffc5",
            border=ft.Border.all(1.5, "#7c994d"),
            border_radius=12,
            padding=ft.Padding.only(left=12, right=12, top=6, bottom=12),
            shadow=ft.BoxShadow(
                blur_radius=10, color="#40000000", offset=ft.Offset(0, 2)
            ),
            content=ft.Column(
                spacing=4,
                tight=True,
                controls=[
                    ft.Column(
                        spacing=2,
                        tight=True,
                        controls=[
                            ft.Text(
                                "Are you sure you want to",
                                font_family="Poppins",
                                size=13,
                                color = "#894e3f"
                            ),
                            ft.Text(
                                message,
                                font_family="Poppins",
                                size=13,
                                color = "#894e3f"
                            )             
                        ]
                    ),
                    ft.Row(
                        spacing=4,
                        tight=True,
                        controls=[
                            ft.TextButton(
                                content="YES",
                                style=ft.ButtonStyle(
                                    color="#ffffff",
                                    shape=ft.RoundedRectangleBorder(radius=3),
                                    bgcolor={
                                    ft.ControlState.DEFAULT: "#7c994d",
                                    ft.ControlState.HOVERED: "#6e9235",
                                    },
                                    text_style={
                                        ft.ControlState.DEFAULT: ft.TextStyle(
                                        font_family='Poppins',
                                        size=14,
                                        weight=ft.FontWeight.BOLD,
                                        ),
                                        ft.ControlState.HOVERED: ft.TextStyle(
                                            font_family="Poppins",
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                    },
                                ),
                                on_click=lambda e: handle_yes(e),
                            ),
                            ft.TextButton(
                                content="NO",
                                style=ft.ButtonStyle(
                                    color="#ffffff",
                                    shape=ft.RoundedRectangleBorder(radius=3),
                                    bgcolor={
                                        ft.ControlState.DEFAULT: "#dd433f",
                                        ft.ControlState.HOVERED: "#d52923",
                                    },
                                    text_style={
                                        ft.ControlState.DEFAULT: ft.TextStyle(
                                            font_family='Poppins',
                                            size=14,
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                        ft.ControlState.HOVERED: ft.TextStyle(
                                            font_family="Poppins",
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                    },
                                ),
                                on_click=lambda e: handle_no(e),
                            )
                        ]
                    )
                ]
            )
        )

    def handle_yes(e):
        close()
        if state["on_yes"]:
            state["on_yes"]()

    def handle_no(e):
        close()


    def close():
        overlay.visible = False
        overlay.update()
        
    def delete_confirmation(mess, action):
        nonlocal message
        message = mess
        state["on_yes"] = action
        overlay.visible = True
        overlay.update()
        
        
        
    overlay = ft.Container(
        visible=False,
        expand=True,
        alignment=ft.Alignment(0.6, 0),
        content=confirm,
    )

    return overlay, delete_confirmation