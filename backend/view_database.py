import sqlite3
import pandas as pd
from tabulate import tabulate
from colorama import Fore, Style, init

init(autoreset=True)

# Connect to SQLite Database
conn = sqlite3.connect("instance/agrotrace.db")


def title(text):
    print("\n")
    print("=" * 120)
    print(Fore.GREEN + Style.BRIGHT + text.center(120))
    print("=" * 120)


def get_tables():
    query = """
    SELECT name
    FROM sqlite_master
    WHERE type='table'
      AND name NOT LIKE 'sqlite_%'
    ORDER BY name;
    """
    return pd.read_sql_query(query, conn)["name"].tolist()

def show_table(table_name):

    # Important columns for each table
    selected_columns = {
        "users": [
            "id",
            "username",
            "email",
            "full_name",
            "phone",
            "role",
            "city",
            "farm_name",
            "created_at"
        ],

        "crops": [
            "id",
            "unique_crop_id",
            "farmer_id",
            "crop_name",
            "seed_variety",
            "soil_type",
            "farm_size",
            "growth_stage",
            "crop_health",
            "created_at"
        ],

        "supply_chain_records": [
            "id",
            "crop_id",
            "actor_id",
            "actor_role",
            "stage",
            "location",
            "timestamp"
        ],

        "audit_logs": [
            "id",
            "user_id",
            "action",
            "timestamp"
        ]
    }

    df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)

    # Hide sensitive columns
    hide_columns = [
        "password_hash",
        "verification_token",
        "reset_otp",
        "reset_otp_expiry"
    ]

    for col in hide_columns:
        if col in df.columns:
            df.drop(columns=[col], inplace=True)

    # Show only available important columns
    if table_name in selected_columns:
        cols = [c for c in selected_columns[table_name] if c in df.columns]
        if cols:
            df = df[cols]

    title(f"{table_name.upper()} TABLE")

    print(Fore.CYAN + f"Total Records : {len(df)}")
    print(Fore.CYAN + f"Total Columns : {len(df.columns)}\n")

    print(
        tabulate(
            df.fillna(""),
            headers="keys",
            tablefmt="rounded_grid",
            showindex=False
        )
    )

while True:

    tables = get_tables()

    title("🌱 AGROTRACE DATABASE VIEWER")

    print("\nAvailable Tables:\n")

    for i, table in enumerate(tables, start=1):
        print(f"{i}. {table}")

    print(f"{len(tables) + 1}. Record Count")
    print(f"{len(tables) + 2}. Exit")

    try:
        choice = int(input("\nEnter Choice: "))
    except ValueError:
        print(Fore.RED + "Please enter a valid number.")
        continue

    if 1 <= choice <= len(tables):

        show_table(tables[choice - 1])

    elif choice == len(tables) + 1:

        title("DATABASE RECORD COUNT")

        cur = conn.cursor()

        data = []

        for table in tables:
            cur.execute(f"SELECT COUNT(*) FROM {table}")
            data.append([table, cur.fetchone()[0]])

        print(
            tabulate(
                data,
                headers=["Table", "Records"],
                tablefmt="fancy_grid"
            )
        )

    elif choice == len(tables) + 2:
        break

    else:
        print(Fore.RED + "Invalid Choice!")

conn.close()