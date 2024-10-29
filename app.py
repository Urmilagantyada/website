# from importlib.metadata import files
import base64
import io
import re
from flask import Flask, jsonify, redirect, render_template, request, send_file, session, url_for,flash
import mysql.connector
from werkzeug.utils import secure_filename
from flask import send_from_directory
import pandas as pd
import random
import os
from mysql.connector import Error
from mysql.connector.errors import IntegrityError
import logging
from flask import Blueprint
import csv
from flask import make_response, request
import xlsxwriter
from datetime import datetime


app = Flask(__name__)

app.config['SECRET_KEY'] = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'uploads'



ALLOWED_EXTENSIONS = {'xlsx', 'xls','pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",  # Make sure to replace with your MySQL password
    database="Omnipro"
)

def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='Omnipro'
    )


@app.route('/')
def login():
    return render_template('login.html')


@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/Employee', methods=['GET', 'POST'])
def Employee():
    mydb = get_db_connection()
    mycursor = mydb.cursor(buffered=True)

    if request.method == 'POST':
        id = request.form.get('id')
        employeename = request.form.get('employeename')
        joiningdate = request.form.get('joiningdate')

        # Validate joining date
        if datetime.strptime(joiningdate, '%Y-%m-%d') > datetime.today():
            return "Error: Date cannot be in the future!", 400

        designation = request.form.get('designation')
        dateofbirth = request.form.get('dateofbirth')

        # Validate date of birth
        if datetime.strptime(dateofbirth, '%Y-%m-%d') > datetime.today():
            return "Error: Date cannot be in the future!", 400
        
        bloodgroup = request.form.get('bloodgroup')
        qualification = request.form.get('qualification')
        gender = request.form.get('gender')
        address = request.form.get('address')
        contactnumber = request.form.get('contactnumber')
        alternatenumber = request.form.get('alternatenumber')
        city = request.form.get('city')
        state = request.form.get('state')
        email = request.form.get('email')
        skype = request.form.get('skype')
        remarks = request.form.get('remarks')
        updateddate = request.form.get('updateddate')

        # Validate updated date
        if datetime.strptime(updateddate, '%Y-%m-%d') > datetime.today():
            return "Error: Date cannot be in the future!", 400

        query = """
        INSERT INTO employee (employeename, joiningdate, designation, dateofbirth, bloodgroup, qualification, gender, address, contactnumber, alternatenumber, city, state, email, skype, remarks, updateddate)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (employeename, joiningdate, designation, dateofbirth, bloodgroup, qualification, gender, address, contactnumber, alternatenumber, city, state, email, skype, remarks, updateddate)
        mycursor.execute(query, values)
        mydb.commit()
        flash("Employee added successfully")
        return redirect(url_for('Employee'))

    # Fetching data for display
    mycursor.execute("SELECT * FROM employee ORDER BY id DESC")
    employee = mycursor.fetchall()
    mycursor.execute("SELECT * FROM branch ORDER BY id DESC")
    value = mycursor.fetchall()
    mycursor.execute("SELECT * FROM city")
    data = mycursor.fetchall()    
    mycursor.execute("SELECT * FROM designations")
    designation_data = mycursor.fetchall()

    search_query = request.args.get('search', '')
    page = int(request.args.get('page', 1))
    per_page = 10
    offset = (page - 1) * per_page

    # Search and pagination query
    mycursor.execute("""
        SELECT COUNT(*) FROM employee 
        WHERE employeename LIKE %s OR email LIKE %s OR status LIKE %s
    """, (f'{search_query}%', f'{search_query}%', f'{search_query}%'))
    total_contacts = mycursor.fetchone()[0]

    mycursor.execute("""
        SELECT * FROM employee
        WHERE employeename LIKE %s OR email LIKE %s OR status LIKE %s
        ORDER BY 
            CASE WHEN status = 1 THEN 0 ELSE 1 END,  -- Prioritize status = 1
            id DESC,                                -- Order by id descending
            email ASC                               -- Order by email ascending
        LIMIT %s OFFSET %s
    """, (f'{search_query}%', f'{search_query}%', f'{search_query}%', per_page, offset))
    employee = mycursor.fetchall()

    mycursor.close()
    mydb.close()

    total_pages = (total_contacts + per_page - 1) // per_page
    max_date = datetime.today().strftime('%Y-%m-%d')

    return render_template('Employee.html',designation_data=designation_data, value=value, data=data, max_date=max_date, employee=employee, page=page, per_page=per_page, total_pages=total_pages, search_query=search_query)


@app.route('/export_employee_data')
def export_employee_data():
    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch data from the employee table
    query = "SELECT * FROM employee"  # Assuming 'status = 1' means active employees
    cursor.execute(query)
    rows = cursor.fetchall()
    columns = [i[0] for i in cursor.description]  # Get column names

    # Debugging: Print fetched data and column names
    print("Columns from employee table:", columns)
    print("Rows from employee table:", rows)

    # Check if no data found
    if not rows:
        print("No  employee data found.")

    # Create a DataFrame for the employee data
    df= pd.DataFrame(rows, columns=columns).drop(columns=['id'], errors='ignore')

    # Close the cursor and connection
    cursor.close()
    conn.close()

    # Convert specific columns to datetime if necessary
    # 'coerce' ensures invalid parsing will be set as NaT (Not a Time)
    date_columns = ['joiningdate', 'dateofbirth', 'updateddate']
    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce').dt.strftime('%d-%m-%Y')  # Convert to desired format

    # Prepare an in-memory output file to write Excel data
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Write the DataFrame to the Excel file
        df.to_excel(writer, sheet_name='Active_Employees', index=False)

        # Access the xlsxwriter workbook and worksheet
        workbook = writer.book
        worksheet = writer.sheets['Active_Employees']

        # Set the format for date columns in Excel
        date_format = workbook.add_format({'num_format': 'dd-mm-yyyy'})

        # Apply the date format to the appropriate columns
        for col_num, col_name in enumerate(df.columns):
            if col_name in date_columns:
                # Apply the date format only to the relevant date columns
                worksheet.set_column(col_num, col_num, 15, date_format)  # Set column width and date format

    # Rewind the buffer
    output.seek(0)

    # Create the response to download the file
    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=employees_data.xlsx"
    response.headers["Content-Type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    
    return response

@app.route('/export_part_data')
def export_part_data():
    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch data from the employee table
    query = "SELECT * FROM part_item"  # Assuming 'status = 1' means active employees
    cursor.execute(query)
    rows = cursor.fetchall()
    columns = [i[0] for i in cursor.description]  # Get column names

    # Debugging: Print fetched data and column names
    print("Columns from part_item table:", columns)
    print("Rows from part_item table:", rows)

    # Check if no data found
    if not rows:
        print("No Part Numbers  found.")

    # Create a DataFrame for the employee data
    df= pd.DataFrame(rows, columns=columns).drop(columns=['id','excel'], errors='ignore')

    # Close the cursor and connection
    cursor.close()
    conn.close()

    # Convert specific columns to datetime if necessary
    # 'coerce' ensures invalid parsing will be set as NaT (Not a Time)
    date_columns = ['date']
    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce').dt.strftime('%d-%m-%Y')  # Convert to desired format

    # Prepare an in-memory output file to write Excel data
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Write the DataFrame to the Excel file
        df.to_excel(writer, sheet_name='Part Numbers', index=False)

        # Access the xlsxwriter workbook and worksheet
        workbook = writer.book
        worksheet = writer.sheets['Part Numbers']

        # Set the format for date columns in Excel
        date_format = workbook.add_format({'num_format': 'dd-mm-yyyy'})

        # Apply the date format to the appropriate columns
        for col_num, col_name in enumerate(df.columns):
            if col_name in date_columns:
                # Apply the date format only to the relevant date columns
                worksheet.set_column(col_num, col_num, 15, date_format)  # Set column width and date format

    # Rewind the buffer
    output.seek(0)

    # Create the response to download the file
    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=Part Numbers.xlsx"
    response.headers["Content-Type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    
    return response


@app.route('/export_information')
def export_information():
    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch data from the employee table
    query = "SELECT * FROM information"  # Assuming 'status = 1' means active employees
    cursor.execute(query)
    rows = cursor.fetchall()
    columns = [i[0] for i in cursor.description]  # Get column names

    # Debugging: Print fetched data and column names
    print("Columns from information table:", columns)
    print("Rows from information table:", rows)

    # Check if no data found
    if not rows:
        print("No information  found.")

    # Create a DataFrame for the employee data
    df= pd.DataFrame(rows, columns=columns).drop(columns=['id'], errors='ignore')

    # Close the cursor and connection
    cursor.close()
    conn.close()

    # Convert specific columns to datetime if necessary
    # 'coerce' ensures invalid parsing will be set as NaT (Not a Time)
    date_columns = ['Date']
    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce').dt.strftime('%d-%m-%Y')  # Convert to desired format

    # Prepare an in-memory output file to write Excel data
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Write the DataFrame to the Excel file
        df.to_excel(writer, sheet_name='Information', index=False)

        # Access the xlsxwriter workbook and worksheet
        workbook = writer.book
        worksheet = writer.sheets['Information']

        # Set the format for date columns in Excel
        date_format = workbook.add_format({'num_format': 'dd-mm-yyyy'})

        # Apply the date format to the appropriate columns
        for col_num, col_name in enumerate(df.columns):
            if col_name in date_columns:
                # Apply the date format only to the relevant date columns
                worksheet.set_column(col_num, col_num, 15, date_format)  # Set column width and date format

    # Rewind the buffer
    output.seek(0)

    # Create the response to download the file
    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=Information Data    .xlsx"
    response.headers["Content-Type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    
    return response

@app.route('/export_expenses')
def export_expenses():
    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch data from the employee table
    query = "SELECT * FROM expenses"  # Assuming 'status = 1' means active employees
    cursor.execute(query)
    rows = cursor.fetchall()
    columns = [i[0] for i in cursor.description]  # Get column names

    # Debugging: Print fetched data and column names
    print("Columns from expenses table:", columns)
    print("Rows from expenses table:", rows)

    # Check if no data found
    if not rows:
        print("No Data  found.")

    # Create a DataFrame for the employee data
    df= pd.DataFrame(rows, columns=columns).drop(columns=['id'], errors='ignore')

    # Close the cursor and connection
    cursor.close()
    conn.close()

    # Convert specific columns to datetime if necessary
    # 'coerce' ensures invalid parsing will be set as NaT (Not a Time)
    date_columns = ['date']
    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce').dt.strftime('%d-%m-%Y')  # Convert to desired format

    # Prepare an in-memory output file to write Excel data
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Write the DataFrame to the Excel file
        df.to_excel(writer, sheet_name='Expenses', index=False)

        # Access the xlsxwriter workbook and worksheet
        workbook = writer.book
        worksheet = writer.sheets['Expenses']

        # Set the format for date columns in Excel
        date_format = workbook.add_format({'num_format': 'dd-mm-yyyy'})

        # Apply the date format to the appropriate columns
        for col_num, col_name in enumerate(df.columns):
            if col_name in date_columns:
                # Apply the date format only to the relevant date columns
                worksheet.set_column(col_num, col_num, 15, date_format)  # Set column width and date format

    # Rewind the buffer
    output.seek(0)

    # Create the response to download the file
    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=Expenses.xlsx"
    response.headers["Content-Type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    
    return response

@app.route('/delete_employee/<int:id>')
def delete_employee(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Update the status to 0 instead of deleting the record
        cursor.execute("UPDATE employee SET status = 0 WHERE id = %s", (id,))
        conn.commit()

        cursor.close()
        conn.close()

        flash('Record has been marked as inactive (status updated to 0)', 'success')
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')

    return redirect(url_for('Employee'))


@app.route('/update_employee', methods=['POST'])
def update_employee():
    if request.method == 'POST':
        id = request.form.get('id')
        new_employeename = request.form.get('employeename')
        joiningdate = request.form.get('joiningdate')
        designation = request.form.get('designation')
        dateofbirth = request.form.get('dateofbirth')
        bloodgroup = request.form.get('bloodgroup')
        qualification = request.form.get('qualification')
        gender = request.form.get('gender')
        address = request.form.get('address')
        contactnumber = request.form.get('contactnumber')
        alternatenumber = request.form.get('alternatenumber')
        city = request.form.get('city')
        state = request.form.get('state')
        email = request.form.get('email')
        skype = request.form.get('skype')
        remarks = request.form.get('remarks')
        updateddate = request.form.get('updateddate')

        

        try:
            mydb = get_db_connection()  # Assuming this is a function to get the DB connection
            mycursor = mydb.cursor()

            # Fetch the current employee details to get the old employee name
            mycursor.execute("SELECT employeename FROM employee WHERE id = %s", (id,))
            result = mycursor.fetchone()
            if result:
                old_employeename = result[0]

                # Update employee record
                update_employee_sql = """
                UPDATE employee 
                SET employeename=%s, joiningdate=%s, designation=%s, dateofbirth=%s, bloodgroup=%s, 
                    qualification=%s, gender=%s, address=%s, contactnumber=%s, alternatenumber=%s, 
                    city=%s, state=%s, email=%s, skype=%s, remarks=%s, updateddate=%s 
                WHERE id=%s
                """
                values = (new_employeename, joiningdate, designation, dateofbirth, bloodgroup, qualification, gender, 
                          address, contactnumber, alternatenumber, city, state, email, skype, remarks, updateddate, id)
                mycursor.execute(update_employee_sql, values)

                # Update related records in other tables
                # Update added_by in the contacts table
                update_contacts_sql = """
                UPDATE contacts 
                SET added_by=%s 
                WHERE added_by=%s
                """
                mycursor.execute(update_contacts_sql, (new_employeename, old_employeename))

                # Add more updates here if there are other tables referring to employee_name
                # Example:
                # update_other_table_sql = """
                # UPDATE other_table
                # SET employee_name_column=%s
                # WHERE employee_name_column=%s
                # """
                # mycursor.execute(update_other_table_sql, (new_employeename, old_employeename))

                mydb.commit()

                flash("Data Updated Successfully")
            else:
                flash("Employee not found")

        except mysql.connector.Error as err:
            flash(f"Error: {err}")
        finally:
            # Close cursor and database connection
            mycursor.close()
            mydb.close()

    return redirect(url_for('Employee'))

@app.route('/check_employee_name', methods=['POST'])
def check_employee_name():
    employeename = request.form['employeename']
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM employee WHERE employeename = %s", (employeename,))
    result = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    
    return jsonify({'exists': result > 0})

@app.route('/Branch', methods=['GET', 'POST'])
def Branch():
    mydb = get_db_connection()
    mycursor = mydb.cursor(buffered=True)
    error = None

    if request.method == 'POST':
        id = request.form.get('id')
        branch = request.form.get('branch')
        query = """
        INSERT INTO branch (id, branch_name)
        VALUES (%s, %s)
        """
        values = (id, branch)
        try:
            mycursor.execute(query, values)
            mydb.commit()
            return redirect(url_for('Branch'))
        except IntegrityError:
            error = "Duplicate entry. Please try again with a different ID or branch."

    mycursor.execute("SELECT * FROM branch")
    branches = mycursor.fetchall()
    mycursor.close()
    mydb.close()

    return render_template('Branch.html', branches=branches, error=error)


@app.route('/delete_branch/<int:id>')
def delete_branch(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Execute DELETE operation
        cursor.execute("DELETE FROM branch WHERE id = %s", (id,))
        conn.commit()

        cursor.close()
        conn.close()

        flash('Record has been deleted successfully', 'success')
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')

    return redirect(url_for('Branch'))




 




@app.route('/City', methods=['GET', 'POST'])
def City():
    mydb = get_db_connection()
    mycursor = mydb.cursor(buffered=True)
    error = None

    if request.method == 'POST':
        id = request.form.get('id')
        city = request.form.get('city')
        query = """
        INSERT INTO city (id, city)
        VALUES (%s, %s)
        """
        values = (id, city)
        try:
            mycursor.execute(query, values)
            mydb.commit()
            return redirect(url_for('City'))
        except IntegrityError:
            error = "Duplicate entry. Please try again with a different ID or city."

    mycursor.execute("SELECT * FROM city")
    cities = mycursor.fetchall()
    mycursor.close()
    mydb.close()

    return render_template('City.html', cities=cities, error=error)




@app.route('/delete_city/<int:id>')
def delete_city(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Execute DELETE operation
        cursor.execute("DELETE FROM city WHERE id = %s", (id,))
        conn.commit()

        cursor.close()
        conn.close()

        flash('Record has been deleted successfully', 'success')
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')

    return redirect(url_for('City'))


@app.route('/Designation', methods=['GET', 'POST'])
def Designation():
    mydb = get_db_connection()
    mycursor = mydb.cursor(buffered=True)

    if request.method == 'POST':
        designation = request.form.get('designation')
        state = request.form.get('state')
        city = request.form.get('city')
        query = """
        INSERT INTO designation (designation, state, city)
        VALUES (%s, %s, %s)
        """
        values = (designation, state, city)
        mycursor.execute(query, values)
        mydb.commit()

        return redirect(url_for('Designation'))

    # List of states in uppercase
    states = [
        'ANDHRA PRADESH', 'ARUNACHAL PRADESH', 'ASSAM', 'BIHAR', 'CHHATTISGARH',
        'GOA', 'GUJARAT', 'HARYANA', 'HIMACHAL PRADESH', 'JHARKHAND',
        'KARNATAKA', 'KERALA', 'MADHYA PRADESH', 'MAHARASHTRA', 'MANIPUR',
        'MEGHALAYA', 'MIZORAM', 'NAGALAND', 'ODISHA', 'PUNJAB',
        'RAJASTHAN', 'SIKKIM', 'TAMIL NADU', 'TELANGANA', 'TRIPURA',
        'UTTAR PRADESH', 'UTTARAKHAND', 'WEST BENGAL'
    ]
    cities = [
    'VISAKHAPATNAM', 'VIJAYAWADA', 'GUNTUR', 'NELLORE', 'KURNOOL',
    'RAJAHMUNDRY', 'KAKINADA', 'TIRUPATI', 'ANANTAPUR', 'KADAPA',
    'ONGOLE', 'SRIKAKULAM', 'ELURU', 'CHITTOOR', 'MACHILIPATNAM',
    'TENALI', 'PRODDATUR', 'VIZIANAGARAM', 'NANDYAL', 'HINDUPUR',
    'BAPATLA', 'TADEPALLIGUDEM', 'ADONI', 'MADANAPALLE', 'TADEPALLE',
    'PUTTUR', 'BHIMAVARAM', 'AMALAPURAM', 'NARASARAOPET', 'PALAKOLLU'
]

    mycursor.execute("SELECT * FROM designation")
    designation = mycursor.fetchall()
    mycursor.execute("SELECT * FROM designation")
    data = mycursor.fetchall()
    mycursor.close()
    mydb.close()

    return render_template('Designation.html', designation=designation, states=states,cities=cities,data=data)




@app.route('/delete_designation/<int:id>')
def delete_designation(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Execute DELETE operation
        cursor.execute("DELETE FROM designation WHERE id = %s", (id,))
        conn.commit()

        cursor.close()
        conn.close()

        flash('Record has been deleted successfully', 'success')
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')

    return redirect(url_for('Designation'))

    


@app.route('/update_designation', methods=['POST'])
def update_designation():
    if request.method == 'POST':
        id = request.form['id']
        designation = request.form['designation']
        state = request.form['state']
        city = request.form['city']
        
        
        

            # Database connection
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="Omnipro"
            )
        mycursor = mydb.cursor()

            # Update SQL query
        sql = "UPDATE designation SET designation=%s, state=%s, city=%s WHERE id=%s"
        val = (designation, state, city,id)
        mycursor.execute(sql, val)
        mydb.commit()

            # Close cursor and database connection
        mycursor.close()
        mydb.close()

        flash("Data Updated Successfully")

    

    return redirect(url_for('Designation'))






    



@app.route('/Delivery_terms', methods=['GET', 'POST'])
def Delivery_terms():
    mydb = get_db_connection()
    mycursor = mydb.cursor(buffered=True)

    if request.method == 'POST':
        # Handle form submission
        DeliveryTerms = request.form.get('DeliveryTerms')
        PaymentTerms = request.form.get('PaymentTerms')
        VIAFreight = request.form.get('VIAFreight')

        query = """
        INSERT INTO deliveryterms (DeliveryTerms, PaymentTerms, VIAFreight)
        VALUES (%s, %s, %s)
        """
        values = (DeliveryTerms, PaymentTerms, VIAFreight)
        mycursor.execute(query, values)
        mydb.commit()

        return redirect(url_for('Delivery_terms'))

    # Search functionality
    search_query = request.args.get('search', '')
    filter_column = request.args.get('filter', 'DeliveryTerms')  # Default to DeliveryTerms if no filter is selected
    page = int(request.args.get('page', 1))
    per_page = 10
    offset = (page - 1) * per_page

    # Ensure the selected filter column is valid
    if filter_column not in ['DeliveryTerms', 'PaymentTerms', 'VIAFreight']:
        filter_column = 'DeliveryTerms'

    # Count total records based on the search
    mycursor.execute(f"SELECT COUNT(*) FROM deliveryterms WHERE {filter_column} LIKE %s", (f'{search_query}%',))
    total_customers = mycursor.fetchone()[0]

    # Fetch paginated records based on the search
    mycursor.execute(f"SELECT * FROM deliveryterms WHERE {filter_column} LIKE %s ORDER BY id DESC LIMIT %s OFFSET %s",
                     (f'{search_query}%', per_page, offset))
    deliveryterms = mycursor.fetchall()

    mycursor.close()
    mydb.close()

    total_pages = (total_customers + per_page - 1) // per_page

    return render_template('Delivery_terms.html', deliveryterms=deliveryterms, page=page, per_page=per_page, total_pages=total_pages, search_query=search_query, filter_column=filter_column)


@app.route('/delete_deliveryterms/<int:id>')
def delete_deliveryterms(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Execute DELETE operation
        cursor.execute("DELETE FROM deliveryterms WHERE id = %s", (id,))
        conn.commit()

        cursor.close()
        conn.close()

        flash('Record has been deleted successfully', 'success')
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')

    return redirect(url_for('Delivery_terms'))

    


@app.route('/update_deliveryterms', methods=['POST'])
def update_deliveryterms():
    if request.method == 'POST':
        id = request.form['id']
        DeliveryTerms = request.form['DeliveryTerms']
        PaymentTerms = request.form['PaymentTerms']
        VIAFreight = request.form['VIAFreight']
        
        
        

            # Database connection
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="Omnipro"
            )
        mycursor = mydb.cursor()

            # Update SQL query
        sql = "UPDATE deliveryterms SET DeliveryTerms=%s, PaymentTerms=%s, VIAFreight=%s WHERE id=%s"
        val = (DeliveryTerms, PaymentTerms, VIAFreight,id)
        mycursor.execute(sql, val)
        mydb.commit()

            # Close cursor and database connection
        mycursor.close()
        mydb.close()

        flash("Data Updated Successfully")

    

    return redirect(url_for('Delivery_terms'))








@app.route('/login', methods=['POST'])
def login_post():
    username = request.form['username']
    password = request.form['password']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM managestaff WHERE StaffName = %s AND Password = %s', (username, password))
    user = cursor.fetchone()
    cursor.close()

    if user:
        session['StaffName'] = user[2]
        if user[3] == 'admin':
            return redirect('/index')
        elif user[3] == 'Referring Doctor':
            return redirect('/index_emp')
        elif user[3] == 'Reporting Doctor':
            return redirect('/index')
        elif user[3] == 'Technician':
            return redirect('/index')
        elif user[3] == 'Reception':
            return redirect('/index')
        
    else:
        return 'Invalid username/password combination'

    

@app.route('/technician_dashboard', methods=['GET', 'POST'])
def technician_dashboard():
    if 'StaffName' in session:
        return render_template('technician_dashboard.html')
    else:
        return redirect('/login')

@app.route('/refering_doctor_dashboard', methods=['GET', 'POST'])
def refering_doctor_dashboard():
    if 'StaffName' in session:
        return render_template('refering_doctor_dashboard.html')
    else:
        return redirect('/login')

@app.route('/reporting_doctor', methods=['GET', 'POST'])
def reporting_doctor():
    if 'StaffName' in session:
        return render_template('reporting_doctor.html')
    else:
        return redirect('/login')

@app.route('/reception_profile_dashboard', methods=['GET', 'POST'])
def reception_profile_dashboard():
    if 'StaffName' in session:
        return render_template('reception_profile_dashboard.html')
    else:
        return redirect('/login')
    
      

@app.route('/password', methods=['POST'])
def password():
    return render_template('password.html')

@app.route('/register', methods=['POST'])
def register():
    return render_template('register.html')


def fetch_patient_details(token):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT studentName, phone, applied_test FROM studentregistration WHERE token_number=%s", (token,))
    patient = cursor.fetchone()
    return patient

@app.route('/get_patient_details', methods=['POST'])
def get_patient_details():
    token = request.form['token']
    mycursor = mydb.cursor()
    mycursor.execute("SELECT studentName, phone, applied_test FROM studentregistration WHERE token_number=%s", (token,))
    patient = mycursor.fetchone()
    mycursor.close()

    if patient:
        return jsonify({'name': patient[0], 'phone': patient[1], 'tests' : patient[2]})
    else:
        return jsonify({'error': 'Patient not found'})

@app.route('/index')
def index():

    
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="Omnipro"
    )
    mycursor = mydb.cursor()

    

    # Count of closed leads
    # mycursor.execute("SELECT COUNT(*) FROM addlead WHERE Status = 'Closed'")
    # count8 = mycursor.fetchone()[0]
    

    return render_template('index.html')

@app.route('/index_emp')
def index_emp():

    
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="Omnipro"
    )
    mycursor = mydb.cursor()

    

    # Count of closed leads
    # mycursor.execute("SELECT COUNT(*) FROM addlead WHERE Status = 'Closed'")
    # count8 = mycursor.fetchone()[0]
    

    return render_template('index_emp.html')

@app.route('/Expenses', methods=['GET', 'POST'])
def Expenses():
    mydb = get_db_connection()
    mycursor = mydb.cursor(buffered=True)

    if request.method == 'POST':
        date = request.form.get('date')
        if datetime.strptime(date, '%Y-%m-%d').date() > datetime.today().date():
            return "Error: Date cannot be in the future!", 400
        expensestype = request.form.get('expensestype')
        amount = request.form.get('amount')
        particulars = request.form.get('particulars')
        
        remarks = request.form.get('remarks')
        query = """
        INSERT INTO expenses (date, expensestype,amount, particulars, remarks)
        VALUES (%s, %s, %s, %s,%s)
        """
        values = (date, expensestype, amount,particulars, remarks)
        mycursor.execute(query, values)
        mydb.commit()

        return redirect(url_for('Expenses'))

    mycursor.execute("SELECT * FROM expenses")
    expenses = mycursor.fetchall()

    mycursor.execute("SELECT type FROM expense_type")
    value = mycursor.fetchall()

    max_date = datetime.today().strftime('%Y-%m-%d')

    search_query = request.args.get('search', '')
    page = int(request.args.get('page', 1))
    per_page = 10
    offset = (page - 1) * per_page
    
    mycursor.execute("SELECT COUNT(*) FROM expenses WHERE 	date LIKE %s OR expensestype LIKE %s OR amount LIKE %s", (f'{search_query}%',f'{search_query}%',f'{search_query}%'))
    total_customers = mycursor.fetchone()[0]
    
    mycursor.execute("SELECT * FROM expenses WHERE date LIKE %s OR expensestype LIKE %s OR amount LIKE %s   ORDER BY id DESC LIMIT %s OFFSET %s",
                   (f'{search_query}%',f'{search_query}%',f'{search_query}%', per_page, offset))
    expenses = mycursor.fetchall()

    mycursor.close()
    mydb.close()
    
    total_pages = (total_customers + per_page - 1) // per_page


    return render_template('Expenses.html',max_date=max_date,value=value, expenses=expenses,page=page, per_page=per_page, total_pages=total_pages, search_query=search_query)


@app.route('/add_expenses', methods=['GET', 'POST'])
def add_expenses():
    if request.method == 'POST':
        # Check if a file was submitted
        if 'file' not in request.files:
            flash('No file part.', 'danger')
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash('No selected file.', 'danger')
            return redirect(request.url)

        # Check for allowed file extensions
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            try:
                # Read the Excel file into a Pandas DataFrame
                df = pd.read_excel(filepath)

                # Database connection
                mydb = get_db_connection()
                if not mydb:
                    flash('Database connection failed.', 'danger')
                    os.remove(filepath)
                    return redirect(url_for('add_expenses'))

                mycursor = mydb.cursor(buffered=True)

                # SQL query to insert data into the expenses table
                insert_query = """
                    INSERT INTO expenses (date, expensestype, amount, particulars, remarks) 
                    VALUES (%s, %s, %s, %s, %s)
                """

                inserted_rows = 0
                invalid_date_rows = []
                duplicate_rows = []

                # Iterate over each row in the Excel file
                for index, row in df.iterrows():
                    date = str(row['date']).strip()
                    expensestype = str(row['expensestype']).strip()
                    amount = row['amount']
                    particulars = str(row['particulars']).strip()
                    remarks = str(row['remarks']).strip()

                    # Validate the date format (assuming YYYY-MM-DD)
                    try:
                        valid_date = pd.to_datetime(date).date()
                    except ValueError:
                        invalid_date_rows.append(f"Row {index + 2}: Invalid date format '{date}'")
                        continue  # Skip this row if date format is invalid

                    # Check for duplicates
                    mycursor.execute("SELECT COUNT(*) FROM expenses WHERE date = %s AND expensestype = %s AND amount = %s AND particulars = %s AND remarks = %s",
                                     (valid_date, expensestype, amount, particulars, remarks))
                    if mycursor.fetchone()[0] > 0:
                        duplicate_rows.append(f"Row {index + 2}: Duplicate entry found.")
                        continue

                    try:
                        # Insert the new expense data
                        mycursor.execute(insert_query, (valid_date, expensestype, amount, particulars, remarks))
                        mydb.commit()
                        inserted_rows += 1
                    except mysql.connector.Error as e:
                        flash(f'Error inserting row {index + 2}: {str(e)}', 'danger')

                # Feedback to the user on the result of the upload
                success_message = f'Successfully inserted {inserted_rows} rows.'
                if invalid_date_rows or duplicate_rows:
                    failure_message = f' {len(invalid_date_rows) + len(duplicate_rows)} rows were not inserted.'
                    if invalid_date_rows:
                        failure_message += f' Invalid date format in rows: {", ".join(invalid_date_rows)}.'
                    if duplicate_rows:
                        failure_message += f' Duplicate rows: {", ".join(duplicate_rows)}.'
                    flash(success_message + failure_message, 'warning')
                else:
                    flash(success_message, 'success')

            except Exception as e:
                flash(f'Error processing file: {str(e)}', 'danger')

            finally:
                # Close the database connection and remove the uploaded file
                if 'mydb' in locals():
                    mycursor.close()
                    mydb.close()
                os.remove(filepath)

            return redirect(url_for('Expenses'))  # Redirect to your desired endpoint

    return render_template('Expenses.html')  # Render your Expenses template









@app.route('/delete_expenses/<int:id>')
def delete_expenses(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Execute DELETE operation
        cursor.execute("DELETE FROM expenses WHERE id = %s", (id,))
        conn.commit()

        cursor.close()
        conn.close()

        flash('Record has been deleted successfully', 'success')
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')

    return redirect(url_for('Expenses'))

    


@app.route('/update_expenses', methods=['POST'])
def update_expenses():
    if request.method == 'POST':
        id = request.form['id']
        date = request.form['date']
        expensestype = request.form['expensestype']
        amount = request.form['amount']
        particulars = request.form['particulars']
        remarks = request.form['remarks']
        
        

            # Database connection
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="Omnipro"
            )
        mycursor = mydb.cursor()

            # Update SQL query
        sql = "UPDATE expenses SET date=%s, expensestype=%s,amount=%s, particulars=%s, remarks=%s WHERE id=%s"
        val = (date, expensestype,amount, particulars, remarks,id)
        mycursor.execute(sql, val)
        mydb.commit()

            # Close cursor and database connection
        mycursor.close()
        mydb.close()

        flash("Data Updated Successfully")

    

    return redirect(url_for('Expenses'))




@app.route('/Information', methods=['GET', 'POST'])
def Information():
    mydb = get_db_connection()
    mycursor = mydb.cursor(buffered=True)

    if request.method == 'POST':
        
        Date = request.form.get('Date')
        Source = request.form.get('source')
        City = request.form.get('city')
        Title = request.form.get('Title')
        Information = request.form.get('Information')
        Author_Keywords = request.form.get('Author_Keywords')
        Email = request.form.get('Email')
        Phone = request.form.get('Phone')
        Subject = request.form.get('Subject')
        query = """
        INSERT INTO information ( Date, Source, City, Title, Information, Author_Keywords, Email, Phone, Subject)
        VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = ( Date, Source, City, Title, Information, Author_Keywords, Email, Phone, Subject)
        mycursor.execute(query, values)
        mydb.commit()

        return redirect(url_for('Information'))

    mycursor.execute("SELECT * FROM information")
    information = mycursor.fetchall()

    
    mycursor.execute("SELECT * FROM city")
    value = mycursor.fetchall()

    mycursor.execute("SELECT * FROM source")
    sources = mycursor.fetchall()

    search_query = request.args.get('search', '')
    page = int(request.args.get('page', 1))
    per_page = 10
    offset = (page - 1) * per_page
    
    mycursor.execute("SELECT COUNT(*) FROM information WHERE Date LIKE %s OR Source LIKE %s OR Author_Keywords	 LIKE %s", (f'{search_query}%',f'{search_query}%',f'{search_query}%'))
    total_customers = mycursor.fetchone()[0]
    
    mycursor.execute("SELECT * FROM information WHERE Date LIKE %s OR Source LIKE %s OR Author_Keywords LIKE %s   ORDER BY id DESC LIMIT %s OFFSET %s",
                   (f'{search_query}%',f'{search_query}%',f'{search_query}%', per_page, offset))
    information = mycursor.fetchall()

    mycursor.close()
    mydb.close()
    
    total_pages = (total_customers + per_page - 1) // per_page


    return render_template('Information.html', sources=sources,value=value,information=information,page=page, per_page=per_page, total_pages=total_pages, search_query=search_query)


@app.route('/add_information', methods=['GET', 'POST'])
def add_information():
    if request.method == 'POST':
        # Check if a file was submitted
        if 'file' not in request.files:
            flash('No file part.', 'danger')
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash('No selected file.', 'danger')
            return redirect(request.url)

        # Check for allowed file extensions
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            try:
                # Read the Excel file into a Pandas DataFrame
                df = pd.read_excel(filepath)

                # Database connection
                mydb = get_db_connection()
                if not mydb:
                    flash('Database connection failed.', 'danger')
                    os.remove(filepath)
                    return redirect(url_for('Information'))

                mycursor = mydb.cursor(buffered=True)

                # SQL query to insert data into the information table
                insert_query = """
                    INSERT INTO information (Date, Source, City, Title, Information, Author_Keywords, Email, Phone, Subject)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """

                inserted_rows = 0
                duplicate_rows = []

                # Iterate over each row in the Excel file
                for index, row in df.iterrows():
                    Date = str(row['date']).strip()
                    Source = str(row['source']).strip().upper()
                    City = str(row['city']).strip().upper()
                    Title = str(row['title']).strip().upper()
                    Information = str(row['information']).strip().upper()
                    Author_Keywords = str(row['author_keywords']).strip().upper()
                    Email = str(row['email']).strip()
                    Phone = str(row['phone']).strip()
                    Subject = str(row['subject']).strip().upper()

                    # Check for duplicates
                    mycursor.execute("SELECT COUNT(*) FROM information WHERE Date = %s AND Source = %s AND City = %s AND Title = %s AND Information = %s AND Author_Keywords = %s AND Email = %s AND Phone = %s AND Subject = %s",
                                     (Date, Source, City, Title, Information, Author_Keywords, Email, Phone, Subject))
                    if mycursor.fetchone()[0] > 0:
                        duplicate_rows.append(f"Row {index + 2}: Duplicate entry found.")
                        continue  # Skip this iteration if a duplicate is found

                    try:
                        # Insert the new information data
                        mycursor.execute(insert_query, (Date, Source, City, Title, Information, Author_Keywords, Email, Phone, Subject))
                        mydb.commit()  # Commit the transaction
                        inserted_rows += 1
                    except mysql.connector.Error as e:
                        flash(f'Error inserting row {index + 2}: {str(e)}', 'danger')

                # Feedback to the user on the result of the upload
                success_message = f'Successfully inserted {inserted_rows} rows.'
                if duplicate_rows:
                    failure_message = f' {len(duplicate_rows)} rows were not inserted due to duplication.'
                    failure_message += f' Duplicate rows: {", ".join(duplicate_rows)}.'
                    flash(success_message + failure_message, 'warning')
                else:
                    flash(success_message, 'success')

            except Exception as e:
                flash(f'Error processing file: {str(e)}', 'danger')

            finally:
                # Close the database connection and remove the uploaded file
                if 'mydb' in locals():
                    mycursor.close()
                    mydb.close()
                os.remove(filepath)  # Clean up uploaded file

            return redirect(url_for('Information'))  # Redirect to your desired endpoint

    # If GET request, retrieve existing records to display
    mydb = get_db_connection()
    mycursor = mydb.cursor(buffered=True)
    mycursor.execute("SELECT * FROM information")
    information = mycursor.fetchall()
    mycursor.execute("SELECT * FROM city")
    cities = mycursor.fetchall()
    mycursor.execute("SELECT * FROM source")
    sources = mycursor.fetchall()
    mycursor.close()
    mydb.close()

    return render_template('Information.html', information=information, sources=sources, cities=cities)

@app.route('/delete_information/<int:id>')
def delete_information(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Execute DELETE operation
        cursor.execute("DELETE FROM information WHERE id = %s", (id,))
        conn.commit()

        cursor.close()
        conn.close()

        flash('Record has been deleted successfully', 'success')
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')

    return redirect(url_for('Information'))

    


@app.route('/update_information', methods=['POST'])
def update_information():
    if request.method == 'POST':
        id = request.form['id']
        Date = request.form['Date']
        Source = request.form['Source']
        City = request.form['City']
        Title = request.form['Title']
        Information = request.form.get('Information')
        Author_Keywords = request.form.get('Author_Keywords')
        Email = request.form.get('Email')
        Phone = request.form.get('Phone')
        Subject = request.form.get('Subject')
        
        

            # Database connection
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="Omnipro"
            )
        mycursor = mydb.cursor()

            # Update SQL query
        sql = "UPDATE information SET Date=%s, Source=%s, City=%s, Title=%s, Information=%s, Author_Keywords=%s, Email=%s, Phone=%s, Subject=%s WHERE id=%s"
        val = (Date, Source, City, Title,Information,Author_Keywords,Email,Phone,Subject,id)
        mycursor.execute(sql, val)
        mydb.commit()

            # Close cursor and database connection
        mycursor.close()
        mydb.close()

        flash("Data Updated Successfully")

    

    return redirect(url_for('Information'))





@app.route('/Terminology', methods=['GET', 'POST'])
def Terminology():
    mydb = get_db_connection()
    mycursor = mydb.cursor(buffered=True)

    if request.method == 'POST':
        
        Date = request.form.get('Date')
        Keyword = request.form.get('Keyword')
        Alphabet = request.form.get('Alphabet')
        Description = request.form.get('Description')
        Remarks = request.form.get('Remarks')
        query = """
        INSERT INTO terminology ( Date, Keyword, Alphabet, Description, Remarks)
        VALUES ( %s, %s, %s, %s, %s)
        """
        values = (id, Date, Keyword, Alphabet, Description, Remarks)
        mycursor.execute(query, values)
        mydb.commit()

        return redirect(url_for('Terminology'))

    mycursor.execute("SELECT * FROM terminology")
    terminology = mycursor.fetchall()

    search_query = request.args.get('search', '')
    page = int(request.args.get('page', 1))
    per_page = 10
    offset = (page - 1) * per_page
    
    mycursor.execute("SELECT COUNT(*) FROM terminology WHERE 	Date LIKE %s OR Keyword LIKE %s OR Alphabet LIKE %s", (f'{search_query}%',f'{search_query}%',f'{search_query}%'))
    total_customers = mycursor.fetchone()[0]
    
    mycursor.execute("SELECT * FROM terminology WHERE Date LIKE %s OR Keyword LIKE %s OR Alphabet LIKE %s   ORDER BY id DESC LIMIT %s OFFSET %s",
                   (f'{search_query}%',f'{search_query}%',f'{search_query}%', per_page, offset))
    deliveryterms = mycursor.fetchall()

    mycursor.close()
    mydb.close()
    
    total_pages = (total_customers + per_page - 1) // per_page


    return render_template('Terminology.html', terminology=terminology, page=page, per_page=per_page, total_pages=total_pages, search_query=search_query)

@app.route('/add_terminology', methods=['GET', 'POST'])
def add_terminology():
    if request.method == 'POST':
        # Check if a file was submitted
        if 'file' not in request.files:
            flash('No file part.', 'danger')
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash('No selected file.', 'danger')
            return redirect(request.url)

        # Check for allowed file extensions
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            try:
                # Read the Excel file into a Pandas DataFrame
                df = pd.read_excel(filepath)

                # Check for required columns
                required_columns = ['date', 'keyword', 'alphabet', 'description', 'remarks']
                for column in required_columns:
                    if column not in df.columns:
                        flash(f'Missing column: {column}', 'danger')
                        os.remove(filepath)
                        return redirect(request.url)

                # Database connection
                mydb = get_db_connection()
                if not mydb:
                    flash('Database connection failed.', 'danger')
                    os.remove(filepath)
                    return redirect(url_for('Terminology'))

                mycursor = mydb.cursor(buffered=True)

                # SQL query to insert data into the terminology table
                insert_query = """
                    INSERT INTO terminology (Date, Keyword, Alphabet, Description, Remarks)
                    VALUES (%s, %s, %s, %s, %s)
                """

                inserted_rows = 0
                duplicate_rows = []

                # Iterate over each row in the Excel file
                for index, row in df.iterrows():
                    Date = str(row['date']).strip()
                    Keyword = str(row['keyword']).strip().upper()
                    Alphabet = str(row['alphabet']).strip().upper()
                    Description = str(row['description']).strip().upper()
                    Remarks = str(row['remarks']).strip().upper()

                    # Check for duplicates based on Keyword
                    mycursor.execute("SELECT COUNT(*) FROM terminology WHERE Keyword = %s", (Keyword,))
                    if mycursor.fetchone()[0] > 0:
                        duplicate_rows.append(f"Row {index + 2}: Duplicate entry found for keyword '{Keyword}'.")
                        continue  # Skip this iteration if a duplicate is found

                    try:
                        # Insert the new terminology data
                        mycursor.execute(insert_query, (Date, Keyword, Alphabet, Description, Remarks))
                        inserted_rows += 1
                    except mysql.connector.Error as e:
                        flash(f'Error inserting row {index + 2}: {str(e)}', 'danger')

                # Commit the transaction
                mydb.commit()

                # Feedback to the user on the result of the upload
                success_message = f'Successfully inserted {inserted_rows} rows.'
                if duplicate_rows:
                    failure_message = f' {len(duplicate_rows)} rows were not inserted due to duplication.'
                    failure_message += f' Duplicate rows: {", ".join(duplicate_rows)}.'
                    flash(success_message + failure_message, 'warning')
                else:
                    flash(success_message, 'success')

            except Exception as e:
                flash(f'Error processing file: {str(e)}', 'danger')

            finally:
                # Close the database connection and remove the uploaded file
                if 'mydb' in locals():
                    mycursor.close()
                    mydb.close()
                os.remove(filepath)  # Clean up uploaded file

            return redirect(url_for('Terminology'))  # Redirect to your desired endpoint

    # If GET request, retrieve existing records to display
    mydb = get_db_connection()
    mycursor = mydb.cursor(buffered=True)
    mycursor.execute("SELECT * FROM terminology")
    terminology = mycursor.fetchall()
    mycursor.close()
    mydb.close()

    return render_template('Terminology.html', terminology=terminology)


@app.route('/delete_terminology/<int:id>')
def delete_terminology(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Execute DELETE operation
        cursor.execute("DELETE FROM terminology WHERE id = %s", (id,))
        conn.commit()

        cursor.close()
        conn.close()

        flash('Record has been deleted successfully', 'success')
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')

    return redirect(url_for('Terminology'))

    


@app.route('/update_terminology', methods=['POST'])
def update_terminology():
    if request.method == 'POST':
        id = request.form['id']
        Date = request.form['Date']
        Keyword = request.form['Keyword']
        Alphabet = request.form['Alphabet']
        Description = request.form['Description']
        Remarks = request.form['Remarks']
        
        
        

            # Database connection
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="Omnipro"
            )
        mycursor = mydb.cursor()

            # Update SQL query
        sql = "UPDATE terminology SET Date=%s, Keyword=%s, Alphabet=%s, Description=%s, Remarks=%s  WHERE id=%s"
        val = (Date, Keyword, Alphabet, Description,Remarks,id)
        mycursor.execute(sql, val)
        mydb.commit()

            # Close cursor and database connection
        mycursor.close()
        mydb.close()

        flash("Data Updated Successfully")

    

    return redirect(url_for('Terminology'))

@app.route('/Followup', methods=['GET', 'POST'])
def Followup():
    mydb = get_db_connection()
    mycursor = mydb.cursor(buffered=True)

    if request.method == 'POST':
        
        Issue_Initiated_Date = request.form.get('Issue_Initiated_Date')
        Issue = request.form.get('issue')
        Issue_Particulars = request.form.get('Issue_Particulars')
        Issue_Follow_up_Date = request.form.get('Issue_Follow_up_Date')
        Update_Information = request.form.get('Update_Information')
        Issue_Status = request.form.get('Issue_Status')
        Assigned_To = request.form.get('Assigned_To')
        Assigned_By = request.form.get('Assigned_By')
        query = """
        INSERT INTO follow_up ( Issue_Initiated_Date, Issue, Issue_Particulars,Issue_Follow_up_Date, Update_Information, Issue_Status, Assigned_To, Assigned_By)
        VALUES ( %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = ( Issue_Initiated_Date, Issue, Issue_Particulars,Issue_Follow_up_Date, Update_Information, Issue_Status, Assigned_To, Assigned_By)
        mycursor.execute(query, values)
        mydb.commit()
        flash('Data added Successfully!')
        return redirect(url_for('Followup'))

    mycursor.execute("SELECT * FROM follow_up")
    follow_up = mycursor.fetchall()
    mycursor.execute("SELECT DISTINCT employeename FROM employee WHERE status=1")
    employee = mycursor.fetchall()
    mycursor.execute("SELECT * FROM issue_type")
    value = mycursor.fetchall()

    

    search_query = request.args.get('search', '')
    page = int(request.args.get('page', 1))
    per_page = 10
    offset = (page - 1) * per_page
    
    mycursor.execute("SELECT COUNT(*) FROM follow_up WHERE 	Issue_Initiated_Date LIKE %s OR 	Issue LIKE %s OR Issue_Follow_up_Date LIKE %s", (f'{search_query}%',f'{search_query}%',f'{search_query}%'))
    total_customers = mycursor.fetchone()[0]
    
    mycursor.execute("SELECT * FROM follow_up WHERE Issue_Initiated_Date LIKE %s OR Issue LIKE %s OR Issue_Follow_up_Date LIKE %s   ORDER BY id DESC LIMIT %s OFFSET %s",
                   (f'{search_query}%',f'{search_query}%',f'{search_query}%', per_page, offset))
    follow_up = mycursor.fetchall()

    mycursor.close()
    mydb.close()
    
    total_pages = (total_customers + per_page - 1) // per_page



    return render_template('Followup.html',value=value, employee=employee,follow_up=follow_up,page=page, per_page=per_page, total_pages=total_pages, search_query=search_query)


@app.route('/add_followup', methods=['GET', 'POST'])
def add_followup():
    if request.method == 'POST':
        # Check if a file was submitted
        if 'file' not in request.files:
            flash('No file part.', 'danger')
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash('No selected file.', 'danger')
            return redirect(request.url)

        # Check for allowed file extensions
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            try:
                # Read the Excel file into a Pandas DataFrame
                df = pd.read_excel(filepath)

                # Check for required columns
                required_columns = ['issue_date', 'issue', 'issue_particulars', 'issue_follow_up_date', 'update_information', 'issue_status', 'assigned_to', 'assigned_by']
                for column in required_columns:
                    if column not in df.columns:
                        flash(f'Missing column: {column}', 'danger')
                        os.remove(filepath)
                        return redirect(request.url)

                # Database connection
                mydb = get_db_connection()
                if not mydb:
                    flash('Database connection failed.', 'danger')
                    os.remove(filepath)
                    return redirect(url_for('Followup'))

                mycursor = mydb.cursor(buffered=True)

                # SQL query to insert data into the follow_up table
                insert_query = """
                    INSERT INTO follow_up (Issue_Initiated_Date, Issue, Issue_Particulars, Issue_Follow_up_Date, Update_Information, Issue_Status, Assigned_To, Assigned_By)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """

                inserted_rows = 0
                duplicate_rows = []

                # Iterate over each row in the Excel file
                for index, row in df.iterrows():
                    Issue_Initiated_Date = str(row['issue_date']).strip()
                    Issue = str(row['issue']).strip().upper()
                    Issue_Particulars = str(row['issue_particulars']).strip().upper()
                    Issue_Follow_up_Date = str(row['issue_follow_up_date']).strip()
                    Update_Information = str(row['update_information']).strip().upper()
                    Issue_Status = str(row['issue_status']).strip().upper()
                    Assigned_To = str(row['assigned_to']).strip().upper()
                    Assigned_By = str(row['assigned_by']).strip().upper()

                    # Check for duplicates across all columns
                    mycursor.execute("""
                        SELECT COUNT(*) FROM follow_up 
                        WHERE Issue_Initiated_Date = %s AND Issue = %s AND Issue_Particulars = %s AND 
                              Issue_Follow_up_Date = %s AND Update_Information = %s AND 
                              Issue_Status = %s AND Assigned_To = %s AND Assigned_By = %s
                    """, (Issue_Initiated_Date, Issue, Issue_Particulars, Issue_Follow_up_Date, Update_Information, Issue_Status, Assigned_To, Assigned_By))

                    if mycursor.fetchone()[0] > 0:
                        duplicate_rows.append(f"Row {index + 2}: Duplicate entry found.")
                        continue  # Skip this iteration if a duplicate is found

                    try:
                        # Insert the new follow-up data
                        mycursor.execute(insert_query, (Issue_Initiated_Date, Issue, Issue_Particulars, Issue_Follow_up_Date, Update_Information, Issue_Status, Assigned_To, Assigned_By))
                        inserted_rows += 1
                    except mysql.connector.Error as e:
                        flash(f'Error inserting row {index + 2}: {str(e)}', 'danger')

                # Commit the transaction
                mydb.commit()

                # Feedback to the user on the result of the upload
                success_message = f'Successfully inserted {inserted_rows} rows.'
                if duplicate_rows:
                    failure_message = f' {len(duplicate_rows)} rows were not inserted due to duplication.'
                    failure_message += f' Duplicate rows: {", ".join(duplicate_rows)}.'
                    flash(success_message + failure_message, 'warning')
                else:
                    flash(success_message, 'success')

            except Exception as e:
                flash(f'Error processing file: {str(e)}', 'danger')

            finally:
                # Close the database connection and remove the uploaded file
                if 'mydb' in locals():
                    mycursor.close()
                    mydb.close()
                os.remove(filepath)  # Clean up uploaded file

            return redirect(url_for('Followup'))  # Redirect to your desired endpoint

    # If GET request, retrieve existing records to display
    mydb = get_db_connection()
    mycursor = mydb.cursor(buffered=True)
    mycursor.execute("SELECT * FROM follow_up")
    follow_up = mycursor.fetchall()
    mycursor.close()
    mydb.close()

    return render_template('Followup.html', follow_up=follow_up)

@app.route('/delete_Followup/<int:id>')
def delete_Followup(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Execute DELETE operation
        cursor.execute("DELETE FROM follow_up WHERE id = %s", (id,))
        conn.commit()

        cursor.close()
        conn.close()

        flash('Record has been deleted successfully', 'success')
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')

    return redirect(url_for('Followup'))

    


@app.route('/update_Followup', methods=['POST'])
def update_Followup():
    if request.method == 'POST':
        id = request.form['id']
        Issue_Initiated_Date = request.form['Issue_Initiated_Date']
        Issue = request.form['Issue']
        Issue_Particulars = request.form['Issue_Particulars']
        Issue_Follow_up_Date = request.form['Issue_Follow_up_Date']
        Update_Information = request.form['Update_Information']
        Issue_Status = request.form['Issue_Status']
        Assigned_To = request.form['Assigned_To']
        Assigned_By = request.form['Assigned_By']
        
        

            # Database connection
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="Omnipro"
            )
        mycursor = mydb.cursor()

            # Update SQL query
        sql = "UPDATE follow_up SET Issue_Initiated_Date=%s, Issue=%s, Issue_Particulars=%s, Issue_Follow_up_Date=%s, Update_Information=%s, Issue_Status=%s, Assigned_To=%s ,Assigned_By=%s WHERE id=%s"
        val = (Issue_Initiated_Date, Issue, Issue_Particulars, Issue_Follow_up_Date,Update_Information,Issue_Status,Assigned_To,Assigned_By,id)
        mycursor.execute(sql, val)
        mydb.commit()

            # Close cursor and database connection
        mycursor.close()
        mydb.close()

        flash("Data Updated Successfully")

    

    return redirect(url_for('Followup'))





@app.route('/Item', methods=['GET', 'POST'])
def Item():
    mydb = get_db_connection()
    mycursor = mydb.cursor(buffered=True)

    if request.method == 'POST':
        manufacturername = request.form.get('manufacturername')
        distiproposalsent = request.form.get('Disti_Proposal_Sent')
        updateddate = request.form.get('updateddate')

        # Validate updated date
        if datetime.strptime(updateddate, '%Y-%m-%d') > datetime.today():
            return "Error: Date cannot be in the future!", 400

        followupdate = request.form.get('followupdate')

        # Validate follow-up date
        
        comments = request.form.get('comments')
        remarks = request.form.get('remarks')
        rating = request.form.get('rating')

        query = """
        INSERT INTO item (manufacturername, distiproposalsent, updatedate, followupdate, comments, remarks, rating)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        values = (manufacturername, distiproposalsent, updateddate, followupdate, comments, remarks, rating)
        mycursor.execute(query, values)
        mydb.commit()

        return redirect(url_for('Item'))

    # Search functionality
    search_query = request.args.get('search', '')
    page = int(request.args.get('page', 1))
    per_page = 10
    offset = (page - 1) * per_page

    # Use CONCAT_WS to concatenate all columns for search
    mycursor.execute("""
        SELECT COUNT(*) FROM item 
        WHERE CONCAT_WS(' ', manufacturername, distiproposalsent, updatedate, followupdate, comments, remarks, rating)
        LIKE %s
    """, (f'%{search_query}%',))
    total_contacts = mycursor.fetchone()[0]

    mycursor.execute("""
        SELECT * FROM item 
        WHERE CONCAT_WS(' ', manufacturername, distiproposalsent, updatedate, followupdate, comments, remarks, rating)
        LIKE %s
        ORDER BY manufacturername ASC, remarks ASC 
        LIMIT %s OFFSET %s
    """, (f'%{search_query}%', per_page, offset))
    item = mycursor.fetchall()

    mycursor.execute("SELECT supplier_name FROM suppliers WHERE sub_type = 'manufacturer';")
    suppliers = mycursor.fetchall()

    mycursor.execute("SELECT distinct distiproposalsent FROM item")
    items = mycursor.fetchall()

    mycursor.close()
    mydb.close()

    total_pages = (total_contacts + per_page - 1) // per_page
    max_date = datetime.today().strftime('%Y-%m-%d')

    return render_template('Item.html', max_date=max_date, suppliers=suppliers, item=item,items=items, page=page, per_page=per_page, total_pages=total_pages, search_query=search_query)

@app.route('/check_manufacturer_name', methods=['POST'])
def check_manufacturer_name():
    manufacturername = request.form['manufacturername']
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Query to check if the manufacturer name exists in the item table
    cursor.execute("SELECT COUNT(*) FROM item WHERE manufacturername = %s", (manufacturername,))
    result = cursor.fetchone()[0]
    
    cursor.close()
    conn.close()
    
    # Return whether the name exists or not
    return jsonify({'exists': result > 0})

@app.route('/delete_item/<int:id>')
def delete_item(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Execute DELETE operation
        cursor.execute("DELETE FROM item WHERE id = %s", (id,))
        conn.commit()

        cursor.close()
        conn.close()

        flash('Record has been deleted successfully', 'success')
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')

    return redirect(url_for('Item'))

    


@app.route('/update_item', methods=['POST'])
def update_item():
    if request.method == 'POST':
        id = request.form['id']
        manufacturername = request.form['manufacturername']
        distiproposalsent = request.form['distiproposalsent']
        updatedate = request.form['updatedate']
        followupdate = request.form['followupdate']
        comments = request.form.get('comments')
        remarks = request.form.get('remarks')
        rating = request.form.get('rating')
        
        

            # Database connection
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="Omnipro"
            )
        mycursor = mydb.cursor()

            # Update SQL query
        sql = "UPDATE item SET manufacturername=%s, distiproposalsent=%s, updatedate=%s, followupdate=%s, comments=%s, remarks=%s, rating=%s WHERE id=%s"
        val = (manufacturername, distiproposalsent, updatedate, followupdate,comments,remarks,rating,id)
        mycursor.execute(sql, val)
        mydb.commit()

            # Close cursor and database connection
        mycursor.close()
        mydb.close()

        flash("Data Updated Successfully")

    

    return redirect(url_for('Item'))



@app.route('/upload_pdf', methods=['POST'])
def upload_pdf():
    if 'pdf_file' in request.files:
        pdf_file = request.files['pdf_file']
        if pdf_file.filename != '':
            pdf_content = pdf_file.read()
            test_name = request.form['testName']  # Retrieve the test name from the form data

            conn = get_db_connection()
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO addnewdata (test_name, reports) VALUES (%s, %s)", (test_name, pdf_content))
                conn.commit()
                return jsonify({'success': True})
            except mysql.connector.Error as err:
                return jsonify({'success': False, 'error': str(err)})
            finally:
                cursor.close()
                conn.close()

    return jsonify({'success': False})
    
@app.route('/add_supplier_contacts', methods=['POST'])
def add_supplier_contacts():
    # Get form data from request
    supplier_name = request.form['suppliername']
    contact_person = request.form['contact_person']
    contact_number = request.form['contact_number']
    email = request.form.get('email', None)  # Optional field
    skype = request.form.get('skype', None)  # Optional field
    added_by = request.form['addedby']
    date = request.form['date']

    # Add contact information to the database
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Check for existing contact with the same details
        check_query = """
            SELECT COUNT(*) FROM contact
            WHERE supplier_name = %s AND contact_person = %s AND contact_number = %s 
            AND email = %s AND skype = %s AND added_by = %s AND date = %s
        """
        cursor.execute(check_query, (supplier_name, contact_person, contact_number, email, skype, added_by, date))
        result = cursor.fetchone()

        if result[0] > 0:
            # Flash message if a duplicate is found
            flash('Duplicate contact already exists.', 'warning')
        else:
            # Insert query
            insert_query = """
                INSERT INTO contact (supplier_name, contact_person, contact_number, email, skype, added_by, date)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (supplier_name, contact_person, contact_number, email, skype, added_by, date))

            # Commit transaction
            connection.commit()

            # Flash success message
            flash('Contact successfully added', 'success')

    except mysql.connector.Error as err:
        # Flash error message if there is an issue
        flash(f'Error: {err}', 'danger')

    finally:
        cursor.close()
        connection.close()

    # Redirect back to the supplier contacts page or another page
    return redirect(url_for('Suppliers'))



@app.route('/add_customer_contacts', methods=['GET', 'POST'])
def add_customer_contacts():
    mydb = get_db_connection()
    mycursor = mydb.cursor(buffered=True)
    error = None
    customername = request.form.get('customername')

    if request.method == 'POST':
        if 'file' in request.files:
            file = request.files['file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                
                df = pd.read_excel(filepath)
                
                valid_number_pattern = re.compile(r'^[0-9\+\-]{10,16}$')
                employee_names = get_employee_names()

                for index, row in df.iterrows():
                    contact_number = str(row['contact_number']).strip()
                    whatsapp_number = str(row['whatsapp']).strip()
                    email = str(row['email']).strip()
                    added_by = str(row['added_by']).strip()

                    if (valid_number_pattern.match(contact_number) and 
                        valid_number_pattern.match(whatsapp_number) and 
                        email.endswith('@gmail.com') and
                        added_by in employee_names):
                        
                        try:
                            mycursor.execute(
                                "INSERT INTO contacts (customer_name, contact_person, contact_number, department, whatsapp, email, skype, added_by, date) "
                                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                                (customername, row['contact_person'].upper(), contact_number, row['department'].upper(), whatsapp_number, email, row['skype'], added_by.upper(), row['date'])
                            )
                            mydb.commit()
                        except IntegrityError:
                            error = "Duplicate entry. Please check the data and try again."
                    
                    else:
                        print(f"Skipped row {index} due to invalid data - Contact: {contact_number}, WhatsApp: {whatsapp_number}, Email: {email}, Added By: {added_by}")
        
        # Handle the manual form submission separately
        contact_person = request.form.get('contact_person')
        contact_number = request.form.get('contact_number')
        department = request.form.get('department')
        whatswpp = request.form.get('whatswpp')
        email = request.form.get('email')
        skype = request.form.get('skype')
        addedby = request.form.get('addedby')
        date = request.form.get('date')
        
        if customername and contact_person and contact_number:
            query = """
            INSERT INTO contacts (customer_name, contact_person, contact_number, department, whatsapp, email, skype, added_by, date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            values = (customername, contact_person.upper(), contact_number, department.upper(), whatswpp, email, skype, addedby.upper(), date)
            
            try:
                mycursor.execute(query, values)
                mydb.commit()
                flash('Contact added successfully!', 'success')
                return redirect(url_for('Customers'))
            except IntegrityError:
                error = "Duplicate entry. Please try again with a different ID or branch."
        else:
            error = "Please fill in all required fields."

    mycursor.execute("SELECT * FROM contacts")
    branches = mycursor.fetchall()


    mycursor.execute("SELECT * FROM employee")
    employees = mycursor.fetchall()
    mycursor.execute("SELECT * FROM customers")
    customers = mycursor.fetchall()
    mycursor.close()
    mydb.close()
    flash("contact added successfully")
    return render_template('manage_calling_data.html', branches=branches, error=error,employees=employees,customers=customers)

@app.route('/add_customer_excel', methods=['GET', 'POST'])
def add_customer_excel():
    mydb = get_db_connection()
    mycursor = mydb.cursor(buffered=True)
    error = None
    customername = request.form.get('customername')

    if request.method == 'POST':
        if 'file' in request.files:
            file = request.files['file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)

                df = pd.read_excel(filepath)
                valid_number_pattern = re.compile(r'^[0-9\+\-]{10,16}$')
                employee_names = get_employee_names()

                contacts = []
                failed_rows = []
                inserted_rows = 0

                for index, row in df.iterrows():
                    contact_name = str(row['contact_person']).strip().upper()
                    contact_number = str(row['contact_number']).strip()
                    whatsapp_number = str(row['whatsapp']).strip()
                    email = str(row['email']).strip()
                    added_by = str(row['added_by']).strip().upper()
                    department = str(row['department']).strip().upper()
                    skype = str(row['skype']).strip()
                    date = str(row['date']).strip()

                    if (valid_number_pattern.match(contact_number) and 
                        valid_number_pattern.match(whatsapp_number) and 
                        email.endswith('@gmail.com') and
                        added_by in employee_names):

                        try:
                            mycursor.execute(
                                "INSERT INTO contacts (customer_name, contact_person, contact_number, department, whatsapp, email, skype, added_by, date) "
                                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                                (customername, contact_name, contact_number, department, whatsapp_number, email, skype, added_by, date)
                            )
                            inserted_rows += 1
                        except IntegrityError:
                            failed_rows.append(f"Row {index + 2}: Duplicate entry")
                    else:
                        failed_rows.append(f"Row {index + 2}: Invalid data - "
                                           f"Contact Number: {contact_number}, "
                                           f"WhatsApp Number: {whatsapp_number}, "
                                           f"Email: {email}, "
                                           f"Added By: {added_by}")

                if inserted_rows > 0:
                    success_message = f'Successfully inserted {inserted_rows} rows.'
                    if failed_rows:
                        success_message += f' Rows not inserted: {"; ".join(failed_rows)}'
                    flash(success_message, 'success')
                elif error:
                    flash(error, 'danger')

                os.remove(filepath)  # Optionally delete the file after processing

        else:
            flash('No file uploaded or invalid file type.', 'danger')

        return redirect(url_for('Customers'))

    mycursor.close()
    mydb.close()

    return render_template('manage_calling_data.html')


@app.route('/add_supplier_excel', methods=['GET', 'POST'])
def add_supplier_excel():
    if request.method == 'POST':
        suppliername = request.form.get('suppliername')

        if 'file' not in request.files:
            flash('No file part.', 'danger')
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash('No selected file.', 'danger')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            try:
                df = pd.read_excel(filepath)

                # Regex for validating contact number
                valid_number_pattern = re.compile(r'^[0-9\+\-]{10,16}$')

                # Fetch valid employee names
                employee_names = get_employee_names()

                # Database connection
                mydb = get_db_connection()
                if not mydb:
                    flash('Database connection failed.', 'danger')
                    os.remove(filepath)
                    return redirect(url_for('manage_suppliers'))

                mycursor = mydb.cursor(buffered=True)

                insert_query = """
                    INSERT INTO contact (supplier_name, contact_person, contact_number, email, skype, added_by,date)
                    VALUES (%s, %s, %s, %s, %s, %s,%s)
                """

                # Check for a duplicate row by comparing all fields
                check_query = """
                    SELECT COUNT(*) FROM contact 
                    WHERE supplier_name = %s AND contact_person = %s AND contact_number = %s AND email = %s
                    AND skype = %s AND added_by = %s AND date=%s
                """

                inserted_rows = 0
                failed_rows = []

                # Iterate over each row in the Excel file
                for index, row in df.iterrows():
                    contact_person = str(row['contact_person']).strip()
                    contact_number = str(row['contact_number']).strip()
                    email = str(row['email']).strip()
                    skype = str(row['skype']).strip()
                    added_by = str(row['added_by']).strip()
                    date = pd.to_datetime(row['date']).date()  # Extract only the date part

                    # Validate contact number, email, and employee name
                    if (valid_number_pattern.match(contact_number) and
                        '@' in email and
                        added_by in employee_names):

                        # Check if a row with the exact data already exists
                        mycursor.execute(check_query, (suppliername, contact_person, contact_number, email, skype, added_by,date))
                        if mycursor.fetchone()[0] == 0:
                            try:
                                mycursor.execute(insert_query, (suppliername, contact_person, contact_number, email, skype, added_by,date))
                                mydb.commit()
                                inserted_rows += 1
                            except mysql.connector.Error as e:
                                failed_rows.append(f"Row {index + 2}: Database error - {str(e)}")
                        else:
                            failed_rows.append(f"Row {index + 2}: Duplicate entry")

                    else:
                        failed_rows.append(f"Row {index + 2}: Invalid data - Contact Number: {contact_number}, Email: {email}, Added By: {added_by}")

                if inserted_rows > 0:
                    success_message = f'Successfully inserted {inserted_rows} rows.'
                    if failed_rows:
                        success_message += f' Rows not inserted: {"; ".join(failed_rows)}'
                    flash(success_message, 'success')
                else:
                    flash('No valid data was inserted.', 'danger')

            except Exception as e:
                flash(f'Error processing file: {str(e)}', 'danger')

            finally:
                if 'mydb' in locals():
                    mycursor.close()
                    mydb.close()
                os.remove(filepath)  # Optionally delete the file after processing

            return redirect(url_for('Suppliers'))

    return render_template('Suppliers.html')


@app.route('/add_new_supp', methods=['GET', 'POST'])
def add_new_supp():
    if request.method == 'POST':
        # Check if a file was submitted
        if 'file' not in request.files:
            flash('No file part.', 'danger')
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash('No selected file.', 'danger')
            return redirect(request.url)

        # Check for allowed file extensions
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            try:
                # Read the Excel file into a Pandas DataFrame
                df = pd.read_excel(filepath)

                # Database connection
                mydb = get_db_connection()
                if not mydb:
                    flash('Database connection failed.', 'danger')
                    os.remove(filepath)
                    return redirect(url_for('manage_suppliers'))

                mycursor = mydb.cursor(buffered=True)

                # SQL query to insert data into the `suppliers` table
                insert_query = """
                    INSERT INTO suppliers (supplier_name, sub_type, contact_number, fax, website, address, remarks, applications)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """

                # SQL query to check for exact duplicates by matching all columns
                check_query = """
                    SELECT COUNT(*) FROM suppliers 
                    WHERE supplier_name = %s AND sub_type = %s AND contact_number = %s AND fax = %s 
                    AND website = %s AND address = %s AND remarks = %s AND applications = %s
                """

                inserted_rows = 0
                duplicate_rows = []
                invalid_subtype_rows = []

                # Iterate over each row in the Excel file
                for index, row in df.iterrows():
                    supplier_name = str(row['supplier_name']).strip()
                    sub_type = str(row['supplier_type']).strip()
                    contact_number = str(row['contact_number']).strip()
                    fax = str(row['fax']).strip()
                    website = str(row['website']).strip()
                    address = str(row['address']).strip()
                    remarks = str(row['remarks']).strip()
                    applications = str(row['applications']).strip()
                    supplier_type = get_supplier_type()

                    # Validate sub_type as either 'manufacturer' or 'distributor'
                    if sub_type not in supplier_type:
                        invalid_subtype_rows.append(f"Row {index + 2}: Invalid sub_type '{sub_type}'")
                        continue  # Skip this row if sub_type is invalid

                    # Check for duplicates by comparing all columns
                    mycursor.execute(check_query, (supplier_name, sub_type, contact_number, fax, website, address, remarks, applications))
                    if mycursor.fetchone()[0] == 0:  # No duplicates found
                        try:
                            # Insert the new supplier data
                            mycursor.execute(insert_query, (supplier_name, sub_type, contact_number, fax, website, address, remarks, applications))
                            mydb.commit()
                            inserted_rows += 1
                        except mysql.connector.Error as e:
                            duplicate_rows.append(f"Row {index + 2}: Database error - {str(e)}")
                    else:
                        duplicate_rows.append(f"Row {index + 2}: Duplicate entry")

                # Feedback to the user on the result of the upload
                total_rows = len(df)
                failed_rows = len(duplicate_rows) + len(invalid_subtype_rows)

                success_message = f'Successfully inserted {inserted_rows} rows.'
                if failed_rows > 0:
                    failure_message = f' {failed_rows} rows were not inserted.'
                    if invalid_subtype_rows:
                        failure_message += f' Invalid sub_type in rows: {", ".join(invalid_subtype_rows)}.'
                    if duplicate_rows:
                        failure_message += f' Duplicate rows: {", ".join(duplicate_rows)}.'
                    flash(success_message + failure_message, 'warning')
                else:
                    flash(success_message, 'success')

            except Exception as e:
                flash(f'Error processing file: {str(e)}', 'danger')

            finally:
                # Close the database connection and remove the uploaded file
                if 'mydb' in locals():
                    mycursor.close()
                    mydb.close()
                os.remove(filepath)

            return redirect(url_for('Suppliers'))

    return render_template('Suppliers.html')

@app.route('/add_new_parts', methods=['GET', 'POST'])
def add_new_parts():
    if request.method == 'POST':
        # Check if a file was submitted
        if 'file' not in request.files:
            flash('No file part.', 'danger')
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash('No selected file.', 'danger')
            return redirect(request.url)

        # Check for allowed file extensions
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            try:
                # Read the Excel file into a Pandas DataFrame
                df = pd.read_excel(filepath)

                # Database connection
                mydb = get_db_connection()
                if not mydb:
                    flash('Database connection failed.', 'danger')
                    os.remove(filepath)
                    return redirect(url_for('PartNo'))

                mycursor = mydb.cursor(buffered=True)

                # SQL query to insert data into the `part_item` table
                insert_query = """
                    INSERT INTO part_item (man_part_no, date, remarks)
                    VALUES (%s, %s, %s)
                """

                # SQL query to check for duplicates based on part number and date
                check_query = """
                    SELECT COUNT(*) FROM part_item WHERE man_part_no = %s AND date = %s
                """

                inserted_rows = 0
                duplicate_rows = []

                # Iterate over each row in the Excel file
                for index, row in df.iterrows():
                    part_number = str(row.get('part_number', '')).strip()  # Get part number
                    date_value = row.get('date')  # Get the raw date value from the DataFrame
                    remarks = str(row.get('remarks', '')).strip()  # Get remarks

                    # Use the raw date value directly (it may already be in datetime format)
                    date = date_value if date_value is not None else ''  # Handle None case

                    # Check for duplicates by part number and date
                    mycursor.execute(check_query, (part_number, date))
                    if mycursor.fetchone()[0] == 0:  # No duplicates found
                        try:
                            # Insert the new part data
                            mycursor.execute(insert_query, (part_number, date, remarks))
                            mydb.commit()
                            inserted_rows += 1
                        except mysql.connector.Error as e:
                            duplicate_rows.append(f"Row {index + 2}: Database error - {str(e)}")
                    else:
                        duplicate_rows.append(f"Row {index + 2}: Duplicate entry")

                # Feedback to the user on the result of the upload
                total_rows = len(df)
                failed_rows = len(duplicate_rows)

                success_message = f'Successfully inserted {inserted_rows} rows.'
                if failed_rows > 0:
                    failure_message = f' {failed_rows} rows were not inserted due to duplicates.'
                    if duplicate_rows:
                        failure_message += f' Duplicate rows: {", ".join(duplicate_rows)}.'
                    flash(success_message + failure_message, 'warning')
                else:
                    flash(success_message, 'success')

            except Exception as e:
                flash(f'Error processing file: {str(e)}', 'danger')

            finally:
                # Close the database connection and remove the uploaded file
                if 'mydb' in locals():
                    mycursor.close()
                    mydb.close()
                os.remove(filepath)

            return redirect(url_for('PartNo'))

    return render_template('PartNo.html')
 # Ensure you have a corresponding template
@app.route('/add_crossref', methods=['GET', 'POST'])
def add_crossref():
    if request.method == 'POST':
        # Check if a file was submitted
        if 'file' not in request.files:
            flash('No file part.', 'danger')
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash('No selected file.', 'danger')
            return redirect(request.url)

        # Check for allowed file extensions
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            try:
                # Read the Excel file into a Pandas DataFrame
                df = pd.read_excel(filepath)

                # Database connection
                mydb = get_db_connection()
                if not mydb:
                    flash('Database connection failed.', 'danger')
                    os.remove(filepath)
                    return redirect(url_for('add_crossref'))

                mycursor = mydb.cursor(buffered=True)

                # SQL query to insert data into the cross_ref table
                insert_query = """
                    INSERT INTO cross_ref (man_part_no, man_name, cross_part_no, cross_mfr, remarks, date) 
                    VALUES (%s, %s, %s, %s, %s, %s)
                """

                # SQL query to check for duplicates by comparing all columns
                check_query = """
                    SELECT COUNT(*) FROM cross_ref 
                    WHERE man_part_no = %s AND man_name = %s AND cross_part_no = %s 
                    AND cross_mfr = %s AND remarks = %s AND date = %s
                """

                # SQL query to check if manufacturer part number exists in part_item table
                part_item_check_query = "SELECT COUNT(*) FROM part_item WHERE man_part_no = %s"

                # SQL query to check if manufacturer name exists in suppliers table with sub_type as 'MANUFACTURER'
                supplier_check_query = "SELECT COUNT(*) FROM suppliers WHERE supplier_name = %s AND sub_type = 'MANUFACTURER'"

                inserted_rows = 0
                duplicate_rows = []
                invalid_date_rows = []

                # Iterate over each row in the Excel file
                for index, row in df.iterrows():
                    manufacturerpartno = str(row['manufacturerpartno']).strip()
                    manufacturername = str(row['manufacturername']).strip()
                    crossreferencepartno = str(row['crossreferencepartno']).strip()
                    crossrefMFR = str(row['crossrefMFR']).strip()
                    remarks = str(row['remarks']).strip()
                    updateddate = str(row['updateddate']).strip()

                    # Validate the updated date format (assuming YYYY-MM-DD)
                    try:
                        updated_date = pd.to_datetime(updateddate).date()
                    except ValueError:
                        invalid_date_rows.append(f"Row {index + 2}: Invalid date format '{updateddate}'")
                        continue  # Skip this row if date format is invalid

                    # Check if manufacturer part number exists in part_item table
                    mycursor.execute(part_item_check_query, (manufacturerpartno,))
                    if mycursor.fetchone()[0] == 0:
                        invalid_date_rows.append(f"Row {index + 2}: Manufacturer part number '{manufacturerpartno}' does not exist in part_item table.")
                        continue  # Skip this row if manufacturer part number is not found

                    # Check if manufacturer name exists in suppliers table
                    mycursor.execute(supplier_check_query, (manufacturername,))
                    if mycursor.fetchone()[0] == 0:
                        invalid_date_rows.append(f"Row {index + 2}: Manufacturer name '{manufacturername}' does not exist in suppliers table.")
                        continue  # Skip this row if manufacturer name is not found

                    # Check if cross reference part number exists in part_item table
                    mycursor.execute(part_item_check_query, (crossreferencepartno,))
                    if mycursor.fetchone()[0] == 0:
                        invalid_date_rows.append(f"Row {index + 2}: Cross reference part number '{crossreferencepartno}' does not exist in part_item table.")
                        continue  # Skip this row if cross reference part number is not found

                    # Check if cross reference manufacturer exists in part_item table
                    mycursor.execute(part_item_check_query, (crossrefMFR,))
                    if mycursor.fetchone()[0] == 0:
                        invalid_date_rows.append(f"Row {index + 2}: Cross reference manufacturer '{crossrefMFR}' does not exist in part_item table.")
                        continue  # Skip this row if cross reference manufacturer is not found

                    # Check for duplicates by comparing all relevant fields
                    mycursor.execute(check_query, (manufacturerpartno, manufacturername, crossreferencepartno, crossrefMFR, remarks, updated_date))
                    if mycursor.fetchone()[0] == 0:  # No duplicates found
                        try:
                            # Insert the new cross-reference data
                            mycursor.execute(insert_query, (manufacturerpartno, manufacturername, crossreferencepartno, crossrefMFR, remarks, updated_date))
                            mydb.commit()
                            inserted_rows += 1
                        except mysql.connector.Error as e:
                            duplicate_rows.append(f"Row {index + 2}: Database error - {str(e)}")
                    else:
                        duplicate_rows.append(f"Row {index + 2}: Duplicate entry across all columns")

                # Feedback to the user on the result of the upload
                total_rows = len(df)
                failed_rows = len(duplicate_rows) + len(invalid_date_rows)

                success_message = f'Successfully inserted {inserted_rows} rows.'
                if failed_rows > 0:
                    failure_message = f' {failed_rows} rows were not inserted.'
                    if invalid_date_rows:
                        failure_message += f' Invalid date format in rows: {", ".join(invalid_date_rows)}.'
                    if duplicate_rows:
                        failure_message += f' Duplicate rows: {", ".join(duplicate_rows)}.'
                    flash(success_message + failure_message, 'warning')
                else:
                    flash(success_message, 'success')

            except Exception as e:
                flash(f'Error processing file: {str(e)}', 'danger')

            finally:
                # Close the database connection and remove the uploaded file
                if 'mydb' in locals():
                    mycursor.close()
                    mydb.close()
                os.remove(filepath)

            return redirect(url_for('CrossRefPart'))  # Redirect to your desired endpoint

    return render_template('CrossRefPart.html')


def get_supplier_type():
    """Fetch the list of employee names from the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT supp_type FROM supplier_type")
    suppplier_type = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return suppplier_type

@app.route('/add_supplier_contact', methods=['GET', 'POST'])
def add_supplier_contact():
    mydb = get_db_connection()
    mycursor = mydb.cursor(buffered=True)
    error = None

    if request.method == 'POST':
        id = request.form.get('id')
        supplier_name = request.form.get('supplier_name')
        contact_person = request.form.get('contact_person')
        contact_number = request.form.get('contact_number')
        
        email = request.form.get('email')
        skype = request.form.get('skype')
        addedby = request.form.get('addedby')
        check_query = """
            SELECT COUNT(*) FROM contact 
            WHERE supplier_name = %s AND contact_person = %s AND contact_number = %s AND email = %s AND skype = %s AND added_by = %s
        """
        values = (supplier_name, contact_person, contact_number, email, skype,addedby)
        mycursor.execute(check_query, values)
        result = mycursor.fetchone()[0]

        if result > 0:
            flash('Duplicate entry. The supplier already exists in the database.', 'error')
            return redirect(url_for('manage_customers'))

        
        query = """
                INSERT INTO contact (id,supplier_name, contact_person, contact_number, email, skype, added_by)
                VALUES (%s,%s, %s, %s, %s, %s, %s)
                """
        values = (id, supplier_name,contact_person,contact_number,email,skype,addedby)
        try:
            mycursor.execute(query, values)
            mydb.commit()
            return redirect(url_for('manage_customers'))
        except IntegrityError:
            error = "Duplicate entry. Please try again with a different ID or branch."

    mycursor.execute("SELECT * FROM contact")
    branches = mycursor.fetchall()
    mycursor.close()
    mydb.close()

    return render_template('manage_customers.html', branches=branches, error=error)



@app.route('/download_report/<int:id>', methods=['GET'])
def download_report(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT reports FROM addnewdata WHERE ID = %s", (id,))
        row = cursor.fetchone()
        if row:
            pdf_content = row[0]
            return send_file(
                io.BytesIO(pdf_content),
                download_name=f'report_{id}.pdf',
                as_attachment=True
            )
        else:
            return jsonify({'error': 'File not found'}), 404
    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 500
    finally:
        cursor.close()
        conn.close()
        
@app.route('/fetch_pdf', methods=['GET'])
def fetch_pdf():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT reports FROM addnewdata ORDER BY id DESC LIMIT 1")
    pdf_data = cursor.fetchone()
    cursor.close()

    if pdf_data:
        # Ensure pdf_data[0] is converted to bytes
        pdf_base64 = base64.b64encode(pdf_data[0].encode('utf-8')).decode('utf-8')
        return jsonify({'pdf_data': pdf_base64})
    else:
        return jsonify({'pdf_data': None})
    

  
        

# @app.route('/delete/<string:id_data>', methods = ['GET'])
# def delete(id_data):
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     cursor.execute("DELETE FROM addnewdata WHERE id=%s", (id_data,))
#     mysql.connection.commit()
#     return redirect(url_for('manage_calling_data'))







@app.route('/check_customer_name', methods=['POST'])
def check_customer_name():
    customername = request.form['customername']
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM customers WHERE customer_name = %s", (customername,))
    result = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    
    return jsonify({'exists': result > 0})










@app.route('/RFQ', methods=['GET', 'POST'])
def RFQ():
    mydb = get_db_connection()
    mycursor = mydb.cursor(buffered=True)
    failed_rows = []
    inserted_rows = 0
    rfq_items = []
    max_date = datetime.now().strftime('%Y-%m-%d')

    # Fetch all manufacturer part numbers for validation
    mycursor.execute("SELECT man_part_no FROM part_item")
    valid_man_part_nos = {row[0] for row in mycursor.fetchall()} 
    # Create a set for quick lookup
    mycursor.execute("SELECT supplier_name FROM suppliers WHERE sub_type = 'MANUFACTURER'")
    valid_manufacturer_names = {row[0] for row in mycursor.fetchall()}

    # Fetch all UOMs for validation
    mycursor.execute("SELECT uom_name FROM uom")
    valid_uoms = {row[0] for row in mycursor.fetchall()}
    
    if request.method == 'POST':
        try:
            # Get form data
            RFQno = request.form['RFQno']
            RFQdate = request.form.get('RFQdate')
            duedate = request.form['duedate']
            customername = request.form['customer_name']
            endcustomer = request.form['endcustomer']
            project = request.form['project']
            applications = request.form['applications']
            assignedto = request.form['assignedto']
            customercontact = request.form['customercontact']

            customerpartno = request.form.getlist('customerpartno[]')
            manfacturedpartno = request.form.getlist('manfacturedpartno[]')
            manfacturedname = request.form.getlist('manfacturedname[]')
            regularquantity = request.form.getlist('regularquantity[]')
            UOM = request.form.getlist('UOM[]')
            extendedquantity = request.form.getlist('extendedquantity[]')
            targetprice = request.form.getlist('targetprice[]')
            remarks = request.form.getlist('remarks[]')

            # Process form data for RFQ items
            for i in range(len(customerpartno)):
                rfq_item = (
                    customerpartno[i], manfacturedpartno[i], manfacturedname[i],
                    regularquantity[i], UOM[i], extendedquantity[i], targetprice[i], remarks[i]
                )
                if all(rfq_item):  # Check if all fields are filled
                    rfq_items.append(rfq_item)
                else:
                    failed_rows.append(f'Form row {i + 1} is missing data')

            # Process file upload
            if 'file' in request.files:
                file = request.files['file']
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)

                    df = pd.read_excel(filepath)

                    # Set to track inserted rows to avoid duplicates within the Excel file
                    inserted_identifiers = set()

                    for index, row in df.iterrows():
                        row_number = index + 2
                        customer_part_no = str(row['customer_part_number']).strip()
                        manufacturer_part_no = str(row['manufacturer_part_number']).strip()
                        manufactured_name = str(row['manufactured_name']).strip()
                        req_quantity = str(row['required_quantity']).strip()
                        uom = str(row['uom']).strip()
                        ext_quantity = str(row['extended_quantity']).strip()
                        tar_price = str(row['target_price']).strip()
                        remark = str(row['remarks']).strip()

                        # Create a unique identifier for each row
                        row_identifier = (
                            customer_part_no, manufacturer_part_no, manufactured_name,
                            req_quantity, uom, ext_quantity, tar_price, remark
                        )

                        if all(row_identifier):
                            # Check if this row is already identified as inserted in this batch
                            if row_identifier in inserted_identifiers:
                                failed_rows.append(f'Duplicate found at row {row_number} within Excel')
                                continue

                            # Validate manufactured part number
                            if manufacturer_part_no not in valid_man_part_nos:
                                failed_rows.append(f'Invalid manufactured part number at row {row_number}')
                                continue
                            # Validate manufacturer name
                            if manufactured_name not in valid_manufacturer_names:
                                failed_rows.append(f'Invalid manufacturer name at row {row_number}')
                                continue

                            # Validate UOM
                            if uom not in valid_uoms:
                                failed_rows.append(f'Invalid UOM at row {row_number}')
                                continue
                            # Check for duplicate row based on RFQ number and item details in the database
                            check_query = """
                                SELECT COUNT(*) FROM opp_rfq_item 
                                WHERE rfq_no = %s 
                                AND customer_part_no = %s 
                                AND manufacturer_part_no = %s 
                                AND manufacturer_name = %s 
                                AND req_quantity = %s 
                                AND uom = %s 
                                AND ext_quantity = %s 
                                AND tar_price = %s 
                                AND remarks = %s
                            """
                            check_values = (RFQno, customer_part_no, manufacturer_part_no, manufactured_name,
                                            req_quantity, uom, ext_quantity, tar_price, remark)
                            mycursor.execute(check_query, check_values)
                            exists = mycursor.fetchone()[0]

                            if exists == 0:  # Insert only if the row does not exist in the database
                                rfq_items.append(row_identifier)
                                inserted_identifiers.add(row_identifier)  # Mark this row as inserted
                                inserted_rows += 1
                            else:
                                failed_rows.append(f'Duplicate found at row {row_number} in database')

            # Insert RFQ details into the database
            rfq_query = """
                INSERT INTO opp_rfq (rfq_no, rfq_date, due_date, customer_name, end_customer, project, application, assign, cus_contact)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            rfq_values = (RFQno, RFQdate, duedate, customername, endcustomer, project, applications, assignedto, customercontact)
            mycursor.execute(rfq_query, rfq_values)
            mydb.commit()

            # Insert RFQ items into the database
            for item in rfq_items:
                item_query = """
                    INSERT INTO opp_rfq_item (rfq_no, customer_part_no, manufacturer_part_no, manufacturer_name, req_quantity, uom, ext_quantity, tar_price, remarks)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                item_values = (RFQno, item[0], item[1], item[2], item[3], item[4], item[5], item[6], item[7])
                mycursor.execute(item_query, item_values)
            mydb.commit()

            flash(f'Successfully inserted {inserted_rows} rows. Rows not inserted: {", ".join(failed_rows)}', 'success')
            return redirect(url_for('RFQ'))

        except Exception as e:
            print(f"Error inserting data: {str(e)}")
            mydb.rollback()
            flash(f'An error occurred while adding RFQ and RFQ items: {str(e)}', 'danger')

    # Fetch existing RFQ and other required data
    mycursor.execute("SELECT * FROM opp_rfq")
    opp_rfq = mycursor.fetchall()

    mycursor.execute("SELECT DISTINCT employeename FROM employee WHERE status=1")
    employee = mycursor.fetchall()

    mycursor.execute("SELECT DISTINCT customer_name FROM contacts")
    customers = mycursor.fetchall()

    mycursor.execute("SELECT man_part_no FROM part_item")
    part_item = mycursor.fetchall()

    mycursor.execute("SELECT * FROM uom")
    uom = mycursor.fetchall()

    mycursor.execute("SELECT distinct contact_person FROM contacts")
    contacts = mycursor.fetchall()

    mycursor.execute("SELECT supplier_name FROM suppliers WHERE sub_type = 'MANUFACTURER'")
    manufacturer_names = mycursor.fetchall()

    search_query = request.args.get('search', '')
    page = int(request.args.get('page', 1))
    per_page = 10
    offset = (page - 1) * per_page
    
    mycursor.execute("SELECT COUNT(*) FROM opp_rfq WHERE rfq_no LIKE %s", (f'{search_query}%',))
    total_customers = mycursor.fetchone()[0]
    
    mycursor.execute("SELECT * FROM opp_rfq WHERE rfq_no LIKE %s ORDER BY id DESC LIMIT %s OFFSET %s",
                   (f'{search_query}%', per_page, offset))
    opp_rfq = mycursor.fetchall()

    mycursor.close()
    mydb.close()
    
    total_pages = (total_customers + per_page - 1) // per_page

    return render_template('RFQ.html', max_date=max_date,uom=uom,contacts=contacts, employee=employee, manufacturer_names=manufacturer_names, opp_rfq=opp_rfq, part_item=part_item, customers=customers, page=page, per_page=per_page, total_pages=total_pages, search_query=search_query)
    


@app.route('/RFQQ', methods=['GET', 'POST'])
def RFQQ():
    mydb = get_db_connection()
    mycursor = mydb.cursor(buffered=True)
    failed_rows = []
    inserted_rows = 0
    rfq_items = []
    max_date = datetime.now().strftime('%Y-%m-%d')

    # Fetch all manufacturer part numbers for validation
    mycursor.execute("SELECT man_part_no FROM part_item")
    valid_man_part_nos = {row[0] for row in mycursor.fetchall()} 
    # Create a set for quick lookup
    mycursor.execute("SELECT supplier_name FROM suppliers WHERE sub_type = 'MANUFACTURER'")
    valid_manufacturer_names = {row[0] for row in mycursor.fetchall()}

    # Fetch all UOMs for validation
    mycursor.execute("SELECT uom_name FROM uom")
    valid_uoms = {row[0] for row in mycursor.fetchall()}
    
    if request.method == 'POST':
        try:
            # Get form data
            RFQno = request.form['RFQno']
            RFQdate = request.form.get('RFQdate')
            duedate = request.form['duedate']
            customername = request.form['customer_name']
            endcustomer = request.form['endcustomer']
            project = request.form['project']
            applications = request.form['applications']
            assignedto = request.form['assignedto']
            customercontact = request.form['customercontact']

            customerpartno = request.form.getlist('customerpartno[]')
            manfacturedpartno = request.form.getlist('manfacturedpartno[]')
            manfacturedname = request.form.getlist('manfacturedname[]')
            regularquantity = request.form.getlist('regularquantity[]')
            UOM = request.form.getlist('UOM[]')
            extendedquantity = request.form.getlist('extendedquantity[]')
            targetprice = request.form.getlist('targetprice[]')
            remarks = request.form.getlist('remarks[]')

            # Process form data for RFQ items
            for i in range(len(customerpartno)):
                rfq_item = (
                    customerpartno[i], manfacturedpartno[i], manfacturedname[i],
                    regularquantity[i], UOM[i], extendedquantity[i], targetprice[i], remarks[i]
                )
                if all(rfq_item):  # Check if all fields are filled
                    rfq_items.append(rfq_item)
                else:
                    failed_rows.append(f'Form row {i + 1} is missing data')

            # Process file upload
            if 'file' in request.files:
                file = request.files['file']
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)

                    df = pd.read_excel(filepath)

                    # Set to track inserted rows to avoid duplicates within the Excel file
                    inserted_identifiers = set()

                    for index, row in df.iterrows():
                        row_number = index + 2
                        customer_part_no = str(row['customer_part_number']).strip()
                        manufacturer_part_no = str(row['manufacturer_part_number']).strip()
                        manufactured_name = str(row['manufactured_name']).strip()
                        req_quantity = str(row['required_quantity']).strip()
                        uom = str(row['uom']).strip()
                        ext_quantity = str(row['extended_quantity']).strip()
                        tar_price = str(row['target_price']).strip()
                        remark = str(row['remarks']).strip()

                        # Create a unique identifier for each row
                        row_identifier = (
                            customer_part_no, manufacturer_part_no, manufactured_name,
                            req_quantity, uom, ext_quantity, tar_price, remark
                        )

                        if all(row_identifier):
                            # Check if this row is already identified as inserted in this batch
                            if row_identifier in inserted_identifiers:
                                failed_rows.append(f'Duplicate found at row {row_number} within Excel')
                                continue

                            # Validate manufactured part number
                            if manufacturer_part_no not in valid_man_part_nos:
                                failed_rows.append(f'Invalid manufactured part number at row {row_number}')
                                continue
                            # Validate manufacturer name
                            if manufactured_name not in valid_manufacturer_names:
                                failed_rows.append(f'Invalid manufacturer name at row {row_number}')
                                continue

                            # Validate UOM
                            if uom not in valid_uoms:
                                failed_rows.append(f'Invalid UOM at row {row_number}')
                                continue
                            # Check for duplicate row based on RFQ number and item details in the database
                            check_query = """
                                SELECT COUNT(*) FROM opp_rfq_item 
                                WHERE rfq_no = %s 
                                AND customer_part_no = %s 
                                AND manufacturer_part_no = %s 
                                AND manufacturer_name = %s 
                                AND req_quantity = %s 
                                AND uom = %s 
                                AND ext_quantity = %s 
                                AND tar_price = %s 
                                AND remarks = %s
                            """
                            check_values = (RFQno, customer_part_no, manufacturer_part_no, manufactured_name,
                                            req_quantity, uom, ext_quantity, tar_price, remark)
                            mycursor.execute(check_query, check_values)
                            exists = mycursor.fetchone()[0]

                            if exists == 0:  # Insert only if the row does not exist in the database
                                rfq_items.append(row_identifier)
                                inserted_identifiers.add(row_identifier)  # Mark this row as inserted
                                inserted_rows += 1
                            else:
                                failed_rows.append(f'Duplicate found at row {row_number} in database')

            # Insert RFQ details into the database
            rfq_query = """
                INSERT INTO opp_rfq (rfq_no, rfq_date, due_date, customer_name, end_customer, project, application, assign, cus_contact)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            rfq_values = (RFQno, RFQdate, duedate, customername, endcustomer, project, applications, assignedto, customercontact)
            mycursor.execute(rfq_query, rfq_values)
            mydb.commit()

            # Insert RFQ items into the database
            for item in rfq_items:
                item_query = """
                    INSERT INTO opp_rfq_item (rfq_no, customer_part_no, manufacturer_part_no, manufacturer_name, req_quantity, uom, ext_quantity, tar_price, remarks)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                item_values = (RFQno, item[0], item[1], item[2], item[3], item[4], item[5], item[6], item[7])
                mycursor.execute(item_query, item_values)
            mydb.commit()

            flash(f'Successfully inserted {inserted_rows} rows. Rows not inserted: {", ".join(failed_rows)}', 'success')
            return redirect(url_for('RFQQ'))

        except Exception as e:
            print(f"Error inserting data: {str(e)}")
            mydb.rollback()
            flash(f'An error occurred while adding RFQ and RFQ items: {str(e)}', 'danger')

    # Fetch existing RFQ and other required data
    mycursor.execute("SELECT * FROM opp_rfq")
    opp_rfq = mycursor.fetchall()

    mycursor.execute("SELECT DISTINCT employeename FROM employee WHERE status=1")
    employee = mycursor.fetchall()

    mycursor.execute("SELECT DISTINCT customer_name FROM contacts")
    customers = mycursor.fetchall()

    mycursor.execute("SELECT man_part_no FROM part_item")
    part_item = mycursor.fetchall()

    mycursor.execute("SELECT * FROM uom")
    uom = mycursor.fetchall()

    mycursor.execute("SELECT distinct contact_person FROM contacts")
    contacts = mycursor.fetchall()

    mycursor.execute("SELECT supplier_name FROM suppliers WHERE sub_type = 'MANUFACTURER'")
    manufacturer_names = mycursor.fetchall()

    search_query = request.args.get('search', '')
    page = int(request.args.get('page', 1))
    per_page = 10
    offset = (page - 1) * per_page
    
    mycursor.execute("SELECT COUNT(*) FROM opp_rfq WHERE rfq_no LIKE %s", (f'{search_query}%',))
    total_customers = mycursor.fetchone()[0]
    
    mycursor.execute("SELECT * FROM opp_rfq WHERE rfq_no LIKE %s ORDER BY id DESC LIMIT %s OFFSET %s",
                   (f'{search_query}%', per_page, offset))
    opp_rfq = mycursor.fetchall()

    mycursor.close()
    mydb.close()
    
    total_pages = (total_customers + per_page - 1) // per_page

    return render_template('RFQQ.html', max_date=max_date,uom=uom,contacts=contacts, employee=employee, manufacturer_names=manufacturer_names, opp_rfq=opp_rfq, part_item=part_item, customers=customers, page=page, per_page=per_page, total_pages=total_pages, search_query=search_query)




@app.route('/add_rfq', methods=['GET', 'POST']) 
def add_rfq():
    mydb = get_db_connection()
    mycursor = mydb.cursor(buffered=True)
    error = None

    if request.method == 'POST':
        RFQno = request.form['RFQno']
        customerpartno = request.form.getlist('customerpartno[]')
        manfacturedpartno = request.form.getlist('manfacturedpartno[]')
        manfacturedname = request.form.getlist('manufactured_name[]')
        regularquantity = request.form.getlist('regularquantity[]')
        UOM = request.form.getlist('UOM[]')
        extendedquantity = request.form.getlist('extendedquantity[]')
        targetprice = request.form.getlist('targetprice[]')
        remarks = request.form.getlist('remarks[]')

        # Insert records into the database
        query = """
            INSERT INTO opp_rfq_item (rfq_no, customer_part_no, manufacturer_part_no, manufacturer_name, req_quantity, uom, ext_quantity, tar_price, remarks)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        duplicates_found = False  # Flag to track duplicate entries
        inserted_rows = 0  # Counter for successful inserts

        for i in range(len(customerpartno)):
            # Check for duplicates
            check_query = """
                SELECT COUNT(*) FROM opp_rfq_item 
                WHERE rfq_no = %s AND customer_part_no = %s AND manufacturer_part_no = %s AND manufacturer_name = %s 
                AND req_quantity = %s AND uom = %s AND ext_quantity = %s AND tar_price = %s AND remarks = %s
            """
            values = (RFQno, customerpartno[i], manfacturedpartno[i], manfacturedname[i], 
                      regularquantity[i], UOM[i], extendedquantity[i], targetprice[i], remarks[i])
            mycursor.execute(check_query, values)
            result = mycursor.fetchone()[0]

            if result == 0:  # Only insert if no duplicate
                try:
                    mycursor.execute(query, values)
                    inserted_rows += 1
                except mysql.connector.IntegrityError as ie:
                    error = f"Error inserting record: {str(ie)}"
                    flash(error, 'danger')  # Flash error message
                except Exception as e:
                    error = f"An unexpected error occurred: {str(e)}"
                    flash(error, 'danger')  # Flash error message
            else:
                duplicates_found = True  # Set flag if duplicate found

        mydb.commit()  # Commit after all insert attempts

        # Provide feedback based on the insertion and duplicates found
        if inserted_rows > 0:
            flash(f'Successfully inserted {inserted_rows} rows into opp_rfq_item.', 'success')
        if duplicates_found:
            flash('Some entries were not added because they already exist in the database.', 'warning')

        return redirect(url_for('RFQ'))

    # Fetch existing data for rendering the template
    mycursor.execute("SELECT * FROM opp_rfq")
    opp_rfq = mycursor.fetchall()
    mycursor.execute("SELECT man_part_no FROM part_item")
    part_item = mycursor.fetchall()
    mycursor.execute("SELECT supplier_name FROM suppliers WHERE sub_type = 'MANUFACTURER'")
    manufacturer_names = mycursor.fetchall()

    mycursor.execute("SELECT * FROM opp_rfq_item")
    suppliers = mycursor.fetchall()

    # Close cursor and database connection
    mycursor.close()
    mydb.close()

    return render_template('RFQ.html', manufacturer_names=manufacturer_names, suppliers=suppliers, 
                           opp_rfq=opp_rfq, error=error, part_item=part_item)

@app.route('/check_rfq_no', methods=['POST'])
def check_rfq_no():
    RFQno = request.form['RFQno']
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM opp_rfq WHERE rfq_no = %s", (RFQno,))
    result = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    
    return jsonify({'exists': result > 0})



@app.route('/get_contacts', methods=['POST'])
def get_contacts():
    customer_name = request.form.get('customer_name')
    conn = get_db_connection()
    cursor = conn.cursor()
    # Fetch contact persons related to the selected customer_name
    cursor.execute("SELECT contact_person FROM contacts WHERE customer_name = %s", (customer_name,))
    contacts = cursor.fetchall()
    conn.close()
    # Convert fetched contacts to a list of contact person names
    contact_names = [contact[0] for contact in contacts]
    return jsonify(contact_names)

@app.route('/get_contact', methods=['POST'])
def get_contact():
    supplier_name = request.form.get('supplier_name')  # Retrieve the supplier name from the POST request

    if supplier_name:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetch contact persons related to the selected supplier_name
        cursor.execute("SELECT contact_person FROM contact WHERE supplier_name = %s", (supplier_name,))
        contacts = cursor.fetchall()

        cursor.close()
        conn.close()

        # Convert fetched contacts to a list of contact person names
        contact_names = [contact[0] for contact in contacts]
        return jsonify(contact_names)  # Return the contact names as a JSON response

    return jsonify([])  # Return an empty list if no contacts are found


@app.route('/get_manufacturer_name', methods=['GET'])
def get_manufacturer_name():
    connection = get_db_connection()
    cursor = connection.cursor()

    # Query to select manufacturer names
    cursor.execute("SELECT supplier_name FROM suppliers WHERE sub_type = 'MANUFACTURER'")
    manufacturer_names = cursor.fetchall()

    # Convert tuples to a simple list of names
    manufacturer_names_list = [name[0] for name in manufacturer_names]

    # Close the cursor and connection
    cursor.close()
    connection.close()
    
    # Return the manufacturer names as a JSON response
    return jsonify(manufacturer_names_list)

# Route to fetch part numbers from the part_item table
@app.route('/get_part_no', methods=['GET'])
def get_part_no():
    connection = get_db_connection()
    cursor = connection.cursor()

    # Query to select part numbers
    cursor.execute("SELECT man_part_no FROM part_item")
    manufacturer_part_nos = cursor.fetchall()

    # Convert tuples to a simple list of part numbers
    manufacturer_part_nos_list = [part_no[0] for part_no in manufacturer_part_nos]

    # Close the cursor and connection
    cursor.close()
    connection.close()
    
    # Return the part numbers as a JSON response
    return jsonify(manufacturer_part_nos_list)



@app.route('/add_opp_rfq_excel', methods=['GET', 'POST'])
def add_opp_rfq_excel():
    if request.method == 'POST':
        rfq_no = request.form.get('RFQno')

        # Check if a file is present in the request
        if 'file' not in request.files:
            flash('No file part.', 'danger')
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash('No selected file.', 'danger')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            try:
                # Read the Excel file into a DataFrame
                df = pd.read_excel(filepath)

                # Database connection
                mydb = get_db_connection()
                if not mydb:
                    flash('Database connection failed.', 'danger')
                    os.remove(filepath)
                    return redirect(url_for('RFQ'))

                mycursor = mydb.cursor(buffered=True)

                # Fetch all valid manufacturers and UOMs
                mycursor.execute("SELECT man_part_no FROM part_item")
                valid_man_part_nos = {row[0] for row in mycursor.fetchall()}

                mycursor.execute("SELECT supplier_name FROM suppliers WHERE sub_type = 'MANUFACTURER'")
                valid_manufacturer_names = {row[0] for row in mycursor.fetchall()}

                mycursor.execute("SELECT uom_name FROM uom")
                valid_uoms = {row[0] for row in mycursor.fetchall()}

                # SQL query to insert data into the opp_rfq_item table
                insert_query = """
                    INSERT INTO opp_rfq_item 
                    (rfq_no, customer_part_no, manufacturer_part_no, manufacturer_name, req_quantity, uom, ext_quantity, tar_price, remarks)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """

                # SQL query to check for a duplicate row
                check_query = """
                    SELECT COUNT(*) FROM opp_rfq_item 
                    WHERE rfq_no = %s AND customer_part_no = %s AND manufacturer_part_no = %s 
                    AND manufacturer_name = %s AND req_quantity = %s AND uom = %s 
                    AND ext_quantity = %s AND tar_price = %s AND remarks = %s
                """

                inserted_rows = 0
                failed_rows = []

                # Iterate over each row in the DataFrame
                for index, row in df.iterrows():
                    # Extract values from the row and clean the data
                    customer_part_no = str(row['customer_part_number']).strip()
                    manufacturer_part_no = str(row['manufacturer_part_number']).strip()
                    manufactured_name = str(row['manufactured_name']).strip()
                    req_quantity = str(row['required_quantity']).strip()
                    uom = str(row['uom']).strip()
                    ext_quantity = str(row['extended_quantity']).strip()
                    tar_price = row['target_price']
                    remark = str(row['remarks']).strip()

                    # Validate manufactured part number
                    if manufacturer_part_no not in valid_man_part_nos:
                        failed_rows.append(f"Row {index + 2}: Invalid manufactured part number.")
                        continue

                    # Validate manufacturer name
                    if manufactured_name not in valid_manufacturer_names:
                        failed_rows.append(f"Row {index + 2}: Invalid manufacturer name.")
                        continue

                    # Validate UOM
                    if uom not in valid_uoms:
                        failed_rows.append(f"Row {index + 2}: Invalid UOM.")
                        continue

                    # Prepare data for insertion
                    data = (
                        rfq_no,
                        customer_part_no,
                        manufacturer_part_no,
                        manufactured_name,
                        req_quantity,
                        uom,
                        ext_quantity,
                        tar_price,
                        remark
                    )

                    # Check for duplicates in the database
                    mycursor.execute(check_query, data)
                    if mycursor.fetchone()[0] == 0:
                        try:
                            # Insert if no duplicates are found
                            mycursor.execute(insert_query, data)
                            mydb.commit()
                            inserted_rows += 1
                        except mysql.connector.Error as e:
                            failed_rows.append(f"Row {index + 2}: Database error - {str(e)}")
                    else:
                        failed_rows.append(f"Row {index + 2}: Duplicate entry")

                # Provide feedback based on the insertion results
                if inserted_rows > 0:
                    success_message = f'Successfully inserted {inserted_rows} rows.'
                    if failed_rows:
                        success_message += f' Rows not inserted: {"; ".join(failed_rows)}'
                    flash(success_message, 'success')
                else:
                    flash('No valid data was inserted.', 'danger')

            except Exception as e:
                flash(f'Error processing file: {str(e)}', 'danger')

            finally:
                if 'mydb' in locals():
                    mycursor.close()
                    mydb.close()
                os.remove(filepath)  # Optionally delete the file after processing

            return redirect(url_for('RFQ'))

    return render_template('RFQ.html')


@app.route('/manage_rfq', methods=['GET'])
def manage_rfq():
    conn = get_db_connection()
    cursor = conn.cursor()
   
    que = 'SELECT *FROM opp_rfq_item'
    cursor.execute(que)
    opp_rfq_item = cursor.fetchall()

    query3 =   'select * from opp_rfq'
    cursor.execute(query3)
    customers = cursor.fetchall()

    query4 =   'select man_part_no from part_item'
    cursor.execute(query4)
    part_item = cursor.fetchall()

    
    query5 =   'select uom_name from uom'
    cursor.execute(query5)
    uom = cursor.fetchall()

    query6 =   'select supplier_name from suppliers where sub_type="MANUFACTURER"'
    cursor.execute(query6)
    suppliers = cursor.fetchall()

    search_query = request.args.get('search', '')
    page = int(request.args.get('page', 1))
    per_page = 10
    offset = (page - 1) * per_page

    # Count total matching records for pagination
    cursor.execute("""
        SELECT COUNT(*) FROM opp_rfq_item 
        WHERE rfq_no LIKE %s OR customer_part_no LIKE %s 
    """, (f'{search_query}%', f'{search_query}%'))
    total_contacts = cursor.fetchone()[0]

    # Fetch matching records with pagination
    cursor.execute("""
        SELECT * FROM opp_rfq_item 
        WHERE rfq_no LIKE %s OR customer_part_no LIKE %s 
        ORDER BY id DESC, customer_part_no   ASC 
        LIMIT %s OFFSET %s
    """, (f'{search_query}%', f'{search_query}%', per_page, offset))
    opp_rfq_item = cursor.fetchall()

    cursor.close()
    conn.close()

    total_pages = (total_contacts + per_page - 1) // per_page

    return render_template('manage_rfq.html',suppliers=suppliers,uom=uom,part_item=part_item,opp_rfq_item=opp_rfq_item, customers=customers,  page=page, per_page=per_page, total_pages=total_pages, search_query=search_query)

@app.route('/delete_rfq/<int:id>')
def delete_rfq(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Execute DELETE operation
        cursor.execute("DELETE FROM opp_rfq WHERE id = %s", (id,))
        conn.commit()

        cursor.close()
        conn.close()

        flash('Record has been deleted successfully', 'success')
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')

    return redirect(url_for('RFQ'))







@app.route('/update_rfq', methods=['POST'])
def update_rfq():
    if request.method == 'POST':
        id = request.form['id']
        RFQno = request.form.get('RFQno')
        RFQdate = request.form.get('RFQdate')
        duedate = request.form.get('duedate')
        customername = request.form.get('customername')
        endcustomer = request.form.get('endcustomer')
        project = request.form.get('project')
        applications = request.form.get('applications')
        assignedto = request.form.get('assignedto')
        customercontact = request.form.get('customercontact')

            # Database connection
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="Omnipro"
            )
        mycursor = mydb.cursor()

            # Update SQL query
        sql = "UPDATE opp_rfq SET rfq_no=%s, rfq_date=%s, due_date=%s, customer_name=%s, end_customer=%s,project=%s, application=%s, assign=%s, cus_contact=%s WHERE id=%s"       
       
        val = (RFQno, RFQdate, duedate, customername,endcustomer,project,applications,assignedto,customercontact,id)
        mycursor.execute(sql, val)
        mydb.commit()

            
        mycursor.close()
        mydb.close()

        flash("Data Updated Successfully")

    return redirect(url_for('RFQ'))


@app.route('/delete_opprfq/<int:id>')
def delete_opprfq(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Execute DELETE operation
        cursor.execute("DELETE FROM opp_rfq_item WHERE id = %s", (id,))
        conn.commit()

        cursor.close()
        conn.close()

        flash('Record has been deleted successfully', 'success')
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')

    return redirect(url_for('manage_rfq'))


@app.route('/update_opprfq', methods=['POST'])
def update_opprfq():
    if request.method == 'POST':
        id = request.form['id']  # Make sure this is correctly assigned
        RFQno = request.form.get('RFQno')
        customerpartno = request.form.get('customerpartno')
        manfacturedpartno = request.form.get('manfacturedpartno') 
        manfacturedname = request.form.get('manfacturedname')
        regularquantity = request.form.get('regularquantity') 
        UOM = request.form.get('UOM')
        extendedquantity = request.form.get('extendedquantity')
        targetprice = request.form.get('targetprice')
        remarks = request.form.get('remarks')

        # Database connection
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="Omnipro"
        )
        mycursor = mydb.cursor()

        # Update SQL query
        sql = """UPDATE opp_rfq_item 
                 SET rfq_no=%s, customer_part_no=%s, manufacturer_part_no=%s, 
                     manufacturer_name=%s, req_quantity=%s, uom=%s, ext_quantity=%s, 
                     tar_price=%s, remarks=%s 
                 WHERE id=%s"""
        val = (RFQno, customerpartno, manfacturedpartno, manfacturedname, regularquantity, UOM, extendedquantity, targetprice, remarks, id)
        mycursor.execute(sql, val)
        mydb.commit()

        # Close cursor and database connection
        mycursor.close()
        mydb.close()

        flash("Data Updated Successfully")

    return redirect(url_for('manage_rfq'))


# Add UOM
@app.route('/add_uom', methods=['POST'])
def add_uom():
    data = request.json
    uom_name = data.get('uom_name')

    if not uom_name:
        return jsonify({'status': 'error', 'message': 'UOM name is required.'})

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO uom (uom_name) VALUES (%s)', (uom_name,))
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'status': 'success', 'uom_name': uom_name})
    except mysql.connector.Error as err:
        return jsonify({'status': 'error', 'message': str(err)})

# Fetch UOMs
@app.route('/get_uom', methods=['GET'])
def get_uom():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT uom_name FROM uom')
    uoms = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return jsonify(uoms)




 

@app.route('/Supplier_RFQ', methods=['GET'])
def Supplier_RFQ():
    conn = get_db_connection()
    cursor = conn.cursor()
    query1 = 'SELECT ID,StudentName,FatherName,Phone, Email,Campus,State,Source,Status,Course,College,AcademicYear,AssignedTo FROM addlead'
    cursor.execute(query1)
    addlead = cursor.fetchall()
    conn.commit()
    cursor.close()
    conn.close()
    return render_template('Supplier_RFQ.html',addlead=addlead)

@app.route('/bulk_watsapp', methods=['GET','POST'])
def bulk_watsapp():
    conn = get_db_connection()
    cursor = conn.cursor()
    phone_numbers = request.form.get('phone_numbers')
    message = request.form.get('message')

    # Split phone numbers by newline or comma
    phone_numbers_list = [number.strip() for number in re.split(r'\n|,', phone_numbers)]

    # Construct and open WhatsApp links for each phone number
    for number in phone_numbers_list:
        whatsapp_url = f'https://wa.me/{number}?text={message}'
        # Open each link in a new tab or window
        os.system(f'start {whatsapp_url}')
    que = 'SELECT Phone FROM addlead'
    cursor.execute(que)
    addlead = cursor.fetchall()
    conn.commit()
    cursor.close()
    conn.close()
    return render_template('bulk_watsapp.html', success=True, addlead=addlead)

# Define a route to send WhatsApp messages
@app.route('/send_whatsapp', methods=['POST'])
def send_whatsapp():
    conn = get_db_connection()
    cursor = conn.cursor()
    # Query the database to fetch phone numbers from specific rows
    cursor.execute("SELECT Phone FROM addlead ")
    rows = cursor.fetchall()
    
    # Construct the WhatsApp message URL
    whatsapp_url = "https://wa.me/"
    for row in rows:
        Phone = row[0]
        # Construct the WhatsApp URL with the phone number and message text if needed
        whatsapp_url = f"https://wa.me/{Phone}?text=Hello%2C%20this%20is%20a%20test%20message."
        # return render_template('send_whatsapp.html', whatsapp_url=whatsapp_url)
    conn.commit()
    cursor.close()
    conn.close()
    return render_template('Supplier_RFQ.html', whatsapp_url=whatsapp_url)

@app.route('/CrossRefPart', methods=['GET', 'POST'])
def CrossRefPart():
    mydb = get_db_connection()
    mycursor = mydb.cursor(buffered=True)

    if request.method == 'POST':
        if 'upload' in request.form:  # Check if the upload button was clicked
            file = request.files['file']
            if file and file.filename.endswith('.xlsx'):
                df = pd.read_excel(file)

                # Fetch existing part items and manufacturers
                mycursor.execute("SELECT part_no FROM part_item")
                existing_part_items = {row[0] for row in mycursor.fetchall()}

                mycursor.execute("SELECT name FROM suppliers WHERE sub_type='MANUFACTURER'")
                existing_suppliers = {row[0] for row in mycursor.fetchall()}

                valid_entries = 0
                invalid_entries = []

                # Validate and prepare data for insertion
                for index, row in df.iterrows():
                    manufacturerpartno = row['manufacturerpartno']
                    manufacturername = row['manufacturername']
                    crossreferencepartno = row['crossreferencepartno']
                    crossrefMFR = row['crossrefMFR']
                    remarks = row['remarks']
                    updateddate = row['updateddate']

                    # Check for empty values
                    if not manufacturername or not manufacturerpartno:
                        invalid_entries.append((index + 1, row))
                        continue  # Skip this entry

                    # Check if updateddate is not empty and validate the date format
                    if updateddate and datetime.strptime(updateddate, '%Y-%m-%d') > datetime.today():
                        return "Error: Date cannot be in the future!", 400

                    if (manufacturerpartno in existing_part_items) and (manufacturername in existing_suppliers):
                        query = """
                        INSERT INTO cross_ref (man_part_no, man_name, cross_part_no, cross_mfr, remarks, date) 
                        VALUES (%s, %s, %s, %s, %s, %s)
                        """
                        values = (manufacturerpartno, manufacturername, crossreferencepartno, crossrefMFR, remarks, updateddate)
                        mycursor.execute(query, values)
                        valid_entries += 1
                    else:
                        invalid_entries.append((index + 1, row))  # Store row number and data for invalid entries

                mydb.commit()

                # Provide feedback to the user
                if valid_entries > 0:
                    flash(f'Successfully uploaded {valid_entries} valid entries.', 'success')
                if invalid_entries:
                    invalid_rows = ', '.join(str(row[0]) for row in invalid_entries)  # Get row numbers
                    flash(f'The following rows were invalid and not uploaded: {invalid_rows}.', 'error')
            else:
                flash('Invalid file format. Please upload an Excel (.xlsx) file.', 'error')

        else:  # Regular form submission
            manufacturerpartno = request.form.get('manufacturerpartno')
            manufacturername = request.form.get('manufacturername')
            crossreferencepartno = request.form.get('crossreferencepartno')
            crossrefMFR = request.form.get('crossrefMFR')
            remarks = request.form.get('remarks')
            updateddate = request.form.get('updateddate')

            # Check for empty values
            if not manufacturername or not manufacturerpartno:
                flash('Manufacturer name and part number cannot be empty.', 'error')
                return redirect(url_for('CrossRefPart'))

            # Check if updateddate is not empty and validate the date format
            if updateddate and datetime.strptime(updateddate, '%Y-%m-%d') > datetime.today():
                return "Error: Date cannot be in the future!", 400

            query = """
            INSERT INTO cross_ref (man_part_no, man_name, cross_part_no, cross_mfr, remarks, date) 
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            values = (manufacturerpartno, manufacturername, crossreferencepartno, crossrefMFR, remarks, updateddate)
            mycursor.execute(query, values)
            mydb.commit()

        mycursor.close()
        mydb.close()
        flash("data added successfully!")
        return redirect(url_for('CrossRefPart'))

    mycursor.execute("SELECT * FROM cross_ref")
    crossreferencepart = mycursor.fetchall()

    mycursor.execute("SELECT * FROM part_item")
    part_item = mycursor.fetchall()

    mycursor.execute("SELECT * FROM suppliers WHERE sub_type='MANUFACTURER'")
    suppliers = mycursor.fetchall()

    search_query = request.args.get('search', '')
    page = int(request.args.get('page', 1))
    per_page = 10
    offset = (page - 1) * per_page

    # Fetch count of total suppliers
    mycursor.execute("SELECT COUNT(*) FROM cross_ref WHERE man_part_no LIKE %s OR man_name LIKE %s OR date LIKE %s ", (f'{search_query}%', f'{search_query}%', f'{search_query}%'))
    total_cross = mycursor.fetchone()[0]

    # Fetch paginated supplier offers
    mycursor.execute("SELECT * FROM cross_ref WHERE man_part_no LIKE %s OR man_name LIKE %s OR date LIKE %s ORDER BY id DESC LIMIT %s OFFSET %s",
                   (f'{search_query}%', f'{search_query}%',f'{search_query}%',per_page, offset))
    crossreferencepart = mycursor.fetchall()



    total_pages = (total_cross + per_page - 1) // per_page
    max_date = datetime.today().strftime('%Y-%m-%d')

    mycursor.close()
    mydb.close()

    return render_template('CrossRefPart.html', max_date=max_date, suppliers=suppliers, part_item=part_item, crossreferencepart=crossreferencepart,page=page, per_page=per_page, total_pages=total_pages, search_query=search_query)

@app.route('/delete_CrossRefPart/<int:id>')
def delete_CrossRefPart(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Execute DELETE operation
        cursor.execute("DELETE FROM cross_ref WHERE id = %s", (id,))
        conn.commit()

        cursor.close()
        conn.close()

        flash('Record has been deleted successfully', 'success')
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')

    return redirect(url_for('CrossRefPart'))

    


@app.route('/update_CrossRefPart', methods=['POST'])
def update_CrossRefPart():
    if request.method == 'POST':
        id = request.form['id']
        manufacturerpartno = request.form['manufacturerpartno']

        manufacturername = request.form['manufacturername']
        crossreferencepartno = request.form['crossreferencepartno']
        crossrefMFR = request.form['crossrefMFR']
        remarks = request.form.get('remarks')
        updateddate = request.form.get('date')
        
        

            # Database connection
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="Omnipro"
            )
        mycursor = mydb.cursor()

            # Update SQL query
        sql = "UPDATE cross_ref SET man_part_no=%s, man_name=%s, cross_part_no=%s, cross_mfr=%s, remarks=%s, date=%s, WHERE id=%s"
        val = (manufacturerpartno,manufacturername, crossreferencepartno,crossrefMFR,remarks,updateddate,id)
        mycursor.execute(sql, val)
        mydb.commit()

            # Close cursor and database connection
        mycursor.close()
        mydb.close()

        flash("Data Updated Successfully")

    return redirect(url_for('CrossRefPart'))


@app.route('/Suppliers_Offers', methods=['GET', 'POST'])
def Suppliers_Offers():
    mydb = get_db_connection()
    mycursor = mydb.cursor(buffered=True)
    failed_rows = []
    inserted_rows = 0
    additems = []

    # Fetch all manufacturer part numbers for validation
    mycursor.execute("SELECT man_part_no FROM part_item")
    valid_man_part_nos = {row[0] for row in mycursor.fetchall()}

    # Fetch all manufacturer names for validation
    mycursor.execute("SELECT supplier_name FROM suppliers WHERE sub_type = 'MANUFACTURER'")
    valid_manufacturer_names = {row[0] for row in mycursor.fetchall()}

    if request.method == 'POST':
        try:
            # Get form data
            suppliername = request.form.get('suppliername')
            dates = request.form.get('date')  # Date from the form
            if datetime.strptime(dates, '%Y-%m-%d').date() > datetime.today().date():
                return "Error: Date cannot be in the future!", 400

            remarks = request.form.get('remarks')
            comments = request.form.get('comments')

            # Process dynamically added items
            contact_count = int(request.form.get('contact_count', 0))
            for i in range(1, contact_count + 1):
                manufacturer_part_no = request.form.get(f'contact_part_{i}', '').strip()
                description = request.form.get(f'contact_des_{i}', '').strip()
                manufacturer = request.form.get(f'contact_manufacturer_{i}', '').strip()
                quantity = request.form.get(f'contact_qty_{i}', '').strip()
                date = request.form.get(f'contact_date_{i}', '').strip()

                if all([manufacturer_part_no, description, manufacturer, quantity, date]):
                    # Validation checks
                    if manufacturer_part_no not in valid_man_part_nos:
                        failed_rows.append(f'Invalid manufacturer part number at row {i}')
                        continue
                    if manufacturer not in valid_manufacturer_names:
                        failed_rows.append(f'Invalid manufacturer name at row {i}')
                        continue

                    additems.append((manufacturer_part_no, description, manufacturer, quantity, date))
                    inserted_rows += 1
                else:
                    failed_rows.append(f'Form row {i} is incomplete.')

            # Initialize variables for Excel upload
            excel_failed_rows = []
            excel_inserted_rows = 0

            # Handle file upload for Excel data
            if 'file' in request.files:
                file = request.files['file']
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)

                    # Read the Excel file
                    df = pd.read_excel(filepath)

                    for index, row in df.iterrows():
                        manufacturer_part_no = str(row.get('ManufacturerPartNo')).strip()
                        description = str(row.get('Description')).strip()
                        manufacturer = str(row.get('Manufacturer')).strip()
                        quantity = str(row.get('Qty')).strip()
                        date = str(row.get('price')).strip()

                        if all([manufacturer_part_no, description, manufacturer, quantity, date]):
                            if manufacturer_part_no not in valid_man_part_nos:
                                excel_failed_rows.append(f'Invalid manufacturer part number at row {index + 2}')
                                continue
                            if manufacturer not in valid_manufacturer_names:
                                excel_failed_rows.append(f'Invalid manufacturer name at row {index + 2}')
                                continue

                            # If the row is valid, append it
                            additems.append((manufacturer_part_no, description, manufacturer, quantity, date))
                            excel_inserted_rows += 1
                        else:
                            excel_failed_rows.append(f'Row {index + 2} is incomplete.')

            # Insert supplier offer details into the database
            mycursor.execute(
                "INSERT INTO supplier_offers (suppliername, date, remarks, comments) VALUES (%s,%s, %s, %s)",
                (suppliername, dates, remarks, comments)
            )
            mydb.commit()

            # Insert each add item into the add_item table
            for additem in additems:
                mycursor.execute(
                    "INSERT INTO add_item (suppliername, manufacturer_part_no, description, manufacturer, quantity, date) "
                    "VALUES (%s, %s, %s, %s, %s, %s)",
                    (suppliername, additem[0], additem[1], additem[2], additem[3], additem[4])
                )
            mydb.commit()

            # Prepare a combined alert message specific to the Excel upload
            combined_message = f'Successfully inserted {inserted_rows} rows from form and {excel_inserted_rows} rows from Excel.'

            if failed_rows or excel_failed_rows:
                combined_message += f' Rows not inserted: {", ".join(failed_rows + excel_failed_rows)}'

            flash(combined_message, 'success')
            return redirect(url_for('Suppliers_Offers'))

        except Exception as e:
            print(f"Error inserting data: {str(e)}")
            mydb.rollback()
            flash('An error occurred while adding suppliers offer and add items.', 'danger')
        finally:
            mycursor.close()
            mydb.close()

    # Fetch suppliers and their offers for display
    search_query = request.args.get('search', '')
    page = int(request.args.get('page', 1))
    per_page = 10
    offset = (page - 1) * per_page

    # Fetch count of total suppliers
    mycursor.execute("SELECT COUNT(*) FROM supplier_offers WHERE suppliername LIKE %s OR date LIKE %s", (f'{search_query}%', f'{search_query}%'))
    total_suppliers = mycursor.fetchone()[0]

    # Fetch paginated supplier offers
    mycursor.execute("SELECT * FROM supplier_offers WHERE suppliername LIKE %s OR date LIKE %s ORDER BY id DESC LIMIT %s OFFSET %s",
                   (f'{search_query}%', f'{search_query}%', per_page, offset))
    suppliersoffer = mycursor.fetchall()

    # Fetch suppliers and part items for dropdown
    mycursor.execute("SELECT * FROM suppliers")
    suppliers = mycursor.fetchall()

    mycursor.execute("SELECT man_part_no FROM part_item")
    part_item = mycursor.fetchall()

    mycursor.execute("SELECT supplier_name FROM suppliers WHERE sub_type='MANUFACTURER'")
    manufacturerproduct = mycursor.fetchall()

    total_pages = (total_suppliers + per_page - 1) // per_page
    max_date = datetime.today().strftime('%Y-%m-%d')

    return render_template('Suppliers_Offers.html', max_date=max_date, manufacturerproduct=manufacturerproduct, part_item=part_item, suppliers=suppliers, suppliersoffer=suppliersoffer, page=page, per_page=per_page, total_pages=total_pages, search_query=search_query)
    








@app.route('/add_supplier_offer', methods=['GET', 'POST'])
def add_supplier_offer():
    mydb = get_db_connection()
    mycursor = mydb.cursor(buffered=True)
    error = None

    if request.method == 'POST':
        suppliername = request.form['suppliername']
        manufacturer_part_no = request.form.getlist('manufacturer_part_no')
        description = request.form.getlist('description')
        manufacturer = request.form.getlist('manufacturer')
        quantity = request.form.getlist('quantity')
        date = request.form.getlist('date')
        

        # Insert records into the database
        query = """
            INSERT INTO add_item (suppliername, manufacturer_part_no, description, manufacturer, quantity, date)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        for i in range(len(manufacturer_part_no)):
            # Check for duplicates
            check_query = """
                SELECT COUNT(*) FROM add_item 
                WHERE suppliername = %s AND manufacturer_part_no = %s AND description = %s AND manufacturer = %s AND quantity = %s AND date = %s 
            """
            values = (suppliername, manufacturer_part_no[i], description[i], manufacturer[i], quantity[i], date[i])
            mycursor.execute(check_query, values)
            result = mycursor.fetchone()[0]

            if result == 0:  # Only insert if no duplicate found
                try:
                    mycursor.execute(query, values)
                except mysql.connector.IntegrityError as ie:
                    error = f"Error inserting record: {str(ie)}"
                except Exception as e:
                    error = f"An unexpected error occurred: {str(e)}"
            else:
                error = f"Duplicate entry found for RFQ NO {suppliername} with customer part number {manufacturer_part_no[i]}."

        mydb.commit()  # Commit after all insert attempts
        if not error:
            flash('Item successfully added', 'success')
        else:
            flash(error, 'danger')
        return redirect(url_for('Suppliers_Offers'))

    # Fetch existing data for rendering the template
    mycursor.execute("SELECT * FROM opp_rfq")
    opp_rfq = mycursor.fetchall()
    mycursor.execute("SELECT man_part_no FROM part_item")
    part_item = mycursor.fetchall()
    mycursor.execute("SELECT supplier_name FROM suppliers WHERE sub_type = 'MANUFACTURER'")
    manufacturer_names = mycursor.fetchall()

    mycursor.execute("SELECT * FROM opp_rfq_item")
    suppliers = mycursor.fetchall()
    mycursor.close()
    mydb.close()

    return render_template('manage_suppliers_offers.html', manufacturer_names=manufacturer_names, suppliers=suppliers, opp_rfq=opp_rfq, error=error, part_item=part_item)

@app.route('/manage_suppliers_offers', methods=['GET'])
def manage_suppliers_offers():
    conn = get_db_connection()
    cursor = conn.cursor()
   
    que = 'SELECT *FROM add_item'
    cursor.execute(que)
    add_item = cursor.fetchall()

    que = 'SELECT *FROM supplier_offers'
    cursor.execute(que)
    supplier_offers = cursor.fetchall()

    query1 = 'SELECT *FROM suppliers'
    cursor.execute(query1)
    suppliers = cursor.fetchall()

    query = 'SELECT *FROM customers'
    cursor.execute(query)
    customers = cursor.fetchall()

    query2 = 'SELECT *FROM part_item'
    cursor.execute(query2)
    part_item = cursor.fetchall()

    
    query3 = 'SELECT supplier_name FROM suppliers where sub_type="MANUFACTURER"'
    cursor.execute(query3)
    manufacturer = cursor.fetchall()
    
    search_query = request.args.get('search', '')
    page = int(request.args.get('page', 1))
    per_page = 10
    offset = (page - 1) * per_page
    cursor.execute("""
        SELECT COUNT(*) FROM add_item 
        WHERE suppliername LIKE %s OR manufacturer_part_no LIKE %s
    """, (f'{search_query}%', f'{search_query}%'))
    total_contacts = cursor.fetchone()[0]

    cursor.execute("""
        SELECT * FROM add_item 
        WHERE suppliername LIKE %s OR manufacturer_part_no LIKE %s 
        ORDER BY item_id DESC, manufacturer_part_no ASC 
        LIMIT %s OFFSET %s
    """, (f'{search_query}%', f'{search_query}%', per_page, offset))
    add_item = cursor.fetchall()


    cursor.close()
    conn.close()
    total_pages = (total_contacts + per_page - 1) // per_page

    return render_template('manage_suppliers_offers.html',manufacturer=manufacturer,part_item=part_item,suppliers=suppliers,add_item=add_item,suppliersoffers=supplier_offers,customers=customers,page=page, per_page=per_page, total_pages=total_pages, search_query=search_query)



@app.route('/delete_suppliersoffer/<int:id>')
def delete_suppliersoffer(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Execute DELETE operation
        cursor.execute("DELETE FROM supplier_offers WHERE id = %s", (id,))
        conn.commit()

        cursor.close()
        conn.close()

        flash('Record has been deleted successfully', 'success')
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')

    return redirect(url_for('Suppliers_Offers'))



@app.route('/update_supplier_offers', methods=['POST'])
def update_supplier_offers():
    if request.method == 'POST':
        id = request.form['id']
        suppliername = request.form.get('suppliername')
        date = request.form.get('date')

        remarks = request.form.get('remarks')
        comments = request.form.get('comments')
        
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="Omnipro"
        )
        mycursor = mydb.cursor()

        # Update SQL query
        sql = "UPDATE supplier_offers SET suppliername=%s,date=%s, remarks=%s, comments=%s WHERE id=%s"
        val = (suppliername,date, remarks, comments, id)
        mycursor.execute(sql, val)
        mydb.commit()

        # Close cursor and database connection
        mycursor.close()
        mydb.close()

        flash("Data Updated Successfully")

    return redirect(url_for('Suppliers_Offers'))




@app.route('/delete_add_item/<int:item_id>')
def delete_add_item(item_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Execute DELETE operation
        cursor.execute("DELETE FROM add_item WHERE item_id = %s", (item_id,))
        conn.commit()

        cursor.close()
        conn.close()

        flash('Record has been deleted successfully', 'success')
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')

    return redirect(url_for('manage_suppliers_offers'))


    
@app.route('/update_add_item', methods=['POST'])
def update_add_item():
    if request.method == 'POST':
        id = request.form['id']
        suppliername = request.form.get('suppliername')

        manufacturer_part_no = request.form['manufacturer_part_no']
        description = request.form.get('description')
        manufacturer = request.form.get('manufacturer')  # Fixed this line
          # Fixed this line
        quantity = request.form.get('quantity') 
        date = request.form.get('date')  # Fixed this line
         # Fixed this line
         # Fixed this line
         # Fixed this line

        # Database connection
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="Omnipro"
        )
        mycursor = mydb.cursor()

        # Update SQL query
        sql = "UPDATE add_item SET suppliername=%s, manufacturer_part_no=%s, description=%s, manufacturer=%s, quantity=%s,date=%s  WHERE item_id=%s"
        val = (suppliername,manufacturer_part_no,description,  manufacturer,quantity,date, id)
        mycursor.execute(sql, val)
        mydb.commit()

        # Close cursor and database connection
        mycursor.close()
        mydb.close()


        flash("Data Updated Successfully")

    return redirect(url_for('manage_suppliers_offers'))

@app.route('/PartNo', methods=['GET', 'POST'])
def PartNo():
    if request.method == 'POST':
        try:
            manufacturerpartno = request.form['Manufacturerpartno']
            updateddate = request.form['UpdatedDate']
            remarks = request.form['remarks']

            # Ensure date is not in the future
            if datetime.strptime(updateddate, '%Y-%m-%d').date() > datetime.today().date():
                flash("Error: date cannot be in the future!", 'danger')
                return redirect(url_for('PartNo'))

            # Capture contacts dynamically
            contacts = []
            contact_count = int(request.form.get('contact_count', 1))
            for i in range(1, contact_count + 1):
                contact_part = request.form.get(f'contact_part_{i}', '')
                contact_date = request.form.get(f'contact_date_{i}', '')
                contact_remarks = request.form.get(f'contact_remarks_{i}', '')

                if contact_part and contact_date and contact_remarks:
                    contacts.append((contact_part, contact_date, contact_remarks))

            # Check for duplicate part number
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT man_part_no FROM part_item")
            existing_parts = {row[0] for row in cursor.fetchall()}  # Fetch existing part numbers

            # Prepare lists for new parts and contacts
            new_contacts = []
            if manufacturerpartno in existing_parts:
                flash('Error: Manufacturer part number already exists!', 'danger')
            else:
                # Insert the manufacturer part number into the database
                cursor.execute(
                    "INSERT INTO part_item (man_part_no, date, remarks) VALUES (%s, %s, %s)",
                    (manufacturerpartno, updateddate, remarks)
                )

                # Insert contacts if they don't already exist
                for contact in contacts:
                    contact_part_no = contact[0]
                    if contact_part_no not in existing_parts:
                        new_contacts.append(contact)

                # Insert new contacts into the database
                for contact in new_contacts:
                    cursor.execute(
                        "INSERT INTO part_item (man_part_no, date, remarks) VALUES (%s, %s, %s)",
                        (contact[0], contact[1], contact[2])
                    )

                flash('Part numbers and contacts added successfully!', 'success')

            conn.commit()
            cursor.close()
            conn.close()
            return redirect(url_for('PartNo'))

        except Exception as e:
            app.logger.error(f"Error occurred: {str(e)}")
            flash("An unexpected error occurred. Please try again.", 'danger')
            return redirect(url_for('PartNo'))

    # Handle GET request to fetch and display part items with pagination and search
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        search_query = request.args.get('search', '')
        page = int(request.args.get('page', 1))
        per_page = 10
        offset = (page - 1) * per_page

        # Count total part items matching the search
        cursor.execute(
            "SELECT COUNT(*) FROM part_item WHERE man_part_no LIKE %s OR date LIKE %s",
            (f'%{search_query}%', f'%{search_query}%')
        )
        total_customers = cursor.fetchone()[0]

        # Fetch paginated items based on the search query
        cursor.execute(
            "SELECT * FROM part_item WHERE man_part_no LIKE %s OR date LIKE %s ORDER BY id DESC LIMIT %s OFFSET %s",
            (f'%{search_query}%', f'%{search_query}%', per_page, offset)
        )
        items = cursor.fetchall()

        cursor.close()
        conn.close()

        total_pages = (total_customers + per_page - 1) // per_page
        max_date = datetime.today().strftime('%Y-%m-%d')

        return render_template(
            'PartNo.html',
            max_date=max_date,
            items=items,
            page=page,
            per_page=per_page,
            total_pages=total_pages,
            search_query=search_query
        )
    except Exception as e:
        app.logger.error(f"Error occurred while fetching part items: {str(e)}")
        flash("An error occurred while fetching part items. Please try again.", 'danger')
        return redirect(url_for('PartNo'))


@app.route('/add_partno', methods=['GET', 'POST'])
def add_partno():
    mydb = get_db_connection()
    mycursor = mydb.cursor(buffered=True)
    error = None

    if request.method == 'POST':
        manufacturer_part_no = request.form.get('manufacturer_part_no')  # Changed to get() for single selection
        productname = request.form.get('part_no')
        addedby = request.form.get('date')  # Ensure this field is included in the form

        # Prepare the SQL query
        query = """
            INSERT INTO part_number (man_part_no, part_no, date)
            VALUES (%s, %s, %s)
        """
        values = (manufacturer_part_no, productname, addedby)

        try:
            mycursor.execute(query, values)
            mydb.commit()
            flash("Part No added successfully!")

            return redirect(url_for('manage_partno'))
        except IntegrityError:
            mydb.rollback()  # Rollback in case of an error
            error = "Duplicate entry. Please try again with a different Part No or Manufacturer."

    # Fetch existing part numbers for display
    mycursor.execute("SELECT * FROM part_number")
    branches = mycursor.fetchall()
    mycursor.close()
    mydb.close()

    return render_template('manage_partno.html', branches=branches, error=error)


@app.route('/check_part_no', methods=['POST'])
def check_part_no():
    Manufacturerpartno = request.form['Manufacturerpartno']
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM part_item WHERE man_part_no = %s", (Manufacturerpartno,))
    result = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    
    return jsonify({'exists': result > 0})


@app.route('/manage_partno', methods=['GET'])
def manage_partno():
    conn = get_db_connection()
    cursor = conn.cursor()
   
    que = 'SELECT *FROM part_number'
    cursor.execute(que)
    part_number = cursor.fetchall()
    query3 =   'select * from part_item'
    cursor.execute(query3)
    customers = cursor.fetchall()

    conn.commit()
    cursor.close()
    conn.close()
    return render_template('manage_partno.html',part_number=part_number,customers=customers)



@app.route('/delete_partitem/<int:id>')
def delete_partitem(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Execute DELETE operation
        cursor.execute("DELETE FROM part_item WHERE id = %s", (id,))
        conn.commit()

        cursor.close()
        conn.close()

        flash('Record has been deleted successfully', 'success')
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')

    return redirect(url_for('PartNo'))


@app.route('/update_partitem', methods=['POST'])
def update_partitem():
    if request.method == 'POST':
        id = request.form['id']
        Manufacturerpartno = request.form.get('Manufacturerpartno')
        UpdatedDate = request.form.get('UpdatedDate')
        remarks = request.form.get('remarks')
        

            # Database connection
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="Omnipro"
            )
        mycursor = mydb.cursor()

            # Update SQL query
        sql = "UPDATE part_item SET man_part_no=%s, date=%s, remarks=%s WHERE id=%s"       
       
        val = (Manufacturerpartno, UpdatedDate, remarks, id)
        mycursor.execute(sql, val)
        mydb.commit()

            
        mycursor.close()
        mydb.close()

        flash("Data Updated Successfully")

    return redirect(url_for('PartNo'))



@app.route('/delete_partno/<int:id>')
def delete_partno(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Execute DELETE operation
        cursor.execute("DELETE FROM part_number WHERE id = %s", (id,))
        conn.commit()

        cursor.close()
        conn.close()

        flash('Record has been deleted successfully', 'success')
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')

    return redirect(url_for('manage_partno'))


@app.route('/update_partno', methods=['POST'])
def update_partno():
    if request.method == 'POST':
        id = request.form['id']  # Make sure this is correctly assigned
        Manufacturerpartno = request.form.get('Manufacturerpartno')
        part_no = request.form.get('part_no')
        date = request.form.get('date') 
        

        # Database connection
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="Omnipro"
        )
        mycursor = mydb.cursor()

        # Update SQL query
        sql = """UPDATE part_number SET man_part_no=%s, part_no=%s, date=%s WHERE id=%s"""
        val = (Manufacturerpartno, part_no, date, id)
        mycursor.execute(sql, val)
        mydb.commit()

        # Close cursor and database connection
        mycursor.close()
        mydb.close()

        flash("Data Updated Successfully")

    return redirect(url_for('manage_partno'))










@app.route('/Customer_Po', methods=['GET', 'POST'])
def Customer_Po():
    mydb = get_db_connection()
    if mydb is None:
        return "Database connection error", 500
    mycursor = mydb.cursor(buffered=True)

    if request.method == 'POST':
        try:
            # Fetch form data (e.g. PO details)
            PO_Date = request.form.get('PO_Date')
            PO_No = request.form.get('PO_No')
            PO_Recd_Date = request.form.get('PO_Recd_Date')
            Customer_Name = request.form.get('customer_name')
            Total_PO_Value = request.form.get('Total_PO_Value')
            No_of_Items_in_PO = request.form.get('No_of_Items_in_PO')
            PO_Delivery_Date = request.form.get('PO_Delivery_Date')
            Employee_Name = request.form.get('Employee_Name')
            Customer_Contact = request.form.get('customercontact')

            # Handle file upload (Excel data)
            file = request.files.get('file')
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)

                # Read the Excel file using pandas
                df = pd.read_excel(filepath)

                # Ensure the Excel file has the required columns
                required_columns = [
                    'PO_part_no', 'MFR', 'PO_Quantity', 'PO_U_P', 'PO_Item_Value',
                    'PO_Ship_Qty', 'PO_Balance_Qty', 'PO_Item_Delivery_Date',
                    'Freight_Charges', 'Other_Charges', 'Item_Status'
                ]
                if not all(col in df.columns for col in required_columns):
                    flash("The uploaded Excel file does not contain all required columns.")
                    return redirect(url_for('Customer_Po'))

                # Extract data from the DataFrame (Excel data)
                PO_part_nos = df['PO_part_no'].tolist()
                MFRs = df['MFR'].tolist()
                PO_Qtys = df['PO_Quantity'].tolist()
                PO_U_Ps = df['PO_U_P'].tolist()
                PO_Item_Values = df['PO_Item_Value'].tolist()
                PO_Ship_Qtys = df['PO_Ship_Qty'].tolist()
                PO_Balance_Qtys = df['PO_Balance_Qty'].tolist()
                PO_Item_Delivery_Dates = df['PO_Item_Delivery_Date'].tolist()
                Freight_Chargess = df['Freight_Charges'].tolist()
                Other_Chargess = df['Other_Charges'].tolist()
                Item_Statuss = df['Item_Status'].tolist()

            # Insert data into purchase_cus table
            supplier_query = """
            INSERT INTO purchase_cus (PO_Date, PO_No, PO_Recd_Date, Customer_Name, Total_PO_Value, No_of_Items_in_PO, PO_Delivery_Date, Employee_Name, Customer_Contact, PO_Remarks, PO_Notes, total_remarks)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            supplier_values = (
                PO_Date, PO_No, PO_Recd_Date, Customer_Name, Total_PO_Value,
                No_of_Items_in_PO, PO_Delivery_Date, Employee_Name,
                Customer_Contact, request.form.get('PO_Remarks'),
                request.form.get('PO_Notes'), request.form.get('total_Remarks')
            )
            mycursor.execute(supplier_query, supplier_values)
            mydb.commit()

            # Insert each item from Excel data into purchase_cus_item
            if file and allowed_file(file.filename):
                for i in range(len(PO_part_nos)):
                    item_query = """
                    INSERT INTO purchase_cus_item (PO_No, part_no, MFR, PO_Qty, PO_U_P, PO_Item_Value, PO_Ship_Qty, PO_Balance_Qty, PO_Item_Delivery_Date, Freight_Charges, Other_Charges, Item_Status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    item_values = (
                        PO_No, PO_part_nos[i], MFRs[i], PO_Qtys[i], PO_U_Ps[i],
                        PO_Item_Values[i], PO_Ship_Qtys[i], PO_Balance_Qtys[i],
                        PO_Item_Delivery_Dates[i], Freight_Chargess[i], 
                        Other_Chargess[i], Item_Statuss[i]
                    )
                    mycursor.execute(item_query, item_values)

            # Handle dynamic JS form data (added rows)
            po_part_nos = request.form.getlist('PO_part_no[]')
            mfrs = request.form.getlist('MFR[]')
            po_quantities = request.form.getlist('PO_Quantity[]')
            po_unit_prices = request.form.getlist('PO_U_P[]')
            po_item_values = request.form.getlist('PO_Item_Value[]')
            po_ship_qtys = request.form.getlist('PO_Ship_Qty[]')
            po_balance_qtys = request.form.getlist('PO_Balance_Qty[]')
            po_item_delivery_dates = request.form.getlist('PO_Item_Delivery_Date[]')
            freight_charges = request.form.getlist('Freight_Charges[]')
            other_charges = request.form.getlist('Other_Charges[]')
            item_statuses = request.form.getlist('Item_Status[]')

            # Insert dynamic JS form data into the database
            for i in range(len(po_part_nos)):
                query = """
                INSERT INTO purchase_cus_item (PO_No, part_no, MFR, PO_Qty, PO_U_P, PO_Item_Value, PO_Ship_Qty, PO_Balance_Qty, PO_Item_Delivery_Date, Freight_Charges, Other_Charges, Item_Status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                values = (
                    PO_No, po_part_nos[i], mfrs[i],
                    po_quantities[i], po_unit_prices[i], po_item_values[i],
                    po_ship_qtys[i], po_balance_qtys[i], po_item_delivery_dates[i],
                    freight_charges[i], other_charges[i], item_statuses[i]
                )
                mycursor.execute(query, values)

            mydb.commit()

            flash("Customer P.O and items have been successfully added.")
            return redirect(url_for('Customer_Po'))

        except Exception as e:
            print(f"Error inserting data: {str(e)}")
            mydb.rollback()
            flash(f"An error occurred while processing the request: {str(e)}")
            return redirect(url_for('Customer_Po'))

    # Fetch customer and employee data for dropdowns
    try:
        mycursor.execute("SELECT * FROM purchase_cus")
        purchase_cus = mycursor.fetchall()
    except Exception as e:
        print(f"Error fetching data: {str(e)}")
        return "An error occurred while fetching data", 500

    mycursor.execute("SELECT customer_name FROM customers")
    customers = mycursor.fetchall()
    mycursor.execute("SELECT man_part_no FROM part_item")
    part_item = mycursor.fetchall()
    
    

    mycursor.execute("SELECT DISTINCT employeename FROM employee WHERE status=1")
    employee = mycursor.fetchall()

    return render_template('Customer_Po.html', part_item=part_item,employee=employee, purchase_cus=purchase_cus, customers=customers)


@app.route('/add_customer_po_excel', methods=['GET', 'POST'])
def add_customer_po_excel():
    if request.method == 'POST':
        po_no = request.form.get('PO_No')

        # Check if a file is present in the request
        if 'file' not in request.files:
            flash('No file part.', 'danger')
            return redirect(url_for('Customer_Po'))

        file = request.files['file']
        if file.filename == '':
            flash('No selected file.', 'danger')
            return redirect(url_for('Customer_Po'))

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            try:
                # Read the Excel file into a DataFrame
                df = pd.read_excel(filepath)

                # Database connection
                mydb = get_db_connection()
                if not mydb:
                    flash('Database connection failed.', 'danger')
                    os.remove(filepath)
                    return redirect(url_for('Customer_Po'))

                mycursor = mydb.cursor(buffered=True)

                # Fetch all valid manufacturers and UOMs
                mycursor.execute("SELECT man_part_no FROM part_item")
                valid_man_part_nos = {row[0] for row in mycursor.fetchall()}

                

                # SQL query to insert data into purchase_cus_item table
                insert_query = """
                    INSERT INTO purchase_cus_item 
                    (PO_No, part_no, MFR, PO_Qty, PO_U_P, PO_Item_Value, PO_Ship_Qty, PO_Balance_Qty, PO_Item_Delivery_Date, Freight_Charges, Other_Charges, Item_Status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """

                # SQL query to check for duplicate rows
                check_query = """
                    SELECT COUNT(*) FROM purchase_cus_item 
                    WHERE PO_No = %s AND part_no = %s AND MFR = %s 
                    AND PO_Qty = %s AND PO_U_P = %s AND PO_Item_Value = %s 
                    AND PO_Ship_Qty = %s AND PO_Balance_Qty = %s AND PO_Item_Delivery_Date = %s 
                    AND Freight_Charges = %s AND Other_Charges = %s AND Item_Status = %s
                """

                inserted_rows = 0
                failed_rows = []

                # Validate and insert each row in the DataFrame
                for index, row in df.iterrows():
                    # Extract and clean data
                    PO_part_no = str(row['PO_part_no']).strip()
                    MFR = str(row['MFR']).strip()
                    PO_Quantity = row['PO_Quantity']
                    PO_U_P = row['PO_U_P']
                    PO_Item_Value = row['PO_Item_Value']
                    PO_Ship_Qty = row['PO_Ship_Qty']
                    PO_Balance_Qty = row['PO_Balance_Qty']
                    PO_Item_Delivery_Date = row['PO_Item_Delivery_Date']
                    Freight_Charges = row['Freight_Charges']
                    Other_Charges = row['Other_Charges']
                    Item_Status = str(row['Item_Status']).strip()

                    # Validate manufactured part number and UOM
                    if PO_part_no not in valid_man_part_nos:
                        failed_rows.append(f"Row {index + 2}: Invalid part number '{PO_part_no}'.")
                        continue

                    # Check for duplicates in the database
                    mycursor.execute(check_query, (
                        po_no, PO_part_no, MFR, PO_Quantity, PO_U_P, PO_Item_Value,
                        PO_Ship_Qty, PO_Balance_Qty, PO_Item_Delivery_Date, Freight_Charges,
                        Other_Charges, Item_Status
                    ))
                    if mycursor.fetchone()[0] > 0:
                        failed_rows.append(f"Row {index + 2}: Duplicate entry found.")
                        continue

                    # Insert valid row into the database
                    mycursor.execute(insert_query, (
                        po_no, PO_part_no, MFR, PO_Quantity, PO_U_P, PO_Item_Value,
                        PO_Ship_Qty, PO_Balance_Qty, PO_Item_Delivery_Date, Freight_Charges,
                        Other_Charges, Item_Status
                    ))
                    inserted_rows += 1

                # Commit changes to the database
                mydb.commit()
                
                # Flash success and error messages
                if inserted_rows > 0:
                    flash(f"Successfully added {inserted_rows} rows.", "success")
                if failed_rows:
                    flash("Some rows could not be added: " + ", ".join(failed_rows), "warning")

            except Exception as e:
                mydb.rollback()
                flash(f"An error occurred: {str(e)}", "danger")
            finally:
                os.remove(filepath)  # Clean up the uploaded file
                mydb.close()

            return redirect(url_for('Customer_Po'))



@app.route('/manage_purchase', methods=['GET'])
def manage_purchase():
    conn = get_db_connection()
    cursor = conn.cursor()

    que = 'SELECT * FROM purchase_cus_item'
    cursor.execute(que)
    purchase_cus_item = cursor.fetchall()
    customer = 'SELECT * FROM purchase_cus'
    cursor.execute(customer)
    suppliers = cursor.fetchall()

    conn.commit()
    cursor.close()
    conn.close()
    return render_template('manage_purchase.html', purchase_cus_item=purchase_cus_item, suppliers=suppliers)







@app.route('/add_customer_po', methods=['GET', 'POST'])
def add_customer_po():
    mydb = get_db_connection()
    mycursor = mydb.cursor(buffered=True)
    error = None

    if request.method == 'POST':
        PO_No = request.form['PO_No']
        part_no = request.form.getlist('part_no[]')
        MFR = request.form.getlist('MFR[]')
        PO_Qty = request.form.getlist('PO_Quantity[]')
        PO_U_P = request.form.getlist('PO_U_P[]')
        PO_Item_Value = request.form.getlist('PO_Item_Value[]')
        PO_Ship_Qty = request.form.getlist('PO_Ship_Qty[]')
        PO_Balance_Qty = request.form.getlist('PO_Balance_Qty[]')
        PO_Item_Delivery_Date = request.form.getlist('PO_Item_Delivery_Date[]')
        Freight_Charges = request.form.getlist('Freight_Charges[]')
        Other_Charges = request.form.getlist('Other_Charges[]')
        Item_Status = request.form.getlist('Item_Status[]')

        list_length = len(part_no)
        lists = [PO_No, part_no, MFR, PO_Qty, PO_U_P, PO_Item_Value, 
                 PO_Ship_Qty, PO_Balance_Qty, PO_Item_Delivery_Date, Freight_Charges, Other_Charges, Item_Status]

        if not all(len(lst) == list_length for lst in lists):
            error = "Mismatch in the number of items for one or more fields."
            flash(error, 'danger')
            return redirect(url_for('add_customer_po'))

        query = """
            INSERT INTO purchase_cus_item (PO_No, part_no, MFR, PO_Qty, PO_U_P, PO_Item_Value, PO_Ship_Qty, 
            PO_Balance_Qty, PO_Item_Delivery_Date, Freight_Charges, Other_Charges, Item_Status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        duplicates_found = False
        inserted_rows = 0

        for i in range(list_length):
            if not all([part_no[i], MFR[i], PO_Qty[i], PO_U_P[i], PO_Item_Value[i], 
                        PO_Ship_Qty[i], PO_Balance_Qty[i], PO_Item_Delivery_Date[i], 
                        Freight_Charges[i], Other_Charges[i], Item_Status[i]]):
                continue

            check_query = """
                SELECT COUNT(*) FROM purchase_cus_item 
                WHERE PO_No = %s AND part_no = %s AND MFR = %s AND PO_Qty = %s 
                AND PO_U_P = %s AND PO_Item_Value = %s AND PO_Ship_Qty = %s AND PO_Balance_Qty = %s
                AND PO_Item_Delivery_Date = %s AND Freight_Charges = %s AND Other_Charges = %s AND Item_Status = %s
            """
            values = (PO_No, part_no[i], MFR[i], PO_Qty[i], PO_U_P[i], PO_Item_Value[i], PO_Ship_Qty[i], 
                      PO_Balance_Qty[i], PO_Item_Delivery_Date[i], Freight_Charges[i], Other_Charges[i], Item_Status[i])
            mycursor.execute(check_query, values)
            result = mycursor.fetchone()[0]

            if result == 0:
                try:
                    mycursor.execute(query, values)
                    inserted_rows += 1
                except mysql.connector.IntegrityError as ie:
                    error = f"Error inserting record: {str(ie)}"
                    flash(error, 'danger')
                except Exception as e:
                    error = f"An unexpected error occurred: {str(e)}"
                    flash(error, 'danger')
            else:
                duplicates_found = True

        mydb.commit()

        if inserted_rows > 0:
            flash(f'Successfully inserted {inserted_rows} rows into purchase_cus_item.', 'success')
        if duplicates_found:
            flash('Some entries were not added because they already exist in the database.', 'warning')

        return redirect(url_for('add_customer_po'))

    mycursor.execute("SELECT man_part_no FROM part_item")
    part_item = mycursor.fetchall()

    mycursor.execute("SELECT * FROM purchase_cus")
    purchase_cus = mycursor.fetchall()

    mycursor.close()
    mydb.close()

    return render_template('Customer_Po.html', purchase_cus=purchase_cus, error=error, part_item=part_item)



@app.route('/delete_customerpo/<int:id>')
def delete_customerpo(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Execute DELETE operation
        cursor.execute("DELETE FROM purchase_cus WHERE id = %s", (id,))
        conn.commit()

        cursor.close()
        conn.close()

        flash('Record has been deleted successfully', 'success')
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')

    return redirect(url_for('Customer_Po'))



@app.route('/update_customerpo', methods=['POST'])
def update_customerpo():
    if request.method == 'POST':
        # Access form data using square brackets
        PO_Date = request.form['PO_Date']
        PO_No = request.form['PO_No']
        PO_Recd_Date = request.form['PO_Recd_Date']
        Customer_Name = request.form['Customer_Name']
        Total_PO_Value = request.form['Total_PO_Value']
        No_of_Items_in_PO = request.form['No_of_Items_in_PO']
        PO_Delivery_Date = request.form['PO_Delivery_Date']
        Employee_Name = request.form['Employee_Name']
        Customer_Contact = request.form['Customer_Contact']
        PO_Remarks = request.form['PO_Remarks']
        PO_Notes = request.form['PO_Notes']
        total_Remarks = request.form['total_Remarks']
        id = request.form['id']  # Make sure 'id' is retrieved correctly

        # Database connection
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="Omnipro"
        )
        mycursor = mydb.cursor()

        # Update SQL query
        sql = """UPDATE purchase_cus SET PO_Date=%s, PO_No=%s, PO_Recd_Date=%s, Customer_Name=%s, 
                 Total_PO_Value=%s, No_of_Items_in_PO=%s, PO_Delivery_Date=%s, Employee_Name=%s, 
                 Customer_Contact=%s, PO_Remarks=%s, PO_Notes=%s ,total_Remarks=%s WHERE id=%s"""
        val = (PO_Date, PO_No, PO_Recd_Date, Customer_Name, Total_PO_Value, No_of_Items_in_PO, 
               PO_Delivery_Date, Employee_Name, Customer_Contact, PO_Remarks, PO_Notes, total_Remarks, id)
        mycursor.execute(sql, val)
        mydb.commit()

        # Close cursor and database connection
        mycursor.close()
        mydb.close()

        flash("Data Updated Successfully")

    return redirect(url_for('Customer_Po'))



@app.route('/delete_cuspo/<int:id>')
def delete_cuspo(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Execute DELETE operation
        cursor.execute("DELETE FROM purchase_cus_item WHERE id = %s", (id,))
        conn.commit()

        cursor.close()
        conn.close()

        flash('Record has been deleted successfully', 'success')
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')

    return redirect(url_for('manage_purchase'))



@app.route('/update_cuspo', methods=['POST'])
def update_cuspo():
    if request.method == 'POST':
        id = request.form['id']
        PO_No = request.form['PO_No']
        part_no = request.form['part_no']
        MFR = request.form.get('MFR')
        PO_Qty = request.form.get('PO_Qty')  # Renamed to avoid conflict
        PO_U_P = request.form.get('PO_U_P')
        PO_Item_Value = request.form.get('PO_Item_Value')
        PO_Ship_Qty = request.form['PO_Ship_Qty']
        PO_Balance_Qty = request.form.get('PO_Balance_Qty')
        PO_Item_Delivery_Date = request.form.get('PO_Item_Delivery_Date')
        Freight_Charges = request.form.get('Freight_Charges')
        Other_Charges = request.form['Other_Charges']
        Item_Status = request.form.get('Item_Status')
      
        # Database connection
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="Omnipro"
        )
        mycursor = mydb.cursor()

        # Update SQL query
        sql = """UPDATE purchase_cus_item 
                 SET PO_No=%s, part_no=%s, MFR=%s, PO_Qty=%s, 
                     PO_U_P=%s, PO_Item_Value=%s, PO_Ship_Qty=%s, PO_Balance_Qty=%s, PO_Item_Delivery_Date=%s,Freight_Charges=%s ,Other_Charges=%s, Item_Status=%s
                 WHERE id=%s"""
        val = (PO_No, part_no, MFR, PO_Qty, PO_U_P, PO_Item_Value, PO_Ship_Qty, PO_Balance_Qty, PO_Item_Delivery_Date,Freight_Charges,Other_Charges,Item_Status, id)
        mycursor.execute(sql, val)
        mydb.commit()

        # Close cursor and database connection
        mycursor.close()
        mydb.close()

        flash("Data Updated Successfully")

    return redirect(url_for('manage_purchase'))





@app.route('/Supplier_Po', methods=['GET', 'POST'])
def Supplier_Po():
    mydb = get_db_connection()  # Function to establish a DB connection
    if mydb is None:
        return "Database connection error", 500

    mycursor = mydb.cursor(buffered=True)

    if request.method == 'POST':
        try:
            # Collect form data
            PO_Date = request.form.get('PO_Date', '')
            PO_No = request.form.get('PO_No', '')
            supplier_name = request.form.get('supplier_name', '')
            supplier_Contact = request.form.get('supplier_Contact', '')
            Total_PO_Value = request.form.get('Total_PO_Value', '')
            No_of_Items_in_PO = request.form.get('No_of_Items_in_PO', '')
            PO_Delivery_Date = request.form.get('PO_Delivery_Date', '')
            Employee_Name = request.form.get('Employee_Name', '')
            PO_Remarks = request.form.get('PO_Remarks', '')
            PO_Notes = request.form.get('PO_Notes', '')
            total_Remarks = request.form.get('total_Remarks', '')

            # Handle file upload (Excel data)
            file = request.files.get('file')
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)

                # Read the Excel file using pandas
                df = pd.read_excel(filepath)

                # Fix possible extra spaces/quotes in the column names
                df.columns = df.columns.str.strip().str.replace('"', '')

                # Required columns
                required_columns = [
                    'part_no', 'mfr', 'item_Quantity', 'dbc', 'part_cost', 'item_ext',
                    'PO_ship_Qty', 'PO_Balance_Qty', 'PO_Item_Delivery_Date',
                    'Freight_Charges', 'Other_Charges', 'Item_Status'
                ]
                
                # Check if all required columns are present
                if not all(col in df.columns for col in required_columns):
                    missing_columns = [col for col in required_columns if col not in df.columns]
                    flash(f"The uploaded Excel file is missing the following columns: {', '.join(missing_columns)}")
                    return redirect(url_for('Supplier_Po'))

                # Extract data from the DataFrame (Excel data)
                part_nos = df['part_no'].tolist()
                MFRs = df['mfr'].tolist()
                item_Qtys = df['item_Quantity'].tolist()
                dbcs = df['dbc'].tolist()
                part_costs = df['part_cost'].tolist()
                item_exts = df['item_ext'].tolist()
                PO_ship_Qtys = df['PO_ship_Qty'].tolist()
                PO_Balance_Qtys = df['PO_Balance_Qty'].tolist()
                PO_Item_Delivery_Dates = df['PO_Item_Delivery_Date'].tolist()
                Freight_Chargess = df['Freight_Charges'].tolist()
                Other_Chargess = df['Other_Charges'].tolist()
                Item_Statuss = df['Item_Status'].tolist()

            # Insert supplier details into the purchase_supp table
            supplier_query = """
            INSERT INTO purchase_supp (PO_Date, PO_No, supplier_name, supplier_Contact, Total_PO_Value, No_of_Items_in_PO, PO_Delivery_Date, Employee_Name, PO_Remarks, PO_Notes, total_Remarks)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            supplier_values = (PO_Date, PO_No, supplier_name, supplier_Contact, Total_PO_Value, No_of_Items_in_PO, PO_Delivery_Date, Employee_Name, PO_Remarks, PO_Notes, total_Remarks)
            mycursor.execute(supplier_query, supplier_values)
            mydb.commit()

            # Insert items from Excel data into purchase_supp_item table
            if file and allowed_file(file.filename):
                for i in range(len(part_nos)):
                    item_query = """
                    INSERT INTO purchase_supp_item (PO_NO,part_no, MFR, item_Qty, dbc, part_cost, item_ext, PO_ship_Qty, Balance_Qty, PO_Item_Delivery_Date, Freight_Charges, Other_Charges, Item_Status)
                    VALUES (%s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s)
                    """
                    item_values = (
                        PO_No,part_nos[i], MFRs[i], item_Qtys[i], dbcs[i], part_costs[i], 
                        item_exts[i], PO_ship_Qtys[i], PO_Balance_Qtys[i], 
                        PO_Item_Delivery_Dates[i], Freight_Chargess[i], Other_Chargess[i], 
                        Item_Statuss[i]
                    )
                    mycursor.execute(item_query, item_values)

            # Insert dynamic JS form data into purchase_supp_item table
            part_nos_dynamic = request.form.getlist('PO_part_no[]')
            MFRs_dynamic = request.form.getlist('MFR[]')
            item_Qtys_dynamic = request.form.getlist('PO_Qty[]')
            dbcs_dynamic = request.form.getlist('PO_dbc[]')
            part_costs_dynamic = request.form.getlist('PO_up[]')
            item_exts_dynamic = request.form.getlist('PO_ext[]')
            PO_ship_Qtys_dynamic = request.form.getlist('PO_Ship_Qty[]')
            PO_Balance_Qtys_dynamic = request.form.getlist('PO_Balance_Qty[]')
            PO_Item_Delivery_Dates_dynamic = request.form.getlist('PO_Item_Delivery_Date[]')
            Freight_Chargess_dynamic = request.form.getlist('Freight_Charges[]')
            Other_Chargess_dynamic = request.form.getlist('Other_Charges[]')
            Item_Statuss_dynamic = request.form.getlist('Item_Status[]')

            for i in range(len(part_nos_dynamic)):
                item_query_dynamic = """
                INSERT INTO purchase_supp_item (PO_No,part_no, MFR, item_Qty, dbc, part_cost, item_ext, PO_ship_Qty, Balance_Qty, PO_Item_Delivery_Date, Freight_Charges, Other_Charges, Item_Status)
                VALUES (%s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s)
                """
                item_values_dynamic = (
                    PO_No,part_nos_dynamic[i], MFRs_dynamic[i], item_Qtys_dynamic[i], 
                    dbcs_dynamic[i], part_costs_dynamic[i], item_exts_dynamic[i], 
                    PO_ship_Qtys_dynamic[i], PO_Balance_Qtys_dynamic[i], 
                    PO_Item_Delivery_Dates_dynamic[i], Freight_Chargess_dynamic[i], 
                    Other_Chargess_dynamic[i], Item_Statuss_dynamic[i]
                )
                mycursor.execute(item_query_dynamic, item_values_dynamic)

            mydb.commit()

            flash("Supplier P.O and items have been successfully added.")
            return redirect(url_for('Supplier_Po'))

        except Exception as e:
            print(f"Error inserting data: {str(e)}")
            mydb.rollback()
            flash(f"An error occurred while processing the request: {str(e)}")
            return redirect(url_for('Supplier_Po'))

    try:
        mycursor.execute("SELECT * FROM purchase_supp")
        Supplier_Po = mycursor.fetchall()
    except Exception as e:
        print(f"Error fetching data: {str(e)}")
        return "An error occurred while fetching data", 500

    mycursor.execute("SELECT DISTINCT employeename FROM employee WHERE status=1")
    employee = mycursor.fetchall()

    mycursor.execute("SELECT supplier_name FROM suppliers")
    suppliers = mycursor.fetchall()

    mycursor.execute("SELECT man_part_no FROM part_item")
    part_item = mycursor.fetchall()

    mycursor.execute("SELECT * FROM purchase_supp")
    purchase_supp = mycursor.fetchall()

    return render_template('Supplier_Po.html',part_item=part_item,purchase_supp=purchase_supp, employee=employee, suppliers=suppliers, Supplier_Po=Supplier_Po)



@app.route('/add_supplier_po', methods=['GET', 'POST'])
def add_supplier_po():
    mydb = get_db_connection()
    mycursor = mydb.cursor(buffered=True)
    error = None

    if request.method == 'POST':
        PO_No = request.form['PO_No']
        part_no = request.form.getlist('PO_part_no[]')
        MFR = request.form.getlist('MFR[]')
        PO_Qty = request.form.getlist('PO_Qty[]')
        PO_dbc = request.form.getlist('PO_dbc[]')
        PO_up = request.form.getlist('PO_up[]')
        PO_ext = request.form.getlist('PO_ext[]')
        PO_Ship_Qty = request.form.getlist('PO_Ship_Qty[]')
        PO_Balance_Qty = request.form.getlist('PO_Balance_Qty[]')
        PO_Item_Delivery_Date = request.form.getlist('PO_Item_Delivery_Date[]')
        Freight_Charges = request.form.getlist('Freight_Charges[]')
        Other_Charges = request.form.getlist('Other_Charges[]')
        Item_Status = request.form.getlist('Item_Status[]')

        list_length = len(part_no)
        lists = [part_no, MFR, PO_Qty, PO_dbc, PO_up, PO_ext, PO_Ship_Qty, PO_Balance_Qty, PO_Item_Delivery_Date, Freight_Charges, Other_Charges, Item_Status]

        if not all(len(lst) == list_length for lst in lists):
            error = "Mismatch in the number of items for one or more fields."
            flash(error, 'danger')
            return redirect(url_for('manage_purchase_supplier'))

        query = """
            INSERT INTO purchase_supp_item (PO_No, part_no, MFR, item_Qty, dbc, part_cost, item_ext, PO_ship_Qty, Balance_Qty, PO_Item_Delivery_Date, Freight_Charges, Other_Charges, Item_Status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        duplicates_found = False
        inserted_rows = 0

        for i in range(list_length):
            if not all([part_no[i], MFR[i], PO_Qty[i], PO_dbc[i], PO_up[i], PO_ext[i], PO_Ship_Qty[i], PO_Balance_Qty[i], PO_Item_Delivery_Date[i], Freight_Charges[i], Other_Charges[i], Item_Status[i]]):
                continue

            check_query = """
                SELECT COUNT(*) FROM purchase_supp_item 
                WHERE PO_No = %s AND part_no = %s AND MFR = %s AND item_Qty = %s 
                AND dbc = %s AND part_cost = %s AND item_ext = %s AND PO_Ship_Qty = %s 
                AND Balance_Qty = %s AND PO_Item_Delivery_Date = %s 
                AND Freight_Charges = %s AND Other_Charges = %s AND Item_Status = %s
            """
            values = (PO_No, part_no[i], MFR[i], PO_Qty[i], PO_dbc[i], PO_up[i], PO_ext[i], PO_Ship_Qty[i], PO_Balance_Qty[i], PO_Item_Delivery_Date[i], Freight_Charges[i], Other_Charges[i], Item_Status[i])
            mycursor.execute(check_query, values)
            result = mycursor.fetchone()[0]

            if result == 0:
                try:
                    mycursor.execute(query, values)
                    inserted_rows += 1
                except mysql.connector.IntegrityError as ie:
                    error = f"Error inserting record: {str(ie)}"
                    flash(error, 'danger')
                except Exception as e:
                    error = f"An unexpected error occurred: {str(e)}"
                    flash(error, 'danger')
            else:
                duplicates_found = True

        mydb.commit()

        if inserted_rows > 0:
            flash(f'Successfully inserted {inserted_rows} rows into purchase_supp_item.', 'success')
        if duplicates_found:
            flash('Some entries were not added because they already exist in the database.', 'warning')

        return redirect(url_for('manage_purchase_supplier'))

    mycursor.execute("SELECT man_part_no FROM part_item")
    part_item = mycursor.fetchall()

    mycursor.execute("SELECT * FROM purchase_supp")
    purchase_supp = mycursor.fetchall()

    mycursor.close()
    mydb.close()

    return render_template('manage_purchase_supplier.html', purchase_supp=purchase_supp, error=error, part_item=part_item)


@app.route('/add_supplier_po_excel', methods=['POST'])
def add_supplier_po_excel():
    mydb = get_db_connection()
    mycursor = mydb.cursor(buffered=True)

    if 'file' not in request.files or request.files['file'].filename == '':
        flash('No file selected', 'danger')
        return redirect(url_for('manage_purchase_supplier'))

    file = request.files['file']
    PO_No = request.form['PO_No']

    try:
        # Read the Excel file into a DataFrame
        df = pd.read_excel(file)

        # Required columns
        required_columns = [
            'part_no', 'MFR', 'PO_Qty', 'dbc', 'PO_up', 'PO_ext', 
            'PO_Ship_Qty', 'PO_Balance_Qty', 'PO_Item_Delivery_Date', 
            'Freight_Charges', 'Other_Charges', 'Item_Status'
        ]

        # Check if all required columns are present
        if not all(column in df.columns for column in required_columns):
            missing_columns = [col for col in required_columns if col not in df.columns]
            flash(f"Missing columns in the uploaded file: {', '.join(missing_columns)}", 'danger')
            return redirect(url_for('manage_purchase_supplier'))

        query = """
            INSERT INTO purchase_supp_item (PO_No, part_no, MFR, item_Qty, dbc, part_cost, item_ext, PO_Ship_Qty, Balance_Qty, PO_Item_Delivery_Date, Freight_Charges, Other_Charges, Item_Status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        duplicates_found = False
        inserted_rows = 0

        # Iterate through each row in the DataFrame and insert data into the database
        for index, row in df.iterrows():
            values = (
                PO_No, row['part_no'], row['MFR'], row['PO_Qty'], row['dbc'], row['PO_up'], 
                row['PO_ext'], row['PO_Ship_Qty'], row['PO_Balance_Qty'], row['PO_Item_Delivery_Date'],
                row['Freight_Charges'], row['Other_Charges'], row['Item_Status']
            )

            # Check if the row already exists in the database to avoid duplicates
            check_query = """
                SELECT COUNT(*) FROM purchase_supp_item 
                WHERE PO_No = %s AND part_no = %s AND MFR = %s AND item_Qty = %s 
                AND dbc = %s AND part_cost = %s AND item_ext = %s AND PO_Ship_Qty = %s 
                AND Balance_Qty = %s AND PO_Item_Delivery_Date = %s 
                AND Freight_Charges = %s AND Other_Charges = %s AND Item_Status = %s
            """
            mycursor.execute(check_query, values)
            result = mycursor.fetchone()[0]

            if result == 0:
                try:
                    mycursor.execute(query, values)
                    inserted_rows += 1
                except mysql.connector.IntegrityError as ie:
                    flash(f"Error inserting record at row {index + 2}: {str(ie)}", 'danger')
                except Exception as e:
                    flash(f"An unexpected error occurred at row {index + 2}: {str(e)}", 'danger')
            else:
                duplicates_found = True

        mydb.commit()

        # Flash messages for insertions and duplicates
        if inserted_rows > 0:
            flash(f'Successfully inserted {inserted_rows} rows into purchase_supp_item.', 'success')
        if duplicates_found:
            flash('Some entries were not added because they already exist in the database.', 'warning')

    except Exception as e:
        flash(f"Failed to process file: {str(e)}", 'danger')
    finally:
        mycursor.close()
        mydb.close()

    return redirect(url_for('manage_purchase_supplier'))



@app.route('/manage_purchase_supplier', methods=['GET'])
def manage_purchase_supplier():
    conn = get_db_connection()
    cursor = conn.cursor()

    que = 'SELECT * FROM purchase_supp_item'
    cursor.execute(que)
    purchase_supp_item = cursor.fetchall()
    customer = 'SELECT * FROM purchase_supp'
    cursor.execute(customer)
    suppliers = cursor.fetchall()

    conn.commit()
    cursor.close()
    conn.close()
    return render_template('manage_purchase_supplier.html', purchase_supp_item=purchase_supp_item, suppliers=suppliers)


@app.route('/delete_supplierpo/<int:id>')
def delete_supplierpo(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Execute DELETE operation
        cursor.execute("DELETE FROM purchase_supp WHERE id = %s", (id,))
        conn.commit()

        cursor.close()
        conn.close()

        flash('Record has been deleted successfully', 'success')
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')

    return redirect(url_for('Supplier_Po'))

    


@app.route('/update_supplierpo', methods=['POST'])
def update_supplierpo():
    if request.method == 'POST':
        # Access form data using square brackets
        id = request.form['id']
        PO_Date = request.form['PO_Date']
        PO_No = request.form['PO_No']
        supplier_name = request.form['supplier_name']
        supplier_Contact = request.form['supplier_Contact']
        Total_PO_Value = request.form['Total_PO_Value']
        No_of_Items_in_PO = request.form['No_of_Items_in_PO']
        PO_Delivery_Date = request.form['PO_Delivery_Date']
        Employee_Name = request.form['Employee_Name']
        Customer_Contact = request.form['PO_Remarks']
        PO_Notes = request.form['PO_Notes']
        total_Remarks = request.form['total_Remarks']
        
        # Database connection
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="Omnipro"
        )
        mycursor = mydb.cursor()

        # Update SQL query
        sql = """UPDATE purchase_supp SET PO_Date=%s, PO_No=%s, supplier_name=%s, supplier_Contact=%s, 
                 Total_PO_Value=%s, No_of_Items_in_PO=%s, PO_Delivery_Date=%s, Employee_Name=%s, 
                  PO_Remarks=%s, PO_Notes=%s ,total_Remarks=%s WHERE id=%s"""
        val = (PO_Date, PO_No, supplier_name, supplier_Contact, Total_PO_Value, No_of_Items_in_PO, 
               PO_Delivery_Date, Employee_Name, Customer_Contact, PO_Notes,total_Remarks, id)
        mycursor.execute(sql, val)
        mydb.commit()

        # Close cursor and database connection
        mycursor.close()
        mydb.close()

        flash("Data Updated Successfully")

    return redirect(url_for('Supplier_Po'))





@app.route('/delete_suppo/<int:id>')
def delete_suppo(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Execute DELETE operation
        cursor.execute("DELETE FROM purchase_supp_item WHERE id = %s", (id,))
        conn.commit()

        cursor.close()
        conn.close()

        flash('Record has been deleted successfully', 'success')
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')

    return redirect(url_for('manage_purchase_supplier'))


@app.route('/update_suppo', methods=['POST'])
def update_suppo():
    if request.method == 'POST':
        id = request.form['id']
        PO_No = request.form['PO_No']
        PO_part_no = request.form['PO_part_no']
        MFR = request.form.get('MFR')
        PO_Qty = request.form.get('PO_Qty')
        PO_dbc = request.form.get('PO_dbc')
        PO_up = request.form.get('PO_up')
        PO_ext = request.form.get('PO_ext')
        PO_Ship_Qty = request.form['PO_Ship_Qty']
        PO_Balance_Qty = request.form.get('PO_Balance_Qty')
        PO_Item_Delivery_Date = request.form.get('PO_Item_Delivery_Date')
        Freight_Charges = request.form.get('Freight_Charges')
        Other_Charges = request.form['Other_Charges']
        Item_Status = request.form.get('Item_Status')

        # Database connection
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="Omnipro"
        )
        mycursor = mydb.cursor()

        # Corrected Update SQL query
        sql = """UPDATE purchase_supp_item 
                 SET PO_No=%s, part_no=%s, MFR=%s, item_Qty=%s, 
                     dbc=%s, part_cost=%s, item_ext=%s, PO_Ship_Qty=%s, Balance_Qty=%s, PO_Item_Delivery_Date=%s, Freight_Charges=%s, Other_Charges=%s, Item_Status=%s
                 WHERE id=%s"""
        val = (PO_No, PO_part_no, MFR, PO_Qty, PO_dbc, PO_up, PO_ext, PO_Ship_Qty, PO_Balance_Qty, PO_Item_Delivery_Date, Freight_Charges, Other_Charges, Item_Status, id)
        mycursor.execute(sql, val)
        mydb.commit()

        # Close cursor and database connection
        mycursor.close()
        mydb.close()

        flash("Data Updated Successfully")

    return redirect(url_for('manage_purchase_supplier'))





@app.route('/CustomerInvoice', methods=['GET', 'POST'])
def CustomerInvoice():
    mydb = get_db_connection()
    if mydb is None:
        return "Database connection error", 500
    mycursor = mydb.cursor(buffered=True)

    if request.method == 'POST':
        try:
            print("Form Data:", request.form)
            print("Files Data:", request.files)

            Customer_Name = request.form.get('Customer_Name', '')
            PO_Date = request.form.get('Customerinvoicedate', '')
            PO_No = request.form.get('CustomerinvoiceNo', '')
            PO_Recd_Date = request.form.get('REP/Sales', '')
            Paymentterms = request.form.get('Paymentterms', '')
            Total_PO_Value = request.form.get('Deliveryterms', '')
            No_of_Items_in_PO = request.form.get('VIA/Freigh', '')
            PO_Delivery_Date = request.form.get('shipto', '')
            Employee_Name = request.form.get('billto', '')
            Customer_Contact = request.form.get('Remarks', '')
            Terms = request.form.get('Terms&Conditions', '')
            No_of_Items_in_PO = request.form.get('NoofitemsinP.O', '')
            Totalinvoicevalue = request.form.get('Totalinvoicevalue', '')
            Attachment = request.files.get('Attachment')
            AWBAttachment = request.files.get('AWBAttachment')
            Invoicestatus = request.form.get('Invoicestatus', '')
            Bankdetails = request.form.get('Bankdetails', '')
            total_remarks = request.form.get('total_remarks', '')

            if Attachment:
                print("Attachment File Name:", Attachment.filename)
            if AWBAttachment:
                print("AWB Attachment File Name:", AWBAttachment.filename)

            supplier_query = """
            INSERT INTO customer_invoice (customer_name, cust_date, cust_inv_no, sales, pay_terms, del_terms, freight, ship, bill, remarks, terms, NO_items, inv_value, attachment, AWB_attachment, inv_status, bank_details,total_remarks)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s)
            """
            supplier_values = (
                Customer_Name, PO_Date, PO_No, PO_Recd_Date, Paymentterms, Total_PO_Value, No_of_Items_in_PO, PO_Delivery_Date, Employee_Name,
                Customer_Contact, Terms, No_of_Items_in_PO, Totalinvoicevalue,
                Attachment.filename if Attachment else None, AWBAttachment.filename if AWBAttachment else None,
                Invoicestatus, Bankdetails,total_remarks
            )
            mycursor.execute(supplier_query, supplier_values)

            PO_part_nos = request.form.getlist('po_no[]')
            MFRs = request.form.getlist('cust_part_no[]')
            PO_Qtys = request.form.getlist('mfr_part_no[]')
            PO_U_Ps = request.form.getlist('manufacturer[]')
            PO_Item_Values = request.form.getlist('qty[]')
            PO_Ship_Qtys = request.form.getlist('qty_ship[]')
            PO_Balance_Qtys = request.form.getlist('qty_bo[]')
            PO_Item_Delivery_Dates = request.form.getlist('item_price[]')
            Freight_Chargess = request.form.getlist('item_value[]')

            for i in range(len(PO_part_nos)):
                item_query = """
                INSERT INTO customer_invoice_items (customer_name, po_no, cust_part_no, mfr_part_no, manufacturer, qty, qty_ship, qty_bo, item_price, item_value)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                item_values = (Customer_Name, PO_part_nos[i], MFRs[i], PO_Qtys[i], PO_U_Ps[i], PO_Item_Values[i], PO_Ship_Qtys[i], PO_Balance_Qtys[i], PO_Item_Delivery_Dates[i], Freight_Chargess[i])
                mycursor.execute(item_query, item_values)

            mydb.commit()
            return redirect(url_for('CustomerInvoice'))

        except Exception as e:
            print(f"Error inserting data: {str(e)}")
            print(e.__traceback__)
            mydb.rollback()
            return "An error occurred while processing the request", 500

    try:
        mycursor.execute("SELECT * FROM customer_invoice")
        customer_invoice = mycursor.fetchall()
    except Exception as e:
        print(f"Error fetching data: {str(e)}")
        return "An error occurred while fetching data", 500

    return render_template('CustomerInvoice.html', customer_invoice=customer_invoice)


@app.route('/manage_cus_invoice', methods=['GET'])
def manage_cus_invoice():
    conn = get_db_connection()
    cursor = conn.cursor()

    que = 'SELECT * FROM customer_invoice_items'
    cursor.execute(que)
    customer_invoice_items = cursor.fetchall()
    customer = 'SELECT * FROM customer_invoice'
    cursor.execute(customer)
    customers = cursor.fetchall()

    conn.commit()
    cursor.close()
    conn.close()
    return render_template('manage_cus_invoice.html', customer_invoice_items=customer_invoice_items, customers=customers)





@app.route('/delete_invoice/<int:id>')
def delete_invoice(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Execute DELETE operation
        cursor.execute("DELETE FROM customer_invoice WHERE id = %s", (id,))
        conn.commit()

        cursor.close()
        conn.close()

        flash('Record has been deleted successfully', 'success')
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')

    return redirect(url_for('CustomerInvoice'))

@app.route('/update_invoice', methods=['POST'])
def update_invoice():
    if request.method == 'POST':
        id = request.form['id']
        Customer_Name = request.form.get('Customer_Name')
        Customerinvoicedate = request.form.get('Customerinvoicedate')
        CustomerinvoiceNo = request.form.get('CustomerinvoiceNo')
        REP = request.form.get('REP')
        Paymentterms = request.form.get('Paymentterms')
        Deliveryterms = request.form.get('Deliveryterms')
        VIA = request.form.get('VIA')
        shipto = request.form.get('shipto')
        billto = request.form.get('billto')
        Remarks = request.form.get('Remarks')
        Terms = request.form.get('Terms')
        Noofitems = request.form.get('Noofitems')
        Totalinvoicevalue = request.form.get('Totalinvoicevalue')
        Invoicestatus = request.form.get('Invoicestatus')
        Bankdetails = request.form.get('Bankdetails')
        total_remarks = request.form.get('total_remarks')

        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="Omnipro"
        )
        mycursor = mydb.cursor()

        # Update SQL query
        sql = """
        UPDATE customer_invoice 
        SET customer_name=%s, cust_date=%s, cust_inv_no=%s, sales=%s, pay_terms=%s,
            del_terms=%s, freight=%s, ship=%s, bill=%s, remarks=%s, terms=%s, NO_items=%s, 
            inv_value=%s, inv_status=%s, bank_details=%s, total_remarks=%s 
        WHERE id=%s
        """
        val = (
            Customer_Name, Customerinvoicedate, CustomerinvoiceNo, REP, Paymentterms, 
            Deliveryterms, VIA, shipto, billto, Remarks, Terms, Noofitems, 
            Totalinvoicevalue, Invoicestatus, Bankdetails, total_remarks, id
        )

        mycursor.execute(sql, val)
        mydb.commit()

        # Close cursor and database connection
        mycursor.close()
        mydb.close()

        flash("Data Updated Successfully")
    return redirect(url_for('CustomerInvoice'))




@app.route('/delete_cus_invoice/<int:id>')
def delete_cus_invoice(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Execute DELETE operation
        cursor.execute("DELETE FROM  customer_invoice_items WHERE id = %s", (id,))
        conn.commit()

        cursor.close()
        conn.close()

        flash('Record has been deleted successfully', 'success')
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')

    return redirect(url_for('manage_cus_invoice'))

@app.route('/update_cus_invoice', methods=['GET', 'POST'])
def update_cus_invoice():
    if request.method == 'POST':
        id = request.form['id']
        customer_name = request.form.get('customer_name')  # Updated to match form name
        po_no = request.form.get('po_no')
        cust_part = request.form.get('cust_part')
        part_no = request.form.get('mfr_part_no')
        manufacturer = request.form.get('manufacturer')
        qty_order = request.form.get('qty_order')
        qty_ship = request.form.get('qty_ship')
        qty_b = request.form.get('qty_b')
        unit_price = request.form.get('unit_price')
        item_value = request.form.get('item_value')

        # Database connection
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="Omnipro"
        )
        mycursor = mydb.cursor()

        # Check if customer_name exists in customer_invoice
        mycursor.execute("SELECT customer_name FROM customer_invoice WHERE customer_name = %s", (customer_name,))
        result = mycursor.fetchone()

        if not result:
            flash("Customer Name does not exist.")
            return redirect(url_for('manage_cus_invoice'))

        # Update SQL query
        sql = """
            UPDATE customer_invoice_items 
            SET customer_name = %s, po_no = %s, cust_part_no = %s, mfr_part_no = %s, manufacturer = %s, 
                qty = %s, qty_ship = %s, qty_bo = %s, item_price = %s, item_value = %s 
            WHERE id = %s
        """
        val = (customer_name, po_no, cust_part, part_no, manufacturer, qty_order, qty_ship, qty_b, unit_price, item_value, id)
        mycursor.execute(sql, val)
        mydb.commit()

        mycursor.close()
        mydb.close()

        flash("Data Updated Successfully")

    return redirect(url_for('manage_cus_invoice'))


       



@app.route('/SupplierInvoice', methods=['GET', 'POST'])
def SupplierInvoice():
    mydb = get_db_connection()
    if mydb is None:
        return "Database connection error", 500
    mycursor = mydb.cursor(buffered=True)

    if request.method == 'POST':
        try:
            
            print("Form Data:", request.form)
            print("Files Data:", request.files)

            supplier_name = request.form.get('supplier_name', '')
            Vendorinvoicedate = request.form.get('Vendorinvoicedate', '')
            VendorInvoiceNo = request.form.get('VendorInvoiceNo', '')
            Vendorcontact = request.form.get('Vendorcontact', '')
            VendorPaymentterms = request.form.get('VendorPaymentterms', '')
            VendorDeliveryterms = request.form.get('VendorDeliveryterms', '')
            Freigh = request.form.get('VIA/Freigh', '')
            shipto = request.form.get('shipto', '')
            billto = request.form.get('billto', '')
            Remarks = request.form.get('Remarks', '')
            Terms = request.form.get('Terms&Conditions', '')
            No_of_Items_in_PO = request.form.get('NoofitemsinP.O', '')
            Totalinvoicevalue = request.form.get('Totalinvoicevalue', '')
            Attachment = request.files.get('Attachment')
            AWBAttachment = request.files.get('AWBAttachment')
            Invoicestatus = request.form.get('Invoicestatus', '')
            Bankdetails = request.form.get('Bankdetails', '')
            total_remarks = request.form.get('total_remarks', '')

            if Attachment:
                print("Attachment File Name:", Attachment.filename)
            if AWBAttachment:
                print("AWB Attachment File Name:", AWBAttachment.filename)

            supplier_query = """
            INSERT INTO supplier_invoice (supplier_name,supp_date, supp_inv_no,supp_contact, pay_terms, del_terms, 	freight, ship, bill, remarks, terms, NO_items, inv_value, attachment,AWB_attachment,inv_status,bank_details,total_remarks)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s)
            """    

            supplier_values = (
                supplier_name, Vendorinvoicedate, VendorInvoiceNo, Vendorcontact, VendorPaymentterms, VendorDeliveryterms, Freigh, shipto, billto,Remarks,
                Terms, No_of_Items_in_PO, Totalinvoicevalue,
                Attachment.filename if Attachment else None, AWBAttachment.filename if AWBAttachment else None,
                Invoicestatus, Bankdetails,total_remarks
            )
            mycursor.execute(supplier_query, supplier_values)

            PO_part_nos = request.form.getlist('po_no[]')
            MFRs = request.form.getlist('supp_part_no[]')
            PO_Qtys = request.form.getlist('mfr_part_no[]')
            PO_U_Ps = request.form.getlist('manufacturer[]')
            PO_Item_Values = request.form.getlist('qty[]')
            PO_Ship_Qtys = request.form.getlist('qty_ship[]')
            PO_Balance_Qtys = request.form.getlist('qty_bo[]')
            PO_Item_Delivery_Dates = request.form.getlist('item_price[]')
            Freight_Chargess = request.form.getlist('item_value[]')



            for i in range(len(PO_part_nos)):
                item_query = """
                INSERT INTO supplier_invoice_items (supplier_name, po_no, supp_part_no, mfr_part_no, manufacturer, qty, qty_ship, qty_bo, item_price, item_value)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                item_values = (supplier_name, PO_part_nos[i], MFRs[i], PO_Qtys[i], PO_U_Ps[i], PO_Item_Values[i], PO_Ship_Qtys[i], PO_Balance_Qtys[i], PO_Item_Delivery_Dates[i], Freight_Chargess[i])
                mycursor.execute(item_query, item_values)

            mydb.commit()
            return redirect(url_for('SupplierInvoice'))

        except Exception as e:
            print(f"Error inserting data: {str(e)}")
            print(e.__traceback__)
            mydb.rollback()
            return "An error occurred while processing the request", 500

    try:
        mycursor.execute("SELECT * FROM supplier_invoice")
        supplier_invoice = mycursor.fetchall()
    except Exception as e:
        print(f"Error fetching data: {str(e)}")
        return "An error occurred while fetching data", 500

    return render_template('SupplierInvoice.html', supplier_invoice=supplier_invoice)



@app.route('/manage_sup_invoice', methods=['GET'])
def manage_sup_invoice():
    conn = get_db_connection()
    cursor = conn.cursor()

    que = 'SELECT * FROM supplier_invoice_items'
    cursor.execute(que)
    supplier_invoice_items = cursor.fetchall()
    customer = 'SELECT * FROM customer_invoice'
    cursor.execute(customer)
    customers = cursor.fetchall()

    conn.commit()
    cursor.close()
    conn.close()
    return render_template('manage_sup_invoice.html', supplier_invoice_items=supplier_invoice_items, customers=customers)


@app.route('/delete_supplierinvoice/<int:id>')
def delete_supplierinvoice(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Execute DELETE operation
        cursor.execute("DELETE FROM supplier_invoice WHERE id = %s", (id,))
        conn.commit()

        cursor.close()
        conn.close()

        flash('Record has been deleted successfully', 'success')
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')

    return redirect(url_for('SupplierInvoice'))



@app.route('/update_supplierinvoice', methods=['POST'])
def update_supplierinvoice():
    if request.method == 'POST':
        id = request.form['id']
        Customer_Name = request.form.get('supplier_name')
        Customerinvoicedate = request.form.get('Vendorinvoicedate')
        CustomerinvoiceNo = request.form.get('VendorInvoiceNo')
        REP = request.form.get('Vendorcontact')
        Paymentterms = request.form.get('VendorPaymentterms')
        Deliveryterms = request.form.get('VendorDeliveryterms')
        VIA = request.form.get('VIA')
        shipto = request.form.get('shipto')
        billto = request.form.get('billto')
        Remarks = request.form.get('Remarks')
        Terms = request.form.get('Terms')
        Noofitems = request.form.get('Noofitems')
        Totalinvoicevalue = request.form.get('Totalinvoicevalue')
        Invoicestatus = request.form.get('Invoicestatus')
        Bankdetails = request.form.get('Bankdetails')
        total_remarks = request.form.get('total_remarks')

        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="Omnipro"
        )
        mycursor = mydb.cursor()

        # Update SQL query
        sql = """
        UPDATE supplier_invoice 
        SET supplier_name=%s, supp_date=%s, supp_inv_no=%s, supp_contact=%s, pay_terms=%s,
            del_terms=%s, freight=%s, ship=%s, bill=%s, remarks=%s, terms=%s, NO_items=%s, 
            inv_value=%s, inv_status=%s, bank_details=%s, total_remarks=%s 
        WHERE id=%s
        """
        val = (
            Customer_Name, Customerinvoicedate, CustomerinvoiceNo, REP, Paymentterms, 
            Deliveryterms, VIA, shipto, billto, Remarks, Terms, Noofitems, 
            Totalinvoicevalue, Invoicestatus, Bankdetails, total_remarks, id
        )

        mycursor.execute(sql, val)
        mydb.commit()

        # Close cursor and database connection
        mycursor.close()
        mydb.close()

        flash("Data Updated Successfully")
    return redirect(url_for('SupplierInvoice'))




@app.route('/delete_sup_invoice/<int:id>')
def delete_sup_invoice(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Execute DELETE operation
        cursor.execute("DELETE FROM  customer_invoice_items WHERE id = %s", (id,))
        conn.commit()

        cursor.close()
        conn.close()

        flash('Record has been deleted successfully', 'success')
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')

    return redirect(url_for('manage_sup_invoice'))

@app.route('/update_sup_invoice', methods=['GET', 'POST'])
def update_sup_invoice():
    if request.method == 'POST':
        id = request.form['id']
        customer_name = request.form.get('supplier_name')  # Updated to match form name
        po_no = request.form.get('po_no')
        cust_part = request.form.get('supp_part_no')
        part_no = request.form.get('mfr_part_no')
        manufacturer = request.form.get('manufacturer')
        qty_order = request.form.get('qty')
        qty_ship = request.form.get('qty_ship')
        qty_b = request.form.get('qty_bo')
        unit_price = request.form.get('item_price')
        item_value = request.form.get('item_value')

        # Database connection
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="Omnipro"
        )
        mycursor = mydb.cursor()

        # Check if customer_name exists in customer_invoice
        mycursor.execute("SELECT supplier_name FROM supplier_invoice WHERE supplier_name = %s", (supplier_name,))
        result = mycursor.fetchone()

        if not result:
            flash("Customer Name does not exist.")
            return redirect(url_for('manage_sup_invoice'))

        # Update SQL query
        sql = """
            UPDATE supplier_invoice_items 
            SET supplier_name = %s, po_no = %s, supp_part_no = %s, mfr_part_no = %s, manufacturer = %s, 
                qty = %s, qty_ship = %s, qty_bo = %s, item_price = %s, item_value = %s 
            WHERE id = %s
        """
        val = (customer_name, po_no, cust_part, part_no, manufacturer, qty_order, qty_ship, qty_b, unit_price, item_value, id)
        mycursor.execute(sql, val)
        mydb.commit()

        mycursor.close()
        mydb.close()

        flash("Data Updated Successfully")

    return redirect(url_for('manage_sup_invoice'))



@app.route('/Suppliers', methods=['GET', 'POST'])
def Suppliers():
    if request.method == 'POST':
        supplier_name = request.form['supplier_name']
        sup_type = request.form['sup_type']
        contact_number = request.form['contact_number']
        fax = request.form['fax']
        website = request.form['website']
        address = request.form['address']
        remarks = request.form['remarks']
        applications = request.form['applications']

        contact_person_names = request.form.getlist('contactpersonname[]')
        contact_numbers = request.form.getlist('contactno[]')
        emails = request.form.getlist('email[]')
        skypes = request.form.getlist('skype[]')
        added_bys = request.form.getlist('addedby[]')
        dates = request.form.getlist('date[]')

        contacts = []
        failed_rows = []
        inserted_rows = 0

        # Process form data for contacts
        for i in range(len(contact_person_names)):
            contact_name = contact_person_names[i]
            contact_number = contact_numbers[i]
            email = emails[i]
            skype = skypes[i]
            added_by = added_bys[i]
            date = dates[i]

            if contact_name and contact_number and email and skype and added_by and date:

                contacts.append((contact_name, contact_number, email, skype, added_by,date))
            else:
                failed_rows.append(f'Form row {i + 1}')  # Store row number for failed rows

        # Process file upload
        if 'file' in request.files:
            file = request.files['file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)

                df = pd.read_excel(filepath)
                valid_number_pattern = re.compile(r'^[0-9\+\-]{10,16}$')
                employee_names = get_employee_names()

                inserted_contacts = set()
                seen_rows = set()

                for index, row in df.iterrows():
                    row_number = index + 2
                    contact_name = str(row['contact_person']).strip().upper()
                    contact_number = str(row['contact_number']).strip()
                    email = str(row['email']).strip()
                    skype = str(row['skype']).strip()
                    added_by = str(row['added_by']).strip().upper()
                    date = pd.to_datetime(row['date']).date()  # Extract only the date part

                    # Create a unique identifier for each row based on all columns
                    row_identifier = (contact_name, contact_number, email, skype, added_by,date)

                    if row_identifier not in seen_rows:
                        seen_rows.add(row_identifier)
                        
                        if (valid_number_pattern.match(contact_number) and 
                            email.endswith('@gmail.com') and
                            added_by in employee_names):

                            contacts.append(row_identifier)
                            inserted_rows += 1
                        else:
                            failed_rows.append(f'{row_number}')  # Store row number for failed rows

                    else:
                        failed_rows.append(f'{row_number} (Duplicate)')  # Store row number for duplicate rows

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Insert supplier details
            cursor.execute(
                "INSERT INTO suppliers (supplier_name, sub_type, contact_number, fax, website, address, remarks, applications) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (supplier_name, sup_type, contact_number, fax, website, address, remarks, applications)
            )
            supplier_id = cursor.lastrowid

            # Insert contacts into the `contact` table
            for contact in contacts:
                cursor.execute(
                    "INSERT INTO contact (supplier_name, contact_person, contact_number, email, skype, added_by,date) "
                    "VALUES (%s, %s, %s, %s, %s, %s,%s)",
                    (supplier_name, contact[0], contact[1], contact[2], contact[3], contact[4],contact[5])
                )

            conn.commit()
            flash(f'Successfully inserted {inserted_rows} rows. Rows not inserted: {", ".join(failed_rows)}', 'success')
        except mysql.connector.Error as err:
            if err.errno == 1062:
                flash('Duplicate entry found. Please check the details and try again.', 'danger')
            else:
                flash('An error occurred while adding the supplier. Please try again.', 'danger')
            conn.rollback()
        finally:
            cursor.close()
            conn.close()

        return redirect(url_for('Suppliers'))

    # Handle GET request
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM suppliers")
    suppliers = cursor.fetchall()
    cursor.execute("SELECT * FROM employee where status=1")
    employees = cursor.fetchall()
    cursor.execute("SELECT DISTINCT sub_type FROM suppliers ")
    supp = cursor.fetchall()

    cursor.execute("SELECT * FROM supplier_type ")
    supp_type = cursor.fetchall()

    cursor.execute("SELECT * FROM supplier_type")
    supplier_type = cursor.fetchall()

    # Pagination and search functionality
    search_query = request.args.get('search', '')
    page = int(request.args.get('page', 1))
    per_page = 10
    offset = (page - 1) * per_page

    cursor.execute("SELECT COUNT(*) FROM suppliers WHERE supplier_name LIKE %s", (f'{search_query}%',))
    total_suppliers = cursor.fetchone()[0]

    cursor.execute("SELECT * FROM suppliers WHERE supplier_name LIKE %s ORDER BY id DESC LIMIT %s OFFSET %s",
                   (f'{search_query}%', per_page, offset))
    suppliers = cursor.fetchall()

    cursor.close()
    conn.close()

    total_pages = (total_suppliers + per_page - 1) // per_page

    return render_template('Suppliers.html',supp_type=supp_type,supp=supp, supplier_type=supplier_type,suppliers=suppliers, employees=employees, page=page, per_page=per_page, total_pages=total_pages, search_query=search_query)





@app.route('/get_employee_names', methods=['GET'])
def get_employee_names():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT employeename FROM employee where status=1")
    employee_names = cursor.fetchall()
    cursor.close()
    connection.close()
    
    # Convert the list of tuples into a simple list
    employee_names_list = [name[0] for name in employee_names]
    
    return jsonify(employee_names_list)



@app.route('/manage_customers', methods=['GET'])
def manage_customers():
    conn = get_db_connection()
    cursor = conn.cursor()

    que = 'SELECT *FROM suppliers'
    cursor.execute(que)
    suppliers = cursor.fetchall()

    query = 'SELECT * FROM employee where status=1'
    cursor.execute(query)
    employee = cursor.fetchall()

    # Handle search and pagination
    search_query = request.args.get('search', '')
    page = int(request.args.get('page', 1))
    per_page = 10
    offset = (page - 1) * per_page

    # Count total matching records for pagination (searching by the first letter in both supplier_name and contact_person)
    cursor.execute("""
        SELECT COUNT(*) FROM contact 
        WHERE supplier_name LIKE %s OR contact_person LIKE %s
    """, (f'{search_query}%', f'{search_query}%'))
    total_contacts = cursor.fetchone()[0]

    # Fetch matching records with pagination (searching by the first letter in both supplier_name and contact_person)
    cursor.execute("""
        SELECT * FROM contact 
        WHERE supplier_name LIKE %s OR contact_person LIKE %s 
        ORDER BY id DESC, contact_person ASC 
        LIMIT %s OFFSET %s
    """, (f'{search_query}%', f'{search_query}%', per_page, offset))
    contact = cursor.fetchall()


    

    cursor.close()
    conn.close()

    total_pages = (total_contacts + per_page - 1) // per_page

    return render_template('manage_customers.html',employee=employee, contact=contact, suppliers=suppliers,page=page, per_page=per_page, total_pages=total_pages, search_query=search_query)




@app.route('/delete_suppliers/<int:id>')
def delete_suppliers(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Execute DELETE operation
        cursor.execute("DELETE FROM suppliers WHERE id = %s", (id,))
        conn.commit()

        cursor.close()
        conn.close()

        flash('Record has been deleted successfully', 'success')
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')

    return redirect(url_for('Suppliers'))

@app.route('/export_suppliers_data')
def export_suppliers_data():
    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch data from the first table (suppliers)
    query1 = "SELECT * FROM suppliers"
    cursor.execute(query1)
    rows1 = cursor.fetchall()
    columns1 = [i[0] for i in cursor.description]
    
    # Debugging: Print fetched data and column names
    print("Columns from 'suppliers' table:", columns1)
    print("Rows from 'suppliers' table:", rows1)
    
    # Check if rows1 is empty
    if not rows1:
        print("No data found in 'suppliers' table.")

    # Create DataFrame for suppliers
    df1 = pd.DataFrame(rows1, columns=columns1).drop(columns=['id','excel_file'], errors='ignore')

    # Fetch data from the second table (contact)
    query2 = "SELECT * FROM contact"
    cursor.execute(query2)
    rows2 = cursor.fetchall()
    columns2 = [i[0] for i in cursor.description]
    
    # Debugging: Print fetched data and column names
    print("Columns from 'contact' table:", columns2)
    print("Rows from 'contact' table:", rows2)
    
    # Check if rows2 is empty
    if not rows2:
        print("No data found in 'contact' table.")

    # Create DataFrame for contact
    df2 = pd.DataFrame(rows2, columns=columns2).drop(columns=['id'], errors='ignore')

    # Close the cursor and connection
    cursor.close()
    conn.close()

    # Convert date columns to datetime if necessary
    if 'Date' in df2.columns:
        df2['Date'] = pd.to_datetime(df2['Date'], errors='coerce').dt.date

    # Export data to Excel with multiple sheets
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df1.to_excel(writer, sheet_name='Suppliers', index=False)
        df2.to_excel(writer, sheet_name='Contact', index=False)

        # Access the xlsxwriter workbook and worksheets
        workbook = writer.book
        contact_sheet = writer.sheets['Contact']

        # Define a date format for Excel (day-month-year)
        date_format = workbook.add_format({'num_format': 'dd-mm-yyyy'})

        # Apply date formatting to columns if 'Date' exists
        for col_num, col_name in enumerate(df2.columns):
            if pd.api.types.is_datetime64_any_dtype(df2[col_name]) or (df2[col_name].dtype == 'object' and col_name.lower() == 'date'):
                contact_sheet.set_column(col_num, col_num, 20, date_format)

    # Prepare response
    output.seek(0)  # Ensure to seek back to the start of the BytesIO object
    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=suppliers_data_export.xlsx"
    response.headers["Content-type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    return response

@app.route('/export_Distribution_Proposals') 
def export_Distribution_Proposals():
    try:
        # Connect to the database
        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetch all data from the item table
        query = """
        SELECT manufacturername, distiproposalsent, updatedate, followupdate, comments, remarks, rating 
        FROM item
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        columns = [i[0] for i in cursor.description]

        # Debugging: Print fetched data and column names
        print("Columns from item table:", columns)
        print("Rows from item table:", rows)

        # Check if rows have data
        if not rows:
            return "No data available to export.", 400

        # Create DataFrame for item data
        df = pd.DataFrame(rows, columns=columns)

        # Close the cursor and connection
        cursor.close()
        conn.close()

        # Define valid date columns that need to be formatted
        date_columns = ['updatedate', 'followupdate']  # Exclude distiproposalsent as it's not a date

        # Convert date columns to datetime and format them
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce').dt.strftime('%d-%m-%Y')

        # Export data to Excel
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Distribution_Proposals', index=False)

            # Access the xlsxwriter workbook and worksheet
            workbook = writer.book
            worksheet = writer.sheets['Distribution_Proposals']

            # Define a date format for Excel (day-month-year)
            date_format = workbook.add_format({'num_format': 'dd-mm-yyyy'})

            # Apply date formatting to the relevant date columns
            for col_num, col_name in enumerate(df.columns):
                if col_name in date_columns:
                    worksheet.set_column(col_num, col_num, 20, date_format)
                else:
                    worksheet.set_column(col_num, col_num, 20)  # Set general width for other columns

        # Prepare the response for download
        output.seek(0)
        response = make_response(output.getvalue())
        response.headers["Content-Disposition"] = "attachment; filename=distribution_proposals_data.xlsx"
        response.headers["Content-type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        
        return response

    except Exception as e:
        # Handle exceptions and return an error response
        print(f"An error occurred while exporting: {e}")
        return "An error occurred while exporting the data.", 500

@app.route('/export_Manfactured_products_data')
def export_Manfactured_products_data():
    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch data from the first table (suppliers)
    query1 = "SELECT * FROM manufacturer_product"
    cursor.execute(query1)
    rows1 = cursor.fetchall()
    columns1 = [i[0] for i in cursor.description]
    
    # Debugging: Print fetched data and column names
    print("Columns from 'manufacturer_product' table:", columns1)
    print("Rows from 'manufacturer_product' table:", rows1)
    
    # Check if rows1 is empty
    if not rows1:
        print("No data found in 'manufacturer_product' table.")

    # Create DataFrame for suppliers
    df1 = pd.DataFrame(rows1, columns=columns1).drop(columns=['id'], errors='ignore')

    # Fetch data from the second table (contact)
    query2 = "SELECT * FROM manufacturer_product_stock"
    cursor.execute(query2)
    rows2 = cursor.fetchall()
    columns2 = [i[0] for i in cursor.description]
    
    # Debugging: Print fetched data and column names
    print("Columns from 'manufacturer_product_stock' table:", columns2)
    print("Rows from 'manufacturer_product_stock' table:", rows2)
    
    # Check if rows2 is empty
    if not rows2:
        print("No data found in 'manufacturer_product_stock' table.")

    # Create DataFrame for contact
    df2 = pd.DataFrame(rows2, columns=columns2).drop(columns=['stock_id'], errors='ignore')

    # Close the cursor and connection
    cursor.close()
    conn.close()

    # Convert date columns to datetime if necessary
    if 'Date' in df2.columns:
        df2['Date'] = pd.to_datetime(df2['Date'], errors='coerce').dt.date

    # Export data to Excel with multiple sheets
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df1.to_excel(writer, sheet_name='manufacturer_product', index=False)
        df2.to_excel(writer, sheet_name='manufacturer_product_stock', index=False)

        # Access the xlsxwriter workbook and worksheets
        workbook = writer.book
        contact_sheet = writer.sheets['manufacturer_product_stock']

        # Define a date format for Excel (day-month-year)
        date_format = workbook.add_format({'num_format': 'dd-mm-yyyy'})

        # Apply date formatting to columns if 'Date' exists
        for col_num, col_name in enumerate(df2.columns):
            if pd.api.types.is_datetime64_any_dtype(df2[col_name]) or (df2[col_name].dtype == 'object' and col_name.lower() == 'date'):
                contact_sheet.set_column(col_num, col_num, 20, date_format)

    # Prepare response
    output.seek(0)  # Ensure to seek back to the start of the BytesIO object
    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=Manufacturer products.xlsx"
    response.headers["Content-type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    return response

@app.route('/export_Manfactured_suppliers_data')
def export_Manfactured_suppliers_data():
    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch data from the first table (suppliers)
    query1 = "SELECT * FROM manufacturer_supplier"
    cursor.execute(query1)
    rows1 = cursor.fetchall()
    columns1 = [i[0] for i in cursor.description]
    
    # Debugging: Print fetched data and column names
    print("Columns from 'manufacturer_supplier' table:", columns1)
    print("Rows from 'manufacturer_supplier' table:", rows1)
    
    # Check if rows1 is empty
    if not rows1:
        print("No data found in 'manufacturer_supplier' table.")

    # Create DataFrame for suppliers
    df1 = pd.DataFrame(rows1, columns=columns1).drop(columns=['id'], errors='ignore')

    # Fetch data from the second table (contact)
    query2 = "SELECT * FROM manufacturer_supplier_stock"
    cursor.execute(query2)
    rows2 = cursor.fetchall()
    columns2 = [i[0] for i in cursor.description]
    
    # Debugging: Print fetched data and column names
    print("Columns from 'manufacturer_supplier_stock' table:", columns2)
    print("Rows from 'manufacturer_supplier_stock' table:", rows2)
    
    # Check if rows2 is empty
    if not rows2:
        print("No data found in 'manufacturer_supplier_stock' table.")

    # Create DataFrame for contact
    df2 = pd.DataFrame(rows2, columns=columns2).drop(columns=['stock_id'], errors='ignore')

    # Close the cursor and connection
    cursor.close()
    conn.close()

    # Convert date columns to datetime if necessary
    if 'Date' in df2.columns:
        df2['Date'] = pd.to_datetime(df2['Date'], errors='coerce').dt.date

    # Export data to Excel with multiple sheets
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df1.to_excel(writer, sheet_name='manufacturer_supplier', index=False)
        df2.to_excel(writer, sheet_name='manufacturer_supplier_stock', index=False)

        # Access the xlsxwriter workbook and worksheets
        workbook = writer.book
        contact_sheet = writer.sheets['manufacturer_supplier_stock']

        # Define a date format for Excel (day-month-year)
        date_format = workbook.add_format({'num_format': 'dd-mm-yyyy'})

        # Apply date formatting to columns if 'Date' exists
        for col_num, col_name in enumerate(df2.columns):
            if pd.api.types.is_datetime64_any_dtype(df2[col_name]) or (df2[col_name].dtype == 'object' and col_name.lower() == 'date'):
                contact_sheet.set_column(col_num, col_num, 20, date_format)

    # Prepare response
    output.seek(0)  # Ensure to seek back to the start of the BytesIO object
    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=Manufacturer suppliers.xlsx"
    response.headers["Content-type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    return response

@app.route('/export_cross_ref')
def export_cross_ref():
    try:
        # Connect to the database
        conn = get_db_connection()  # Replace with your actual DB connection function
        cursor = conn.cursor()

        # Fetch all data from the cross_ref table
        query = "SELECT * FROM cross_ref"
        cursor.execute(query)
        rows = cursor.fetchall()
        columns = [i[0] for i in cursor.description]

        # Debugging: Print fetched data and column names
        print("Columns from cross_ref table:", columns)
        print("Rows from cross_ref table:", rows)

        # Check if rows have data
        if not rows:
            return "No data available to export.", 400

        # Create DataFrame from the fetched data
        df = pd.DataFrame(rows, columns=columns).drop(columns=['id', 'excel'], errors='ignore')

        # Close the cursor and connection
        cursor.close()
        conn.close()

        # Define valid date columns that need to be formatted
        date_columns = ['date']  # Adjust this list based on your actual date column names

        # Convert date columns to datetime and format them
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce').dt.strftime('%d-%m-%Y')

        # Create an Excel file in memory
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Cross Reference Part', index=False)

            # Access the xlsxwriter workbook and worksheet
            workbook = writer.book
            worksheet = writer.sheets['Cross Reference Part']

            # Define a date format for Excel (day-month-year)
            date_format = workbook.add_format({'num_format': 'dd-mm-yyyy'})

            # Apply date formatting to the relevant date columns
            for col_num, col_name in enumerate(df.columns):
                if col_name in date_columns:
                    worksheet.set_column(col_num, col_num, 20, date_format)
                else:
                    worksheet.set_column(col_num, col_num, 20)  # Set general width for other columns

        # Prepare the response for download
        output.seek(0)
        response = make_response(output.getvalue())
        response.headers["Content-Disposition"] = "attachment; filename=Cross_Reference_Part.xlsx"
        response.headers["Content-type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

        return response

    except Exception as e:
        # Handle exceptions and return an error response
        print(f"An error occurred while exporting: {e}")
        return "An error occurred while exporting the data.", 500

@app.route('/export_all_data')
def export_all_data():
    try:
        # Connect to the database
        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetch all tables in the database
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()

        # Create an in-memory output stream for the Excel file
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            # Iterate over all tables and export their data to separate sheets
            for (table_name,) in tables:
                # Fetch all data from the current table
                query = f"SELECT * FROM {table_name}"
                cursor.execute(query)
                rows = cursor.fetchall()
                columns = [i[0] for i in cursor.description]

                # Create DataFrame for the table data
                df = pd.DataFrame(rows, columns=columns)

                # Write the DataFrame to a new sheet in the Excel file
                df.to_excel(writer, sheet_name=table_name, index=False)

                # Get the xlsxwriter workbook and worksheet objects
                workbook = writer.book
                worksheet = writer.sheets[table_name]

                # Optional: Set column widths and formatting if needed
                for i, col in enumerate(df.columns):
                    worksheet.set_column(i, i, 20)

        # Close the database cursor and connection
        cursor.close()
        conn.close()

        # Prepare the response for downloading the Excel file
        output.seek(0)
        response = make_response(output.getvalue())
        response.headers["Content-Disposition"] = "attachment; filename=all_data_export.xlsx"
        response.headers["Content-type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

        return response

    except Exception as e:
        # Handle exceptions and return an error response
        print(f"An error occurred while exporting: {e}")
        return "An error occurred while exporting the data.", 500

@app.route('/export_opportunity_data')
def export_opportunity_data():
    # Connect to the database
    conn = get_db_connection()  # Ensure you have this function defined
    cursor = conn.cursor()

    # Fetch data from the opp_rfq table
    query1 = "SELECT * FROM opp_rfq"
    cursor.execute(query1)
    rows1 = cursor.fetchall()
    columns1 = [i[0] for i in cursor.description]

    # Debugging: Print fetched data and column names
    print("Columns from 'opp_rfq' table:", columns1)
    print("Rows from 'opp_rfq' table:", rows1)

    # Check if rows1 is empty
    if not rows1:
        print("No data found in 'opp_rfq' table.")

    # Create DataFrame for opp_rfq
    df1 = pd.DataFrame(rows1, columns=columns1).drop(columns=['id'], errors='ignore')

    # Drop the 'id' column from df1 if it exists
    if 'id' in df1.columns:
        df1.drop(columns=['id'], inplace=True)

    # Fetch data from the opp_rfq_item table
    query2 = "SELECT * FROM opp_rfq_item"
    cursor.execute(query2)
    rows2 = cursor.fetchall()
    columns2 = [i[0] for i in cursor.description]

    # Debugging: Print fetched data and column names
    print("Columns from 'opp_rfq_item' table:", columns2)
    print("Rows from 'opp_rfq_item' table:", rows2)

    # Check if rows2 is empty
    if not rows2:
        print("No data found in 'opp_rfq_item' table.")

    # Create DataFrame for opp_rfq_item
    df2 = pd.DataFrame(rows2, columns=columns2).drop(columns=['id'], errors='ignore')

    # Drop the 'id' column from df2 if it exists
    if 'id' in df2.columns:
        df2.drop(columns=['id'], inplace=True)

    # Close the cursor and connection
    cursor.close()
    conn.close()

    # Convert date columns to datetime if necessary in df1 (without time)
    date_columns_rfq = ['rfq_date', 'due_date']  # Specify your date columns
    for date_col in date_columns_rfq:
        if date_col in df1.columns:
            df1[date_col] = pd.to_datetime(df1[date_col], errors='coerce').dt.date  # Keep only date

    # Convert date columns to datetime if necessary in df2 (without time)
    date_columns_item = ['Date']  # Specify your date columns in opp_rfq_item
    for date_col in date_columns_item:
        if date_col in df2.columns:
            df2[date_col] = pd.to_datetime(df2[date_col], errors='coerce').dt.date  # Keep only date

    # Export data to Excel with multiple sheets
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Write DataFrames to Excel sheets
        df1.to_excel(writer, sheet_name='opp_rfq', index=False)
        df2.to_excel(writer, sheet_name='opp_rfq_item', index=False)

        # Access the xlsxwriter workbook and worksheets
        workbook = writer.book
        rfq_sheet = writer.sheets['opp_rfq']
        item_sheet = writer.sheets['opp_rfq_item']

        # Define a date format for Excel (day-month-year)
        date_format = workbook.add_format({'num_format': 'dd-mm-yyyy'})

        # Apply date formatting to the opp_rfq sheet
        for col_num, col_name in enumerate(df1.columns):
            if col_name in date_columns_rfq:
                rfq_sheet.set_column(col_num, col_num, 20, date_format)

        # Apply date formatting to the opp_rfq_item sheet
        for col_num, col_name in enumerate(df2.columns):
            if col_name in date_columns_item:
                item_sheet.set_column(col_num, col_num, 20, date_format)

    # Prepare response
    output.seek(0)  # Ensure to seek back to the start of the BytesIO object
    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=Opportunity_RFQ.xlsx"
    response.headers["Content-type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    return response

@app.route('/export_suppliers_offers_data')
def export_suppliers_offers_data():
    # Connect to the database
    conn = get_db_connection()  # Ensure this function is defined elsewhere
    cursor = conn.cursor()

    # Fetch data from the supplier_offers table
    query1 = "SELECT * FROM supplier_offers"
    cursor.execute(query1)
    rows1 = cursor.fetchall()
    columns1 = [i[0] for i in cursor.description]

    # Debugging: Print fetched data and column names
    print("Columns from 'supplier_offers' table:", columns1)
    print("Rows from 'supplier_offers' table:", rows1)

    # Check if rows1 is empty
    if not rows1:
        print("No data found in 'supplier_offers' table.")

    # Create DataFrame for supplier_offers
    df1 = pd.DataFrame(rows1, columns=columns1)

    # Drop 'id' column from df1 if it exists
    if 'id'  and 'excel' in df1.columns:
        df1.drop(columns=['id','excel'], inplace=True)

    # Rename 'Date' column to 'date' if it exists
    if 'Date' in df1.columns:
        df1.rename(columns={'Date': 'date'}, inplace=True)

    # Fetch data from the add_item table
    query2 = "SELECT * FROM add_item"
    cursor.execute(query2)
    rows2 = cursor.fetchall()
    columns2 = [i[0] for i in cursor.description]

    # Debugging: Print fetched data and column names
    print("Columns from 'add_item' table:", columns2)
    print("Rows from 'add_item' table:", rows2)

    # Check if rows2 is empty
    if not rows2:
        print("No data found in 'add_item' table.")

    # Create DataFrame for add_item
    df2 = pd.DataFrame(rows2, columns=columns2)

    # Drop 'item_id' column from df2 if it exists
    if 'item_id' in df2.columns:
        df2.drop(columns=['item_id'], inplace=True)

    # Rename 'created_at' column to 'created_at' if it exists
    if 'created_at' in df2.columns:
        df2.rename(columns={'created_at': 'created_at'}, inplace=True)

    # Close the cursor and connection
    cursor.close()
    conn.close()

    # Convert date columns to datetime if necessary in df1 (keep only date)
    if 'date' in df1.columns:
        df1['date'] = pd.to_datetime(df1['date'], errors='coerce').dt.date  # Keep only date

    # Convert created_at column to datetime in df2 (keep only date)
    if 'created_at' in df2.columns:
        df2['created_at'] = pd.to_datetime(df2['created_at'], errors='coerce').dt.date  # Keep only date

    # Export data to Excel with multiple sheets
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Write DataFrames to Excel sheets
        df1.to_excel(writer, sheet_name='Supplier Offers', index=False)  # Rename sheet to "Supplier Offers"
        df2.to_excel(writer, sheet_name='Add Item', index=False)  # Rename sheet to "Add Item"

        # Access the xlsxwriter workbook and worksheets
        workbook = writer.book
        supplier_offers_sheet = writer.sheets['Supplier Offers']
        add_item_sheet = writer.sheets['Add Item']

        # Define a date format for Excel (day-month-year)
        date_format = workbook.add_format({'num_format': 'dd-mm-yyyy'})

        # Apply date formatting to the supplier_offers sheet for 'date'
        if 'date' in df1.columns:
            date_col_num = df1.columns.get_loc('date')
            supplier_offers_sheet.set_column(date_col_num, date_col_num, 20, date_format)

        # Apply date formatting to the add_item sheet for 'created_at'
        if 'created_at' in df2.columns:
            created_at_col_num = df2.columns.get_loc('created_at')
            add_item_sheet.set_column(created_at_col_num, created_at_col_num, 20, date_format)

    # Prepare response
    output.seek(0)  # Ensure to seek back to the start of the BytesIO object
    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=Suppliers_Offers_Data.xlsx"  # Updated filename
    response.headers["Content-type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    return response


@app.route('/update_suppliers', methods=['POST'])
def update_suppliers():
    if request.method == 'POST':
        # Get form data
        id = request.form['id']
        supplier_name = request.form.get('supplier_name')
        sup_type = request.form.get('sup_type')
        contact_number = request.form.get('contact_number')
        fax = request.form.get('fax')
        website = request.form.get('website')
        address = request.form.get('address')
        remarks = request.form.get('remarks')
        applications = request.form.get('applications')

        try:
            # Connect to the database
            mydb = get_db_connection()
            mycursor = mydb.cursor()

            # Fetch current supplier name to track old name
            mycursor.execute("SELECT supplier_name FROM suppliers WHERE id = %s", (id,))
            result = mycursor.fetchone()
            if result:
                old_supplier_name = result[0]

                # Update suppliers table
                update_supplier_sql = """
                UPDATE suppliers 
                SET supplier_name=%s, sub_type=%s, contact_number=%s, fax=%s, website=%s, 
                    address=%s, remarks=%s, applications=%s 
                WHERE id=%s
                """
                values = (supplier_name, sup_type, contact_number, fax, website, address, remarks, applications, id)
                mycursor.execute(update_supplier_sql, values)

                # Update supplier_name in manufacturer_product table
                update_manufacturer_product_sql = """
                UPDATE manufacturer_product 
                SET manufacturer_name=%s 
                WHERE manufacturer_name=%s
                """
                mycursor.execute(update_manufacturer_product_sql, (supplier_name, old_supplier_name))

                update_manufacturer_supplier_sql = """
                UPDATE manufacturer_supplier 
                SET manufacturer_name=%s 
                WHERE manufacturer_name=%s
                """
                mycursor.execute(update_manufacturer_supplier_sql, (supplier_name, old_supplier_name))

                update_item_sql = """
                UPDATE item 
                SET manufacturername=%s 
                WHERE manufacturername=%s
                """
                mycursor.execute(update_item_sql, (supplier_name, old_supplier_name))

                update_suppliers_offers_sql = """
                UPDATE supplier_offers 
                SET suppliername=%s 
                WHERE suppliername=%s
                """
                mycursor.execute(update_suppliers_offers_sql, (supplier_name, old_supplier_name))
                # Commit changes to the database
                mydb.commit()

                flash("Data Updated Successfully")
            else:
                flash("Supplier not found")

        except mysql.connector.Error as err:
            flash(f"Error: {err}")
        finally:
            # Close cursor and database connection
            mycursor.close()
            mydb.close()

    return redirect(url_for('Suppliers'))




@app.route('/delete_contact/<int:id>')
def delete_contact(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Execute DELETE operation
        cursor.execute("DELETE FROM contact WHERE id = %s", (id,))
        conn.commit()

        cursor.close()
        conn.close()

        flash('Record has been deleted successfully', 'success')
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')

    return redirect(url_for('manage_customers'))


    
@app.route('/update_contact', methods=['POST'])
def update_contact():
    if request.method == 'POST':
        id = request.form['id']
        supplier_name = request.form.get('suppliername')
        contactpersonname = request.form['contactpersonname']
        contactno = request.form.get('contactno')  # Fixed this line
          # Fixed this line
        email = request.form.get('email')  # Fixed this line
        skype = request.form.get('skype')  # Fixed this line
        addedby = request.form.get('addedby')  # Fixed this line
         # Fixed this line

        # Database connection
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="Omnipro"
        )
        mycursor = mydb.cursor()

        # Update SQL query
        sql = "UPDATE contact SET  supplier_name=%s,contact_person=%s, contact_number=%s, email=%s, skype=%s, added_by=%s  WHERE id=%s"
        val = (supplier_name,contactpersonname, contactno,  email, skype, addedby,  id)
        mycursor.execute(sql, val)
        mydb.commit()

        # Close cursor and database connection
        mycursor.close()
        mydb.close()

        flash("Data Updated Successfully")

    return redirect(url_for('manage_customers'))

@app.route('/check_supplier_name', methods=['POST'])
def check_supplier_name():
    supplier_name = request.form['supplier_name']
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM suppliers WHERE supplier_name = %s", (supplier_name,))
    result = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    
    return jsonify({'exists': result > 0})


@app.route('/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filename = secure_filename(file.filename)
            if filename.endswith('.xls') or filename.endswith('.xlsx'):
                db_connection = get_db_connection()
                cursor = db_connection.cursor()

                # Drop existing table if it exists
                cursor.execute("DROP TABLE IF EXISTS datatable")
                
                # Create table
                cursor.execute("CREATE TABLE datatable (column1 VARCHAR(255), column2 VARCHAR(255))")

                # Read Excel file and insert data into MySQL table
                df = pd.read_excel(file)
                for index, row in df.iterrows():
                    cursor.execute("INSERT INTO datatable (column1, column2) VALUES (%s, %s)", (row['Column1'], row['Column2']))  # Adjust column names as needed

                db_connection.commit()  # Commit changes
                cursor.close()
                db_connection.close()
                return jsonify({'success': True})
            elif filename.endswith('.pdf'):
                # Code to extract data from PDF and save to MySQL
                return jsonify({'success': True})
    return jsonify({'success': False})




@app.route('/Manfactured', methods=['GET', 'POST'])
def Manfactured():
    mydb = get_db_connection()
    mycursor = mydb.cursor(buffered=True)

    if request.method == 'POST':
        try:
            # Capture form inputs
            manufacturer_name = request.form['manufacturer_name']
            remarks = request.form['remarks']
            applications = request.form['applications']

            product_names = request.form.getlist('productname[]')
            added_bys = request.form.getlist('addedby[]')
            product_remarks = request.form.getlist('remarks[]')
            dates = request.form.getlist('date[]')
            
            contacts = []
            failed_rows = []
            inserted_rows = 0

            # Insert or update manufacturer details
            manufacturer_query = """
            INSERT INTO manufacturer_product (manufacturer_name, remarks, applications)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE remarks = VALUES(remarks), applications = VALUES(applications)
            """
            manufacturer_values = (manufacturer_name, remarks, applications)
            mycursor.execute(manufacturer_query, manufacturer_values)
            mydb.commit()

            # Insert product details
            for i in range(len(product_names)):
                product_query = """
                INSERT INTO manufacturer_product_stock (manufacturer_name, product_name, added_by, remarks, date)
                VALUES (%s, %s, %s, %s, %s)
                """
                product_values = (manufacturer_name, product_names[i], added_bys[i], product_remarks[i], dates[i])
                mycursor.execute(product_query, product_values)

            # Process file upload
            if 'file' in request.files:
                file = request.files['file']
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)

                    # Read Excel file
                    df = pd.read_excel(filepath)
                    emp=get_employee_names()

                    # Ensure Excel contains only the required columns
                    required_columns = ['product_name', 'added_by', 'remarks', 'date']
                    if not all(col in df.columns for col in required_columns):
                        flash(f'Excel file must contain the columns: {", ".join(required_columns)}', 'error')
                        return redirect(url_for('Manfactured'))

                    for index, row in df.iterrows():
                        row_number = index + 2  # Adjust to show Excel row number correctly
                        product_name = str(row['product_name']).strip().upper()
                        added_by = str(row['added_by']).strip().upper()
                        product_remark = str(row['remarks']).strip()
                        date = str(row['date']).strip()

                        # Validate unique product_name
                        if product_name not in [p[0] for p in contacts] and added_by in emp:
                            contacts.append((manufacturer_name, product_name, added_by, product_remark, date))
                            inserted_rows += 1
                        else:
                            failed_rows.append(f'{row_number}')  # Record the failed row number

            # Insert contacts from Excel into the database
            for contact in contacts:
                mycursor.execute("""
                    INSERT INTO manufacturer_product_stock (manufacturer_name, product_name, added_by, remarks, date)
                    VALUES (%s, %s, %s, %s, %s)
                    """, contact)
            
            mydb.commit()
            
            # Flash success message showing inserted and failed rows
            flash(f'Successfully inserted {inserted_rows} rows. Rows not inserted: {", ".join(failed_rows)}', 'success')
            return redirect(url_for('Manfactured'))

        except Exception as e:
            print(f"Error inserting data: {str(e)}")
            mydb.rollback()

    # Fetch data for the GET request (loading the page)
    mycursor.execute("SELECT * FROM manufacturer_product")
    manufacturerproduct = mycursor.fetchall()
    mycursor.execute("SELECT * FROM employee where status=1")
    employee = mycursor.fetchall()

    

    mycursor.execute("SELECT supplier_name FROM suppliers WHERE sub_type = 'manufacturer';")
    suppliers = mycursor.fetchall()

    mycursor.execute("""
    SELECT s.stock_id, s.product_name, s.added_by, s.remarks, s.date, m.manufacturer_name
    FROM manufacturer_product_stock s
    JOIN manufacturer_product m ON s.manufacturer_name = m.manufacturer_name
    """)
    product_stocks = mycursor.fetchall()

    # Pagination logic
    search_query = request.args.get('search', '')
    page = int(request.args.get('page', 1))
    per_page = 10
    offset = (page - 1) * per_page
    
    mycursor.execute("SELECT COUNT(*) FROM manufacturer_product WHERE manufacturer_name LIKE %s", (f'{search_query}%',))
    total_customers = mycursor.fetchone()[0]
    
    mycursor.execute("SELECT * FROM manufacturer_product WHERE manufacturer_name LIKE %s ORDER BY manufacturer_name ASC LIMIT %s OFFSET %s",
                   (f'{search_query}%', per_page, offset))
    manufacturerproduct = mycursor.fetchall()

    mycursor.close()
    mydb.close()
    
    total_pages = (total_customers + per_page - 1) // per_page

    return render_template('Manfactured.html',employee=employee, suppliers=suppliers, manufacturerproduct=manufacturerproduct, product_stocks=product_stocks, page=page, per_page=per_page, total_pages=total_pages, search_query=search_query)


@app.route('/check_manufacturer_product_name', methods=['POST'])
def check_manufacturer_product_name():
    manufacturername = request.form['manufacturername']
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Query to check if the manufacturer name exists in the item table
    cursor.execute("SELECT COUNT(*) FROM manufacturer_product WHERE manufacturer_name = %s", (manufacturername,))
    result = cursor.fetchone()[0]
    
    cursor.close()
    conn.close()
    
    # Return whether the name exists or not
    return jsonify({'exists': result > 0})


@app.route('/check_manufacturer_supplier_name', methods=['POST'])
def check_manufacturer_supplier_name():
    manufacturername = request.form['manufacturername']
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Query to check if the manufacturer name exists in the item table
    cursor.execute("SELECT COUNT(*) FROM manufacturer_supplier WHERE manufacturer_name = %s", (manufacturername,))
    result = cursor.fetchone()[0]
    
    cursor.close()
    conn.close()
    
    # Return whether the name exists or not
    return jsonify({'exists': result > 0})



@app.route('/add_manfactured', methods=['GET', 'POST'])
def add_manfactured():
    mydb = get_db_connection()
    mycursor = mydb.cursor(buffered=True)
    error = None

    if request.method == 'POST':
        manufacturer_name = request.form.get('manufacturer_name')  # Get manufacturer name
        productname = request.form.get('productname')  # Get product name
        addedby = request.form.get('addedby')  # Get added by
        remarks = request.form.get('remarks')  # Get remarks
        date = request.form.get('date')  # Get the date

        try:
            # Ensure date is not in the future
            if datetime.strptime(date, '%Y-%m-%d').date() > datetime.today().date():
                flash("Error: Date cannot be in the future!", "danger")
                return redirect(url_for('manage_product'))

            # Check if a similar record already exists
            check_query = """
                SELECT * FROM manufacturer_product_stock 
                WHERE manufacturer_name = %s AND product_name = %s AND date = %s
            """
            check_values = (manufacturer_name, productname, date)
            mycursor.execute(check_query, check_values)
            duplicate_row = mycursor.fetchone()

            if duplicate_row:
                # If a duplicate row is found, set error message and redirect
                flash("Duplicate entry: This product already exists for the manufacturer on the given date.", "danger")
            else:
                # Prepare the SQL query to insert a new row
                query = """
                    INSERT INTO manufacturer_product_stock (manufacturer_name, product_name, added_by, remarks, date)
                    VALUES (%s, %s, %s, %s, %s)
                """
                values = (manufacturer_name, productname, addedby, remarks, date)

                # Execute the insertion query
                mycursor.execute(query, values)
                mydb.commit()  # Commit the changes to the database
                flash("Product added successfully!", "success")

        except IntegrityError:
            mydb.rollback()  # Rollback in case of an error
            flash("Duplicate entry. Please try again with a different Product Name or Manufacturer.", "danger")
        
        except Exception as e:
            flash(f"An error occurred: {str(e)}", "danger")
        
        finally:
            # Redirect to manage_product after form submission
            return redirect(url_for('manage_product'))

    # Fetch existing manufacturer products for display
    mycursor.execute("SELECT * FROM manufacturer_product_stock")
    branches = mycursor.fetchall()

    # Close cursor and database connection
    mycursor.close()
    mydb.close()

    max_date = datetime.today().strftime('%Y-%m-%d')

    return render_template('manage_product.html', branches=branches, max_date=max_date, error=error)







@app.route('/add_excel', methods=['GET', 'POST'])
def add_excel():
    if request.method == 'POST':
        suppliername = request.form.get('manufacturer_name')

        if 'file' not in request.files:
            flash('No file part.', 'danger')
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash('No selected file.', 'danger')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            try:
                df = pd.read_excel(filepath)

                # Check for duplicates within the Excel file
                if df.duplicated(subset=['product_name', 'added_by', 'remarks', 'date']).any():
                    flash('Duplicate rows found in the Excel file.', 'danger')
                    os.remove(filepath)
                    return redirect(request.url)

                # Fetch valid employee names
                employee_names = get_employee_names()

                # Database connection
                mydb = get_db_connection()
                if not mydb:
                    flash('Database connection failed.', 'danger')
                    os.remove(filepath)
                    return redirect(url_for('manage_product'))

                mycursor = mydb.cursor(buffered=True)

                insert_query = """
                    INSERT INTO manufacturer_product_stock (manufacturer_name, product_name, added_by, remarks, date)
                    VALUES (%s, %s, %s, %s, %s)
                """

                # Check for a duplicate row in the database by comparing all fields
                check_query = """
                    SELECT COUNT(*) FROM manufacturer_product_stock 
                    WHERE manufacturer_name = %s AND product_name = %s AND added_by = %s AND remarks = %s AND date = %s
                """

                inserted_rows = 0
                failed_rows = []

                # Iterate over each row in the Excel file
                for index, row in df.iterrows():
                    product_name = str(row['product_name']).strip()
                    added_by = str(row['added_by']).strip()
                    remarks = str(row['remarks']).strip()
                    date = str(row['date']).strip()

                    # Validate employee name
                    if added_by in employee_names:

                        # Check if a row with the exact data already exists in the database
                        mycursor.execute(check_query, (suppliername, product_name, added_by, remarks, date))
                        if mycursor.fetchone()[0] == 0:
                            try:
                                mycursor.execute(insert_query, (suppliername, product_name, added_by, remarks, date))
                                mydb.commit()
                                inserted_rows += 1
                            except mysql.connector.Error as e:
                                failed_rows.append(f"Row {index + 2}: Database error - {str(e)}")
                        else:
                            failed_rows.append(f"Row {index + 2}: Duplicate entry in database")

                    else:
                        failed_rows.append(f"Row {index + 2}: Invalid data - Added By: {added_by}")

                if inserted_rows > 0:
                    success_message = f'Successfully inserted {inserted_rows} rows.'
                    if failed_rows:
                        success_message += f' Rows not inserted: {"; ".join(failed_rows)}'
                    flash(success_message, 'success')
                else:
                    flash('No valid data was inserted.', 'danger')

            except Exception as e:
                flash(f'Error processing file: {str(e)}', 'danger')

            finally:
                if 'mydb' in locals():
                    mycursor.close()
                    mydb.close()
                os.remove(filepath)  # Optionally delete the file after processing

            return redirect(url_for('manage_product'))

    return render_template('manage_product.html')


@app.route('/manage_product', methods=['GET'])
def manage_product():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch all manufacturer products and customers
    cursor.execute('SELECT * FROM manufacturer_product_stock')
    manufacturer_product = cursor.fetchall()

    cursor.execute('SELECT * FROM manufacturer_product')
    customers = cursor.fetchall()

    search_query = request.args.get('search', '')
    page = int(request.args.get('page', 1))
    per_page = 10
    offset = (page - 1) * per_page

    # Count total matching records for pagination
    cursor.execute("""
        SELECT COUNT(*) FROM manufacturer_product_stock 
        WHERE manufacturer_name LIKE %s OR product_name LIKE %s
    """, (f'{search_query}%', f'{search_query}%'))
    total_contacts = cursor.fetchone()[0]

    # Fetch matching records with pagination
    cursor.execute("""
        SELECT * FROM manufacturer_product_stock 
        WHERE manufacturer_name LIKE %s OR product_name LIKE %s 
        ORDER BY manufacturer_name ASC, product_name ASC 
        LIMIT %s OFFSET %s
    """, (f'{search_query}%', f'{search_query}%', per_page, offset))
    manufacturer_product = cursor.fetchall()

    cursor.close()
    conn.close()

    total_pages = (total_contacts + per_page - 1) // per_page

    return render_template('manage_product.html', manufacturer_product=manufacturer_product, customers=customers,  page=page, per_page=per_page, total_pages=total_pages, search_query=search_query)



@app.route('/delete_manfactured/<int:id>')
def delete_manfactured(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Execute DELETE operation
        cursor.execute("DELETE FROM manufacturer_product WHERE id = %s", (id,))
        conn.commit()

        cursor.close()
        conn.close()

        flash('Record has been deleted successfully', 'success')
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')

    return redirect(url_for('Manfactured'))



@app.route('/update_manfactured', methods=['POST'])
def update_manfactured():
    if request.method == 'POST':
        id = request.form['id']  # ID should be passed correctly
        manufacturer_name = request.form.get('manufacturer_name')  # Corrected field name
        remarks = request.form.get('remarks')
        applications = request.form.get('applications')

        # Connect to database
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="Omnipro"
        )
        mycursor = mydb.cursor()

        # Update SQL query
        sql = "UPDATE manufacturer_product SET manufacturer_name=%s, remarks=%s, applications=%s WHERE id=%s"
        val = (manufacturer_name, remarks, applications, id)
        mycursor.execute(sql, val)
        mydb.commit()

        # Close cursor and database connection
        mycursor.close()
        mydb.close()

        flash("Data Updated Successfully")

    return redirect(url_for('Manfactured'))




@app.route('/delete_product/<int:stock_id>')
def delete_product(stock_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Execute DELETE operation
        cursor.execute("DELETE FROM manufacturer_product_stock WHERE stock_id = %s", (stock_id,))
        conn.commit()

        cursor.close()
        conn.close()

        flash('Record has been deleted successfully', 'success')
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')

    return redirect(url_for('manage_product'))


    
@app.route('/update_product', methods=['POST'])
def update_product():
    if request.method == 'POST':
        id = request.form['id']
        manufacturer_name = request.form.get('manufacturer_name')
        product_names = request.form.get('productname')
        addedby = request.form.get('addedby')  # Fixed this line
          # Fixed this line
        product_remarks = request.form.get('remarks') 
        date = request.form.get('date')  # Fixed this line
         # Fixed this line
         # Fixed this line
         # Fixed this line

        # Database connection
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="Omnipro"
        )
        mycursor = mydb.cursor()

        # Update SQL query
        sql = "UPDATE manufacturer_product_stock SET manufacturer_name=%s, product_name=%s, added_by=%s, remarks=%s, date=%s  WHERE stock_id=%s"
        val = (manufacturer_name,product_names,addedby,  product_remarks,date, id)
        mycursor.execute(sql, val)
        mydb.commit()

        # Close cursor and database connection
        mycursor.close()
        mydb.close()

        flash("Data Updated Successfully")

    return redirect(url_for('manage_product'))



@app.route('/Manfactured_Supp', methods=['GET', 'POST'])
def Manfactured_Supp():
    mydb = get_db_connection()
    mycursor = mydb.cursor(buffered=True)

    if request.method == 'POST':
        try:
            manufacturer_name = request.form['ManufacturerName']
            remarks = request.form['Remarks']

            SupplierName = request.form.getlist('SupplierName[]')
            SupplierRemarks = request.form.getlist('Remarks[]')
            Date = request.form.getlist('Date[]')

            # Insert manufacturer details
            manufacturer_query = """
            INSERT INTO manufacturer_supplier (manufacturer_name, remarks)
            VALUES (%s, %s)
            """
            manufacturer_values = (manufacturer_name, remarks)
            mycursor.execute(manufacturer_query, manufacturer_values)
            mydb.commit()

            # Insert supplier distributor details from form submission
            for i in range(len(SupplierName)):
                supplier_query = """
                INSERT INTO manufacturer_supplier_stock (manufacturer_name, supplier_name, remarks, date)
                VALUES (%s, %s, %s, %s)
                """
                supplier_values = (manufacturer_name, SupplierName[i], SupplierRemarks[i], Date[i])
                mycursor.execute(supplier_query, supplier_values)

            # Commit the form data insertions
            mydb.commit()

            # Process file upload if it exists
            if 'file' in request.files:
                file = request.files['file']
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)

                    # Read Excel file
                    df = pd.read_excel(filepath)

                    # Validate required columns
                    required_columns = ['supplier_name', 'remarks', 'date']
                    missing_columns = [col for col in required_columns if col not in df.columns]

                    if missing_columns:
                        flash(f'Excel file must contain the columns: {", ".join(missing_columns)}', 'error')
                        return redirect(url_for('Manfactured_Supp'))

                    # Fetch valid suppliers with 'Distributor' sub_type
                    mycursor.execute("SELECT supplier_name FROM suppliers WHERE sub_type != 'manufacturer'")
                    valid_suppliers = {row[0] for row in mycursor.fetchall()}

                    contacts = []
                    failed_rows = []
                    inserted_rows = 0
                    existing_entries = set()  # To keep track of existing entries

                    for index, row in df.iterrows():
                        row_number = index + 2  # Adjust to show Excel row number correctly
                        supplier_name = str(row['supplier_name']).strip().upper()
                        remarks = str(row['remarks']).strip()
                        date = str(row['date']).strip()

                        contact_key = (manufacturer_name, supplier_name, remarks, date)

                        # Check for duplicates before adding
                        if contact_key not in existing_entries:
                            # Validate supplier
                            if supplier_name in valid_suppliers:
                                contacts.append(contact_key)
                                existing_entries.add(contact_key)
                                inserted_rows += 1
                            else:
                                failed_rows.append(f'{row_number}')
                        else:
                            failed_rows.append(f'{row_number} (Duplicate)')

                    # Insert contacts from Excel into the database
                    for contact in contacts:
                        mycursor.execute("""
                            INSERT INTO manufacturer_supplier_stock (manufacturer_name, supplier_name, remarks, date)
                            VALUES (%s, %s, %s, %s)
                        """, contact)

                    mydb.commit()

                    flash(f'Successfully inserted {inserted_rows} rows. Rows not inserted: {", ".join(failed_rows)}', 'success')
                    return redirect(url_for('Manfactured_Supp'))

        except Exception as e:
            print(f"Error inserting data: {str(e)}")
            mydb.rollback()

    # Fetch existing data for GET request
    
    mycursor.execute("SELECT supplier_name FROM suppliers WHERE sub_type = 'manufacturer';")
    suppliers = mycursor.fetchall()
    mycursor.execute("SELECT supplier_name FROM suppliers WHERE sub_type != 'manufacturer';")
    distributor_suppliers = mycursor.fetchall()

    search_query = request.args.get('search', '')
    page = int(request.args.get('page', 1))
    per_page = 10
    offset = (page - 1) * per_page

    mycursor.execute("SELECT COUNT(*) FROM manufacturer_supplier WHERE manufacturer_name LIKE %s", (f'{search_query}%',))
    total_customers = mycursor.fetchone()[0]

    mycursor.execute("SELECT * FROM manufacturer_supplier WHERE manufacturer_name LIKE %s ORDER BY manufacturer_id DESC LIMIT %s OFFSET %s",
                      (f'{search_query}%', per_page, offset))
    manufacturer_supplier = mycursor.fetchall()

  

    mycursor.close()
    mydb.close()

    total_pages = (total_customers + per_page - 1) // per_page
    
    return render_template('Manfactured_Supp.html', distributor_suppliers=distributor_suppliers, suppliers=suppliers, total_pages=total_pages, manufacturer_supplier=manufacturer_supplier, per_page=per_page, page=page)











@app.route('/mng_supp', methods=['GET'])
def mng_supp():
    conn = get_db_connection()
    cursor = conn.cursor()

    query3 =   'select * from manufacturer_supplier_stock'
    cursor.execute(query3)
    supp = cursor.fetchall()


    query3 =   'select * from manufacturer_supplier'
    cursor.execute(query3)
    customers = cursor.fetchall()


    
    search_query = request.args.get('search', '')
    page = int(request.args.get('page', 1))
    per_page = 10
    offset = (page - 1) * per_page

    # Count total matching records for pagination
    cursor.execute("""
        SELECT COUNT(*) FROM manufacturer_supplier_stock 
        WHERE manufacturer_name LIKE %s OR supplier_name LIKE %s
    """, (f'{search_query}%', f'{search_query}%'))
    total_contacts = cursor.fetchone()[0]

    # Fetch matching records with pagination
    cursor.execute("""
        SELECT * FROM manufacturer_supplier_stock 
        WHERE manufacturer_name LIKE %s OR supplier_name LIKE %s 
        ORDER BY stock_id DESC, supplier_name ASC 
        LIMIT %s OFFSET %s
    """, (f'{search_query}%', f'{search_query}%', per_page, offset))
    supp = cursor.fetchall()

    cursor.close()
    conn.close()

    total_pages = (total_contacts + per_page - 1) // per_page

    max_date = datetime.today().strftime('%Y-%m-%d')


    return render_template('mng_supp.html',max_date=max_date,supp=supp, customers=customers,  page=page, per_page=per_page, total_pages=total_pages, search_query=search_query)


@app.route('/add_manfactured_supp', methods=['GET', 'POST'])
def add_manfactured_supp():
    mydb = get_db_connection()
    mycursor = mydb.cursor(buffered=True)
    error = None

    if request.method == 'POST':
        manufacturer_name = request.form.get('ManufacturerName')  # Get manufacturer name
        supplier_name = request.form.get('SupplierName')  # Get supplier name
        remarks = request.form.get('Remarks')  # Get remarks
        date = request.form.get('date')  # Get the date

        try:
            # Ensure the date is not in the future
            if datetime.strptime(date, '%Y-%m-%d').date() > datetime.today().date():
                flash("Error: Date cannot be in the future!", "danger")
                return redirect(url_for('mng_supp'))

            # Check if the record (manufacturer_name, supplier_name, date) already exists
            check_query = """
                SELECT * FROM manufacturer_supplier_stock 
                WHERE manufacturer_name = %s AND supplier_name = %s AND date = %s
            """
            check_values = (manufacturer_name, supplier_name, date)
            mycursor.execute(check_query, check_values)
            duplicate_row = mycursor.fetchone()

            if duplicate_row:
                # If a duplicate row is found, set error message and redirect
                flash("Duplicate entry: This manufacturer and supplier combination already exists on the given date.", "danger")
            else:
                # Prepare the SQL query to insert a new row
                query = """
                    INSERT INTO manufacturer_supplier_stock (manufacturer_name, supplier_name, remarks, date)
                    VALUES (%s, %s, %s, %s)
                """
                values = (manufacturer_name, supplier_name, remarks, date)

                # Execute the insertion query
                mycursor.execute(query, values)
                mydb.commit()  # Commit the changes to the database
                flash("Supplier successfully added!", "success")

        except mysql.connector.IntegrityError:
            mydb.rollback()  # Rollback in case of a database constraint violation
            flash("Duplicate entry or constraint violation. Please try again with different details.", "danger")
        
        except Exception as e:
            flash(f"An unexpected error occurred: {str(e)}", "danger")
        
        finally:
            # Redirect to the supplier management page after form submission
            return redirect(url_for('mng_supp'))

    # Fetch existing manufacturer-supplier stocks for display
    mycursor.execute("SELECT * FROM manufacturer_supplier_stock")
    branches = mycursor.fetchall()

    mycursor.execute("SELECT * FROM manufacturer_supplier_stock")
    suppliers = mycursor.fetchall()

    # Close cursor and database connection
    mycursor.close()
    mydb.close()

    max_date = datetime.today().strftime('%Y-%m-%d')

    return render_template('mng_supp.html', max_date=max_date, suppliers=suppliers, branches=branches, error=error)



@app.route('/add_supp_excel', methods=['GET', 'POST'])
def add_supp_excel():
    if request.method == 'POST':
        suppliername = request.form.get('manufacturer_name')

        if 'file' not in request.files:
            flash('No file part or selected file.', 'danger')
            return redirect(request.url)

        file = request.files['file']

        if file and allowed_file(file.filename):
            try:
                # Read the file into a pandas DataFrame directly from memory
                df = pd.read_excel(file)

                # Check for duplicate rows in the Excel file
                duplicate_rows_in_excel = df.duplicated(subset=['supplier_name', 'remarks', 'date'])
                if duplicate_rows_in_excel.any():
                    flash('Duplicate rows found within the Excel file.', 'danger')
                    return redirect(request.url)

                # Database connection
                mydb = get_db_connection()
                if not mydb:
                    flash('Database connection failed.', 'danger')
                    return redirect(url_for('mng_supp'))

                mycursor = mydb.cursor(buffered=True)

                # Query to check if supplier_name is a distributor
                distributor_check_query = """
                    SELECT COUNT(*) FROM suppliers WHERE supplier_name = %s AND sub_type != 'manufacturer'
                """

                insert_query = """
                    INSERT INTO manufacturer_supplier_stock (manufacturer_name, supplier_name, remarks, date)
                    VALUES (%s, %s, %s, %s)
                """
                check_query = """
                    SELECT COUNT(*) FROM manufacturer_supplier_stock 
                    WHERE manufacturer_name = %s AND supplier_name = %s AND remarks = %s AND date = %s
                """

                inserted_rows = 0
                failed_rows = []

                # Iterate over each row in the Excel file
                for index, row in df.iterrows():
                    supplier_name = str(row['supplier_name']).strip()
                    remarks = str(row['remarks']).strip()
                    date = str(row['date']).strip()

                    # Check if supplier_name is a 'Distributor'
                    mycursor.execute(distributor_check_query, (supplier_name,))
                    if mycursor.fetchone()[0] == 0:
                        failed_rows.append(f"Row {index + 2}: Supplier name is not a 'Distributor'")
                        continue  # Skip this row if it's not a Distributor

                    # Check if a row with the exact data already exists in the database
                    mycursor.execute(check_query, (suppliername, supplier_name, remarks, date))
                    if mycursor.fetchone()[0] == 0:
                        try:
                            mycursor.execute(insert_query, (suppliername, supplier_name, remarks, date))
                            mydb.commit()
                            inserted_rows += 1
                        except mysql.connector.Error as e:
                            failed_rows.append(f"Row {index + 2}: Database error - {str(e)}")
                    else:
                        failed_rows.append(f"Row {index + 2}: Duplicate entry in the database")

                # Handle success and failed rows
                message = []
                if inserted_rows > 0:
                    message.append(f'Successfully inserted {inserted_rows} rows.')
                if failed_rows:
                    message.append(f'Failed to insert {len(failed_rows)} rows. Details: {"; ".join(failed_rows)}')
                
                flash(' '.join(message), 'info')

            except Exception as e:
                flash(f'Error processing file: {str(e)}', 'danger')

            finally:
                if 'mydb' in locals():
                    mycursor.close()
                    mydb.close()

            return redirect(url_for('mng_supp'))

    return render_template('mng_supp.html')





@app.route('/add_supplieroffer_excel', methods=['POST'])
def add_supplieroffer_excel():
    suppliername = request.form.get('suppliername')

    if 'file' not in request.files:
        flash('No file part', 'danger')
        return redirect(url_for('Suppliers_Offers'))

    file = request.files['file']
    if file.filename == '':
        flash('No selected file', 'danger')
        return redirect(url_for('Suppliers_Offers'))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Load Excel file into a pandas DataFrame
        try:
            df = pd.read_excel(filepath)
        except Exception as e:
            flash(f'Error reading the Excel file: {e}', 'danger')
            return redirect(url_for('Suppliers_Offers'))

        # Check if required columns are present
        required_columns = ['ManufacturerPartNo', 'Description', 'Manufacturer', 'Qty', 'price']
        if not all(col in df.columns for col in required_columns):
            flash('Invalid Excel format. Required columns: ManufacturerPartNo, Description, Manufacturer, Qty, price', 'danger')
            return redirect(url_for('Suppliers_Offers'))

        # Database connection
        conn = get_db_connection()
        mycursor = conn.cursor()

        # Fetch valid ManufacturerPartNo and Manufacturer names
        mycursor.execute("SELECT man_part_no FROM part_item")
        valid_man_part_nos = {row[0] for row in mycursor.fetchall()}

        mycursor.execute("SELECT supplier_name FROM suppliers WHERE sub_type = 'MANUFACTURER'")
        valid_manufacturer_names = {row[0] for row in mycursor.fetchall()}

        inserted_rows = 0
        duplicate_rows = []
        failed_rows = []

        # Iterate over rows in the DataFrame
        for index, row in df.iterrows():
            # Safely get the values, default to an empty string if NaN
            ManufacturerPartNo = str(row.get('ManufacturerPartNo', '')).strip() if pd.notna(row.get('ManufacturerPartNo')) else ''
            Description = str(row.get('Description', '')).strip() if pd.notna(row.get('Description')) else ''
            Manufacturer = str(row.get('Manufacturer', '')).strip() if pd.notna(row.get('Manufacturer')) else ''
            Qty = str(row.get('Qty', '')).strip() if pd.notna(row.get('Qty')) else ''
            price = str(row.get('price', '')).strip() if pd.notna(row.get('price')) else ''

            # Track the invalid columns for this row
            invalid_columns = []

            # Check if ManufacturerPartNo and Manufacturer are valid
            if ManufacturerPartNo not in valid_man_part_nos:
                invalid_columns.append('ManufacturerPartNo')
            if Manufacturer not in valid_manufacturer_names:
                invalid_columns.append('Manufacturer')

            # If there are any invalid columns, mark the row as failed
            if invalid_columns:
                failed_rows.append(f"Row {index + 2}: Invalid columns - {', '.join(invalid_columns)}")
                continue

            # Check if this row already exists in the database for all relevant fields
            mycursor.execute(
                """
                SELECT COUNT(*) FROM add_item 
                WHERE suppliername = %s 
                AND manufacturer_part_no = %s 
                AND description = %s 
                AND manufacturer = %s 
                AND quantity = %s 
                AND date = %s
                """,
                (suppliername, ManufacturerPartNo, Description, Manufacturer, Qty, price)
            )
            if mycursor.fetchone()[0] > 0:
                # This row is a duplicate
                duplicate_rows.append(f"Row {index + 2}: Duplicate entry")
            else:
                # Insert the row into the database if both fields are valid and no duplicates exist
                insert_query = """
                    INSERT INTO add_item (suppliername, manufacturer_part_no, description, manufacturer, quantity, date)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                data = (suppliername, ManufacturerPartNo, Description, Manufacturer, Qty, price)

                try:
                    mycursor.execute(insert_query, data)
                    inserted_rows += 1
                except mysql.connector.Error as e:
                    failed_rows.append(f"Row {index + 2}: Database error - {str(e)}")
                    print(f"Error inserting row {index + 2}: {data} - Error: {str(e)}")

        # Commit the transaction if any rows were inserted
        if inserted_rows > 0:
            conn.commit()

        # Create one flash message for success and failure
        message = []
        if inserted_rows > 0:
            message.append(f'Successfully inserted {inserted_rows} rows.')
        if duplicate_rows:
            message.append(f"Skipped {len(duplicate_rows)} duplicate rows.")
        if failed_rows:
            message.append(f"Failed to insert {len(failed_rows)} rows. Details: {'; '.join(failed_rows)}")

        # Display all messages in a single alert
        flash(' '.join(message), 'info')

        # Close the database connection
        mycursor.close()
        conn.close()

    return redirect(url_for('Suppliers_Offers'))


@app.route('/delete_mansupp/<int:manufacturer_id>')
def delete_mansupp(manufacturer_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Execute DELETE operation
        cursor.execute("DELETE FROM manufacturer_supplier WHERE manufacturer_id = %s", (manufacturer_id,))
        conn.commit()

        cursor.close()
        conn.close()

        flash('Record has been deleted successfully', 'success')
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')

    return redirect(url_for('Manfactured_Supp'))


@app.route('/update_mansupp', methods=['POST'])
def update_mansupp():
    if request.method == 'POST':
        id = request.form['id']
        manufacturer_name = request.form.get('manufacturer_name')
        remarks = request.form.get('remarks')
        
        
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="Omnipro"
        )
        mycursor = mydb.cursor()

        # Update SQL query
        sql = "UPDATE manufacturer_supplier SET manufacturer_name=%s, remarks=%s  WHERE manufacturer_id=%s"
        val = (manufacturer_name, remarks, id)
        mycursor.execute(sql, val)
        mydb.commit()

        # Close cursor and database connection
        mycursor.close()
        mydb.close()

        flash("Data Updated Successfully")

    return redirect(url_for('Manfactured_Supp'))




@app.route('/delete_supstock/<int:stock_id>')
def delete_supstock(stock_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Execute DELETE operation
        cursor.execute("DELETE FROM manufacturer_supplier_stock WHERE stock_id = %s", (stock_id,))
        conn.commit()

        cursor.close()
        conn.close()

        flash('Record has been deleted successfully', 'success')
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')

    return redirect(url_for('mng_supp'))


@app.route('/update_supstock', methods=['POST', 'GET'])
def update_supstock():
    if request.method == 'POST':
        # Retrieve form data
        stock_id = request.form['id']
        manufacturer_name = request.form.get('manufacturer_name')
        supplier_name = request.form.get('SupplierName')
         # Updated to match the actual column name
        remarks = request.form.get('Remarks')
        date = request.form.get('date')

        # Ensure the date is not in the future
        if datetime.strptime(date, '%Y-%m-%d').date() > datetime.today().date():
            flash("Error: Date cannot be in the future!", 'danger')
            return redirect(url_for('mng_supp'))

        # Database connection
        try:
            mydb = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="Omnipro"
            )
            mycursor = mydb.cursor()

            # Update SQL query
            sql = """
                UPDATE manufacturer_supplier_stock 
                SET manufacturer_name=%s, supplier_name=%s,  remarks=%s, date=%s  
                WHERE stock_id=%s
            """
            val = (manufacturer_name, supplier_name, remarks, date, stock_id)
            mycursor.execute(sql, val)
            mydb.commit()

            flash("Data Updated Successfully", 'success')

        except mysql.connector.Error as e:
            flash(f"Database error: {str(e)}", 'danger')

        finally:
            if 'mycursor' in locals():
                mycursor.close()
            if 'mydb' in locals():
                mydb.close()

        return redirect(url_for('mng_supp'))

    # If GET request, calculate max_date for the date input
    max_date = datetime.today().strftime('%Y-%m-%d')  # Limit date input to today's date
    return render_template('mng_supp.html', max_date=max_date)



    

@app.route('/process', methods=['POST'])
def process():
    selected_tests = request.form.getlist('Course')
    test_credits = request.form.getlist('Fee')
    for test_id, credits in zip(selected_tests, test_credits):
        # Process the selected tests and their corresponding credits
        # Here you can update your database with the selected tests and credits
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("insert into addcolleges( Course, Fee)values('%s','%s')"%( test_id , credits))
        conn.commit()
        cursor.close()
        conn.close()
        # For demonstration, I'm just printing them
        print(f"Test ID: {test_id}, Credits: {credits}")
    return redirect(url_for('Manfactured'))


@app.route('/search', methods=['POST'])
def search():
    try:
        token = request.json.get('token')

        # Fetch data from MySQL
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT studentName, phone,applied_test FROM studentregistration WHERE token_number = %s", [token])
        patient_data = cursor.fetchone()
        cursor.execute("SELECT applied_test FROM studentregistration WHERE token_number = %s", [token])
        tests_data = cursor.fetchall()
        cursor.close()

        if patient_data:
            studentName, phone,applied_test = patient_data
            tests = [test[0] for test in tests_data]
            return jsonify({'studentName': studentName, 'phone': phone, 'applied_test': applied_test})
        else:
            return jsonify({'error': 'Patient not found!'})
    except Exception as e:
        return jsonify({'error': str(e)})
    
    


@app.route('/staff/<role>')
def get_staff(role):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT StaffName FROM managestaff WHERE StaffRole = %s", (role,))
    staff_names = [row[0] for row in cursor.fetchall()]
    cursor.close()
    return ', '.join(staff_names)

@app.route('/update_test', methods=['POST'])
def update_test():
    selected_test = request.form['Tests']
    credits = request.form['credits']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO addcolleges (Course,fee) VALUES (%s,%s)", (selected_test,credits))
    cursor.commit()
    cursor.close()
    
    cursor = conn.cursor()
    cursor.execute("SELECT CourseName,credits FROM addcourses")
    credits_data = cursor.fetchall()
    cursor.close()
    
    return jsonify(credits_data)

@app.route('/manage_colleges', methods=['GET', 'POST'])
def manage_colleges():
    if request.method == 'POST':
        username = request.form['StaffName']
        password = request.form['Password']

        conn = get_db_connection()
        cursor = conn.cursor()
        query = "SELECT StaffRole, StaffName FROM managestaff WHERE StaffName = %s AND Password = %s"
        cursor.execute(query, (username, password))
        user = cursor.fetchone()

        if user:
            session['doctor_name'] = user[2]
            session['user_role'] = user[3]
            return redirect('/manage_colleges')
    
    user_role = session.get('user_role')
    doctor_name = session.get('SatffName')  # Assuming doctor_id is stored in session

    conn = get_db_connection()
    cursor = conn.cursor()

    if user_role == 'admin':
        query = "SELECT * FROM addcolleges"  # Admin can see all doctors
    elif user_role == 'Referring Doctor':
        query = """
            SELECT * FROM addcolleges
            WHERE doctor_name = %s
        """
        cursor.execute(query, (doctor_name,))
    else:
        # Default case, adjust as needed
        query = "SELECT * FROM addcolleges WHERE 1=0"

    cursor.execute(query)
    addcolleges = cursor.fetchall()

    cursor.close()
    conn.close()


   

    return render_template('manage_colleges.html',addcolleges=addcolleges)








@app.route('/SupplierQuotation', methods=['GET', 'POST'])
def SupplierQuotation():
    mydb = get_db_connection()
    mycursor = mydb.cursor(buffered=True)

    if request.method == 'POST':
        try:
            # Capture form inputs
            supplier_name = request.form['manfacturename']
            rfq_date = request.form['supplierrfqdate']
            if datetime.strptime(rfq_date, '%Y-%m-%d').date() > datetime.today().date():
                return "Error: Date cannot be in the future!", 400
            quote_date = request.form['supplierquotedate']
            supplier_contact = request.form['Suppliercontact']
            remarks = request.form['remarks']

            # Insert supplier quote details
            supplier_quote_query = """
            INSERT INTO supplier_quote (supplier_name, rfq_date, quote_date, supplier_contact, remarks)
            VALUES (%s, %s, %s, %s, %s)
            """
            supplier_quote_values = (supplier_name, rfq_date, quote_date, supplier_contact, remarks)
            mycursor.execute(supplier_quote_query, supplier_quote_values)
            mydb.commit()

            # Get the last inserted supplier_quote ID
            supplier_quote_id = mycursor.lastrowid

            # Insert RFQ items from the form
            part_nos = request.form.getlist('quotedpart[]')
            makes = request.form.getlist('quotedmake[]')
            quantity_requested = request.form.getlist('quotedrequest[]')
            stocks = request.form.getlist('stock[]')
            prices = request.form.getlist('price[]')
            items = request.form.getlist('item[]')
            details = request.form.getlist('quotedetails[]')
            item_remarks = request.form.getlist('remarks[]')

            for i in range(len(part_nos)):
                # Check if the exact row already exists in the database
                check_duplicate_query = """
                SELECT COUNT(*) FROM supplier_quote_rfq
                WHERE supplier_name = %s AND part_no = %s AND make = %s AND quantity_requested = %s
                AND stock = %s AND price = %s AND item = %s AND details = %s AND remarks = %s
                """
                mycursor.execute(check_duplicate_query, (supplier_name, part_nos[i], makes[i], quantity_requested[i], stocks[i], prices[i], items[i], details[i], item_remarks[i]))
                duplicate_count = mycursor.fetchone()[0]

                # If no duplicate is found, insert the row
                if duplicate_count == 0:
                    rfq_item_query = """
                    INSERT INTO supplier_quote_rfq (supplier_name, part_no, make, quantity_requested, stock, price, item, details, remarks)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    rfq_item_values = (supplier_name, part_nos[i], makes[i], quantity_requested[i], stocks[i], prices[i], items[i], details[i], item_remarks[i])
                    mycursor.execute(rfq_item_query, rfq_item_values)

            # Process file upload (Excel data)
            if 'file' in request.files:
                file = request.files['file']
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)

                    # Read Excel file using pandas
                    df = pd.read_excel(filepath)

                    # Ensure the Excel file contains the required columns
                    required_columns = ['part_no', 'quoted_make', 'quantity_requested', 'supplier_stock', 'unit_price', 'items_value', 'quote_details', 'remarks']
                    if not all(col in df.columns for col in required_columns):
                        missing_columns = [col for col in required_columns if col not in df.columns]
                        flash(f'Excel file must contain the following columns: {", ".join(missing_columns)}', 'error')
                        return redirect(url_for('SupplierQuotation'))

                    # Loop through each row in the Excel file and insert into the database
                    for index, row in df.iterrows():
                        part_no = str(row['part_no']).strip().upper()
                        make = str(row['quoted_make']).strip().upper()
                        quantity_requested = str(row['quantity_requested']).strip().upper()
                        supplier_stock = str(row['supplier_stock']).strip()
                        unit_price = str(row['unit_price']).strip()
                        items_value = str(row['items_value']).strip()
                        quote_details = str(row['quote_details']).strip()
                        remark = str(row['remarks']).strip()

                        # Check for duplicates before inserting
                        check_duplicate_query = """
                        SELECT COUNT(*) FROM supplier_quote_rfq
                        WHERE supplier_name = %s AND part_no = %s AND make = %s AND quantity_requested = %s
                        AND stock = %s AND price = %s AND item = %s AND details = %s AND remarks = %s
                        """
                        mycursor.execute(check_duplicate_query, (supplier_name, part_no, make, quantity_requested, supplier_stock, unit_price, items_value, quote_details, remark))
                        duplicate_count = mycursor.fetchone()[0]

                        # If no duplicate is found, insert the row
                        if duplicate_count == 0:
                            rfq_item_query = """
                            INSERT INTO supplier_quote_rfq (supplier_name, part_no, make, quantity_requested, stock, price, item, details, remarks)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """
                            mycursor.execute(rfq_item_query, (supplier_name, part_no, make, quantity_requested, supplier_stock, unit_price, items_value, quote_details, remark))

            mydb.commit()
            flash('Successfully added supplier quotation and items!', 'success')
            return redirect(url_for('SupplierQuotation'))

        except Exception as e:
            print(f"Error inserting data: {str(e)}")
            mydb.rollback()
            flash('An error occurred while processing your request. Please try again.', 'error')

    # Fetch supplier names for the GET request
    mycursor.execute("SELECT supplier_name FROM suppliers WHERE sub_type = 'manufacturer';")
    suppliers = mycursor.fetchall()

    # Fetch previously inserted supplier quotations for display
    mycursor.execute("SELECT * FROM supplier_quote")
    SupplierQuotation = mycursor.fetchall()
    mycursor.execute("SELECT contact_person FROM contact")
    contact = mycursor.fetchall()
    max_date = datetime.today().strftime('%Y-%m-%d')

    search_query = request.args.get('search', '')
    page = int(request.args.get('page', 1))
    per_page = 10
    offset = (page - 1) * per_page
    
    mycursor.execute("SELECT COUNT(*) FROM supplier_quote WHERE supplier_name LIKE %s OR rfq_date LIKE %s OR quote_date LIKE %s", (f'{search_query}%',f'{search_query}%',f'{search_query}%'))
    total_customers = mycursor.fetchone()[0]
    
    mycursor.execute("SELECT * FROM supplier_quote WHERE supplier_name LIKE %s OR rfq_date LIKE %s OR quote_date LIKE %s   ORDER BY id DESC LIMIT %s OFFSET %s",
                   (f'{search_query}%',f'{search_query}%',f'{search_query}%', per_page, offset))
    SupplierQuotation = mycursor.fetchall()

    mycursor.close()
    mydb.close()
    
    total_pages = (total_customers + per_page - 1) // per_page


    return render_template('SupplierQuotation.html',contact=contact,max_date=max_date, SupplierQuotation=SupplierQuotation, suppliers=suppliers,page=page, per_page=per_page, total_pages=total_pages, search_query=search_query)





@app.route('/add_supplierquo', methods=['POST'])
def add_supplierquo():
    mydb = get_db_connection()  # Establish DB connection
    mycursor = mydb.cursor(buffered=True)
    error = None

    if request.method == 'POST':
        # Get form data
        supplier_name = request.form['supplier_name']
        part_no = request.form['part_no']  # Ensure this matches the column name in your form and table
        make = request.form['make']
        quantity_requested = request.form['quantity_requested']
        stock = request.form['stock']
        price = request.form['price']
        item = request.form['item']
        details = request.form['details']
        remarks = request.form['remarks']

        # Check if the exact row already exists
        check_query = """
            SELECT COUNT(*) FROM supplier_quote_rfq 
            WHERE supplier_name = %s AND part_no = %s AND make = %s AND quantity_requested = %s 
            AND stock = %s AND price = %s AND item = %s AND details = %s AND remarks = %s
        """
        
        values = (supplier_name, part_no, make, quantity_requested, stock, price, item, details, remarks)
        mycursor.execute(check_query, values)
        result = mycursor.fetchone()[0]  # Fetch the result of the query

        if result == 0:  # No duplicate found, so insert the new record
            try:
                # Insert the new record
                insert_query = """
                    INSERT INTO supplier_quote_rfq(supplier_name, part_no, make, quantity_requested, stock, price, item, details, remarks)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                mycursor.execute(insert_query, values)
                mydb.commit()  # Commit the transaction
                flash('Supplier quote added successfully.', 'success')
            except mysql.connector.IntegrityError as ie:
                error = f"Error inserting record: {str(ie)}"
                flash(error, 'danger')
            except Exception as e:
                error = f"An unexpected error occurred: {str(e)}"
                flash(error, 'danger')
        else:  # Duplicate record found
            flash('This supplier quote already exists in the database.', 'warning')

        mycursor.close()  # Close the cursor
        mydb.close()  # Close the database connection

        # Redirect back to the appropriate page after the operation
        return redirect(url_for('SupplierQuotation'))

    # If not a POST request, render the Supplier Quotation form/page
    return render_template('SupplierQuotation.html')


@app.route('/add_supplier_quote_excel', methods=['GET', 'POST'])
def add_supplier_quote_excel():
    mydb = get_db_connection()
    mycursor = mydb.cursor(buffered=True)
    error = None
    supplier_name = request.form.get('manufacture_name')

    if request.method == 'POST':
        if 'file' in request.files:
            file = request.files['file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)

                # Read the Excel file using pandas
                df = pd.read_excel(filepath)

                # Ensure the Excel file contains the required columns
                required_columns = ['part_no', 'quoted_make', 'quantity_requested', 'supplier_stock', 'unit_price', 'items_value', 'quote_details', 'remarks']
                if not all(col in df.columns for col in required_columns):
                    missing_columns = [col for col in required_columns if col not in df.columns]
                    flash(f'Excel file must contain the following columns: {", ".join(missing_columns)}', 'error')
                    return redirect(url_for('SupplierQuotation'))

                # Iterate over each row in the Excel file and insert into the database
                for index, row in df.iterrows():
                    part_no = str(row['part_no']).strip().upper()
                    quoted_make = str(row['quoted_make']).strip().upper()
                    quantity_requested = str(row['quantity_requested']).strip()
                    supplier_stock = str(row['supplier_stock']).strip()
                    unit_price = str(row['unit_price']).strip()
                    items_value = str(row['items_value']).strip()
                    quote_details = str(row['quote_details']).strip()
                    remarks = str(row['remarks']).strip()

                    # Check for duplicates before inserting
                    check_duplicate_query = """
                    SELECT COUNT(*) FROM supplier_quote_rfq
                    WHERE supplier_name = %s AND part_no = %s AND make = %s AND quantity_requested=%s
                    AND stock = %s AND price = %s AND item = %s AND details = %s AND remarks = %s
                    """
                    mycursor.execute(check_duplicate_query, (supplier_name, part_no, quoted_make, quantity_requested,
                                                             supplier_stock, unit_price, items_value, quote_details, remarks))
                    duplicate_count = mycursor.fetchone()[0]

                    # Insert if no duplicate is found
                    if duplicate_count == 0:
                        insert_query = """
                        INSERT INTO supplier_quote_rfq (supplier_name, part_no, make, quantity_requested, stock, price, item, details, remarks)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """
                        mycursor.execute(insert_query, (supplier_name, part_no, quoted_make, quantity_requested,
                                                        supplier_stock, unit_price, items_value, quote_details, remarks))

                mydb.commit()
                flash('Supplier quotation items added successfully!', 'success')
            else:
                flash('Invalid file type. Please upload a valid Excel file.', 'error')
        else:
            flash('No file uploaded. Please select a file.', 'error')

    mycursor.close()
    mydb.close()
    return redirect(url_for('SupplierQuotation'))




@app.route('/manage_supquo', methods=['GET'])
def manage_supquo():
    conn = get_db_connection()
    cursor = conn.cursor()
   
    que = 'SELECT *FROM supplier_quote_rfq'
    cursor.execute(que)
    supplier_quote_rfq = cursor.fetchall()
    customer = 'SELECT *FROM supplier_quote'
    cursor.execute(customer)
    customers = cursor.fetchall()

    
    search_query = request.args.get('search', '')
    page = int(request.args.get('page', 1))
    per_page = 10
    offset = (page - 1) * per_page

    # Count total matching records for pagination
    cursor.execute("""
        SELECT COUNT(*) FROM supplier_quote_rfq 
        WHERE supplier_name LIKE %s OR part_no LIKE %s 
    """, (f'{search_query}%', f'{search_query}%'))
    total_contacts = cursor.fetchone()[0]

    # Fetch matching records with pagination
    cursor.execute("""
        SELECT * FROM supplier_quote_rfq 
        WHERE supplier_name LIKE %s OR part_no LIKE %s 
        ORDER BY id DESC, part_no   ASC 
        LIMIT %s OFFSET %s
    """, (f'{search_query}%', f'{search_query}%', per_page, offset))
    supplier_quote_rfq = cursor.fetchall()

    cursor.close()
    conn.close()

    total_pages = (total_contacts + per_page - 1) // per_page

    return render_template('manage_supquo.html',supplier_quote_rfq=supplier_quote_rfq,customers=customers,  page=page, per_page=per_page, total_pages=total_pages, search_query=search_query)





    


@app.route('/delete_supplierquotation/<int:id>')
def delete_supplierquotation(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Execute DELETE operation
        cursor.execute("DELETE FROM supplier_quote WHERE id = %s", (id,))
        conn.commit()

        cursor.close()
        conn.close()

        flash('Record has been deleted successfully', 'success')
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')

    return redirect(url_for('SupplierQuotation'))


@app.route('/update_supplierquotation', methods=['POST'])
def update_supplierquotation():
    if request.method == 'POST':
        # Fetch form data
        id = request.form['id']
        manfacturename = request.form.get('manfacturename')
        supplierrfqdate = request.form.get('supplierrfqdate')
        supplierquotedate = request.form.get('supplierquotedate')
        Suppliercontact = request.form.get('Suppliercontact')
        remarks = request.form.get('remarks')
        
        # Database connection
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="Omnipro"
        )
        mycursor = mydb.cursor()

        # Update SQL query
        sql = """UPDATE supplier_quote 
                 SET supplier_name=%s, rfq_date=%s, quote_date=%s, supplier_contact=%s, remarks=%s 
                 WHERE id=%s"""
        val = (manfacturename, supplierrfqdate, supplierquotedate, Suppliercontact, remarks, id)
        mycursor.execute(sql, val)
        mydb.commit()

        # Close cursor and database connection
        mycursor.close()
        mydb.close()

        flash("Data Updated Successfully", "success")
    
    return redirect(url_for('SupplierQuotation'))




@app.route('/delete_sup_quote_rfq/<int:id>')
def delete_sup_quote_rfq(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Execute DELETE operation
        cursor.execute("DELETE FROM supplier_quote_rfq WHERE id = %s", (id,))
        conn.commit()

        cursor.close()
        conn.close()

        flash('Record has been deleted successfully', 'success')
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')

    return redirect(url_for('manage_supquo'))


@app.route('/update_supquorfq', methods=['POST'])
def update_supquorfq():
    if request.method == 'POST':
        id = request.form['id']
        suppliername = request.form['suppliername']
        part_no = request.form['part_no']
        make = request.form.get('make')
        requested = request.form.get('request')  # Renamed to avoid conflict
        stock = request.form.get('stock')
        price = request.form.get('price')
        item = request.form['item']
        details = request.form.get('details')
        remarks = request.form.get('remarks')
      
        # Database connection
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="Omnipro"
        )
        mycursor = mydb.cursor()

        # Update SQL query
        sql = """UPDATE supplier_quote_rfq 
                 SET supplier_name=%s, part_no=%s, make=%s, request=%s, 
                     stock=%s, price=%s, item=%s, details=%s, remarks=%s 
                 WHERE id=%s"""
        val = (suppliername, part_no, make, requested, stock, price, item, details, remarks, id)
        mycursor.execute(sql, val)
        mydb.commit()

        # Close cursor and database connection
        mycursor.close()
        mydb.close()

        flash("Data Updated Successfully")

    return redirect(url_for('manage_supquo'))


@app.route('/CustomerQuotation', methods=['GET', 'POST'])
def CustomerQuotation():
    mydb = get_db_connection()
    mycursor = mydb.cursor(buffered=True)

    if request.method == 'POST':
        try:
            # Capture form inputs
            customer_name = request.form['customer_name']
            rfq_date = request.form['customerrfqdate']
            quote_date = request.form['customerquotedate']
            customercontact = request.form['customercontact']
            remarks = request.form['remarks']

            # Check for invalid date (RFQ date cannot be in the future)
            if datetime.strptime(rfq_date, '%Y-%m-%d').date() > datetime.today().date():
                return "Error: RFQ date cannot be in the future!", 400

            # Insert customer quote details into customer_quote
            customer_quote_query = """
            INSERT INTO customer_quote(customer_name, rfq_date, quote_date, customer_contact, remarks)
            VALUES (%s, %s, %s, %s, %s)
            """
            customer_quote_values = (customer_name, rfq_date, quote_date, customercontact, remarks)
            mycursor.execute(customer_quote_query, customer_quote_values)
            mydb.commit()

            # Get the last inserted customer_quote ID
            customer_quote_id = mycursor.lastrowid
            print(f"Inserted customer_quote with ID: {customer_quote_id}")

            # Insert RFQ items from the form (dynamic data)
            part_nos = request.form.getlist('quotedpart[]')
            makes = request.form.getlist('quotedmake[]')
            quantity_requested = request.form.getlist('quotedrequest[]')
            stocks = request.form.getlist('stock[]')
            prices = request.form.getlist('price[]')
            items = request.form.getlist('item[]')
            details = request.form.getlist('quotedetails[]')
            item_remarks = request.form.getlist('remarks[]')

            print(f"Part Nos: {part_nos}, Makes: {makes}, Quantities: {quantity_requested}")

            for i in range(len(part_nos)):
                # Check for duplicates before inserting
                check_duplicate_query = """
                SELECT COUNT(*) FROM customer_quote_rfq
                WHERE customer_name = %s AND part_no = %s AND make = %s AND quantity_requested = %s
                AND stock = %s AND price = %s AND item = %s AND details = %s AND remarks = %s
                """
                mycursor.execute(check_duplicate_query, (customer_name, part_nos[i], makes[i], quantity_requested[i], stocks[i], prices[i], items[i], details[i], item_remarks[i]))
                duplicate_count = mycursor.fetchone()[0]

                if duplicate_count == 0:
                    rfq_item_query = """
                    INSERT INTO customer_quote_rfq(customer_name, part_no, make, quantity_requested, stock, price, item, details, remarks)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    mycursor.execute(rfq_item_query, (customer_name, part_nos[i], makes[i], quantity_requested[i], stocks[i], prices[i], items[i], details[i], item_remarks[i]))

            # Process file upload (Excel data)
            if 'file' in request.files:
                file = request.files['file']
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)

                    # Read Excel file using pandas
                    df = pd.read_excel(filepath)

                    required_columns = ['part_no', 'quoted_make', 'quantity_requested', 'supplier_stock', 'unit_price', 'items_value', 'quote_details', 'remarks']
                    if not all(col in df.columns for col in required_columns):
                        missing_columns = [col for col in required_columns if col not in df.columns]
                        flash(f'Missing columns in Excel: {", ".join(missing_columns)}', 'error')
                        return redirect(url_for('CustomerQuotation'))

                    for index, row in df.iterrows():
                        part_no = str(row['part_no']).strip().upper()
                        make = str(row['quoted_make']).strip().upper()
                        quantity_requested = str(row['quantity_requested']).strip().upper()
                        supplier_stock = str(row['supplier_stock']).strip()
                        unit_price = str(row['unit_price']).strip()
                        items_value = str(row['items_value']).strip()
                        quote_details = str(row['quote_details']).strip()
                        remark = str(row['remarks']).strip()

                        check_duplicate_query = """
                        SELECT COUNT(*) FROM customer_quote_rfq
                        WHERE customer_name = %s AND part_no = %s AND make = %s AND quantity_requested = %s
                        AND stock = %s AND price = %s AND item = %s AND details = %s AND remarks = %s
                        """
                        mycursor.execute(check_duplicate_query, (customer_name, part_no, make, quantity_requested, supplier_stock, unit_price, items_value, quote_details, remark))
                        duplicate_count = mycursor.fetchone()[0]

                        if duplicate_count == 0:
                            rfq_item_query = """
                            INSERT INTO customer_quote_rfq (customer_name, part_no, make, quantity_requested, stock, price, item, details, remarks)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """
                            mycursor.execute(rfq_item_query, (customer_name, part_no, make, quantity_requested, supplier_stock, unit_price, items_value, quote_details, remark))

            mydb.commit()
            flash('Successfully added customer quotation and items!', 'success')
            return redirect(url_for('CustomerQuotation'))

        except Exception as e:
            print(f"Error inserting data: {str(e)}")
            mydb.rollback()
            flash('An error occurred while processing your request. Please try again.', 'error')

    # Fetch supplier names for the GET request
    mycursor.execute("SELECT supplier_name FROM suppliers WHERE sub_type = 'manufacturer';")
    suppliers = mycursor.fetchall()

    # Fetch previously inserted customer quotations for display
    mycursor.execute("SELECT * FROM customer_quote")
    CustomerQuotation = mycursor.fetchall()

    max_date = datetime.today().strftime('%Y-%m-%d')

    search_query = request.args.get('search', '')
    page = int(request.args.get('page', 1))
    per_page = 10
    offset = (page - 1) * per_page

    # Correct the table reference in the count query
    mycursor.execute("SELECT COUNT(*) FROM customer_quote WHERE customer_name LIKE %s OR rfq_date LIKE %s OR quote_date LIKE %s", (f'{search_query}%', f'{search_query}%', f'{search_query}%'))
    total_customers = mycursor.fetchone()[0]

    mycursor.execute("SELECT DISTINCT customer_name FROM contacts")
    customers = mycursor.fetchall()

    mycursor.execute("SELECT distinct contact_person FROM contacts")
    contacts = mycursor.fetchall()

    mycursor.execute("SELECT * FROM customer_quote WHERE customer_name LIKE %s OR rfq_date LIKE %s OR quote_date LIKE %s ORDER BY id DESC LIMIT %s OFFSET %s",
                     (f'{search_query}%', f'{search_query}%', f'{search_query}%', per_page, offset))
    CustomerQuotation = mycursor.fetchall()

    mycursor.close()
    mydb.close()

    total_pages = (total_customers + per_page - 1) // per_page

    return render_template('CustomerQuotation.html', CustomerQuotation=CustomerQuotation, customers=customers, contacts=contacts, max_date=max_date,suppliers=suppliers, page=page, per_page=per_page, total_pages=total_pages, search_query=search_query)



@app.route('/manage_cusquo', methods=['GET'])
def manage_cusquo():
    conn = get_db_connection()
    cursor = conn.cursor()
   
    que = 'SELECT *FROM customer_quote_rfq'
    cursor.execute(que)
    customer_quote_rfq = cursor.fetchall()
    customer = 'SELECT *FROM customer_quote'
    cursor.execute(customer)
    customers = cursor.fetchall()

    
    search_query = request.args.get('search', '')
    page = int(request.args.get('page', 1))
    per_page = 10
    offset = (page - 1) * per_page

    # Count total matching records for pagination
    cursor.execute("""
        SELECT COUNT(*) FROM customer_quote_rfq 
        WHERE customer_name LIKE %s OR part_no LIKE %s 
    """, (f'{search_query}%', f'{search_query}%'))
    total_contacts = cursor.fetchone()[0]

    # Fetch matching records with pagination
    cursor.execute("""
        SELECT * FROM customer_quote_rfq 
        WHERE customer_name LIKE %s OR part_no LIKE %s 
        ORDER BY id DESC, part_no   ASC 
        LIMIT %s OFFSET %s
    """, (f'{search_query}%', f'{search_query}%', per_page, offset))
    customer_quote_rfq = cursor.fetchall()

    cursor.close()
    conn.close()

    total_pages = (total_contacts + per_page - 1) // per_page

    return render_template('manage_cusquo.html',customer_quote_rfq=customer_quote_rfq,customers=customers,  page=page, per_page=per_page, total_pages=total_pages, search_query=search_query)





@app.route('/Add_invoices', methods=['GET', 'POST'])
def Add_invoices():
    mydb=mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="Omnipro"
    )
    mycursor=mydb.cursor() 
    if request.method == 'POST':
        # Retrieve form data
        invoice_no = request.form.get('invoice_No')
        patient_name = request.form.get('PatientName')
        token_number = request.form.get('TokenNumber')
        invoice_date = request.form.get('invoice_Date')
        phone_number = request.form.get('PhoneNumber')
        test = request.form.get('Course')
        price = request.form.get('Amount')
        discount = request.form.get('discount')
        total_amount = request.form.get('totalamount')
        #GrandTotal= request.form['GrandTotal']
        # GST=request.form['GST']
        # DueAmount=request.form['DueAmount']
        # DueDate=request.form['DueDate']
        # PaidAmount=request.form['PaidAmount']
        # PaymentStaus=request.form['PaymentStaus']
        # PaymentType=request.form['PaymentType']
        
        mycursor.execute("insert into addinvoices(invoice_No,PatientName,TokenNumber,invoice_Date,PhoneNumber,Course, Amount,discount,totalamount)values('%s','%s','%s','%s','%s','%s','%s','%s','%s')"%(invoice_No,PatientName,TokenNumber,invoice_Date,PhoneNumber,Course, Amount,discount,totalamount))
        mydb.commit()
        mycursor.close()
        return render_template('Add_invoices.html')
    else:
        # If the request method is not POST, render the form template
         # Connect to the database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT ID, CourseName FROM addcourses")
        course_data = cursor.fetchall()
        cursor.close()
        conn.close()
        
    return render_template('Add_invoices.html',course_data=course_data)


@app.route('/get_test_price', methods=['POST'])
def get_test_price():
    test_name = request.form.get('CourseName')
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT price FROM addcourses WHERE CourseName = %s", (test_name,))
    test = cursor.fetchone()
    cursor.close()
    connection.close()
    return jsonify({'price': test['price'] if test else 0})

@app.route('/manage_invoices', methods=['GET'])
def manage_invoices():
    conn = get_db_connection()
    cursor = conn.cursor()
    query7 = 'SELECT invoice_No,PatientName,TokenNumber,invoice_Date,PhoneNumber,Course, Amount,discount,totalamount FROM addinvoices'
    cursor.execute(query7)
    addinvoices = cursor.fetchall()
    conn.commit()
    cursor.close()
    conn.close()
    return render_template('manage_invoices.html', addinvoices =addinvoices)





@app.route('/get_suppliers')
def get_suppliers():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT employeename FROM employee where status=1")
    suppliers = cursor.fetchall()
    cursor.close()
    db.close()
    return jsonify(suppliers)


    
@app.route('/Customers', methods=['GET', 'POST'])
def Customers():
    if request.method == 'POST':
        customername = request.form['customername']
        branch = request.form['branch']
        city = request.form['city']
        contactnumber = request.form['contactnumber']
        contactfax = request.form['contactfax']
        website = request.form['website']
        pincode = request.form['pincode']
        address = request.form['address']
        customerprofile = request.form['customerprofile']
        remarks = request.form['remarks']
        products = request.form['products']
        applications = request.form['applications']

        contacts = []
        failed_rows = []
        inserted_rows = 0

        # Process form data
        contact_count = int(request.form.get('contact_count', 1))
        for i in range(1, contact_count + 1):
            contact_name = request.form.get(f'contact_name_{i}', '')
            contact_number = request.form.get(f'contact_number_{i}', '')
            contact_dep = request.form.get(f'contact_dep_{i}', '')
            contact_whats = request.form.get(f'contact_whats_{i}', '')
            contact_email = request.form.get(f'contact_email_{i}', '')
            contact_skype = request.form.get(f'contact_skype_{i}', '')
            contact_added = request.form.get(f'contact_added_{i}', '')
            contact_date = request.form.get(f'contact_date_{i}', '')

            if contact_name and contact_number and contact_dep and contact_whats and contact_email and contact_skype and contact_added and contact_date:
                contacts.append((contact_name, contact_number, contact_dep, contact_whats, contact_email, contact_skype, contact_added, contact_date))
            else:
                failed_rows.append(f'Form row {i}')  # Store row number as a string

        # Process file upload
        if 'file' in request.files:
            file = request.files['file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)

                df = pd.read_excel(filepath)
                valid_number_pattern = re.compile(r'^[0-9\+\-]{10,16}$')
                employee_names = get_employee_names()

                # Track already inserted rows to avoid duplicates
                inserted_contacts = set()

                for index, row in df.iterrows():
                    # Adjust row index for actual Excel row number (starting from 2)
                    row_number = index + 2
                    contact_name = str(row['contact_person']).strip().upper()
                    contact_number = str(row['contact_number']).strip()
                    whatsapp_number = str(row['whatsapp']).strip()
                    email = str(row['email']).strip()
                    added_by = str(row['added_by']).strip().upper()
                    department = str(row['department']).strip().upper()
                    skype = str(row['skype']).strip()
                    date = str(row['date']).strip()

                    # Check for duplicates based on a combination of relevant fields
                    contact_identifier = (contact_name, contact_number, department, whatsapp_number, email, skype, added_by, date)
                    
                    if (valid_number_pattern.match(contact_number) and 
                        valid_number_pattern.match(whatsapp_number) and 
                        email.endswith('@gmail.com') and
                        added_by in employee_names and
                        contact_identifier not in inserted_contacts):

                        contacts.append(contact_identifier)
                        inserted_contacts.add(contact_identifier)  # Mark as inserted
                        inserted_rows += 1
                    else:
                        failed_rows.append(f'{row_number}')  # Store actual row number

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO customers (customer_name, branch, city, contact_number, contact_fax, website, pincode, address, customer_profile, remarks, products, applications) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (customername, branch, city, contactnumber, contactfax, website, pincode, address, customerprofile, remarks, products, applications)
            )
            customer_id = cursor.lastrowid
            
            for contact in contacts:
                cursor.execute(
                    "INSERT INTO contacts (customer_name, contact_person, contact_number, department, whatsapp, email, skype, added_by, date) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (customername, contact[0], contact[1], contact[2], contact[3], contact[4], contact[5], contact[6], contact[7])
                )
            
            conn.commit()
            flash(f'Successfully inserted {inserted_rows} rows. Rows not inserted: {", ".join(failed_rows)}', 'success')
        except mysql.connector.Error as err:
            if err.errno == 1062:
                flash('Duplicate entry found. Please check the details and try again.', 'danger')
            else:
                flash('An error occurred while adding the customer. Please try again.', 'danger')
            conn.rollback()
        finally:
            cursor.close()
            conn.close()

        return redirect(url_for('Customers'))

    # Handle GET request
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM branch ORDER BY id DESC")
    value = cursor.fetchall()
    cursor.execute("SELECT * FROM city ORDER BY id DESC")
    data = cursor.fetchall()
    cursor.execute("SELECT * FROM employee where status=1")
    employee = cursor.fetchall()
    
    search_query = request.args.get('search', '')
    page = int(request.args.get('page', 1))
    per_page = 10
    offset = (page - 1) * per_page
    
    cursor.execute("SELECT COUNT(*) FROM customers WHERE customer_name LIKE %s", (f'{search_query}%',))
    total_customers = cursor.fetchone()[0]
    
    cursor.execute("SELECT * FROM customers WHERE customer_name LIKE %s ORDER BY id DESC LIMIT %s OFFSET %s",
                   (f'{search_query}%', per_page, offset))
    customers = cursor.fetchall()

    cursor.close()
    conn.close()
    
    total_pages = (total_customers + per_page - 1) // per_page

    return render_template('Customers.html', customers=customers, value=value, data=data, employee=employee, page=page, per_page=per_page, total_pages=total_pages, search_query=search_query)


def get_employee_names():
    """Fetch the list of employee names from the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT employeename FROM employee")
    employee_names = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return employee_names

@app.route('/export_data')
def export_data():
    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch data from the first table (customers)
    query1 = "SELECT * FROM customers"
    cursor.execute(query1)
    rows1 = cursor.fetchall()
    columns1 = [i[0] for i in cursor.description]
    
    # Debugging: Print fetched data and column names
    print("Columns from 'customers' table:", columns1)
    print("Rows from 'customers' table:", rows1)
    
    # Check if rows1 is empty
    if not rows1:
        print("No data found in 'customers' table.")

    # Create DataFrame for customers and drop the 'id' column
    df1 = pd.DataFrame(rows1, columns=columns1).drop(columns=['id','excel_file'], errors='ignore')

    # Fetch data from the second table (contacts)
    query2 = "SELECT * FROM contacts"
    cursor.execute(query2)
    rows2 = cursor.fetchall()
    columns2 = [i[0] for i in cursor.description]
    
    # Debugging: Print fetched data and column names
    print("Columns from 'contacts' table:", columns2)
    print("Rows from 'contacts' table:", rows2)
    
    # Check if rows2 is empty
    if not rows2:
        print("No data found in 'contacts' table.")

    # Create DataFrame for contacts and drop the 'id' column
    df2 = pd.DataFrame(rows2, columns=columns2).drop(columns=['id'], errors='ignore')

    # Close the cursor and connection
    cursor.close()
    conn.close()

    # Convert date columns to datetime if necessary
    if 'Date' in df2.columns:
        df2['Date'] = pd.to_datetime(df2['Date'], errors='coerce').dt.date

    # Export data to Excel with multiple sheets
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df1.to_excel(writer, sheet_name='Customers', index=False)
        df2.to_excel(writer, sheet_name='Contacts', index=False)

        # Access the xlsxwriter workbook and worksheets
        workbook = writer.book
        contact_sheet = writer.sheets['Contacts']

        # Define a date format for Excel (day-month-year)
        date_format = workbook.add_format({'num_format': 'dd-mm-yyyy'})

        # Apply date formatting to columns if 'Date' exists
        for col_num, col_name in enumerate(df2.columns):
            if pd.api.types.is_datetime64_any_dtype(df2[col_name]) or (df2[col_name].dtype == 'object' and col_name.lower() == 'date'):
                contact_sheet.set_column(col_num, col_num, 20, date_format)

    # Prepare response
    output.seek(0)  # Ensure to seek back to the start of the BytesIO object
    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=Customers-Data.xlsx"
    response.headers["Content-type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    return response

@app.route('/add_branch', methods=['POST'])
def add_branch():
    branch_name = request.form.get('branchName')
    
    if branch_name:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO branch (branch_name) VALUES (%s)", [branch_name])
        conn.commit()
        cursor.close()
        return jsonify(success=True, branch_name=branch_name)
    return jsonify(success=False), 400

@app.route('/add_expense', methods=['POST'])
def add_expense():
    expense_type_name = request.form.get('expenseTypeName')
    
    if expense_type_name:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO expense_type (type) VALUES (%s)", [expense_type_name])
        conn.commit()
        cursor.close()
        return jsonify(success=True, expense_type_name=expense_type_name)
    return jsonify(success=False), 400

@app.route('/add_source', methods=['POST'])
def add_source():
    source_name = request.form.get('sourceName')

    if source_name:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO source (source) VALUES (%s)", [source_name])
        conn.commit()
        cursor.close()
        return jsonify(success=True, source_name=source_name)
    return jsonify(success=False), 400
    
@app.route('/add_issue', methods=['POST'])
def add_issue():
    issue_name = request.form.get('issueName')

    if issue_name:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO issue_type (type) VALUES (%s)", [issue_name])
        conn.commit()
        cursor.close()
        return jsonify(success=True, issue_name=issue_name)
    return jsonify(success=False), 400


@app.route('/add_supplier_type', methods=['POST'])
def add_supplier_type():
    branch_name = request.form.get('branchName')
    
    if branch_name:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO supplier_type (supp_type) VALUES (%s)", [branch_name])
        conn.commit()
        cursor.close()
        return jsonify(success=True, branch_name=branch_name)
    return jsonify(success=False), 400

@app.route('/add_designation', methods=['POST'])
def add_designation():
    designation_name = request.form.get('designationName')
    
    # Check if the designation name is provided
    if designation_name:
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Insert new designation into the designations table
            cursor.execute("INSERT INTO designations (designation_name) VALUES (%s)", [designation_name])
            conn.commit()
            new_designation_id = cursor.lastrowid  # Get the last inserted designation ID
            return jsonify(success=True, designation_id=new_designation_id, designation_name=designation_name)
        except Exception as e:
            conn.rollback()  # Roll back in case of error
            return jsonify(success=False, message=str(e)), 500
        finally:
            cursor.close()
            conn.close()  # Ensure the connection is closed

    return jsonify(success=False, message='Designation name is required'), 400


@app.route('/add_city', methods=['POST'])
def add_city():
    city_name = request.form.get('cityName')
    if city_name:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("INSERT INTO city (city) VALUES (%s)", [city_name])
        conn.commit()
        new_city_id = cursor.lastrowid  # Get the last inserted city ID
        cursor.close()
        return jsonify(success=True, city_id=new_city_id, city_name=city_name)
    return jsonify(success=False), 400

@app.route('/download_sample_excel')
def download_sample_excel():
    try:
        return send_from_directory(
            directory=app.config['UPLOAD_FOLDER'], 
            path='customer-contacts.xlsx',  # Correct usage in Flask 2.x
            as_attachment=True
        )
    except Exception as e:
        return str(e), 404

@app.route('/download_sample_excel_supp')
def download_sample_excel_supp():
    try:
        return send_from_directory(
            directory=app.config['UPLOAD_FOLDER'], 
            path='supplier-contacts.xlsx',  # Correct usage in Flask 2.x
            as_attachment=True
        )
    except Exception as e:
        return str(e), 404

@app.route('/download_sample_excel_opportunity_rfq')
def download_sample_excel_opportunity_rfq():
    try:
        return send_from_directory(
            directory=app.config['UPLOAD_FOLDER'], 
            path='opportunity_rfq.xlsx',  # Correct usage in Flask 2.x
            as_attachment=True
        )
    except Exception as e:
        return str(e), 404

@app.route('/download_sample_excel_manfactured')
def download_sample_excel_manfactured():
    try:
        return send_from_directory(
            directory=app.config['UPLOAD_FOLDER'], 
            path='manfactured.xlsx',  # Correct usage in Flask 2.x
            as_attachment=True
        )
    except Exception as e:
        return str(e), 404
   

@app.route('/download_sample_excel_manfactured_supp')
def download_sample_excel_manfactured_supp():
    try:
        return send_from_directory(
            directory=app.config['UPLOAD_FOLDER'], 
            path='manage_suppliers.xlsx',  # Correct usage in Flask 2.x
            as_attachment=True
        )
    except Exception as e:
        return str(e), 404
@app.route('/download_sample_excel_suppliers_offers')
def download_sample_excel_suppliers_offers():
    try:
        return send_from_directory(
            directory=app.config['UPLOAD_FOLDER'], 
            path='suppliers_offers.xlsx',  # Correct usage in Flask 2.x
            as_attachment=True
        )
    except Exception as e:
        return str(e), 404

        

@app.route('/manage_calling_data', methods=['GET', 'POST'])
def manage_calling_data():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch customers and employees for display
    cursor.execute('SELECT * FROM customers')
    customers = cursor.fetchall()

    employee = 'SELECT * FROM employee where status=1'
    cursor.execute(employee)
    employees = cursor.fetchall()

    # Handle form submission (POST)
    if request.method == 'POST':
        # Process form data here (e.g., saving new contact or customer)
        # Assuming some process like:
        # contact_name = request.form.get('contact_name')
        # customer_name = request.form.get('customer_name')
        # Add your logic here to save data in DB
        
        # After successful processing:
        flash('Form submitted successfully!', 'success')
        return redirect(url_for('manage_calling_data'))  # Redirect to avoid form resubmission

    # Handle search and pagination (GET)
    search_query = request.args.get('search', '')
    page = int(request.args.get('page', 1))
    per_page = 10
    offset = (page - 1) * per_page

    # Count total matching records for pagination
    cursor.execute("""
        SELECT COUNT(*) FROM contacts 
        WHERE customer_name LIKE %s OR contact_person LIKE %s
    """, (f'{search_query}%', f'{search_query}%'))
    total_contacts = cursor.fetchone()[0]

    # Fetch matching records with pagination
    cursor.execute("""
        SELECT * FROM contacts 
        WHERE customer_name LIKE %s OR contact_person LIKE %s 
        ORDER BY id DESC, contact_person ASC 
        LIMIT %s OFFSET %s
    """, (f'{search_query}%', f'{search_query}%', per_page, offset))
    contacts = cursor.fetchall()

    cursor.close()
    conn.close()

    total_pages = (total_contacts + per_page - 1) // per_page
    max_date = datetime.today().strftime('%Y-%m-%d')

    return render_template('manage_calling_data.html', max_date=max_date, contacts=contacts, customers=customers, employees=employees, 
                           page=page, per_page=per_page, total_pages=total_pages, search_query=search_query)


@app.route('/delete_customers/<int:id>')
def delete_customers(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Execute DELETE operation
        cursor.execute("DELETE FROM customers WHERE id = %s", (id,))
        conn.commit()

        cursor.close()
        conn.close()

        flash('Record has been deleted successfully', 'success')
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')

    return redirect(url_for('Customers'))

    


@app.route('/update_customers', methods=['POST'])
def update_customers():
    if request.method == 'POST':
        id = request.form['id']
        customername = request.form.get('customername')
        branch = request.form.get('branch')
        city = request.form.get('city')
        contactnumber = request.form.get('contactnumber')
        contactfax = request.form.get('contactfax')
        website = request.form.get('website')
        pincode = request.form.get('pincode')
        address = request.form.get('address')
        customerprofile = request.form.get('customerprofile')
        remarks = request.form.get('remarks')
        products = request.form.get('products')
        applications = request.form.get('applications')
       
        # contactpersonname = request.form.get('contactpersonname')
        # contactno = request.form.get('contactno')
        # department = request.form.get('department')
        # email = request.form.get('email')
        # skype = request.form.get('skype')
        # addedby = request.form.get('addedby')
        # date = request.form.get('date')
        
        

            # Database connection
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="Omnipro"
            )
        mycursor = mydb.cursor()

            # Update SQL query
        sql = "UPDATE customers SET customer_name=%s, branch=%s, city=%s, contact_number=%s, contact_fax=%s,website=%s, pincode=%s, address=%s, customer_profile=%s, remarks=%s, products=%s,applications=%s WHERE id=%s"       
        # contactpersonname=%s, contactno=%s, department,email=%s, skype=%s,addedby=%s, date=%s WHERE id=%s
        val = (customername, branch, city, contactnumber,contactfax,website,pincode,address,customerprofile,remarks,products,applications,id)
        mycursor.execute(sql, val)
        mydb.commit()

            # Close cursor and database connection
        mycursor.close()
        mydb.close()

        flash("Data Updated Successfully")

    

    return redirect(url_for('Customers'))





@app.route('/delete_contacts/<int:id>')
def delete_contacts(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Execute DELETE operation
        cursor.execute("DELETE FROM contacts WHERE id = %s", (id,))
        conn.commit()
        cursor.close()
        conn.close()

        flash('Record has been deleted successfully', 'success')
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')

    return redirect(url_for('manage_calling_data'))


    
@app.route('/update_contacts', methods=['POST', 'GET'])
def update_contacts():
    if request.method == 'POST':
        id = request.form['id']
        customername = request.form.get('customername')
        contactpersonname = request.form['contactpersonname']
        contactno = request.form.get('contactno')
        department = request.form.get('department')
        email = request.form.get('email')
        skype = request.form.get('skype')
        addedby = request.form.get('addedby')
        date = request.form.get('date')  # Corrected

        # Ensure the date is not in the future
        if datetime.strptime(date, '%Y-%m-%d').date() > datetime.today().date():
            return "Error: Date cannot be in the future!", 400

        # Database connection
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="Omnipro"
        )
        mycursor = mydb.cursor()

        # Update SQL query
        sql = """
        UPDATE contacts 
        SET customer_name=%s, contact_person=%s, contact_number=%s, 
            department=%s, email=%s, skype=%s, added_by=%s, date=%s 
        WHERE id=%s
        """
        val = (customername, contactpersonname, contactno, department, email, skype, addedby, date, id)
        mycursor.execute(sql, val)
        mydb.commit()

        mycursor.close()
        mydb.close()

        flash("Data Updated Successfully")
        return redirect(url_for('manage_calling_data'))

    # If GET request, calculate max_date for the date input
    max_date = datetime.today().strftime('%Y-%m-%d')  # Date limited to today's date
    return render_template('manage_calling_data.html', max_date=max_date)










@app.route('/update_courses', methods=['GET', 'POST'])
def update_courses():
    return render_template('update_courses.html')

@app.route('/update_colleges', methods=['GET', 'POST'])
def update_colleges():
    return render_template('update_colleges.html')

@app.route('/update_invoices', methods=['GET', 'POST'])
def update_invoices():
    return render_template('update_invoices.html') 
 



if __name__ == '__main__':
    app.run(debug=True)