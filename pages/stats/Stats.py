import flet as ft
import flet_charts as fch 
from datetime import datetime
from db import get_connection, get_menu, order_history, get_specific_history, get_history_by_date_range
from sorting import insertionSort


BROWN = "#894e3f"
CREAM = "#fff8e5"
TERRACOTTA = "#c37960"
CARD_BG = "#f5ead8"
TABLE_BG = "#f8edd3"
ROW_BG = "#f0dcb0"
LINE = "#e3b9a2"

# Expanded list of warm, theme-matched colors for your pie chart and legends
DEFAULT_PIE_COLORS = [
    "#df7a07", "#fbe09a", "#f2b469", "#ffdc5e", "#c37960", 
    "#894e3f", "#a74e38", "#e9522c", "#d9822b", "#f4a261", 
    "#e76f51", "#b5838d", "#e5989b", "#ffb703", "#fb8500",
    "#bc6c25", "#dda15e", "#9b2226", "#ae2012", "#bb3e03"
]

best_seller = {
    "name": "",        
    "units": "",       
    "image_src": "",   
}


def build(app):
    active_period = ''

    products = []
    def load_products(date=None, start=None, end=None):
        nonlocal products, total_units, total_sales
        total_units = 0
        total_sales = 0
        conn = get_connection()
        
        if not date and not start and not end:
            orders = order_history(conn)
            products = get_menu(conn)
            for p in products:
                p["units_sold"] = 0
                p["percent_units"] = 0
                p["percent_sales"] = 0

            for order in orders:
                for item in order["items"]:
                    for p in products:
                        if item["p_name"] == p["p_name"]:
                            p["units_sold"] += int(item["quantity"])

            total_units = sum(product["units_sold"] for product in products)
            total_sales = sum((product["units_sold"] * product['price']) for product in products)
            for p in products:
                p["percent_units"] = ((p["units_sold"] / total_units) * 100) if total_units else 0
                p["percent_sales"] = (((p["units_sold"] * p['price']) / total_sales ) * 100) if total_sales else 0
                    
            products[:] = insertionSort(products, "units_sold")
        elif date and not start and not end:
            orders = get_specific_history(conn, date)
            products = get_menu(conn)
            for p in products:
                p["units_sold"] = 0
                p["percent_units"] = 0
                p["percent_sales"] = 0
            for order in orders:
                for item in order["items"]:
                    for p in products:
                        if item["p_name"] == p["p_name"]:
                            p["units_sold"] += int(item["quantity"])
                
            total_units = sum(product["units_sold"] for product in products) 
            total_sales = sum((product["units_sold"] * product['price']) for product in products) 
            for p in products:
                p["percent_units"] = ((p["units_sold"] / total_units) * 100) if total_units else 0
                p["percent_sales"] = (((p["units_sold"] * p['price']) / total_sales ) * 100) if total_sales else 0
                                
            products[:] = insertionSort(products, "units_sold")
        else:
            orders = get_history_by_date_range(conn, start, end)
            products = get_menu(conn)
            for p in products:
                p["units_sold"] = 0
                p["percent_units"] = 0
                p["percent_sales"] = 0
            for order in orders:
                for item in order["items"]:
                    for p in products:
                        if item["p_name"] == p["p_name"]:
                            p["units_sold"] += int(item["quantity"])
                            
            total_units = sum(product["units_sold"] for product in products) 
            total_sales = sum((product["units_sold"] * product['price']) for product in products) 
            for p in products:
                p["percent_units"] = ((p["units_sold"] / total_units) * 100) if total_units else 0
                p["percent_sales"] = (((p["units_sold"] * p['price']) / total_sales ) * 100) if total_sales else 0
                                            
            products[:] = insertionSort(products, "units_sold")

        

    load_products()
    best_seller = products[0] if products else {"p_name": "", "units_sold": 0, "img": "", "price": 0}


    def on_date_picked(e: ft.Event[ft.DatePicker]):
        start_date = e.control.start_value + datetime.now().astimezone().utcoffset()
        end_date = e.control.end_value + datetime.now().astimezone().utcoffset()
        start = start_date.strftime("%Y-%m-%d")
        end = end_date.strftime("%Y-%m-%d")
        load_products(None, start, end)
        refresh_statistics()
    
    def period_selected(period):
        nonlocal active_period
        active_period = period
        if period == "ALL-TIME":
            load_products()
        elif period == "THIS MONTH":
            load_products(datetime.now().strftime("%Y-%m"))
        elif period == "THIS YEAR":
            load_products(datetime.now().strftime("%Y"))
            print(active_period)
        elif period == "DATE PICKER":
            app.page.show_dialog(ft.DateRangePicker(on_change=on_date_picked))
            
        refresh_statistics()
    
    def build_period_bar():
        def tab(label, icon=None):
            selected = label == active_period
            row = [
                ft.Text(
                    label,
                    size=14,
                    color="white",
                    font_family="Anton",
                )
            ]
            if icon:
                row.append(ft.Icon(icon, color="white", size=18))
            
            return ft.Container(
                content=ft.Row(row, spacing=4, tight=True),
                bgcolor="white,0.40" if selected else None,
                border_radius=ft.BorderRadius.all(20),
                padding=ft.Padding.symmetric(horizontal=12, vertical=6),
                on_click=lambda e, l=label: period_selected(l),
            )
    
        return ft.Container(
            height=60,
            bgcolor=BROWN,
            padding=ft.Padding.symmetric(horizontal=8),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_AROUND,
                controls=[
                    tab("ALL-TIME"),
                    tab("THIS YEAR"),
                    tab("THIS MONTH"),
                    tab("DATE PICKER", ft.Icons.CALENDAR_MONTH),
                ],
            ),
        )
    
    period_bar_holder = ft.Container()
    
    def build_best_seller_card():
        img_src = best_seller.get("img") if best_seller else None
        if img_src:
            picture = ft.Image(
                src=img_src,
                width=160,
                height=90,
                fit=ft.BoxFit.COVER,
                border_radius=ft.BorderRadius.all(15),
            )
        else:
            picture = ft.Container(
                width=130,
                height=90,
                bgcolor="#f3dcae",
                border_radius=ft.BorderRadius.all(15),
                alignment=ft.Alignment.CENTER,
                content=ft.Icon(ft.Icons.CAKE, color=TERRACOTTA, size=40),
            )
    
        units = best_seller.get("units_sold", "") if best_seller else ""
        return ft.Container(
            expand=1,
            height=250,
            bgcolor=CARD_BG,
            border=ft.Border.all(3, TERRACOTTA),
            border_radius=ft.BorderRadius.all(15),
            padding=ft.Padding.all(8),
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=6,
                controls=[
                    ft.Text(
                        "BEST SELLING\nPRODUCT",
                        size=22,
                        text_align=ft.TextAlign.CENTER,
                        color=TERRACOTTA,
                        font_family="Anton",
                        weight=ft.FontWeight.W_600,
                    ),
                    ft.Container(
                        bgcolor="white",
                        border_radius=ft.BorderRadius.all(18),
                        padding=ft.Padding.all(8),
                        shadow=ft.BoxShadow(
                            blur_radius=8, color="#30000000", offset=ft.Offset(0, 2)
                        ),
                        content=ft.Column(
                            spacing=0,
                            alignment=ft.Alignment.CENTER,
                            controls=[
                                picture,
                                ft.Container(height=4),
                                ft.Text(
                                    best_seller.get("p_name", "") if best_seller else "",  
                                    size=14,
                                    color=BROWN,
                                    font_family="Poppins-Bold",
                                    weight=ft.FontWeight.BOLD,
                                    max_lines=1,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                ),
                                ft.Text(
                                    f"{units} units" if units != "" else "",  
                                    size=11,
                                    color=BROWN,
                                    font_family="Poppins",
                                ),
                            ],
                        ),
                    ),
                ],
            ),
        )

    click = {"status" : "percent_sales"}
    
    def build_pie_chart(key):
        if not products:
            return fch.PieChart(
                sections=[
                    fch.PieChartSection(
                        value=1, 
                        color="#ead9b8", 
                        radius=45, 
                        title=""
                    )
                ],
                sections_space=0,
                center_space_radius=0,
                height=100,
                width=100,
            )
        return fch.PieChart(
            sections=[
                fch.PieChartSection(
                    value=p[key],
                    title=f"{p[key]:.0f}%",
                    color=DEFAULT_PIE_COLORS[i % len(DEFAULT_PIE_COLORS)],
                    radius=50,
                    title_style=ft.TextStyle(
                        size=7, 
                        color="black", 
                        font_family="Poppins-Bold"
                    ),
                )
                for i, p in enumerate(products)
            ],
            sections_space=0,
            center_space_radius=0,
            height=100,
            width=100,
            margin=ft.Margin.only(bottom=5)
        )
    
    def build_legend():
        return ft.Column(
            spacing=2,
            alignment=ft.MainAxisAlignment.END,
            controls=[
                ft.Row(
                    spacing=4,
                    controls=[
                        ft.Container(
                            width=8,
                            height=8,
                            border_radius=ft.BorderRadius.all(4),
                            bgcolor=DEFAULT_PIE_COLORS[i % len(DEFAULT_PIE_COLORS)],
                        ),
                        ft.Text(
                            p["p_name"],
                            size=8,
                            color="black",
                            font_family="Poppins",
                            expand=True,
                        ),
                    ],
                )
                for i, p in enumerate(products)
            ],
        )
    
    pie_chart = ft.Container(
        content=build_pie_chart("percent_sales"),
        on_click=lambda e: update_sales_card(e),
    )

    total_units = sum(product["units_sold"] for product in products)
    total_sales = sum((product["units_sold"] * product['price']) for product in products)
    overall_sales = {"status" : total_sales}

    def update_sales_card(e):
        if click["status"] == "percent_sales":
            click["status"] = "percent_units"
            sales_text.value = f"{total_units} units"
        else:
            click["status"] = "percent_sales"
            sales_text.value = f"₱ {str(total_sales)}"

        pie_chart.content = build_pie_chart(click["status"])
        sales_text.update()
        pie_chart.update()

    sales_text = ft.Text(
        f"₱ {str(total_sales)}",
        size=20,
        color="#4a2c20",
        font_family="Anton",
    )
    
    overall_sales_card = ft.Container(
            expand=1,
            height=250,
            bgcolor=CARD_BG,
            border=ft.Border.all(3, TERRACOTTA),
            border_radius=ft.BorderRadius.all(15),
            padding=ft.Padding.all(8),
            content=ft.Column(
                scroll=ft.ScrollMode.AUTO,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=4,
                tight=True,
                controls=[
                    ft.Text(
                        "OVERALL SALES:",
                        size=22,
                        color=TERRACOTTA,
                        font_family="Anton",
                        weight=ft.FontWeight.W_600,
                    ),
                    sales_text,
                    pie_chart,
                    build_legend(),
                ],
            ),
        )
    
      # ------------------------------ RANKING TABLE ------------------------------
    W_RANK, W_UNITS, W_REV = 48, 52, 88
    
    def header_cell(text, width=None, expand=False):
        return ft.Container(
            width=width,
            expand=expand,
            height=34,
            bgcolor="#fcf7ea",
            border_radius=ft.BorderRadius.all(8),
            alignment=ft.Alignment.CENTER,
            content=ft.Text(
                text,
                size=13,
                color=TERRACOTTA,
                font_family="Anton",
                text_align=ft.TextAlign.CENTER,
            ),
        )
    
    def body_cell(content, width=None, expand=False):
        return ft.Container(
            width=width,
            expand=expand,
            alignment=ft.Alignment.CENTER,
            content=content,
        )
    
    def table_text(value, size=12):
        return ft.Text(
            str(value),
            size=size,
            color=BROWN,
            font_family="Poppins-Bold",
            weight=ft.FontWeight.BOLD,
            text_align=ft.TextAlign.CENTER,
        )
    
    def vline():
        return ft.Container(width=1, bgcolor=LINE)
    
    def build_row(index, item):
        if item is None:
            rank_c = ft.Text("")
            name_c = ft.Text("")
            units_c = ft.Text("")
            rev_c = ft.Text("")
        else:
            rank_text = ft.Text(
                str(index + 1),
                size=22,
                color=BROWN,
                font_family="Anton",
            )
            rank_c = (
                ft.Row(
                    controls=[
                        ft.Icon(
                            ft.Icons.STAR, 
                            color="#4a2c20", 
                            size=18
                        ), 
                        rank_text
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=0,
                )
                if index == 0
                else rank_text
            )
        name_c = table_text(item["p_name"])      
        units_c = table_text(item["units_sold"])    
        rev_c = table_text(item["units_sold"] * item["price"])    
    
        return ft.Container(
            height=46,
            bgcolor=ROW_BG,
            border=ft.Border.only(bottom=ft.BorderSide(1.5, LINE)),
            content=ft.Row(
                spacing=0,
                controls=[
                    body_cell(rank_c, width=W_RANK),
                    vline(),
                    body_cell(name_c, expand=True),
                    vline(),
                    body_cell(units_c, width=W_UNITS),
                    vline(),
                    body_cell(rev_c, width=W_REV),
                ],
            ),
        )
    
    def build_ranking_table():
        rows = []
        for i, item in enumerate(products):
            rows.append(build_row(i, item))
    
        return ft.Container(
            bgcolor=TABLE_BG,
            border=ft.Border.all(2, LINE),
            border_radius=ft.BorderRadius.all(30),
            padding=ft.Padding.all(12),
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=8,
                controls=[
                    ft.Text(
                        "RANKING OF PRODUCTS",
                        size=30,
                        color=BROWN,
                        font_family="Anton",
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Row(
                        spacing=4,
                        controls=[
                            header_cell("Rank", width=W_RANK),
                            header_cell("Product Name", expand=True),
                            header_cell("Unit sold", width=W_UNITS),
                            header_cell("Total revenue", width=W_REV),
                        ],
                    ),
                    ft.Column(
                        spacing=0, 
                        controls=rows
                    ),
                ],
            ),
        )

    body_holder = ft.Column(
        scroll=ft.ScrollMode.AUTO,
        expand=True,
        spacing=0,
    )

    def refresh_sales_card():
        if click["status"] == "percent_sales":
            sales_text.value = f"₱ {total_sales}"
        else:
            sales_text.value = f"{total_units} units"
        pie_chart.content = build_pie_chart(click["status"])
        overall_sales_card.content.controls[3] = build_legend() 

    def refresh_statistics():
        nonlocal best_seller
        best_seller = products[0] if products else {"p_name": "", "units_sold": 0, "img": "", "price": 0}
        refresh_sales_card()
        period_bar_holder.content = build_period_bar()
        body_holder.controls = [
            ft.Container(
                padding=ft.Padding.only(left=12, right=12, top=14),
                content=ft.Row(
                    spacing=10,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    controls=[build_best_seller_card(), overall_sales_card],
                ),
            ),
            ft.Container(
                margin=ft.Margin.symmetric(horizontal=20, vertical=14),
                height=2,
                bgcolor=LINE,
            ),
            ft.Container(
                padding=ft.Padding.only(left=10, right=10, bottom=16),
                content=build_ranking_table(),
            ),
        ]
        app.page.update()

    view = ft.Column(
        expand=True,
        spacing=0,
        controls=[period_bar_holder, body_holder],
    )

    refresh_statistics()

    def on_show():
        nonlocal active_period
        active_period = None
        load_products()
        refresh_statistics()

    return view, on_show