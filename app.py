# ? Cross-origin Resource Sharing - here it allows the view and core applications deployed on different ports to communicate. No need to know anything about it since it's only used once
from flask_cors import CORS, cross_origin
# ? Python's built-in library for JSON operations. Here, is used to convert JSON strings into Python dictionaries and vice-versa
import json
import psycopg2
import os
# ? flask - library used to write REST API endpoints (functions in simple words) to communicate with the client (view) application's interactions
# ? request - is the default object used in the flask endpoints to get data from the requests
# ? Response - is the default HTTP Response object, defining the format of the returned data by this api
from flask import Flask, request, Response, render_template, flash, redirect
# ? sqlalchemy is the main library we'll use here to interact with PostgresQL DBMS
import sqlalchemy
# ? Just a class to help while coding by suggesting methods etc. Can be totally removed if wanted, no change
from typing import Dict


# ? web-based applications written in flask are simply called apps are initialized in this format from the Flask base class. You may see the contents of `__name__` by hovering on it while debugging if you're curious
app = Flask(__name__)

# ? Just enabling the flask app to be able to communicate with any request source
CORS(app)
# YOUR_POSTGRES_PASSWORD = "postgres"
# connection_string = f"postgresql://postgres:{YOUR_POSTGRES_PASSWORD}@localhost/postgres"
# engine = sqlalchemy.create_engine(
#     "postgresql://postgres:postgres@localhost/postgres"
# )

# ? `db` - the database (connection) object will be used for executing queries on the connected database named `postgres` in our deployed Postgres DBMS
# db = engine.connect()
# ? building our `engine` object from a custom configuration string
# ? for this project, we'll use the default postgres user, on a database called `postgres` deployed on the same machine
def get_db_connection():
    conn = psycopg2.connect(host='localhost',
                            database='postgres',
                            user='postgres',
                            password='postgres')
    return conn


# ? A dictionary containing
data_types = {
    'boolean': 'BOOL',
    'integer': 'INT',
    'text': 'TEXT',
    'time': 'TIME',
}

# ? @app.get is called a decorator, from the Flask class, converting a simple python function to a REST API endpoint (function)
# test 
# @app.route('/')
# def index():
#     conn = get_db_connection()
#     cur = conn.cursor()
#     cur.execute('SELECT * FROM users;')
#     users = cur.fetchall()
#     cur.close()
#     conn.close()
#     return render_template('index.html')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/', methods = ["POST"])
def branch(): 
    email = request.form.get('username')
    user_type = request.form.get("type_of_user")
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        if user_type == "customer":
            statement = f'select * from users u where u.email = \'{email}\';'
            cur.execute(statement)
            user = cur.fetchall()
            if user:
                cur.close()
                conn.close()
                return render_template('customer_filter.html')
        else:
            statement = f'select * from users u, merchants m where u.email = \'{email}\' and m.manager = \'{email}\';'
            cur.execute(statement)
            user = cur.fetchall()
            if user:
                cur.close()
                conn.close()
                return render_template('merchant_selling.html', result = user)
    except:
        #find out how to flash error 
        flash("Error in login")
    return render_template('index.html')

@app.route('/signup', methods = ["POST"])
def signup():
    signup_type = request.form.get('type_of_user')
    if signup_type == "customer":
        return render_template("signup_customer.html")
    elif signup_type == "merchant":
        return render_template("signup_merchant.html")


@app.route("/customer_signup", methods = ["POST"])
def customer_signup():
    email = request.form.get("username")
    first_name = request.form.get("firstname")
    last_name = request.form.get("lastname")
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        statement = f'INSERT INTO users VALUES (\'{first_name}\', \'{last_name}\', \'{email}\');'
        cur.execute(statement)
        cur.close()
        conn.commit()
        conn.close()
    except:
        print("error")
    return render_template("index.html")

    #insert into user table
    #try and except 
    #return to index.html

@app.route("/merchant_signup", methods = ["POST"])
def merchant_signup():
    email = request.form.get("username")
    first_name = request.form.get("firstname")
    last_name = request.form.get("lastname")
    flower_type = request.form.get("flowertype")
    arrangement= request.form.get("flowerarrangement")
    price = request.form.get("price")
    shop_name = request.form.get("shopname")
    item_code = request.form.get("code")
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        statement1 = f'INSERT INTO users VALUES (\'{first_name}\', \'{last_name}\', \'{email}\');'
        cur.execute(statement1)
        conn.commit()
    except:
        print("error")
    try:
        statement2 = f'INSERT INTO merchants VALUES (\'{item_code}\', \'{flower_type}\', \'{arrangement}\',	{price}, \'{shop_name}\', \'{email}\');'
        cur.execute(statement2)
        conn.commit()
        cur.close()
        conn.close()
    except:
        print("error")
    return render_template("index.html")
    #inseret into user table
    #insert into merchant table
    #try and except 
    #return to index.html

@app.route("/customer_filter", methods = ["POST"])
def filter():
    flower_type = request.form.get("flowertype")
    arrangement= request.form.get("flowerarrangement")
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        statement = f'SELECT * FROM merchants m WHERE m.flower_type = \'{flower_type}\' AND m.arrangement = \'{arrangement}\';'
        cur.execute(statement)
        shop = cur.fetchall()
        if shop:
            cur.close()
            conn.close()
            return render_template('customer_onsale.html', result = shop)
    except:
        print("error")
    return render_template("customer_filter.html")
    

@app.route("/to_cart", methods = ["POST"])
def to_cart():
    email = request.form.get("username")
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        statement = f'SELECT m.code, m.flower_type, m.arrangement, m.price, m.shop, m.manager FROM users u, merchants m, transactions t WHERE u.email = \'{email}\' AND t.buyer = \'{email}\' AND t.code = m.code;'
        cur.execute(statement)
        shop = cur.fetchall()
        if shop:
            cur.close()
            conn.close()
            return render_template('customer_cart.html', result = shop)
    except:
        print("error")
    return render_template("customer_filter.html")

    #filter and display result from db


@app.route("/customer_onsale", methods = ["POST"])
#find out the returned data from the db 
def add_to_cart():
    email = request.form.get("username")
    item_code = request.form.get("code")
    identifier = request.form.get("identifier")
    date = request.form.get("date")
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        statement = f'INSERT INTO transactions VALUES (\'{identifier}\', \'{date}\', \'{item_code}\', \'{email}\');'
        cur.execute(statement)
        conn.commit()
        cur.close()
        conn.close()
    except:
        print("error")
    return render_template("customer_filter.html")

#insert record of the transaction then redirect back to customer filter page

@app.route("/merchant_to_add", methods = ["POST"])
def merchant_to_add():
    return render_template("merchant_add.html")

@app.route("/merchant_add", methods = ["POST"])
def merchant_add():
    email = request.form.get("username")
    flower_type = request.form.get("flowertype")
    arrangement= request.form.get("flowerarrangement")
    price = request.form.get("price")
    shop_name = request.form.get("shopname")
    item_code = request.form.get("code")
    conn = get_db_connection()
    cur = conn.cursor()
    try: 
        statement = f'INSERT INTO merchants VALUES (\'{item_code}\', \'{flower_type}\', \'{arrangement}\',	{price}, \'{shop_name}\', \'{email}\');'
        cur.execute(statement)
        conn.commit()
        cur.close()
        conn.close()
        return render_template("index.html")
    except:
        print("error")
    return render_template("merchant_selling.html")
    #check user.email = merchant.manager 
    #insert into merchant table
    #redirect back to index.html



        




@app.get("/table")
def get_relation():
    # ? This method returns the contents of a table whose name (table-name) is given in the url `http://localhost:port/table?name=table-name`
    # ? Below is the default way of parsing the arguments from http url's using flask's request object
    relation_name = request.args.get('name', default="", type=str)
    # ? We use try-except statements for exception handling since any wrong query will crash the whole flow
    try:
        # ? Statements are built using f-strings - Python's formatted strings
        # ! Use cursors for better results
        statement = sqlalchemy.text(f"SELECT * FROM {relation_name};")
        # ? Results returned by the DBMS after execution are stored into res object defined in sqlalchemy (for reference)
        res = db.execute(statement)
        # ? committing the statement writes the db state to the disk; note that we use the concept of rollbacks for safe DB management
        db.commit()
        # ? Data is extracted from the res objects by the custom function for each query case
        # ! Note that you'll have to write custom handling methods for your custom queries
        data = generate_table_return_result(res)
        # ? Response object is instantiated with the formatted data and returned with the success code 200
        return Response(data, 200)
    except Exception as e:
        # ? We're rolling back at any case of failure
        db.rollback()
        # ? At any error case, the error is returned with the code 403, meaning invalid request
        # * You may customize it for different exception types, in case you may want
        return Response(str(e), 403)


# ? a flask decorator listening for POST requests at the url /table-create
@app.post("/table-create")
def create_table():
    # ? request.data returns the binary body of the POST request
    data = request.data.decode()
    try:
        # ? data is converted from stringified JSON to a Python dictionary
        table = json.loads(data)
        # ? data, or table, is an object containing keys to define column names and types of the table along with its name
        statement = generate_create_table_statement(table)
        # ? the remaining steps are the same
        db.execute(statement)
        db.commit()
        return Response(statement.text)
    except Exception as e:
        db.rollback()
        return Response(str(e), 403)


@app.post("/table-insert")
# ? a flask decorator listening for POST requests at the url /table-insert and handles the entry insertion into the given table/relation
# * You might wonder why PUT or a similar request header was not used here. Fundamentally, they act as POST. So the code was kept simple here
def insert_into_table():
    # ? Steps are common in all of the POST behaviors. Refer to the statement generation for the explanatory
    data = request.data.decode()
    try:
        insertion = json.loads(data)
        statement = generate_insert_table_statement(insertion)
        db.execute(statement)
        db.commit()
        return Response(statement.text)
    except Exception as e:
        db.rollback()
        return Response(str(e), 403)


@app.post("/table-update")
# ? a flask decorator listening for POST requests at the url /table-update and handles the entry updates in the given table/relation
def update_table():
    # ? Steps are common in all of the POST behaviors. Refer to the statement generation for the explanatory
    data = request.data.decode()
    try:
        update = json.loads(data)
        statement = generate_update_table_statement(update)
        db.execute(statement)
        db.commit()
        return Response(statement.text, 200)
    except Exception as e:
        db.rollback()
        return Response(str(e), 403)


@app.post("/entry-delete")
# ? a flask decorator listening for POST requests at the url /entry-delete and handles the entry deletion in the given table/relation
def delete_row():
    # ? Steps are common in all of the POST behaviors. Refer to the statement generation for the explanatory
    data = request.data.decode()
    try:
        delete = json.loads(data)
        statement = generate_delete_statement(delete)
        db.execute(statement)
        db.commit()
        return Response(statement.text)
    except Exception as e:
        db.rollback()
        return Response(str(e), 403)


def generate_table_return_result(res):
    # ? An empty Python list to store the entries/rows/tuples of the relation/table
    rows = []

    # ? keys of the SELECT query result are the columns/fields of the table/relation
    columns = list(res.keys())

    # ? Constructing the list of tuples/rows, basically, restructuring the object format
    for row_number, row in enumerate(res):
        rows.append({})
        for column_number, value in enumerate(row):
            rows[row_number][columns[column_number]] = value

    # ? JSON object with the relation data
    output = {}
    output["columns"] = columns  # ? Stores the fields
    output["rows"] = rows  # ? Stores the tuples

    """
        The returned object format:
        {
            "columns": ["a","b","c"],
            "rows": [
                {"a":1,"b":2,"c":3},
                {"a":4,"b":5,"c":6}
            ]
        }
    """
    # ? Returns the stringified JSON object
    return json.dumps(output)


def generate_delete_statement(details: Dict):
    # ? Fetches the entry id for the table name
    table_name = details["relationName"]
    id = details["deletionId"]
    # ? Generates the deletion query for the given entry with the id
    statement = f"DELETE FROM {table_name} WHERE id={id};"
    return sqlalchemy.text(statement)


def generate_update_table_statement(update: Dict):

    # ? Fetching the table name, entry/tuple id and the update body
    table_name = update["name"]
    id = update["id"]
    body = update["body"]

    # ? Default for the SQL update statement
    statement = f"UPDATE {table_name} SET "
    # ? Constructing column-to-value maps looping
    for key, value in body.items():
        statement += f"{key}=\'{value}\',"

    # ?Finalizing the update statement with table and row details and returning
    statement = statement[:-1]+f" WHERE {table_name}.id={id};"
    return sqlalchemy.text(statement)


def generate_insert_table_statement(insertion: Dict):
    # ? Fetching table name and the rows/tuples body object from the request
    table_name = insertion["name"]
    body = insertion["body"]
    valueTypes = insertion["valueTypes"]

    # ? Generating the default insert statement template
    statement = f"INSERT INTO {table_name}  "

    # ? Appending the entries with their corresponding columns
    column_names = "("
    column_values = "("
    for key, value in body.items():
        column_names += (key+",")
        if valueTypes[key] == "TEXT" or valueTypes[key] == "TIME":
            column_values += (f"\'{value}\',")
        else:
            column_values += (f"{value},")

    # ? Removing the last default comma
    column_names = column_names[:-1]+")"
    column_values = column_values[:-1]+")"

    # ? Combining it all into one statement and returning
    #! You may try to expand it to multiple tuple insertion in another method
    statement = statement + column_names+" VALUES "+column_values+";"
    return sqlalchemy.text(statement)


def generate_create_table_statement(table: Dict):
    # ? First key is the name of the table
    table_name = table["name"]
    # ? Table body itself is a JSON object mapping field/column names to their values
    table_body = table["body"]
    # ? Default table creation template query is extended below. Note that we drop the existing one each time. You might improve this behavior if you will
    # ! ID is the case of simplicity
    statement = f"DROP TABLE IF EXISTS {table_name}; CREATE TABLE {table_name} (id serial NOT NULL PRIMARY KEY,"
    # ? As stated above, column names and types are appended to the creation query from the mapped JSON object
    for key, value in table_body.items():
        statement += (f"{key}"+" "+f"{value}"+",")
    # ? closing the final statement (by removing the last ',' and adding ');' termination and returning it
    statement = statement[:-1] + ");"
    return sqlalchemy.text(statement)

# ? This method can be used by waitress-serve CLI 
def create_app():
   return app

# ? The port where the debuggable DB management API is served
PORT = 2222
# ? Running the flask app on the localhost/0.0.0.0, port 2222
# ? Note that you may change the port, then update it in the view application too to make it work (don't if you don't have another application occupying it)
if __name__ == "__main__":
    app.run("0.0.0.0", PORT)
    # ? Uncomment the below lines and comment the above lines below `if __name__ == "__main__":` in order to run on the production server
    # ? Note that you may have to install waitress running `pip install waitress`
    # ? If you are willing to use waitress-serve command, please add `/home/sadm/.local/bin` to your ~/.bashrc
    # from waitress import serve
    # serve(app, host="0.0.0.0", port=PORT)
