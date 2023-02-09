from flask import Flask
from models import *
from flask import request
from flask_cors import CORS, cross_origin

app = Flask(__name__)
cors = CORS(app, resources={r"/extract-file/": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route("/")
def index():
    return "Welcome to the index page."
@app.route("/hi/")
def who():
    return "Who are you?"

@app.route("/hi/<username>")
def greet(request):
    return f"Hi there, {username}!"

@app.route("/extract-file/", methods=['POST'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def extract_file():
    print(request)
    files = request.files["file"]
    for f in request.files.getlist('file'):
        print("file name : ", f.filename)
        extract_file_model(f, f.filename)
    return "extraction successful"

@app.route("/get-file/", methods=['GET'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def get_file():
    return get_file_model()

@app.route("/get-username/", methods=['GET'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def get_username():
    return get_username_model()

@app.route("/create-username/", methods=['POST'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def create_username():
    values = request.get_json()
    print(values)
    create_username_model(values['username'], values['password'])
    return "username inserted successfully"

@app.route("/get-user-detail/", methods=['GET'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def get_user_detail():
    args = request.args
    id = args.get('id')
    return get_user_detail_model(id)

@app.route("/get-user-phone/", methods=['GET'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def get_user_phone():
    args = request.args
    id = args.get('id')
    return get_user_phone_model(id)

@app.route("/update-user-phone/", methods=['PUT'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def update_user_phone():
    args = request.args
    country_code = args.get('country_code')
    phone = args.get('phone')
    user_id = args.get('id')
    update_user_phone_model(country_code, phone, user_id)
    return "updated phone successfully"

@app.route("/user/extract-file/", methods=['POST'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def extract_file_user():
    print(request)
    files = request.files["file"]
    args = request.args
    user_id = args.get('id')
    for f in request.files.getlist('file'):
        print("file name : ", f.filename)
        extract_file_user_model(f, f.filename, user_id)
    return "extraction successful"

@app.route("/get-user-file/", methods=['GET'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def get_user_file():
    args = request.args
    user_id = args.get('id')
    return get_user_file_model(user_id)

@app.route("/get-dashboard-data/", methods=['GET'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def get_dashboard_data():
    args = request.args
    user_id = args.get('id')
    return get_dashboard_data_model()

@app.route("/map-processed-files/", methods=['PUT'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def map_processed_files():
    args = request.args
    user_id = args.get('id')
    map_processed_files_model(user_id)
    return "Files Mapped Successfully"

@app.route("/get-user-dashboard-data/", methods=['GET'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def get_user_dashboard_data():
    args = request.args
    user_id = args.get('id')
    return get_user_dashboard_data_model(user_id)

@app.route("/update_user-data/", methods=['PUT'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def update_user_data():
    args = request.args
    key = args.get('key')
    value = args.get('value')
    user_id = args.get('id')
    update_user_data_model(key, value, user_id)
    return "User Details Updated Successfully"