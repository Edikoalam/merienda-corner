import flet as ft

from db import get_connection, init_db
from pages.history.History import build as history_page
from pages.inventory.Inventory import build as inventory_page
from pages.home.Home import build as home_page
from pages.orders.Orders import build as orders_page
from pages.stats.Stats import build as stats_page
from pages.menu.Menu import build as menu_page

FONTS = {
    "Anton": "fonts/Anton-Regular.ttf",
    "Poppins": "fonts/Poppins-Regular.ttf",
    "Poppins-Bold": "fonts/Poppins-Bold.ttf",
    "Handelson": "fonts/HandelsonW00Three.ttf",
}

IMAGES = {
    "BananaBread" : "images/bananabread.png",
    "YemaCake" : "images/yemacake.png",
    "LecheFlan" : "images/lecheflan.png",
    "MajaBlanca": "images/majablanca.png",
    "ChefHat" : "images/chef_hat.png"
}

NAV_ICONS = [
    ft.Icons.HOME,
    ft.Icons.INVENTORY,
    ft.Icons.FASTFOOD,
    ft.Icons.HISTORY,
    ft.Icons.PIE_CHART,
]


class App:
    pass


def main(page: ft.Page):
    page.title = "Marinel's Sari-Sari Merienda Corner"
    page.window.width = 400
    page.window.height = 800
    page.window.resizable = False
    page.bgcolor = "#fff8e5"
    page.padding = 0
    page.fonts = FONTS

    conn = get_connection()
    init_db(conn)
    conn.close()

    app = App()
    app.page = page
    app.stack = ft.Stack(expand=True)

    def go(index):
            view, on_show = pages[index]
            body.content = view
            body.update()
            for i in range(len(NAV_ICONS)):
                if i != index:
                    page.bottom_appbar.content.controls[i].content.bgcolor = None
                    page.bottom_appbar.update()
            if index == 5:
                on_show()
            else:
                page.bottom_appbar.content.controls[index].content.bgcolor = "#6b382b" 
                page.bottom_appbar.update()
                on_show()

    pages = [
        home_page(app, go),
        inventory_page(app),
        orders_page(app),
        history_page(app),
        stats_page(app),
        menu_page(app)
    ]

    body = ft.Container(expand=True, content=pages[0][0])

    page.bottom_appbar = ft.BottomAppBar(
        bgcolor="#894e3f",
        height=70,
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_AROUND,
            controls=[
                ft.Container(   
                    content=ft.IconButton(
                        icon,
                        icon_size=30,
                        icon_color="#fff8e5",
                        on_click=lambda e, i=i: go(i),
                    ),
                    bgcolor=None,
                    border_radius=ft.BorderRadius.all(30),
                )
                for i, icon in enumerate(NAV_ICONS)
            ],
        ),
    )

    app.stack.controls.append(body)
    page.add(ft.SafeArea(expand=True, content=app.stack))
    pages[0][1]()


if __name__ == "__main__":
    ft.run(main)