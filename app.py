from flask import Flask, jsonify, request
import os
import psycopg2
from models import Loan 

DATABASE_URL = os.environ['DATABASE_URL']
def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    return conn

loanstreet_api = Flask(__name__)
# TODOs: 
# OpenAPI doc
# Client (Rust + TUI?)
# Data sanity checking + sanitization
# Error handling
# Tests


# Adding a health check route just to have a simple way to confirm liveness
@app.route('/api/health')
def health_check():
    return 'API health check successful', 200

# Create a new loan
@app.route('/api/loan', methods=["POST"])
def create_loan():
    # Verify that there is a JSON body on the request
    if not request.is_json:
        # Codes
        return "Please make sure the request has a JSON body", 400
    loan_data = request.get_json()
    # Create a new Loan object to verify and sanitize the data
    try:
        new_loan = Loan(loan_data)
    except ValueError as e:
        return str(e), 400
    
    # Connect to DB and insert the data
    conn = get_db_connection()
    cur = conn.cursor()
    insert_query = "INSERT INTO loans (amount, rate, length, monthly_amount) VALUES (%s, %s, %s, %s) RETURNING id"
    cur.execute(insert_query, (new_loan.amount, new_loan.rate, new_loan.length, new_loan.monthly_payment))
    new_loan_id = cur.fetchone()[0]
    cur.close()
    conn.close()

    return "Successfully added loan " + str(new_loan_id), 200
    
# Retrieve all loans - not requested in the spec, but added this in to have an easy way to view all existing loans
@app.route('/api/loans', methods=["GET"])
def get_all_loans():
    conn = get_db_connection()
    cur = conn.cursor()
    select_all_query = "SELECT * from loans"
    cur.execute(select_all_query)
    loans = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(loans), 200

# Retrieve a single loan by ID
@app.route('/api/loan/<id>', methods=["GET"])
def get_loan(id):
    conn = get_db_connection()
    cur = conn.cursor()
    select_loan_query = "SELECT * from loans WHERE id = %s"
    cur.execute(select_loan_query, id)
    loan = cur.fetchone()
    cur.close()
    conn.close()
    return jsonify(loan), 200

# Update a loan with new data - not yet implemented
@app.route('/api/loan/<id>', methods=["PUT"])
def update_loan(id):
    # Make sure you can't accidentally blow something up
    return "update " + str(id)

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