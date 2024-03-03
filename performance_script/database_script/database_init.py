from database_script.mongodb_init import insert_data_into_mongodb
from database_script.mysql_init import insert_data_into_mysql
from database_script.neo4j_init import insert_data_into_neo4j


def populate_data(data=50):
    insert_data_into_mongodb(data)
    insert_data_into_mysql(data)
    insert_data_into_neo4j(data)

if __name__ == "__main__":
    populate_data()
    print("Data inserted into all databases")