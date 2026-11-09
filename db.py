import os
import sqlite3
import shutil
from pathlib import Path
from datetime import datetime, timedelta

BUNDLED_DB = Path(__file__).resolve().parent / "project.db"

def get_connection():
    app_data_path = os.getenv("FLET_APP_STORAGE_DATA")

    if app_data_path:
        db_path = Path(app_data_path) / "project.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)
        if not db_path.exists() and BUNDLED_DB.exists():
            shutil.copy(BUNDLED_DB, db_path)   # first launch: seed with your data
    else:
        db_path = BUNDLED_DB                   # running locally in VS Code

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(conn):
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS menu (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            p_name TEXT NOT NULL UNIQUE,
            price INTEGER NOT NULL,
            units_left INTEGER DEFAULT 0,
            img TEXT DEFAULT ''
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            c_name TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            order_type TEXT NOT NULL,
            address TEXT NOT NULL,
            order_time TEXT NOT NULL,
            order_date TEXT NOT NULL,
            type_date TEXT NOT NULL,
            type_time TEXT NOT NULL,
            total INTEGER
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            menu_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(id),
            FOREIGN KEY (menu_id) REFERENCES menu(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            ingredient_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            unit TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            img TEXT 
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTs batches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ingredient_id INTEGER NOT NULL,
            purchase_date TEXT NOT NULL,
            expiration_date TEXT NOT NULL,
            FOREIGN KEY (ingredient_id) REFERENCES inventory(ingredient_id)
        )
    ''')

    print("ok")
    conn.commit()

def add_menu(conn, p_name, price, img, units=0):
    cursor = conn.cursor()
    try:
        if not p_name or p_name == "" or price is None:
            return "Product name and price cannot be empty."

        for row in get_menu(conn):
            if row['p_name'] == p_name:
                return "Menu item already exists."
        else:
            cursor.execute('''
                INSERT INTO menu(p_name, price, img, units_left)
                VALUES (?, ?, ?, ?)
            ''', (p_name, price, img, units))
            conn.commit()
    except sqlite3.IntegrityError as e:
        print(f"Failed to add menu item: {e}")

def update_menu(conn, menu_id, p_name, price, img, units):
    cursor = conn.cursor()
    try:
        if not p_name or p_name == "" or price is None:
            return "Product name and price cannot be empty."

        same=0
        for row in get_menu(conn):
            if row['p_name'] == p_name:
                same += 1
        if same > 1:
            return "Menu item already exists."
        else:
            cursor.execute('''
                UPDATE menu
                SET p_name = ?, price = ?, img = ?, units_left = ?
                WHERE id = ?
            ''', (p_name, price, img,units, menu_id))
            conn.commit()

            print('updated')
    except sqlite3.Error as e:
        print(f"Failed to update menu item: {e}")

def delete_menu(conn, menu_id):
    cursor = conn.cursor()
    try:
        cursor.execute('''
            DELETE FROM menu
            WHERE id = ?
        ''', (menu_id,))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Failed to delete menu item: {e}")

def get_menu(conn):
    c = conn.cursor()
    c.execute("SELECT *, price FROM menu")
    rows = c.fetchall()
    return [dict(row) for row in rows]

def new_order(conn, c_name, status, order_type, address, order_time, order_date, type_date, type_time):
    cursor = conn.cursor()

    try:
        if not c_name or not status or not order_type or not address or not order_time or not order_date:
            return "Complete the required values"
        
        cursor.execute('''
            INSERT INTO orders (c_name, status, order_type, address, order_time, order_date, type_date, type_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)

        ''', (c_name, status, order_type, address, order_time, order_date, type_date, type_time)
        )

        order_id = cursor.lastrowid

        print("nasave sa db")

        conn.commit()

        return order_id
    except sqlite3.Error as e:
            conn.rollback()
            print(f"Failed to create order: {e}")
            return None

def add_order_items(conn, order_id, items, menu):
    cursor = conn.cursor()

    for item in items:
        for m in menu:
            if item["p_name"] == m["p_name"]:
                item["menu_id"] = m["id"] 
                if m["units_left"] != 0:
                    m["units_left"] -= item["quantity"]
       
    try:
        cursor.executemany('''
            INSERT INTO order_items (order_id, menu_id, quantity)
            VALUES (?,?,?)
        ''', [(order_id, item["menu_id"], item["quantity"]) for item in items]
        )

        cursor.executemany(
            """
                UPDATE menu
                SET units_left = ?
                WHERE id = ?
            """,
            [(m["units_left"], m["id"]) for m in menu]
        )

        conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        print(f"Failed to add order items: {e}")

def insert_total(conn, order_id, total):
    cursor = conn.cursor()

    try:
        cursor.execute('''
            UPDATE orders
            SET total = ?
            WHERE id = ?
        ''', (total, order_id)
        )

        conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        print(f"Failed to update total: {e}")

def update_order(conn, order_id, c_name, order_type, address, order_time, order_date,type_date, type_time, total, items, menu):
    c = conn.cursor()
    try:        
        for item in items:
            for m in menu:
                if item["p_name"] == m["p_name"]:
                    item["menu_id"] = m["id"] 
                    if m["units_left"] != 0:
                        m["units_left"] -= item["quantity"]
        
        if not c_name  or not order_type or not address or not order_time or not order_date or total is None:
            return "Complete the required values"
        
        
        c.execute('''
            UPDATE orders
            SET c_name = ?, order_type = ?, address = ?, order_time = ?, order_date = ?, total = ?, type_date = ?, type_time = ?
            WHERE id = ?
        ''', (c_name, order_type, address, order_time, order_date, total,type_date, type_time, order_id))

        c.execute('DELETE FROM order_items WHERE order_id = ?', (order_id,))

        c.executemany(
            '''
                INSERT INTO order_items (order_id, menu_id, quantity)
                VALUES (?,?,?)
            ''', [(order_id, item["menu_id"], item["quantity"]) for item in items]
        )
        
        c.executemany(
            """
                UPDATE menu
                SET units_left = ?
                WHERE id = ?
            """,
            [(m["units_left"], m["id"]) for m in menu]
        )

        conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        print(f"Failed to update order: {e}")

def active_queue(conn):
    c = conn.cursor()
    try:
        c.execute('''
            SELECT *
            FROM orders
            WHERE status = 'PENDING' OR status = 'pending'    
        ''')

        rows = c.fetchall()

        order_list = [dict(row) for row in rows]

        for order in order_list:
            c.execute('''
                SELECT m.p_name, oi.quantity
                FROM order_items oi
                JOIN menu m ON m.id = oi.menu_id
                WHERE oi.order_id = ?
            ''', (order["id"],))
            order_items = c.fetchall()
            order['items'] = [dict(item) for item in order_items]

        return order_list
    
    except sqlite3.Error as e:
        print(f"Failed to retrieve active queue: {e}")
        print("may mali")
        return []    

def order_history(conn):
    c = conn.cursor()
    print("history")
    try:
        c.execute('''
            SELECT *
            FROM orders
            WHERE status != 'PENDING'
        ''',)

        rows = c.fetchall()

        order_list = [dict(row) for row in rows]

        for order in order_list:
            order_id = order['id']
            c.execute('''
                SELECT m.p_name, oi.quantity
                FROM order_items oi
                JOIN menu m ON m.id = oi.menu_id
                WHERE oi.order_id = ?
            ''', (order_id,))
            order_items = c.fetchall()
            order['items'] = [dict(item) for item in order_items]

        return order_list
    except sqlite3.Error as e:
        print(f"Failed to retrieve order history: {e}")
        return []

def update_status(conn, order_id, status):
    try:
        conn.execute("UPDATE orders SET status = ? WHERE id = ?", (status, order_id))
        conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        print(f"Failed to update status: {e}")

def get_order_count_today():
    today_str = datetime.now().strftime("%Y-%m-%d")
    conn = get_connection()
    try:
        cursor = conn.cursor()
        # FIXED: Added * inside COUNT(*)
        cursor.execute("SELECT COUNT(*) FROM orders WHERE order_date = ?", (today_str,))
        count = cursor.fetchone()[0]
        return count
    except sqlite3.Error as e:
        print(f"Error fetching today's order count: {e}")
        return 0
    finally:
        conn.close()

def get_order_count_tomorrow():
    tomorrow_str = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM orders WHERE order_date = ?", (tomorrow_str,))
        count = cursor.fetchone()[0]
        return count
    except sqlite3.Error as e:
        print(f"Error fetching tomorrow's order count: {e}")
        return 0
    finally:
        conn.close()

def get_orders_today():
    today_str = datetime.now().strftime("%Y-%m-%d")
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM orders WHERE order_date = ? ORDER BY order_time ASC", (today_str,))
        orders = cursor.fetchall()
        return [dict(o) for o in orders]
    except sqlite3.Error as e:
        print(f"Error fetching today's orders: {e}")
        return []
    finally:
        conn.close()

def get_orders_tomorrow():
    tomorrow_str = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM orders WHERE order_date = ? ORDER BY order_time ASC", (tomorrow_str,))
        orders = cursor.fetchall()
        return [dict(o) for o in orders]
    except sqlite3.Error as e:
        print(f"Error fetching tomorrow's orders: {e}")
        return []
    finally:
        conn.close()

def get_orders_by_specific_day(conn, target_day: str):
    print("gumana day start")
    try:
        cursor = conn.cursor()
        cursor.execute("""SELECT * 
                        FROM orders 
                        WHERE type_date = ?
                        AND status = 'PENDING' OR status = 'pending' 
                        ORDER BY order_time ASC""", (target_day,))
        rows = cursor.fetchall()
        
        order_list = [dict(row) for row in rows]
        
        for order in order_list:
            cursor.execute('''
                SELECT m.p_name, oi.quantity
                FROM order_items oi
                JOIN menu m ON m.id = oi.menu_id
                WHERE oi.order_id = ?
            ''', (order["id"],))

            order_items = cursor.fetchall()
            order['items'] = [dict(item) for item in order_items]
        
        return order_list
    except sqlite3.Error as e:
        print(f"Error fetching orders for date {target_day}: {e}")
        return []
    finally:
        conn.close()

def get_history_by_date_range(conn, start_date, end_date: str):
    print("date range")
    print(start_date,end_date)
    try:
        cursor = conn.cursor()
        cursor.execute("""SELECT id, c_name, status, order_type, address, order_time, order_date, total 
                        FROM orders 
                        WHERE status != 'PENDING' AND order_date BETWEEN ? AND ?
                        ORDER BY order_time ASC""", (start_date,end_date),)
        rows = cursor.fetchall()
        
        order_list = [dict(row) for row in rows]
        
        for order in order_list:
            cursor.execute('''
                SELECT m.p_name, oi.quantity
                FROM order_items oi
                JOIN menu m ON m.id = oi.menu_id
                WHERE oi.order_id = ?
            ''', (order["id"],))

            order_items = cursor.fetchall()
            order['items'] = [dict(item) for item in order_items]
        
        return order_list
    except sqlite3.Error as e:
        print(f"Error fetching orders for date {start_date,end_date}: {e}")
        return []

def get_orders_by_specific_month(conn, year_month: str):
    print("gumana months start")
    print(year_month)
    cursor = conn.cursor()
    try:
        cursor.execute("""
        SELECT * FROM orders 
        WHERE type_date LIKE ? 
        AND status = 'PENDING' OR status = 'pending' 
        ORDER BY order_date ASC""", (f"%-{year_month}-%",))
        rows = cursor.fetchall()

        order_list = [dict(row) for row in rows]
        print(order_list)
        for order in order_list:
            cursor.execute('''
            SELECT m.p_name, oi.quantity
            FROM order_items oi
            JOIN menu m ON m.id = oi.menu_id
            WHERE oi.order_id = ?
        ''', (order["id"],))
            order_items = cursor.fetchall()
            order['items'] = [dict(item) for item in order_items]
                
        return order_list
    
    except sqlite3.Error as e:
        print(f"Error fetching orders for month {year_month}: {e}")
        return []
    finally:
        conn.close()

def get_specific_history(conn, year_month: str):
    print("gumana months start")
    print(year_month)
    cursor = conn.cursor()
    try:
        cursor.execute("""
        SELECT * FROM orders 
        WHERE order_date LIKE ? AND status != 'PENDING'
        """, (f"{year_month}-%",))
        rows = cursor.fetchall()

        order_list = [dict(row) for row in rows]
        print(order_list)
        for order in order_list:
            cursor.execute('''
            SELECT m.p_name, oi.quantity
            FROM order_items oi
            JOIN menu m ON m.id = oi.menu_id
            WHERE oi.order_id = ?
        ''', (order["id"],))
            order_items = cursor.fetchall()
            order['items'] = [dict(item) for item in order_items]
                
        return order_list
    
    except sqlite3.Error as e:
        print(f"Error fetching orders for month {year_month}: {e}")
        return []
    
def get_order_items_by_order_id(order_id: int):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT oi.qty, m.p_name, m.price
            FROM order_items oi
            JOIN menu m ON oi.menu_id = m.id
            WHERE oi.order_id = ?
        ''', (order_id,))
        items = cursor.fetchall()
        return [dict(i) for i in items]
    except sqlite3.Error as e:
        print(f"Error fetching items for order {order_id}: {e}")
        return []
    finally:
        conn.close()

def get_inventory_list(conn):
  c = conn.cursor()
  try:
    c.execute("SELECT ingredient_id, name, unit, quantity, img FROM inventory")
    rows = c.fetchall()
    inventory_list = [dict(row) for row in rows]

    for item in inventory_list:
        ingredient_id = item["ingredient_id"]
        c.execute(
            """
                    SELECT id AS batch_id, purchase_date, expiration_date
                    FROM batches
                    WHERE ingredient_id = ?
                """,
            (ingredient_id,),
        )
        batches = c.fetchall()
        item["batches"] = [dict(b) for b in batches]
    conn.close()
    return inventory_list
  except sqlite3.Error as e:
    print(f"Failed to retrieve inventory list: {e}")
    return []

def update_qty(conn, ingredient_id, quantity):
    c = conn.cursor()
    try:
        c.execute(
            """
            UPDATE inventory
            SET quantity = ?
            WHERE ingredient_id = ?
            """,
            (quantity, ingredient_id),
        )
        print(quantity)
        conn.commit()
    except sqlite3.Error as e:
        print(f"Failed to update ingredient: {e}")
        return None
    
def add_ingredient(conn, name, unit, quantity, expiry, img):
    cursor = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
    try:
        if not name or not unit:
            return "Ingredient name and unit cannot be empty."

        cursor.execute(
            """
                INSERT INTO inventory (name, unit, quantity, img)
                VALUES (?, ?, ?, ?)
            """,
            (name, unit, quantity, img),
        )
        ingredient_id = cursor.lastrowid
        print("added ingre")
        cursor.execute(
            """
                INSERT INTO batches (ingredient_id, purchase_date, expiration_date)
                VALUES (?,?,?)
            """,
            (ingredient_id, today, expiry)
        )
        conn.commit()
        print("added batch")
        

        conn.close()

        return ingredient_id
    
    except sqlite3.Error as e:
        print(f"Failed to add ingredient: {e}")
        return None

def add_batch(conn, ingredient_id, expiration_date, quantity, current_qty):
    cursor = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
    try:
        if quantity is None or not expiration_date:
            return "Complete the required batch values."

        cursor.execute(
            """
                INSERT INTO batches (ingredient_id, purchase_date, expiration_date)
                VALUES (?, ?, ?)
            """,
            (ingredient_id, today, expiration_date),
        )

        total = int(current_qty) + int(quantity)

        cursor.execute(
            """
                UPDATE inventory
                SET quantity = ?
                WHERE ingredient_id = ?
            """,
            (total, ingredient_id)
        )

        conn.commit()
        batch_id = cursor.lastrowid
        conn.close()
        return batch_id
    except sqlite3.Error as e:
        conn.rollback()
        print(f"Failed to add batch: {e}")
        return None

def delete_batch(conn, batch_id):
    c = conn.cursor()

    try:
        c.execute(
            """
                DELETE FROM batches
                WHERE batch_id = ?
            """,
            (batch_id,)
        )
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error fetching deleting batch: {e}")
        return

def delete_ingredient(conn, ingredient_id):
    c= conn.cursor()

    try:
        c.execute(
            """
                DELETE FROM inventory
                WHERE ingredient_id = ?
            """,
            (ingredient_id,)
        )
        print("ingre deleted")
        c.execute(
            """
                DELETE FROM batches
                WHERE ingredient_id = ?
            """,
            (ingredient_id,)
        )
        print("barches deleted")
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error fetching deleting ingredient: {e}")
        return

if __name__ == "__main__":
    conn = get_connection()
    init_db(conn)

    today = datetime.now()

    def day(offset):
        return (today + timedelta(days=offset)).strftime("%Y-%m-%d")

    # Fixed and cleaned sample menu items with prices
    sample_menu = [
        ("Leche Flan", 110,"images/lecheflan.png"),
        ("Yema Cake",80, "images/yemacake.png"),
        ("Banana Cake", 100,"images/bananabread.png"),
        ("Maja Blanca", 700, "images/majablanca.png"),
        ("Cheesy Mamon", 60, "images/mamoncake.png"),
        ("Yema Palitaw", 60, "images/yemapalitaw.png"),
        ("H&C Muffins", 15, "images/hamandcheesemuffins.png"),
    ]

    for p_name, price, img in sample_menu:
        error = add_menu(conn, p_name, price, img)
        if error:
            print(f"{p_name}: {error}")

    menu_rows = get_menu(conn)
    print(menu_rows)
    menu_dict = {m['p_name']: m for m in menu_rows}

    # Fixed and clean sample orders with correct calculated totals
    sample_menu = [
        ("Leche Flan", 110,"images/lecheflan.png"),
        ("Yema Cake",80, "images/yemacake.png"),
        ("Banana Cake", 100,"images/bananabread.png"),
        ("Maja Blanca", 700, "images/majablanca.png"),
        ("Cheesy Mamon", 60, "images/mamoncake.png"),
        ("Yema Palitaw", 60, "images/yemapalitaw.png"),
        ("H&C Muffins", 15, "images/hamandcheesemuffins.png"),
    ]

    for p_name, price, img in sample_menu:
        error = add_menu(conn, p_name, price, img)
        if error:
            print(f"{p_name}: {error}")

    menu_rows = get_menu(conn)
    print(menu_rows)
    menu_dict = {m['p_name']: m for m in menu_rows}

    # Fixed and clean sample orders with correct calculated totals
    sample_orders = [
        {
            "c_name": "Jane Doe",
            "status": "PENDING",
            "order_type": "DELIVERY",
            "address": "456 Rose Street, Apt 2B",
            "order_time": "18:45",
            "order_date": "2026-11-08",
            "type_time": "10:00 AM",
            "type_date": "2026-11-09",
            "items": [
                {"p_name": "Leche Flan", "quantity": 2},
                {"p_name": "Yema Cake", "quantity": 1},
                {"p_name": "H&C Muffins", "quantity": 5},
            ],
        },
        {
            "c_name": "Mark Santos",
            "status": "PENDING",
            "order_type": "PICKUP",
            "address": "Walk-in",
            "order_time": "12:30",
            "order_date": "2026-11-08",
            "type_time": "05:00 PM",
            "type_date": "2026-11-08",
            "items": [
                {"p_name": "Cheesy Mamon", "quantity": 4},
                {"p_name": "Yema Palitaw", "quantity": 3},
            ],
        },
        {
            "c_name": "Ana Reyes",
            "status": "PENDING",
            "order_type": "DELIVERY",
            "address": "12 Mabini Street, Malolos",
            "order_time": "19:15",
            "order_date": "2026-11-08",
            "type_time": "03:30 PM",
            "type_date": "2026-11-10",
            "items": [
                {"p_name": "Maja Blanca", "quantity": 1},
                {"p_name": "Banana Cake", "quantity": 2},
            ],
        },
        {
            "c_name": "Carlo Mendoza",
            "status": "PENDING",
            "order_type": "DELIVERY",
            "address": "88 Sampaguita Avenue",
            "order_time": "11:00",
            "order_date": "2026-11-09",
            "type_time": "09:00 AM",
            "type_date": "2026-11-11",
            "items": [
                {"p_name": "Yema Cake", "quantity": 2},
                {"p_name": "H&C Muffins", "quantity": 10},
            ],
        },
        {
            "c_name": "Liza Cruz",
            "status": "PENDING",
            "order_type": "PICKUP",
            "address": "Walk-in",
            "order_time": "16:20",
            "order_date": "2026-11-11",
            "type_time": "02:00 PM",
            "type_date": "2026-11-12",
            "items": [
                {"p_name": "Leche Flan", "quantity": 3},
                {"p_name": "Cheesy Mamon", "quantity": 6},
            ],
        },
        {
            "c_name": "Ben Garcia",
            "status": "DONE",
            "order_type": "DELIVERY",
            "address": "7 Rizal Street",
            "order_time": "20:05",
            "order_date": "2026-11-07",
            "type_time": "09:30 PM",
            "type_date": "2026-11-07",
            "items": [
                {"p_name": "Banana Cake", "quantity": 1},
                {"p_name": "Yema Palitaw", "quantity": 2},
                {"p_name": "H&C Muffins", "quantity": 4},
            ],
        },
        {
            "c_name": "Rica Villanueva",
            "status": "DONE",
            "order_type": "PICKUP",
            "address": "Walk-in",
            "order_time": "13:40",
            "order_date": "2026-11-05",
            "type_time": "04:00 PM",
            "type_date": "2026-11-05",
            "items": [
                {"p_name": "Maja Blanca", "quantity": 2},
            ],
        },
        {
            "c_name": "Paolo Bautista",
            "status": "DONE",
            "order_type": "DELIVERY",
            "address": "21 Bonifacio Road",
            "order_time": "17:10",
            "order_date": "2026-11-03",
            "type_time": "10:30 AM",
            "type_date": "2026-11-04",
            "items": [
                {"p_name": "Leche Flan", "quantity": 4},
                {"p_name": "Yema Cake", "quantity": 2},
            ],
        },
        {
            "c_name": "Nina Flores",
            "status": "CANCELLED",
            "order_type": "DELIVERY",
            "address": "5 Luna Street",
            "order_time": "14:25",
            "order_date": "2026-11-02",
            "type_time": "12:00 PM",
            "type_date": "2026-11-03",
            "items": [
                {"p_name": "Cheesy Mamon", "quantity": 5},
            ],
        },
        {
            "c_name": "Gabriel Torres",
            "status": "DONE",
            "order_type": "PICKUP",
            "address": "Walk-in",
            "order_time": "10:15",
            "order_date": "2026-11-01",
            "type_time": "03:00 PM",
            "type_date": "2026-11-01",
            "items": [
                {"p_name": "Yema Palitaw", "quantity": 4},
                {"p_name": "Banana Cake", "quantity": 1},
            ],
        }
    ]
    
    if conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0] > 0:
        print("orders table already has rows, skipping sample orders")
    else:
        for order in sample_orders:
            order_id = new_order(
                conn,
                order["c_name"],
                order["status"],
                order["order_type"],
                order["address"],
                order["order_time"],
                order["order_date"],
                order["type_date"],
                order["type_time"]
            )
            if not isinstance(order_id, int):
                print(f"{order['c_name']}: {order_id}")
                continue
            
            add_order_items(conn, order_id, order["items"], menu_rows)
            
            # Compute order total correctly from sample menu prices
            total = sum(menu_dict[item["p_name"]]["price"] * item["quantity"] for item in order["items"])
            insert_total(conn, order_id, total)

    # Fixed and cleaned sample inventory data with valid relative expiration windows
    sample_inventory = [
        ("Flour", "KG", 25, [(day(-20), day(160))]),
        ("Sugar", "KG", 18, [(day(-20), day(300))]),
        ("Butter", "KG", 8, [(day(-7), day(21)), (day(-3), day(14))]),
        ("Eggs", "PCS", 120, [(day(-5), day(18)), (day(-2), day(15))]),
        ("Cocoa Powder", "KG", 6, [(day(-40), day(200))]),
        ("Vanilla Essence", "ML", 500, [(day(-60), day(365))]),
        ("Chicken Wings", "KG", 30, [(day(-2), day(5)), (day(-1), day(3))]),
        ("Potatoes", "KG", 40, [(day(-4), day(14))]),
        ("Tea Leaves", "G", 800, [(day(-30), day(240))]),
        ("Ice Cream Mix", "L", 12, [(day(-1), day(35))]),
    ]

    if conn.execute("SELECT COUNT(*) FROM inventory").fetchone()[0] > 0:
        print("inventory table already has rows, skipping sample inventory")
    else:
        try:
            for name, unit, quantity, batches in sample_inventory:
                cursor = conn.execute(
                    "INSERT INTO inventory (name, unit, quantity) VALUES (?, ?, ?)",
                    (name, unit, quantity),
                )
                ingredient_id = cursor.lastrowid
                for purchase_date, expiration_date in batches:
                    conn.execute(
                        "INSERT INTO batches (ingredient_id, purchase_date, expiration_date) VALUES (?, ?, ?)",
                        (ingredient_id, purchase_date, expiration_date),
                    )
            conn.commit()
        except sqlite3.Error as e:
            conn.rollback()
            print(f"Failed to add sample inventory: {e}")

    for table in ("menu", "orders", "order_items", "inventory", "batches"):
        count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"{table}: {count} rows")

    conn.close()

    