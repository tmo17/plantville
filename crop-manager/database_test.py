import argparse
from database_manager import DatabaseManager
import os
from dotenv import load_dotenv

def main(server, database, username, password,port, operation,table_name):
    db_manager = DatabaseManager(server=server, database=database,port=port, username=username, password=password)
    
    if operation.lower() == 'create':
        print("Initializing data in the database...")
        db_manager.initialize('init_plants.json')
        print("Data initialization complete.")
    elif operation.lower() == 'delete':
        print("Deleting all data from the database...")
        db_manager.delete(table_name)
        print("All data deleted.")
    elif operation.lower() == 'drop_table':
        if table_name is None:
            table_name = input("Enter the table name to drop: ")
        db_manager.drop_table(table_name)
    elif operation.lower() == 'print_tables':
        db_manager.print_tables(table_name)
    elif operation.lower() == 'drop_all_tables':
        db_manager.drop_all_tables()


        

    else:
        print(f"Invalid operation: {operation}. Please specify 'create' or 'delete'.")
    db_manager.close()

if __name__ == "__main__":
    load_dotenv()
    server = os.getenv('DB_SERVER')
    database = os.getenv('DB_DATABASE')
    username = os.getenv('DB_USERNAME')
    password = os.getenv('DB_PASSWORD')
    port = os.getenv('DB_PORT')


    
    parser = argparse.ArgumentParser(description='Manage SQL Server database initialization.')
    parser.add_argument('--operation', type=str, required=True, choices=['create', 'delete','drop_table','print_tables','drop_all_tables'], help='Operation to perform: "create" or "delete"')    
    parser.add_argument('--table', type=str, required=False, help='Table on which to perform operations',default=None)

    args = parser.parse_args()

    print(f"Server: {server}")
    print(f"Database: {database}")
    print(f"Username: {username}")
    print(f"Password: {password}")
    print(f"Port: {port}")
    print(f"Operation: {args.operation}")
    print(f"Table: {args.table}")
    
    main(server=server, database=database, username=username,port=port, password=password, operation=args.operation,table_name=args.table)
