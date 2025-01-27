import mysql.connector
from Agently import AgentFactory, create_agent

from crawl import setup_db_connection
import Agently
from datetime import datetime





agent = (
    Agently.create_agent()
    .set_settings("current_model", "OAIClient")
        .set_settings("model.OAIClient.auth.api_key", "sk-e6f6e734fe964bc3a2f3f06523de5f98")
        .set_settings("model.OAIClient.url", "https://dashscope.aliyuncs.com/compatible-mode/v1")
        .set_settings("model.OAIClient.options.model", "qwen-turbo")
)


def generate_sql(request):
    meta_data = meta_data_for_DB

    result = (
        agent
        .input(request)

        .info({ "database meta data": meta_data })
        .info({ "current date": datetime.now().date() })
        .instruct([
            "Generate SQL for MySQL database according {database meta data} to answer {request}",
            "Language: English",
        ])
        .output({
            #"thinkings": ("String", "Your thinkings step by step about how to query data to answer {input}"),
            "SQL": ("String", "SQL String without explanation")
        })
        .start()
    )

    return result

def execute_sql(sql_query, params=None):
    """
    Execute an SQL query on the given database connection.
    """
    conn = setup_db_connection()
    cursor = conn.cursor()
    sql_query = sql_query['SQL']
    try:
        cursor.execute(sql_query, params or ())


        if sql_query.strip().lower().startswith("select"):
            results = cursor.fetchall()
            return results


        conn.commit()
        print("Query executed successfully.")

    except Exception as e:
        conn.rollback()
        print("Error while executing query:", e)

    finally:
        cursor.close()

    return None
meta_data_for_DB = [
    {
        "table_name": "USER",
        "columns": [
            {"name": "User_id", "desc": "User ID", "data type": "int", "example": 1, "notes": "Primary Key, Auto Increment"},
            {"name": "Name", "desc": "User Name", "data type": "string", "example": "Warren Edward Buffett"},
            {"name": "Pass_word", "desc": "User Password", "data type": "string", "example": "1234"}
        ]
    },
    {
        "table_name": "RECORD",
        "columns": [
            {"name": "Record_id", "desc": "Record ID", "data type": "int", "example": 1, "notes": "Primary Key, Auto Increment"},
            {"name": "User_id", "desc": "User ID", "data type": "int", "example": 1, "notes": "Foreign Key references USER(User_id)"},
            {"name": "Generate_data", "desc": "Data generation date", "data type": "date", "example": "2024-12-24"},
            {"name": "Company_name", "desc": "Name of the company", "data type": "string", "example": "GS"},
            {"name": "News_number", "desc": "Number of news articles", "data type": "int", "example": 1}
        ]
    },
    {
        "table_name": "RESULT",
        "columns": [
            {"name": "Result_id", "desc": "Result ID", "data type": "int", "example": 1, "notes": "Primary Key, Auto Increment"},
            {"name": "Record_id", "desc": "Record ID", "data type": "int", "example": 1, "notes": "Foreign Key references RECORD(Record_id)"},
            {"name": "report_content", "desc": "Content of the generated report", "data type": "text", "example": "Detailed report content"}
        ]
    },
    {
        "table_name": "NEWS",
        "columns": [
            {"name": "News_id", "desc": "News ID", "data type": "int", "example": 1, "notes": "Primary Key, Auto Increment"},
            {"name": "Record_id", "desc": "Record ID", "data type": "int", "example": 1, "notes": "Foreign Key references RECORD(Record_id)"},
            {"name": "News_link", "desc": "URL link to the news", "data type": "string", "example": "http://example.com"},
            {"name": "content", "desc": "Content of the news article", "data type": "text", "example": "News content"}
        ]
    }
]

'''
if __name__ == "__main__":
    conn = setup_db_connection()
    try:

        select_query = "SELECT * FROM NEWS;"
        results = execute_sql(conn, select_query)
        print("Query results:", results)

        # Example 2: INSERT query
        insert_query = """
            INSERT INTO NEWS (Record_id, News_link, content)
            VALUES (%s, %s, %s);
        """
        execute_sql(conn, insert_query, (1, "http://example.com", "Example content"))

    finally:
        conn.close()
'''

#sentence = " I want to inser a new news in to my db,record id =1, http://example.com, Example content"
record_id_select = (f"I need to select record id from table record witch company name = GS,userid =1, generate data =2024-12-24,"
                            f"number_of_news=1")
print(generate_sql(record_id_select))
'''
generate_sql(sentence)
print(generate_sql(sentence))
print(generate_sql(sentence)["SQL"])
#execute_sql(generate_sql(sentence))
#SQL = {'SQL': "INSERT INTO NEWS (Record_id, News_link, content) VALUES (1, 'http://example.com', 'Example content');"}
#print(SQL['SQL'])
#execute_sql(SQL['SQL'])
'''