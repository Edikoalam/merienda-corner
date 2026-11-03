import flet as ft
from db import get_connection, get_menu, get_order_count_today, get_order_count_tomorrow
from sorting import insertionSort

TERRACOTTA = "#C47A62"
SAND = "#efd7a6"
CREAM = "#fff8e5"
BROWN = "#8B4D3E"
WHITE = "#ffffff"

def build(app, go):

    menu = []
    conn = get_connection()
    try:
        menu = get_menu(conn)
    finally:
        conn.close()

    def product_card(name, units, img=None):
        return ft.Container(
            width=100,
            padding=8,
            bgcolor="white",
            border_radius=18,
            shadow=ft.BoxShadow(
                blur_radius=10, 
                color="#A8515100", 
                offset=ft.Offset(0, 2)
            ),
            content=ft.Column(
                spacing=0,
                controls=[
                    ft.Container(
                        content=ft.Image(
                            src=img, 
                            width=84, 
                            height=92, 
                            fit=ft.BoxFit.COVER
                        ),
                        border_radius=12,
                        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                    ),
                    ft.Container(height=6),
                    ft.Text(
                        name, 
                        font_family="Poppins-Bold", 
                        size=10, 
                        color=BROWN
                    ),
                    ft.Text(
                        f"{units} units", 
                        font_family="Poppins", 
                        size=10, 
                        color=BROWN
                    ),
                ],
            ),
        )

    header_banner = ft.Container(
        height=60,
        bgcolor=BROWN,
        alignment=ft.Alignment.TOP_CENTER,
        padding=ft.Padding.only(top=12),
        border_radius=ft.BorderRadius.only(bottom_left=30, bottom_right=30),
        content=ft.Text(
            "Baked with love, baking for love",    
            text_align=ft.TextAlign.CENTER,
            style = ft.TextStyle(
                font_family="Handelson",
                size=30,
                color=CREAM,
                shadow=ft.BoxShadow(
                    blur_radius=3,
                    color="#66000000",
                    offset=ft.Offset(1,3)            
                )  
            )
        ),
    )

    title = ft.Container(
        padding=ft.Padding.symmetric(horizontal=26),
        content=ft.Column(
            spacing=5,
            controls=[
                ft.Stack(
                    height=95,
                    controls=[
                        ft.Text(
                            "Marinel’s Sari-Sari\nMerienda Corner",
                            font_family="Poppins-Bold",
                            size=27,
                            color=BROWN,
                            top=16,
                            left=0,
                        ),
                        ft.Image(
                            src="images/chef_hat.png", 
                            width=37, 
                            height=37, 
                            top=0, 
                            left=-8),
                    ],
                ),
                ft.Divider(
                    height=3, 
                    thickness=3, 
                    color=BROWN
                ),
            ],
        ),
    )

    home_txt = ft.Container(
        padding=ft.Padding.only(left=28),
        content=ft.Text(
            "Home", 
            font_family="Poppins-Bold", 
            size=30, 
            color=BROWN
        ),
    )



    today_count = ft.Text(
        get_order_count_today(), 
        font_family="Poppins-Bold", 
        size=30, 
        color=WHITE, 
        no_wrap=True
    )
    
    tomorrow_count = ft.Text(
        get_order_count_tomorrow(), 
        font_family="Poppins-Bold", 
        size=30, 
        color=WHITE, 
        no_wrap=True
    )

    def count_row(number_text, label):
        return ft.Row(
            spacing=0,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    width=60,
                    alignment=ft.Alignment.CENTER_LEFT,
                    content=number_text,
                ),
                ft.Text(label, font_family="Poppins", size=20, color=WHITE, no_wrap=True),
            ],
        )
    
    statistics_cards = ft.Container(
        padding=ft.Padding.symmetric(horizontal=27),
        content=ft.Stack(
            height=186,
            controls=[
                ft.Container( 
                    top=0, left=0, right=0, height=110,
                    bgcolor=BROWN,
                    border_radius=24,
                    alignment=ft.Alignment.TOP_LEFT,
                    padding=ft.Padding.only(left=30, top=-50),
                    content=count_row(today_count, "Orders for today"),
                ),
                ft.Container(
                    top=61, left=0, right=0, height=90,
                    bgcolor=TERRACOTTA,
                    border_radius=24,
                    alignment=ft.Alignment.TOP_LEFT,
                    padding=ft.Padding.only(left=30, top=-20),
                    content=count_row(tomorrow_count, "Orders for tomorrow"),
                ),
                ft.Container(
                    top=123, left=0, right=0, height=63,
                    bgcolor=SAND,
                    border_radius=24,
                    padding=ft.Padding.only(left=30, right=16),
                    on_click=lambda e: go(2),
                    ink=True,
                    ink_color= WHITE,  
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text(
                                "MY QUEUE ORDERS",
                                style=ft.TextStyle(
                                    font_family="Poppins",
                                    size=22,
                                    color=WHITE,
                                    shadow=ft.BoxShadow(
                                        blur_radius=3,
                                        color="#66000000",
                                        offset=ft.Offset(1, 3),
                                    ),
                                ),
                            ),
                            ft.Icon(ft.Icons.CHEVRON_RIGHT, color=WHITE, size=40),
                        ],
                    ),
                ),
            ],
        ),
    )   
    
    #button dapat to
    dessert_menu = ft.Container(
        margin=ft.Margin.symmetric(horizontal=27),
        height=52,
        bgcolor=BROWN,
        border_radius=26,
        alignment=ft.Alignment.CENTER,
        ink=True,
        shadow=ft.BoxShadow(blur_radius=2, color=ft.Colors.BLACK_45),
        ink_color= WHITE,    
        on_click=lambda e: go(5),
        content=ft.Text(
            "DESSERT MENU", 
            font_family="Poppins-Bold", 
            size=32, 
            color=CREAM
        ),
    )
    
        
    best_sellers_row = ft.Row(spacing=8)  
    
    def update_best_sellers(menu): 
        top = insertionSort(menu, "units_sold")
        top3 = top[:3]
        best_sellers_row.controls = [
            product_card(p["p_name"], p["units_sold"], p["img"]) for p in top3
        ]
        app.page.update()
    
    best_sellers = ft.Container(
        padding=ft.Padding.symmetric(horizontal=43),
        content=ft.Column(
            spacing=14,
            controls=[
                ft.Text(
                    "Best-selling products", 
                    font_family="Poppins", 
                    size=22, 
                    color=BROWN
                ),
                best_sellers_row,
            ],
        ),
    )
    
     
    inventory_btn = ft.Container(
        margin=ft.Margin.symmetric(horizontal=24),
        height=63,
        padding=ft.Padding.only(left=30, right=16),
        bgcolor=TERRACOTTA,
        border_radius=24,
        shadow=ft.BoxShadow(blur_radius=2, color=ft.Colors.BLACK_45),
        ink=True,
        ink_color= WHITE,      
        on_click=lambda e: go(1),
        content=ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Text(
                    "My Inventory", 
                    font_family="Poppins", 
                    size=25, 
                    color=WHITE
                ),
                ft.Icon(ft.Icons.CHEVRON_RIGHT, color=WHITE, size=50),
            ],
        ),
    )
    

    view = ft.Container(
        expand=True,
        content= ft.Column(
            expand=True,
            spacing=14,
            scroll=ft.ScrollMode.AUTO,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            controls=[
                header_banner,
                title,
                home_txt,
                statistics_cards,
                dessert_menu,
                best_sellers,
                inventory_btn,
                ft.Container(height=8),
            ],
        )
    )

    sample_products = [
            {"name": "Leche Flan",  "units": 210, "img": "images/lecheflan.png"},
            {"name": "Yema Cake",   "units": 116, "img": "images/yemacake.png"},
            {"name": "Banana Cake", "units": 80,  "img": "images/bananabread.png"},
            {"name": "Maja Blanca ", "units": 45,  "img": "images/majablanca.png"},
        ]
    update_best_sellers(menu)

    return view, lambda: None