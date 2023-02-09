import re
import mysql.connector
import datetime
from flask import jsonify
import phonenumbers


def get_phone_id(x, y):
    for i in x:
        if i[1] == y:
            return i[0]
    return ""


def extract_file_user_model(file, filename, user_id):
    data = file.read().decode('utf-8')
    phone = {}
    for i in re.findall(r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]', data):
        phone[i] = ""
    connection = mysql.connector.connect(
        host='localhost', database='data_pipette', user='root', password='root')
    is_processed = False
    print("checking for db connection")
    try:
        cursor = connection.cursor()
        insert_data_file_sql = """INSERT INTO admin_user_data_files (file, file_name, is_processed, updated_by, updated_at) VALUES (%s,%s,%s,%s,%s)"""
        is_processed = True

        insert_data_file_values = (
            data, filename, is_processed, user_id, datetime.datetime.now())
        cursor.execute(insert_data_file_sql, insert_data_file_values)

        # get last file inserted

        file_id = cursor.lastrowid

        # get_patient_phone

        get_user_phone_sql = """select id, phone from patient_phone where user_id = %s;"""
        cursor.execute(get_user_phone_sql, (user_id,))
        user_phone = cursor.fetchall()

        for key in phone:
            # insert processed file
            insert_processed_file_sql = """insert into admin_user_processed_files (file_id, phone, is_mapped) values (%s,%s,%s)"""
            insert_processed_file_values = (file_id, key, 1)
            cursor.execute(insert_processed_file_sql,
                           insert_processed_file_values)

            record_id = cursor.lastrowid

            phone_id = get_phone_id(user_phone, key)

            if phone_id != "":
                user_file = """insert into patient_records (user_id, phone_id, file_id) values (%s, %s, %s)"""
                cursor.execute(user_file, (user_id, phone_id, record_id))
            else:
                # get user phone id
                get_user_available_phone_sql = """select id from patient_phone where user_id = %s and phone = "" and is_verified = 0 limit 1"""
                cursor.execute(get_user_available_phone_sql, (user_id,))
                user_availble_phone_id = cursor.fetchall()

                # update user Phone
                update_user_phone_sql = """update patient_phone set country_code =%s , phone = %s where id = %s"""
                phone_data = phonenumbers.parse(key)
                cursor.execute(update_user_phone_sql, ('+'+str(phone_data.country_code),
                               phone_data.national_number, user_availble_phone_id[0][0]))

                # map user phone
                map_user_phone_sql = """insert into patient_records (user_id, phone_id, file_id) values (%s, %s, %s)"""
                map_user_phone_values = (
                    user_id, user_availble_phone_id[0][0], record_id)
                cursor.execute(map_user_phone_sql, map_user_phone_values)
        connection.commit()
        print("file inserted successfully as a BLOB into table")

    except mysql.connector.Error as error:
        print("Failed inserting BLOB data into MySQL table {}".format(error))

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")


def dictify_username(record):
    return [dict(zip(("id", "username", "password"), vv)) for vv in record]


def get_username_model():
    connection = mysql.connector.connect(
        host='localhost', database='data_pipette', user='root', password='root')
    print("checking for db connection")
    try:
        cursor = connection.cursor()
        get_username_sql = """select * from user"""
        cursor.execute(get_username_sql)
        return jsonify(dictify_username(cursor.fetchall()))

    except mysql.connector.Error as error:
        print("Failed gettting data from MySQL table {}".format(error))

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")


def create_username_model(username, password):
    connection = mysql.connector.connect(
        host='localhost', database='data_pipette', user='root', password='root')
    print("checking for db connection")
    try:
        cursor = connection.cursor()
        create_username_sql = """insert into user (username, password) values (%s,%s)"""
        create_username_values = (username, password)
        cursor.execute(create_username_sql, create_username_values)

        user_id = cursor.lastrowid

        # insert patient details

        create_user_details_sql = """insert into patient_details (name, address, user_id, email) values (%s,%s,%s,%s)"""
        create_user_details_values = (username, "", user_id, "")
        cursor.execute(create_user_details_sql, create_user_details_values)

        # insert patient phone

        create_user_phone = """insert into patient_phone (user_id, phone, is_verified) values (%s,%s,%s)"""
        for i in range(10):
            create_user_phone_values = (user_id, "", 0)
            cursor.execute(create_user_phone, create_user_phone_values)

        connection.commit()

    except mysql.connector.Error as error:
        print("Failed inserting data into MySQL table {}".format(error))

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")


def dictify_user_detail(record):
    return [dict(zip(("id", "name", "address", "user_id", "email"), vv)) for vv in record]


def get_user_detail_model(user_id):
    connection = mysql.connector.connect(
        host='localhost', database='data_pipette', user='root', password='root')
    print("checking for db connection")
    try:
        cursor = connection.cursor()
        get_user_detail_sql = """select * from patient_details where user_id = %s"""
        cursor.execute(get_user_detail_sql, (user_id,))
        data = dictify_user_detail(cursor.fetchall())
        print(data)
        if data is not None:
            return jsonify(data[0])
        else:
            return jsonify([])

    except mysql.connector.Error as error:
        print("Failed gtetting data from MySQL table {}".format(error))

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")


def dictify_user_phone(record):
    return [dict(zip(("id", "user_id", "country_code", "phone", "is_verified"), vv)) for vv in record]


def get_user_phone_model(id):
    connection = mysql.connector.connect(
        host='localhost', database='data_pipette', user='root', password='root')
    print("checking for db connection")
    try:
        cursor = connection.cursor()
        get_user_detail_sql = """select id, user_id, country_code, phone, is_verified from patient_phone where user_id = %s"""
        cursor.execute(get_user_detail_sql, (id,))
        data = dictify_user_phone(cursor.fetchall())
        if data is not None:
            return jsonify(data)
        else:
            return jsonify([])

    except mysql.connector.Error as error:
        print("Failed getting data from MySQL table {}".format(error))

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")


def update_user_phone_model(country_code, phone, id):
    connection = mysql.connector.connect(
        host='localhost', database='data_pipette', user='root', password='root')
    print("checking for db connection")
    try:
        cursor = connection.cursor()
        update_user_phone_sql = """update patient_phone set is_verified = 1, country_code = %s,phone = %s where id = %s"""
        country_code_value = '+'+country_code
        print(country_code_value)
        update_user_phone_values = (country_code_value, phone, id)
        cursor.execute(update_user_phone_sql, update_user_phone_values)
        connection.commit()

    except mysql.connector.Error as error:
        print("Failed inserting BLOB data into MySQL table {}".format(error))

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")


def dictify_user_file(record):
    return [dict(zip(("id", "file_name", "user_name", "phone", "is_verified", "updated_at"), vv)) for vv in record]


def get_user_file_model(user_id):
    connection = mysql.connector.connect(
        host='localhost', database='data_pipette', user='root', password='root')
    print("checking for db connection")
    try:
        cursor = connection.cursor()
        get_user_files_sql = """select ROW_NUMBER() OVER(PARTITION BY df.updated_by) AS id, df.file_name, u.username, pp.phone, pp.is_verified, df.updated_at from patient_records pr 
join admin_user_data_files df on df.id = pr.file_id
join patient_phone pp on pp.id = pr.phone_id
join user u on u.id = pr.user_id
where pr.user_id = %s;"""
        cursor.execute(get_user_files_sql, (user_id,))
        return jsonify(dictify_user_file(cursor.fetchall()))

    except mysql.connector.Error as error:
        print("Failed getting data from MySQL table {}".format(error))

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")


def get_user_dashboard_data_model(user_id):
    connection = mysql.connector.connect(
        host='localhost', database='data_pipette', user='root', password='root')
    print("checking for db connection")
    result = {}
    try:
        cursor = connection.cursor()
        get_data_files_sql = """SELECT count(*) as data_files FROM patient_records where user_id = %s;"""
        cursor.execute(get_data_files_sql, (user_id,))
        data = cursor.fetchall()
        result["total_files"] = data[0][0]

        get_admin_uploaded_files_sql = """select count(*) from admin_user_data_files audf
        join patient_records pr on pr.file_id = audf.id
        where pr.user_id = %s and updated_by = 1;"""
        cursor.execute(get_admin_uploaded_files_sql, (user_id,))
        data = cursor.fetchall()
        result["admin_uploaded"] = data[0][0]

        get_user_uploaded_files_sql = """select count(*) from admin_user_data_files audf
        join patient_records pr on pr.file_id = audf.id
        where pr.user_id = %s and updated_by != 1;"""
        cursor.execute(get_user_uploaded_files_sql, (user_id,))
        data = cursor.fetchall()
        result["user_uploaded"] = data[0][0]

        get_verified_phone_sql = """SELECT count(*) FROM patient_phone where user_id = %s and is_verified = 1;"""
        cursor.execute(get_verified_phone_sql, (user_id,))
        data = cursor.fetchall()
        result["verified_phone"] = data[0][0]

        get_total_phone_sql = """SELECT count(*) FROM patient_phone where user_id = %s and is_verified != 1 and phone != "";"""
        cursor.execute(get_total_phone_sql, (user_id,))
        data = cursor.fetchall()
        result["total_phone"] = data[0][0]

        return result

    except mysql.connector.Error as error:
        print("Failed getting data from MySQL table {}".format(error))

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")


def update_user_data_model(key, value, user_id):
    connection = mysql.connector.connect(
        host='localhost', database='data_pipette', user='root', password='root')
    print("checking for db connection")
    try:
        cursor = connection.cursor()
        update_user_data_sql = "update patient_details set "+ key +" = %s where user_id = %s"
        update_user_sql_values = (value, user_id)
        cursor.execute(update_user_data_sql, update_user_sql_values)
        connection.commit()

    except mysql.connector.Error as error:
        print("Failed inserting BLOB data into MySQL table {}".format(error))

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")