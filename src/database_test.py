import argparse
from database_manager import DatabaseManager

def main(server, database, username, password, operation,table_name):
    db_manager = DatabaseManager(server, database, username, password)
    if operation.lower() == 'create':
        print("Initializing data in the database...")
        db_manager.initialize('init_plants.json')
        print("Data initialization complete.")
    elif operation.lower() == 'delete':
        print("Deleting all data from the database...")
        db_manager.delete(table_name)
        print("All data deleted.")
    elif operation.lower() == 'drop_table':
        table_name = input("Enter the table name to drop: ")
        db_manager.drop_table(table_name)

    else:
        print(f"Invalid operation: {operation}. Please specify 'create' or 'delete'.")
    db_manager.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Manage SQL Server database initialization.')
    parser.add_argument('--server', type=str, required=True, help='Database server')
    parser.add_argument('--database', type=str, required=True, help='Database name')
    parser.add_argument('--username', type=str, required=True, help='Username')
    parser.add_argument('--password', type=str, required=True, help='Password')
    parser.add_argument('--operation', type=str, required=True, choices=['create', 'delete','drop_table'], help='Operation to perform: "create" or "delete"')

    parser.add_argument('--table', type=str, required=False, help='Table on which to perform operations',default='CurrentPlants')

    args = parser.parse_args()

    main(args.server, args.database, args.username, args.password, args.operation,args.table)
