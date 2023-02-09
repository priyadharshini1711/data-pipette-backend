import re
import mysql.connector
import datetime
from flask import jsonify
import phonenumbers


def extract_file_model(file, filename):
    data = file.read().decode('utf-8')
    phone = {}
    for i in re.findall(r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]', data):
        print(i)
        phone[i] = ""
    print("checking for db connection")
    connection = mysql.connector.connect(
        host='localhost', database='data_pipette', user='root', password='root')
    is_processed = False
    try:
        print("Inserting BLOB into table")
        cursor = connection.cursor()
        insert_data_files = """INSERT INTO admin_user_data_files (file, file_name, is_processed, updated_by, updated_at) VALUES (%s,%s,%s,%s,%s)"""
        is_processed = True

        # Convert data into tuple format
        insert_data_file_values = (
            data, filename, is_processed, 1, datetime.datetime.now())

        cursor.execute(insert_data_files, insert_data_file_values)

        file_id = cursor.lastrowid

        for key in phone:
            insert_processed_file_sql = """insert into admin_user_processed_files (file_id, phone, is_mapped) values (%s,%s,%s)"""
            insert_processed_file_values = (file_id, key, 0)
            cursor.execute(insert_processed_file_sql,
                           insert_processed_file_values)

        connection.commit()
        print("file inserted successfully as a BLOB into table")

    except mysql.connector.Error as error:
        print("Failed inserting BLOB data into MySQL table {}".format(error))

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")


def dictify_files(record):
    return [dict(zip(("id", "file_name", "updated_at", "updated_by", "phone"), r)) for r in record]


def get_file_model():
    connection = mysql.connector.connect(
        host='localhost', database='data_pipette', user='root', password='root')
    print("checking for db connection")
    try:
        cursor = connection.cursor()
        get_files_sql = """select df.id, file_name, updated_at, u.username, phone from admin_user_data_files df 
join admin_user_processed_files pf on pf.file_id = df.id
join user u on u.id = df.updated_by;"""
        cursor.execute(get_files_sql)
        return jsonify(dictify_files(cursor.fetchall()))

    except mysql.connector.Error as error:
        print("Failed getting data from MySQL table {}".format(error))

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")


def get_dashboard_data_model():
    connection = mysql.connector.connect(
        host='localhost', database='data_pipette', user='root', password='root')
    print("checking for db connection")
    result = {}
    try:
        cursor = connection.cursor()
        get_data_files_sql = """SELECT count(*) as data_files FROM admin_user_data_files;"""
        cursor.execute(get_data_files_sql)
        data = cursor.fetchall()
        result["data_files"] = data[0][0]

        get_processed_files_sql = """SELECT count(*) FROM admin_user_processed_files where is_mapped = 1"""
        cursor.execute(get_processed_files_sql)
        data = cursor.fetchall()
        result["mapped_files"] = data[0][0]

        get_users_sql = """SELECT count(*) FROM user where id > 1"""
        cursor.execute(get_users_sql)
        data = cursor.fetchall()
        result["user"] = data[0][0]

        get_verified_sql = """SELECT count(*) FROM patient_phone where is_verified = 1"""
        cursor.execute(get_verified_sql)
        data = cursor.fetchall()
        result["verified_phone"] = data[0][0]

        get_total_phone_sql = """SELECT count(*) FROM patient_phone where phone != %s"""
        cursor.execute(get_total_phone_sql, ("",))
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


def dictify_user_phone(record):
    return [dict(zip(("id", "user_id", "country_code", "phone"), r)) for r in record]


def dictify_processed_files(record):
    return [dict(zip(("id", "file_id", "phone"), r)) for r in record]


def map_processed_files_model(user_id=None):
    connection = mysql.connector.connect(
        host='localhost', database='data_pipette', user='root', password='root')
    print("checking for db connection")
    try:
        print("Inserting BLOB into table")
        cursor = connection.cursor()

        # get user phone

        if (user_id is None):
            get_user_phone_sql = "select id, user_id, country_code, phone from patient_phone where is_verified = 1"
            cursor.execute(get_user_phone_sql)
            user_phone = dictify_user_phone(cursor.fetchall())
        else:
            get_user_phone_sql = "select id, user_id, country_code, phone from patient_phone where is_verified = 1 and user_id = %s"
            cursor.execute(get_user_phone_sql, (user_id,))
            user_phone = dictify_user_phone(cursor.fetchall())

        print(user_phone)

        get_processed_files_sql = "SELECT * FROM admin_user_processed_files where is_mapped = 0;"
        cursor.execute(get_processed_files_sql)
        file = dictify_processed_files(cursor.fetchall())

        print(file)

        for f in file:
            for up in user_phone:
                # print(phonenumbers.parse(up['phone'], None))
                try:
                    x = phonenumbers.parse(f['phone'], None)
                    y = phonenumbers.parse(
                        "".join([up['country_code'], up['phone']]), None)
                    if (x == y):
                        #insert processed files
                        insert_patient_record_sql = """INSERT INTO patient_records (user_id, phone_id, file_id)
                        SELECT * FROM (SELECT %s AS user_id, %s AS phone_id, %s AS file_id) AS tmp
                        WHERE NOT EXISTS (
                            SELECT * FROM patient_records WHERE user_id = %s and phone_id = %s and file_id = %s
                        ) LIMIT 1"""
                        insert_patient_record_values = (
                            up['user_id'], up['id'], f['file_id'], up['user_id'], up['id'], f['file_id'])
                        cursor.execute(insert_patient_record_sql,
                                    insert_patient_record_values)
                        #mapped processed files
                        map_processed_file_sql = "update admin_user_processed_files set is_mapped = 1 where file_id = %s"
                        cursor.execute(map_processed_file_sql, (f['file_id'],))
                except:
                    continue
        connection.commit()
        print("file inserted successfully as a BLOB into table")
        return "User Files mapped Successfully"
    except mysql.connector.Error as error:
        print("Failed inserting BLOB data into MySQL table {}".format(error))

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")
