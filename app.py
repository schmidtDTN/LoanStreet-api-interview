from flask import Flask, jsonify, request
import os
import psycopg2
from psycopg2.extras import DictCursor
from models import Loan
from utils import validate_loan_data 

DATABASE_URL = os.environ['DATABASE_URL']
def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    return conn

app = Flask(__name__)

# Adding a health check route just to have a simple way to confirm liveness
@app.route('/api/health')
def health_check():
    return 'API health check successful', 200

# Create a new loan
@app.route('/api/loan', methods=["POST"])
def create_loan():
    # Verify that there is a JSON body on the request
    if not request.is_json:
        return "Please make sure the request has a JSON body", 400
    loan_data = request.get_json()

    # Validate that the data is sane
    (valid_data, error_message) = validate_loan_data(loan_data)
    # If valid, create a Loan object
    if valid_data:
        new_loan = Loan(None, loan_data['amount'], loan_data['rate'], loan_data['length'], loan_data['monthly_payment'])
    # Throw an error if there's invalid data
    else:
        return str(error_message), 400

    try:
        # Connect to DB and insert the data
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=DictCursor)
        insert_query = "INSERT INTO loans (amount, rate, length, monthly_payment) VALUES (%s, %s, %s, %s) RETURNING id"
        cur.execute(insert_query, (new_loan.amount, new_loan.rate, new_loan.length, new_loan.monthly_payment))
        new_loan_id = cur.fetchone()["id"]
        conn.commit()
        cur.close()
        conn.close()
    except:
        return "Failed to insert loan into database", 500

    return str(new_loan_id), 200
    
# Retrieve all loans - not requested in the spec, but added this in to have an easy way to view all existing loans
@app.route('/api/loans', methods=["GET"])
def get_all_loans():
    try:
        # Get the DB connection and retrieve the list of all loans
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=DictCursor)
        select_all_query = "SELECT * from loans"
        cur.execute(select_all_query)
        rows = cur.fetchall()
        cur.close()
        conn.close()
    except:
        return "Failed to retrieve loans from database", 500

    # Create loan objects and put them in a list so they can be serialized
    loans = []
    for row in rows:
        curr_loan = Loan(row["id"], row["amount"], row["rate"], row["length"], row["monthly_payment"])
        loans.append(curr_loan)
    return jsonify(loans=[l.toJSON() for l in loans]), 200

# Retrieve a single loan by ID
@app.route('/api/loan/<id>', methods=["GET"])
def get_loan(id):
    try:
        # Connect to DB and get loan by ID
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=DictCursor)
        select_loan_query = 'SELECT * from loans WHERE id = %s'
        cur.execute(select_loan_query, (id,))
        row = cur.fetchone()
    except:
        return "Failed to retrieve loan from database", 500
    
    # If that loan ID doesn't exist in the database, return a 404
    if row is None:
        return str.format("Loan with id {} not found in database", id), 404

    # Create loan object so it can be nicely serialized
    loan = Loan(row["id"], row["amount"], row["rate"], row["length"], row["monthly_payment"])
    cur.close()
    conn.close()
    return jsonify(loan.toJSON()), 200

# Update a loan with new data - currently requiring that all fields be provided.
# Allowing for partial updates is V2
@app.route('/api/loan/<id>', methods=["PUT"])
def update_loan(id):
     # Verify that there is a JSON body on the request
    if not request.is_json:
        return "Please make sure the request has a JSON body", 400
    loan_data = request.get_json()

    # Validate that the data is sane
    (valid_data, error_message) = validate_loan_data(loan_data)
    # If valid, create a Loan object
    if valid_data:
        new_loan = Loan(id, loan_data['amount'], loan_data['rate'], loan_data['length'], loan_data['monthly_payment'])
    # Throw an error if there's invalid data
    else:
        return str(error_message), 400

    # Retrieve loan from the database
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=DictCursor)
        select_loan_query = 'SELECT * from loans WHERE id = %s'
        cur.execute(select_loan_query, (id,))
        row = cur.fetchone()
        if row is None:
            return str.format("Loan with id {} not found in database", id), 404
        cur.close()
    except:
        return "Failed to verify loan's existence in the database", 500

    # Update the loan in the database
    try: 
        cur = conn.cursor(cursor_factory=DictCursor)
        update_query = "UPDATE loans SET amount = %s, rate = %s, length = %s, monthly_payment = %s WHERE id = %s"
        cur.execute(update_query, (new_loan.amount, new_loan.rate, new_loan.length, new_loan.monthly_payment, id))
        conn.commit()
        cur.close()
        conn.close()
    except:
        return str(id), 500

    # Make sure you can't accidentally blow something up
    return "Successfully updated loan", 200

# Helper function to initialize/reset the database programmatically
# Naturally, in a real world environment, this would get removed before going to prod
# and/or be _heavily_ secured, but for this, I'm leaving it in for transparency and ease of use
@app.route('/api/db/init', methods=["POST"])
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    cur.execute('DROP TABLE IF EXISTS loans;')
    cur.execute('CREATE TABLE loans (id uuid PRIMARY KEY DEFAULT uuid_generate_v4 (),'
                                    'amount integer NOT NULL,'
                                    'rate numeric(6,3) NOT NULL,'
                                    'length integer NOT NULL,'
                                    'monthly_payment numeric(10,2) NOT NULL);')
    conn.commit()
    cur.close()
    conn.close()
    return "Successfully reset database", 200