from flask import Flask,request,url_for,jsonify,session,make_response,redirect
from flask_session import Session
from flask_cors import CORS
from stoken import dndata,endata
import re
import razorpay
client = razorpay.Client(auth=("rzp_test_TtbMq1fCTuEuDJ", "txJUiIKAA3W12IF1l8wJrlkf"))
import os 
from werkzeug.utils import secure_filename #sanitizes uploaded filenames
from otp import genotp
from flask_bcrypt import Bcrypt
from datetime import datetime,timedelta 
from cmail import send_mail
from mysql.connector import (connection)
from reportlab.platypus import(
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.platypus.flowables import HRFlowable
from datetime import timedelta
from io import BytesIO
BASE_DIR=os.path.dirname(os.path.abspath(__file__))
static_path=os.path.join(BASE_DIR,'static','uploads')
os.makedirs(static_path,exist_ok=True)
mydb = connection.MySQLConnection(user='flaskuser', password='password',
                                 host='localhost',
                                 database='flaskdb')
app=Flask(__name__)
CORS(app,supports_credentials=True,origins=["https://ecommerce-project-frontend-gray.vercel.app/"])
app.secret_key="code@123"
app.config['SESSION_TYPE']='filesystem'
# 2. Session Cookie Settings for Modern Cross-Origin Compliance
# Set to 'None' to allow cookies to be sent over cross-site requests.
# Note: SameSite='None' MANDATORILY requires Secure=True (HTTPS).
app.config['SESSION_COOKIE_SAMESITE'] = 'None'
app.config['SESSION_COOKIE_SECURE'] = True  # Must be True in production (HTTPS)
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Protects against XSS scripts reading the cookie
app.config['PERMANENT_SESSION_LIFETIME']=timedelta(days=1)
app.config['UPLOAD_FOLDER']=static_path
allowed_extensions={'jpg','png','jpeg','webp','gif'}
app.config['ALLOWED_EXTENSIONS']=allowed_extensions
Session(app)
bcrypt=Bcrypt(app)
@app.route('/',methods=['GET'])
def home():
    return jsonify({"status":"healthy"}),200
@app.route('/admin/register',methods=['POST'])
def adminregister():
    cursor=None
    data=request.get_json() #returns client data in dictionary format {}
    if not data:
        return jsonify({"status":"failed","message":"No input data was given"}),400
    admin_username=request.get_json()['username']
    if not admin_username:
        return jsonify({"status":"failed","message":"Username required"}),400
    admin_useremail=data.get('useremail')
    if not admin_useremail:
        return jsonify({"status":"failed","message":"Useremail required"}),400
    pattern=re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    if not pattern.match(admin_useremail):
        return jsonify({"status":"failed","message":"Useremail Invalid"}),400
    admin_userpassword=data.get('userpassword')
    if not admin_userpassword:
        return jsonify({"status":"failed","message":"Userpassword required"}),400
    if len(admin_userpassword)<6:
        return  jsonify({"status":"failed","message":"Userpassword is too short"}),400
    hash_password=bcrypt.generate_password_hash(admin_userpassword).decode('utf-8')
    admin_userphone =data.get('userphone')
    admin_agree=data.get('useragree')
    if not admin_agree:
        return jsonify({"status":"failed","message":"agreement  required"}),400
    admin_useraddress=data.get('useraddress')
    if not admin_useraddress:
        return jsonify({"status":"failed","message":"Useraddress required"}),400
    server_otp=genotp()
    otp_expiry_time=datetime.now()+timedelta(minutes=5)
    try:
        mydb.ping(reconnect=True) #automatically builds connection if any connection lost 
        cursor=mydb.cursor(buffered=True)
        cursor.execute('select adminid, account_status from admindata where admin_useremail=%s',[admin_useremail]) #none
        admin_details = cursor.fetchone() 
        if admin_details:
            if admin_details[1]  =="active":
                return jsonify({"status":"failed","message":"User Already existed"})
            elif admin_details[1]=="suspended":
                return jsonify({"status":"Failed","message":"User is suspended"})
            elif admin_details[1]=="inactive":
                cursor.execute('update admindata set admin_username=%s,admin_address=%s,admin_phoneno=%s,admin_userpassword=%s,otp=%s,otp_expiry_time=%s,account_status=%s where admin_useremail=%s',[admin_username,admin_useraddress,admin_userphone,hash_password,server_otp,otp_expiry_time,'inactive',admin_useremail])
        else:
             cursor.execute('insert into admindata(adminid,admin_username,admin_useremail,admin_address,admin_userpassword,admin_phoneno,admin_agree,otp,otp_expiry_time,account_status) values(uuid_to_bin(uuid()),%s,%s,%s,%s,%s,%s,%s,%s,%s)',[admin_username,admin_useremail,admin_useraddress,hash_password,admin_userphone,admin_agree,server_otp,otp_expiry_time,'inactive'])
        mydb.commit()
        subject="Admin otp for verification"
        body=f"Use given otp for Ecommy online shopping {server_otp}"
        send_mail(to=admin_useremail,subject=subject,body=body)
        return jsonify({"status":"success","message":"User registration otp send to given email"}),200
    except Exception as e:
        mydb.rollback()
        return jsonify({"status":"failed","message":f'{str(e)}'}),500
    finally:
        if cursor:
            cursor.close()
@app.route('/admin/otpverify',methods=['POST'])
def admin_otpverify():
    try:
        cursor=None
        data=request.get_json()
        if not data:
            return jsonify({"status":"failed","message":"No input data was given"}),400
        userotp=data.get('otp')
        useremail=data.get('useremail')
        if (not userotp) or (not useremail):
            return  jsonify({"status":"failed","message":"otp is required"}),400
        user_otp_time=datetime.now() #current time 
        mydb.ping(reconnect=True)
        cursor=mydb.cursor(buffered=True)
        cursor.execute('select adminid,account_status,otp,otp_expiry_time from admindata where admin_useremail=%s',[useremail])
        admin_data=cursor.fetchone()
        if not admin_data:
            return jsonify({"status":"failed","message":"admin details not found"}),400
        if admin_data[1]=='active':
            return jsonify({"status":"failed","message":"User already existed"}),400
        if admin_data[1]=='inactive' and admin_data[3]<user_otp_time:
            return jsonify({"status":"failed","message":"otp expired"}),400
        if admin_data[1]=='inactive' and admin_data[3]>user_otp_time:
            if admin_data[2]!=userotp:
               return jsonify({"status":"failed","message":"Invalid otp pls try again"}),400
        if admin_data[2]==userotp:
            cursor.execute('update admindata set otp=null,otp_expiry_time=null,account_status=%s where admin_useremail=%s',['active',useremail])
        mydb.commit()
        return jsonify({"status":"success","message":"OTP verified successfully"}),200
    except Exception as e:
        mydb.rollback()
        return jsonify({"status":"failed","message":f"cloud not verify otp {str(e)}"})      
@app.route('/admin/login',methods=['POST'])
def adminlogin():
    try:
        cursor=None
        data=request.get_json()
        if not data:
            return jsonify({"status":"failed","message":"No input data was given"}),400
        login_email=data.get("email")
        if not login_email:
            return jsonify({"status":"failed","message":"Email required"}),400
        login_password=data.get("password")
        if not login_password:
            return jsonify({"status":"failed","message":"password required"}),400
        mydb.ping(reconnect=True)
        cursor=mydb.cursor(buffered=True)
        cursor.execute('select bin_to_uuid(adminid),account_status,admin_userpassword from admindata where admin_useremail=%s',[login_email])
        admin_data=cursor.fetchone()
        if not admin_data:
            return jsonify({"status":"failed","message":"Email not registred pls register"}),400
        if admin_data[1]=='inactive':
            return jsonify({"status":"failed","message":"admin details not verified pls register "}),400
        if admin_data[1]=='suspended':
            return jsonify({"status":"failed","message":"admin is suspended"}),400
        if admin_data[1]=='active':
            if not bcrypt.check_password_hash(admin_data[2],login_password):
                return jsonify({"status":"failed","message":"Invalid password"}),400
            else:
                session['adminid']=admin_data[0]
                session['admin_email']=login_email
                print(session,'after login')
                return jsonify({"status":"success","message":"Login successful","admin":{"adminid":session.get('adminid'),"adminemail":session.get('admin_email')}}),200
    except Exception as e:
        return jsonify({"status":"failed","message":f"Could not login {str(e)}"}),500
def allowed_filename(filename):
    return '.' in filename and filename.rsplit('.',1)[-1].lower() in app.config['ALLOWED_EXTENSIONS']
@app.route('/admin/additem',methods=['POST'])
def additem():
    cursor=None
    try:
        if not session.get('adminid'):
            return jsonify({"status":"failed","message":"session data not found Pls login first"}),400
        data=request.form
        if not data:
            return jsonify({"status":"failed",
            "message":"No input data was given"}),401
        item_name=data.get('title')
        if not item_name:
            return jsonify({"status":"failed","message":"item_namer required"}),401
        item_description=data.get('Description')
        item_about=data.get('About_item')
        item_price=data.get("price") #'45.56'
        if not item_price:
            return jsonify({"status":"failed","message":"item_price required"}),401
        item_quantity=data.get('quantity')
        try:
            item_price=float(item_price)
            item_quantity=int(item_quantity)
        except ValueError:
            return jsonify({"status":"failed","message":"price must be decimal value or quantity must be int"}),401
        item_category=data.get("category")
        item_filedata=request.files.get('file')
        print(item_filedata)
        if not item_filedata:
            return jsonify({"status":"failed","message":"item_file required"}),401
        user_filename=item_filedata.filename
        print(user_filename)
        if not item_filedata.mimetype.startswith('image/'):
            return jsonify({"status":"failed","message":"File type invalid"})
        if not allowed_filename(user_filename):
            return jsonify({"status":"failed","message":"File type is not allowed only png,jpg,jpeg,webp,gif"}),401
        secure_file=secure_filename(user_filename)
        f_ext=os.path.splitext(secure_file)[1]
        new_filename=genotp()+f_ext
        save_path=os.path.join(app.config['UPLOAD_FOLDER'],new_filename)
        item_filedata.save(save_path)
        mydb.ping(reconnect=True)
        cursor=mydb.cursor(buffered=True)
        cursor.execute('insert into items(itemid,item_name,item_desc,item_about,item_price,item_stock,item_category,item_imagename,adminid) values(uuid_to_bin(uuid()),%s,%s,%s,%s,%s,%s,%s,uuid_to_bin(%s))',[item_name,item_description,item_about,item_price,item_quantity,item_category,new_filename,session.get('adminid')])
        mydb.commit()
        return jsonify({"status":"success","message":f"item details stored successfully"}),200
    except Exception as e:
        mydb.rollback()
        if save_path:
            os.remove(save_path)
        return jsonify({"status":"'failed","message":f"could not add item {str(e)}"})
    finally:
        if cursor:
            cursor.close()
@app.route('/admin/allitems',methods=['GET'])
def admin_items():
    cursor=None
    try:
        if not session.get('adminid'):
            return jsonify({"status":"failed","message":"session data not found Pls login first"}),400
        mydb.ping(reconnect=True)
        cursor=mydb.cursor(buffered=True)
        cursor.execute('select bin_to_uuid(itemid),item_name,item_desc,item_about,item_price,item_stock,item_category,item_imagename from items where adminid=uuid_to_bin(%s)',[session.get('adminid')])
        items_data=cursor.fetchall() #[(1,'car','car_des'),(2,'bike','bike_desc')]
        print(items_data)
        if not items_data:
            return jsonify({
                "status": "success",
                "products": [],
                "message": "No items added yet"
                }), 200
        products=[]
        for item in items_data:
            products.append({
                'itemid':item[0],
                'itemname':item[1],
                'item_desc':item[2],
                'item_about':item[3],
                'price':item[4],
                'quantity':item[5],
                'category':item[6],
                'image':url_for('static',filename=f'uploads/{item[7]}',_external=True)
            })
            print(products)
        return jsonify({"status":"success","products":products}),200
    except Exception as e:
        return jsonify({"status":"'failed","message":f"could not add item {str(e)}"})
    finally:
        if cursor:
            cursor.close()
@app.route('/admin/item/<itemid>',methods=['GET'])
def admin_viewitem(itemid):
    cursor=None
    try:
        if not session.get('adminid'):
            return jsonify({"status":"failed","message":"session data not found Pls login first"}),400
        mydb.ping(reconnect=True)
        cursor=mydb.cursor(buffered=True)
        cursor.execute('select bin_to_uuid(itemid),item_name,item_desc,item_about,item_price,item_stock,item_category,item_imagename from items where adminid=uuid_to_bin(%s) and itemid=uuid_to_bin(%s)',[session.get('adminid'),itemid])
        items_data=cursor.fetchone() #(1,'car','car_des'),
        if not items_data:
            return jsonify({"status":"failed","message":"No items added"})
        
        product={
            'itemid':items_data[0],
            'itemname':items_data[1],
            'item_desc':items_data[2],
            'item_about':items_data[3],
            'price':items_data[4],
            'quantity':items_data[5],
            'category':items_data[6],
            'image':url_for('static',filename=f'uploads/{items_data[7]}',_external=True)
            }
        print(product)
        return jsonify({"status":"success","product":product}),200
    except Exception as e:
        return jsonify({"status":"'failed","message":f"could not add item {str(e)}"})
    finally:
        if cursor:
            cursor.close()
@app.route('/admin/deleteitem/<itemid>',methods=['DELETE'])
def deleteitem(itemid):
    cursor=None
    try:
        if not session.get('adminid'):
            return jsonify({"status":"failed","message":"session data not found Pls login first"}),400
        mydb.ping(reconnect=True)
        cursor=mydb.cursor(buffered=True)
        cursor.execute('select bin_to_uuid(itemid),item_imagename from items where itemid=uuid_to_bin(%s) and adminid=uuid_to_bin(%s)',[itemid,session.get('adminid')])
        item_count=cursor.fetchone() #(0,) or (1,)
        if not item_count:
            return jsonify({"status":"failed","message":"No item found"})
        #find the item filepath
        remove_path=os.path.join(app.config['UPLOAD_FOLDER'],item_count[1])
        cursor.execute('delete from items where itemid=uuid_to_bin(%s) and adminid=uuid_to_bin(%s)',[itemid,session.get("adminid")])
        mydb.commit()
        if remove_path:
            os.remove(remove_path)
        return jsonify({"status":"success","message":"Item deleted successfully"}),200
    except Exception as e:
        mydb.rollback()
        return jsonify({"status":"'failed","message":f"could not add item {str(e)}"})
    finally:
        if cursor:
            cursor.close()
@app.route('/admin/updateitem/<itemid>',methods=['PUT'])
def updateitem(itemid):
    cursor=None
    old_path=None
    new_path=None
    try:
        if not session.get('adminid'):
            return jsonify({"status":"failed","message":"session data not found Pls login first"}),400
        mydb.ping(reconnect=True)
        cursor=mydb.cursor(buffered=True)
        cursor.execute('select bin_to_uuid(itemid),item_name,item_desc,item_about,item_price,item_stock,item_category,item_imagename from items where itemid=uuid_to_bin(%s) and adminid=uuid_to_bin(%s)',[itemid,session.get('adminid')])
        item_count=cursor.fetchone() #(1,'cxar','car_desc'..)
        if not item_count:
            return jsonify({"status":"failed","message":"No item found"}),404
        updated_data=request.form
        print(updated_data,'item_info')
        if not updated_data:
            return jsonify({"status":"failed",
            "message":"No input updated_data was given"}),401
        updated_item_name=updated_data.get('title')
        if not updated_item_name:
            return jsonify({"status":"failed","message":"item_namer required"}),401
        updated_item_description=updated_data.get('Description')
        updated_item_about=updated_data.get('About_item')
        updated_item_price=updated_data.get("price") #'45.56'
        if not updated_item_price:
            return jsonify({"status":"failed","message":"item_price required"}),401
        updated_item_quantity=updated_data.get('quantity')
        try:
            updated_item_price=float(updated_item_price)
            updated_item_quantity=int(updated_item_quantity)
        except ValueError:
            return jsonify({"status":"failed","message":"price must be decimal value or quantity must be int"}),401
        updated_item_category=updated_data.get("category")
        updated_item_filedata=request.files.get('file')
        print(updated_item_filedata)
        old_image=item_count[7]
        filename=item_count[7]
        if updated_item_filedata:
            new_filename=updated_item_filedata.filename #extract new filename
            if not updated_item_filedata.mimetype.startswith('image/'):
                return jsonify({"status":"failed","message":"File type invalid"})
            if not allowed_filename(new_filename):
                return jsonify({"status":"failed","message":"File type is not allowed only png,jpg,jpeg,webp,gif"}),401
            secure_file=secure_filename(new_filename)
            f_ext=os.path.splitext(secure_file)[1]
            filename=genotp()+f_ext
            new_path=os.path.join(app.config['UPLOAD_FOLDER'],filename)
            updated_item_filedata.save(new_path) #new file save in static folder
            old_path=os.path.join(app.config['UPLOAD_FOLDER'],old_image)
        cursor.execute('update items set item_name=%s,item_desc=%s,item_about=%s,item_price=%s,item_stock=%s,item_category=%s,item_imagename=%s where itemid=uuid_to_bin(%s) and adminid=uuid_to_bin(%s)',[updated_item_name,updated_item_description,updated_item_about,updated_item_price,updated_item_quantity,updated_item_category,filename,itemid,session.get('adminid')])
        mydb.commit()
        if old_path and new_path:
            os.remove(old_path)
        return jsonify({"status":"success","message":"Item Updated successfully"}),200
    except Exception as e:
        mydb.rollback()
        return jsonify({"status":"'failed","message":f"could not update item {str(e)}"})
    finally:
        if cursor:
            cursor.close()
@app.route('/admin/logout',methods=['POST'])
def adminlogout():
    if not session.get('adminid'):
        return jsonify({"status":"failed","message":"session data not found Pls login first"}),400
    session.clear()
    session.modified=True
    return jsonify({"status":"success","message":"Admin Logout successful"}),200

@app.route('/user/register', methods=['POST'])
def userregister():
    cursor = None
    data = request.get_json()

    if not data:
        return jsonify({
            "status": "failed",
            "message": "No input data was given"
        }), 400

    user_username = data.get('username')
    if not user_username:
        return jsonify({
            "status": "failed",
            "message": "Username required"
        }), 400

    user_useremail = data.get('useremail')
    if not user_useremail:
        return jsonify({
            "status": "failed",
            "message": "Useremail required"
        }), 400

    pattern = re.compile(
    r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
)



    if not pattern.match(user_useremail):
        return jsonify({
            "status": "failed",
            "message": "Useremail Invalid"
        }), 400

    user_userpassword = data.get('userpassword')
    if not user_userpassword:
        return jsonify({
            "status": "failed",
            "message": "Userpassword required"
        }), 400

    if len(user_userpassword) < 6:
        return jsonify({
            "status": "failed",
            "message": "Userpassword is too short"
        }), 400

    hash_password = bcrypt.generate_password_hash(
        user_userpassword
    ).decode('utf-8')

    user_userphone = data.get('userphone')

    user_gender = data.get('usergender')
    if not user_gender:
        return jsonify({
            "status": "failed",
            "message": "Usergender required"
        }), 400

    user_useraddress = data.get('useraddress')
    if not user_useraddress:
        return jsonify({
            "status": "failed",
            "message": "Useraddress required"
        }), 400

    server_otp = genotp()
    otp_expiry_time = datetime.now() + timedelta(minutes=5)

    try:
        mydb.ping(reconnect=True)
        cursor = mydb.cursor(buffered=True)

        cursor.execute(
            """
            SELECT userid, account_status
            FROM userdata
            WHERE user_email = %s
            """,
            (user_useremail,)
        )

        user_details = cursor.fetchone()

        if user_details:
            if user_details[1] == "active":
                return jsonify({
                    "status": "failed",
                    "message": "User already exists"
                }), 409

            elif user_details[1] == "suspended":
                return jsonify({
                    "status": "failed",
                    "message": "User is suspended"
                }), 403

            elif user_details[1] == "inactive":
                cursor.execute(
                    """
                    UPDATE userdata
                    SET user_name = %s,
                        user_address = %s,
                        user_phoneno = %s,
                        user_userpassword = %s,
                        user_gender = %s,
                        otp = %s,
                        otp_expiry_time = %s
                    WHERE user_email = %s
                    """,
                    (
                        user_username,
                        user_useraddress,
                        user_userphone,
                        hash_password,
                        user_gender,
                        server_otp,
                        otp_expiry_time,
                        user_useremail
                    )
                )

        else:
            cursor.execute(
                """
                INSERT INTO userdata (
                    userid,
                    user_name,
                    user_email,
                    user_address,
                    user_userpassword,
                    user_phoneno,
                    user_gender,
                    otp,
                    otp_expiry_time,
                    account_status
                )
                VALUES (
                    UUID_TO_BIN(UUID()),
                    %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                """,
                (
                    user_username,
                    user_useremail,
                    user_useraddress,
                    hash_password,
                    user_userphone,
                    user_gender,
                    server_otp,
                    otp_expiry_time,
                    'inactive'
                )
            )

        mydb.commit()
        subject="user otp for verification"
        body=f"Use given otp for Ecommy online shopping {server_otp}"
        send_mail(to=user_useremail,subject=subject,body=body)
        return jsonify({"status":"success","message":"User registration otp send to given email"}),200

    except Exception:
        mydb.rollback()
        app.logger.exception("User registration failed")
        return jsonify({
            "status": "failed",
            "message": "User registration failed"
        }), 500

    finally:
        if cursor:
            cursor.close()

@app.route('/user/otpverify',methods=['POST'])
def user_otpverify():
    try:
        cursor=None
        data=request.get_json()
        if not data:
            return jsonify({"status":"failed","message":"No input data was given"}),400
        userotp=data.get('otp')
        useremail=data.get('user_email')
        if (not userotp) or (not useremail):
            return  jsonify({"status":"failed","message":"otp is required"}),400
        user_otp_time=datetime.now() #current time 
        mydb.ping(reconnect=True)
        cursor=mydb.cursor(buffered=True)
        cursor.execute('select userid,account_status,otp,otp_expiry_time from userdata where user_email=%s',[useremail])
        user_data=cursor.fetchone()
        if not user_data:
            return jsonify({"status":"failed","message":"admin details not found"}),400
        if user_data[1]=='active':
            return jsonify({"status":"failed","message":"User already existed"}),400
        if user_data[1]=='inactive' and user_data[3]<user_otp_time:
            return jsonify({"status":"failed","message":"otp expired"}),400
        if user_data[1]=='inactive' and user_data[3]>user_otp_time:
            if user_data[2]!=userotp:
               return jsonify({"status":"failed","message":"Invalid otp pls try again"}),400
        if user_data[2]==userotp:
            cursor.execute('update userdata set otp=null,otp_expiry_time=null,account_status=%s where user_email=%s',['active',useremail])
        mydb.commit()
        return jsonify({"status":"success","message":"OTP verified successfully"}),200
    except Exception as e:
        mydb.rollback()
        return jsonify({"status":"failed","message":f"cloud not verify otp {str(e)}"})   
    finally:
            if cursor:
                cursor.close()   

@app.route('/user/login',methods=['POST'])
def userlogin():
    try:
        cursor=None
        data=request.get_json()
        if not data:
            return jsonify({"status":"failed","message":"No input data was given"}),400
        login_email=data.get("email")
        if not login_email:
            return jsonify({"status":"failed","message":"Email required"}),400
        login_password=data.get("password")
        if not login_password:
            return jsonify({"status":"failed","message":"password required"}),400
        mydb.ping(reconnect=True)
        cursor=mydb.cursor(buffered=True)
        cursor.execute('select bin_to_uuid(userid),account_status,user_userpassword from userdata where user_email=%s',[login_email])
        user_data=cursor.fetchone()
        if not user_data:
            return jsonify({"status":"failed","message":"Email not registred pls register"}),400
        if user_data[1]=='inactive':
            return jsonify({"status":"failed","message":"admin details not verified pls register "}),400
        if user_data[1]=='suspended':
            return jsonify({"status":"failed","message":"admin is suspended"}),400
        if user_data[1]=='active':
            if not bcrypt.check_password_hash(user_data[2],login_password):
                return jsonify({"status":"failed","message":"Invalid password"}),400
            else:
                session['userid']=user_data[0]
                session['user_email']=login_email
                print(session,'after login')
                return jsonify({"status":"success","message":"Login successful","user":{"userid":session.get('userid'),"useremail":session.get('user_email')}}),200
    except Exception as e:
        return jsonify({"status":"failed","message":f"Could not login {str(e)}"}),500
    finally:
        if cursor:
            cursor.close()
@app.route('/user/products',methods=['GET'])
def products():
    cursor=None
    try:
        mydb.ping(reconnect=True)
        cursor=mydb.cursor(buffered=True)
        cursor.execute('select bin_to_uuid(itemid),item_name,item_desc,item_about,item_price,item_stock,item_category,item_imagename from items ')
        items_data=cursor.fetchall()
        if not items_data:
            return jsonify({"status":"failed","message":"No items added"})
        products=[]
        for item in items_data:
            products.append({
                'itemid':item[0],
                'itemname':item[1],
                'item_desc':item[2],
                'item_about':item[3],
                'price':item[4],
                'quantity':item[5],
                'category':item[6],
                'image':url_for('static',filename=f'uploads/{item[7]}',_external=True)
            })
        return jsonify({"status":"success","products":products}),200
    except Exception as e:
        return jsonify({"status":"'failed","message":f"could not add item {str(e)}"})
    finally:
        if cursor:
            cursor.close()
@app.route('/user/addcart',methods=['POST'])
def addcart():
    cursor=None
    try:
        if not session.get('userid'):
            return jsonify({"status":"failed","message":"pls login first to addcart"}),401
        data=request.get_json()
        if not data:
            return  jsonify({"status":"failed","message":"No input data was given"}),400  
        itemid=data.get('itemid')
        quantity=data.get('quantity',1)
        try:
            quantity=int(quantity)
        except ValueError:
            return jsonify({"status":"failed","message":"quantity should be in integer"})
        userid=session.get('userid')
        mydb.ping(reconnect=True)
        cursor=mydb.cursor(buffered=True)
        cursor.execute("select bin_to_uuid(itemid),item_stock from items where itemid=uuid_to_bin(%s)",[itemid])
        item_data=cursor.fetchone()
        if not item_data:
            return jsonify({"status":"failed","message":"Item not found"}),400
        #quantity validation
        stored_quantity=item_data[1]
        if quantity > stored_quantity:
            return jsonify({"status":"failed","message":"item quantity is exceeded than stock amout"}),400
        #checking item alredy in cart
        cursor.execute("select cart_quantity from cart where itemid=uuid_to_bin(%s) and userid=uuid_to_bin(%s)",[itemid,userid])
        cart_item=cursor.fetchone()
        if cart_item:
            cursor.execute('update cart set cart_quantity=%s where itemid=uuid_to_bin(%s) and userid=uuid_to_bin(%s)',[quantity,itemid,userid])
            message="item already existed in cart"
        else:
            cursor.execute("insert into cart(cartid,itemid,userid,cart_quantity) values(uuid_to_bin(uuid()),uuid_to_bin(%s),uuid_to_bin(%s),%s)",[itemid,userid,quantity])
            message="Item added to cart"
        mydb.commit()
        return jsonify({"status":"success","message":message}),200
    except Exception as e:
        return jsonify({"status":"'failed","message":f"could not add item {str(e)}"})
    finally:
        if cursor:
            cursor.close()
@app.route('/user/viewcart',methods=['GET'])
def viewcart():
    cursor=None
    try:
        if not session.get('userid'):
            return jsonify({"status":"failed","message":"pls login first to addcart"}),401
        mydb.ping(reconnect=True)
        cursor=mydb.cursor(buffered=True)
        cursor.execute("select bin_to_uuid(i.itemid),i.item_name,i.item_price,c.cart_quantity,i.item_category,i.item_imagename from items i inner join cart c on i.itemid=c.itemid where c.userid=uuid_to_bin(%s)",[session.get('userid')])
        cart_items=cursor.fetchall()
        print(cart_items)
        if not cart_items:
            return jsonify({"status":"failed","message":"Cart is Empty"}),400
        items_data=[]
        subtotal=0
        for item in cart_items:
            item_id = item[0]
            item_name = item[1]
            price = float(item[2])
            quantity = int(item[3])
            category = item[4]
            image_name = item[5]

            item_total = round(price * quantity, 2)
            subtotal += item_total

            items_data.append({
                "itemid": item_id,
                "itemname": item_name,
                "price": price,
                "quantity": quantity,
                "total": item_total,
                "image": url_for(
                    'static',
                    filename=f'uploads/{item[5]}',
                    _external=True
                ) if item[5] else None,
                "category": category
            })
        delivery=40
        tax=round(subtotal*0.05,2)
        grandtotal=delivery+tax+subtotal
        return jsonify({"status":"success","cart_items":items_data,"summary":{"delivery":delivery,"tax":tax,"grand_total":grandtotal,"subtotal":subtotal}}),200
    except Exception as e:
        return jsonify({"status":"'failed","message":f"could not view cart{str(e)}"})
    finally:
        if cursor:
            cursor.close()
@app.route('/cart/update',methods=['PUT'])
def cartupdate():
    cursor=None
    try:
        if not session.get('userid'):
            return jsonify({"status":"failed","message":"pls login first to addcart"}),401
        mydb.ping(reconnect=True)
        cursor=mydb.cursor(buffered=True)
        data=request.get_json()
        if not data:
            return  jsonify({"status":"failed","message":"No input data was given"}),400  
        itemid=data.get('itemid')
        print(itemid)
        quantity=data.get('quantity',1)
        try:
            quantity=int(quantity)
        except ValueError:
            return jsonify({"status":"failed","message":"quantity should be in integer"})
        userid=session.get('userid')
        #checking item existed in items
        cursor.execute("select bin_to_uuid(itemid),item_stock from items where itemid=uuid_to_bin(%s)",[itemid])
        item_data=cursor.fetchone()
        print(item_data)
        if not item_data:
            return jsonify({"status":"failed","message":"Item not found"}),400
        #quantity validation
        stored_quantity=item_data[1]
        if quantity > stored_quantity:
            return jsonify({"status":"failed","message":"item quantity is exceeded than stock amout"}),400
        #checking item alredy in cart
        cursor.execute("select cart_quantity from cart where itemid=uuid_to_bin(%s) and userid=uuid_to_bin(%s)",[itemid,userid])
        cart_item=cursor.fetchone()
        print(cart_item)
        if not cart_item:
            return jsonify({"status":"failed","message":"not item found cart"}),404
        cursor.execute('update cart set cart_quantity=%s where itemid=uuid_to_bin(%s) and userid=uuid_to_bin(%s)',[quantity,itemid,userid])
        mydb.commit()
        return jsonify({"status":"success","message":"cart item updated successfully"}),200
    except Exception as e:
        mydb.rollback()
        return jsonify({"status":"'failed","message":f"could not update cart quantity{str(e)}"})
    finally:
        if cursor:
            cursor.close()
@app.route('/cart/remove/<itemid>',methods=['DELETE'])
def cartremove(itemid):
    cursor=None
    try:
        if not session.get('userid'):
            return jsonify({"status":"failed","message":"pls login first to addcart"}),401
        mydb.ping(reconnect=True)
        cursor=mydb.cursor(buffered=True)
        userid=session.get('userid')
        #checking item existed in items
        cursor.execute("select bin_to_uuid(itemid),item_stock from items where itemid=uuid_to_bin(%s)",[itemid])
        item_data=cursor.fetchone()
        print(item_data)
        if not item_data:
            return jsonify({"status":"failed","message":"Item not found"}),400
        #checking item alredy in cart
        cursor.execute("select cart_quantity from cart where itemid=uuid_to_bin(%s) and userid=uuid_to_bin(%s)",[itemid,userid])
        cart_item=cursor.fetchone()
        if not cart_item:
            return jsonify({"status":"failed","message":"not item found cart"}),404
        cursor.execute('delete from cart where itemid=uuid_to_bin(%s) and userid=uuid_to_bin(%s)',[itemid,userid])
        mydb.commit()
        return jsonify({"status":"success","message":"cart item removed successfully"}),200
    except Exception as e:
        mydb.rollback()
        return jsonify({"status":"'failed","message":f"could not remove cart{str(e)}"})
    finally:
        if cursor:
            cursor.close()
@app.route('/payment',methods=['POST'])
def payment():
    cursor=None
    try:
        if not session.get('userid'):
            return jsonify({"status":"failed","message":"pls login first to payment"}),401
        data=request.get_json()
        if not data:
            return  jsonify({"status":"failed","message":"No input data was given"}),400  
        payment_type=data.get("type")
        mydb.ping(reconnect=True)
        cursor=mydb.cursor(buffered=True)
        userid=session.get('userid')
        if payment_type=='cart':
            cursor.execute("select bin_to_uuid(i.itemid),i.item_name,i.item_price,c.cart_quantity,i.item_category,i.item_imagename from items i inner join cart c on i.itemid=c.itemid where c.userid=uuid_to_bin(%s)",[session.get('userid')])
            cart_items=cursor.fetchall()
            print(cart_items)
        else:
            itemid=data.get('itemid')
            quantity=data.get('quantity')
            cursor.execute("select bin_to_uuid(itemid),item_name,item_price,item_category,item_imagename,item_stock from items where itemid=uuid_to_bin(%s)",[itemid])
            item_data=cursor.fetchone()
            print(item_data)
            if not item_data:
                return jsonify({"status":"failed","message":"Item not found"}),400
            #checking cart quantity
            available_stock=item_data[5]
            if available_stock < quantity:
                return jsonify({"status":"failed","message":"Item quantity exceeded than stock"}),401
            cart_items=[(item_data[0],item_data[1],item_data[2],quantity,item_data[3],item_data[4])]
        if not cart_items:
            return jsonify({"status":"fdailed","message":"No item data found"})
        items_data=[]
        subtotal=0
        for item in cart_items:
            item_id = item[0]
            item_name = item[1]
            price = float(item[2])
            quantity = int(item[3])
            category = item[4]
            image_name = item[5]

            item_total = round(price * quantity, 2)
            subtotal += item_total

            items_data.append({
                "itemid": item_id,
                "itemname": item_name,
                "price": price,
                "quantity": quantity,
                "total": item_total,
                "image": url_for(
                    'static',
                    filename=f'uploads/{item[5]}',
                    _external=True
                ) if item[5] else None,
                "category": category
            })
        delivery=40
        tax=round(subtotal*0.05,2)
        grandtotal=delivery+tax+subtotal
        razorpay_amount=grandtotal*100 #convert into paise
        order=client.order.create({
            "amount": razorpay_amount,
            "currency": "INR",
            "receipt": f"{session.get('useremail')}"
            })
        return jsonify({"status":"success","order":{"order_id":order['id'],"amount":order['amount'],"currency":order['currency']},"cart_items":items_data,"summary":{"delivery":delivery,"tax":tax,"grand_total":grandtotal,"subtotal":subtotal},"razorpay_key":"rzp_test_TtbMq1fCTuEuDJ"})
    except Exception as e:
        return jsonify({"status":"'failed","message":f"could not create order{str(e)}"})
    finally:
        if cursor:
            cursor.close()
@app.route('/payment/verify',methods=['POST'])
def verify_payment():
    cursor = None
    try:
        data = request.get_json()
        # -----------------------------------
        # GET FRONTEND DATA
        # -----------------------------------
        payment_id = data.get('razorpay_payment_id')
        order_id = data.get('razorpay_order_id')
        signature = data.get('razorpay_signature')
        mode = data.get('mode','cart')
        # -----------------------------------
        # VERIFY SIGNATURE
        # -----------------------------------
        params_dict = {
            'razorpay_order_id': order_id,

            'razorpay_payment_id': payment_id,

            'razorpay_signature': signature
        }
        try:
            client.utility.verify_payment_signature(params_dict)
        except Exception as e:
            print(e)
            return jsonify({'status': 'failed','message': 'Payment verification failed'}), 400
        # -----------------------------------
        # LOGIN VALIDATION
        # -----------------------------------
        if 'userid' not in session:

            return jsonify({'status': 'failed','message': 'Please login first'}), 401
        # reconnect automatically if mysql connection lost
        mydb.ping(reconnect=True)
        cursor = mydb.cursor(buffered=True)
        userid = session.get('userid')
        # -----------------------------------
        # GET CART ITEMS
        # -----------------------------------
        if mode == 'cart':
            cursor.execute('''select bin_to_uuid(i.itemid),i.item_name,i.item_price,c.cart_quantity,i.item_category,i.item_imagename from items i inner join cart c on i.itemid=c.itemid where c.userid=uuid_to_bin(%s)''',[session.get('userid')])
            cart_items = cursor.fetchall()
        # -----------------------------------
        # SINGLE BUY
        # -----------------------------------
        else:
            itemid = data.get('itemid')
            quantity = int(
                data.get('quantity', 1)
            )
            cursor.execute('select bin_to_uuid(i.itemid),i.item_name,i.item_price,i.item_category,i.item_imagename,item_stock from items i where i.itemid=uuid_to_bin(%s)',[itemid])
            item = cursor.fetchone()
            if not item:
                return jsonify({'status': 'failed','message': 'Item not found'}), 404
            available_stock = item[5]
            if quantity > available_stock:
                return jsonify({'status': 'failed','message': 'Insufficient stock'}), 400
            cart_items = [(item[0],item[1],item[2],quantity,item[3],item[4])]
        # -----------------------------------
        # EMPTY CHECK
        # -----------------------------------
        if not cart_items:

            return jsonify({'status': 'failed','message': 'Cart empty'}), 404
        # -----------------------------------
        # CALCULATE TOTAL
        # -----------------------------------

        subtotal = 0
        for item in cart_items:
            item_price = float(item[2])
            item_quantity = int(item[3])
            subtotal += (item_price * item_quantity)
        delivery = 40
        tax = round(subtotal * 0.05, 2)
        grand_total = subtotal + delivery + tax
        # -----------------------------------
        # STORE ORDER
        # -----------------------------------
        cursor.execute('''INSERT INTO orders(razorpay_ordid,razorpay_payment,userid,total_amount,delivery,tax,grand_total) VALUES(%s,%s,uuid_to_bin(%s),%s,%s,%s,%s)''',[order_id,payment_id,userid,subtotal,delivery,tax,grand_total])
        order_table_id = cursor.lastrowid
        # -----------------------------------
        # STORE ORDER ITEMS
        # -----------------------------------
        insert_item_query = '''INSERT INTO order_items(orderid,itemid,item_name,item_price,item_quantity,sub_total,item_category,item_imagename) VALUES(%s,uuid_to_bin(%s),%s,%s,%s,%s,%s,%s)'''
        ordered_items = []
        for item in cart_items:
            itemid = item[0]
            item_name = item[1]
            item_price = float(item[2])
            item_quantity = int(item[3])
            item_category = item[4]
            item_img = item[5]
            amount = item_price * item_quantity
            cursor.execute(insert_item_query,[order_table_id,str(itemid),item_name,item_price,item_quantity,amount,item_category,item_img])
            # reduce stock
            cursor.execute('''UPDATE items SET item_stock = item_stock - %s WHERE itemid=uuid_to_bin(%s)''',[item_quantity, itemid])
            ordered_items.append({

                'itemid': itemid,

                'itemname': item_name,

                'price': item_price,

                'quantity': item_quantity,

                'subtotal': amount
            })


        # -----------------------------------
        # CLEAR CART
        # -----------------------------------

        if mode == 'cart':
            cursor.execute('''DELETE FROM cart WHERE userid=uuid_to_bin(%s)''',[userid])
        mydb.commit()
        # -----------------------------------
        # SUCCESS RESPONSE
        # -----------------------------------
        return jsonify({

            'status': 'success',

            'message': 'Payment verified successfully',

            'payment': {

                'payment_id': payment_id,

                'order_id': order_id
            },

            'summary': {

                'subtotal': subtotal,

                'delivery': delivery,

                'tax': tax,

                'grand_total': grand_total
            },

            'ordered_items': ordered_items
        })
    except Exception as e:

        mydb.rollback()

        print(e)

        return jsonify({

            'status': 'failed',

            'message': str(e)

        }), 500


    finally:

        if cursor:
            cursor.close()
@app.route('/user/orders',methods=['GET'])       
def myorders():
    cursor=None
    try:
        if not session.get('userid'):
            return jsonify({"status":"failed","message":"pls login first view orders"}),401
        userid=session.get('userid')
        mydb.ping(reconnect=True)
        cursor=mydb.cursor(buffered=True)
        cursor.execute('select orderid,razorpay_ordid,razorpay_payment,total_amount,delivery,tax,grand_total,status from orders where userid=uuid_to_bin(%s)',[userid])
        myorders_data=cursor.fetchall()
        if not myorders_data:
            return jsonify({"status":"failed","message":"No orders found"}),400
        all_orders=[]
        for order in myorders_data:
            orderid=order[0]
            cursor.execute('select bin_to_uuid(itemid),item_name,item_price,item_quantity,sub_total,item_category,item_imagename from order_items where orderid=%s',[orderid])
            items_data=cursor.fetchall()
            if not items_data:
                return jsonify({"status":"failed","message":"No ordered items found"}),400
            order_items=[]
            for item in items_data:
                order_items.append({
                    "image":url_for('static',filename=f'uploads/{item[6]}',_external=True),
                    "itemid":item[0],
                    "itemname":item[1],
                    'price':item[2],
                    'quantity':item[3],
                    'subtotal':item[4],
                    'category':item[5]})
            all_orders.append({
                "orderid":order[0],
                "razorpay_order_id":order[1],
                "razorpay_payment_id":order[2],
                "subtotal":float(order[3]),
                "delivery":int(order[4]),
                "tax":float(order[5]),
                "grand_total":float(order[6]),
                "status":order[7],
                "items":order_items
            })
        return jsonify({"status":"success","orders":all_orders})
    except Exception as e:
        print(e)
        return jsonify({'status': 'failed','message': str(e)}), 500
    finally:
        if cursor:
            cursor.close()
@app.route('/user/ord_details/<ordid>',methods=['GET'])       
def myorder_details(ordid):
    cursor=None
    try:
        if not session.get('userid'):
            return jsonify({"status":"failed","message":"pls login first view orders"}),401
        userid=session.get('userid')
        mydb.ping(reconnect=True)
        cursor=mydb.cursor(buffered=True)
        cursor.execute('select orderid,razorpay_ordid,razorpay_payment,total_amount,delivery,tax,grand_total,status from orders where userid=uuid_to_bin(%s) and orderid=%s',[userid,ordid])
        myorders_data=cursor.fetchone() #(1,'razorpay-01')
        if not myorders_data:
            return jsonify({"status":"failed","message":"No orders found"}),400
        #------------------order format------------
        order_json={
            "orderid":myorders_data[0],
            "razorpay_order_id":myorders_data[1],
            "razorpay_payment_id":myorders_data[2],
            "subtotal":float(myorders_data[3]),
            "delivery":int(myorders_data[4]),
            "tax":float(myorders_data[5]),
            "grand_total":float(myorders_data[6]),
            "status":myorders_data[7]      
        }
        cursor.execute('select bin_to_uuid(itemid),item_name,item_price,item_quantity,sub_total,item_category,item_imagename from order_items where orderid=%s',[ordid])
        items_data=cursor.fetchall()
        if not items_data:
            return jsonify({"status":"failed","message":"No ordered items found"}),400
        items_json=[]
        for item in items_data:
            items_json.append({
            'order_id':ordid,
            "item_image":url_for('static',filename=f'uploads/{item[6]}',_external=True),
            "itemid":item[0],
            "item_name":item[1],
            'item_price':item[2],
            'item_quantity':item[3],
            'subtotal':item[4],
            'item_category':item[5]})
        return jsonify({"status":"success","orders":order_json,'items':items_json})
    except Exception as e:
        print(e)
        return jsonify({'status': 'failed','message': str(e)}), 500
    finally:
        if cursor:
            cursor.close()
@app.route(
    '/api/invoice/<int:ord_id>',
    methods=['GET']
)
def get_invoice(ord_id):

    cursor = None

    try:

        # ---------------- LOGIN CHECK ----------------
        if 'userid' not in session:

            return jsonify({

                'status': 'failed',

                'message': 'Please login first'

            }), 401


        # reconnect automatically if mysql connection lost
        mydb.ping(reconnect=True)

        cursor = mydb.cursor(buffered=True)


        userid = session.get('userid')


        # ---------------- GET ORDER ----------------
        cursor.execute(
            '''
            SELECT

                orderid,
                razorpay_ordid,
                razorpay_payment,
                total_amount,
                delivery,
                tax,
                grand_total,
                status

            FROM orders

            WHERE userid=uuid_to_bin(%s)
            AND orderid=%s
            ''',
            [userid, ord_id]
        )

        order_data = cursor.fetchone()


        if not order_data:

            return jsonify({

                'status': 'failed',

                'message': 'Order not found'

            }), 404


        # ---------------- GET ORDER ITEMS ----------------
        cursor.execute(
            '''
            SELECT

                item_name,
                item_price,
                item_quantity,
                sub_total,
                item_category

            FROM order_items

            WHERE orderid=%s
            ''',
            [ord_id]
        )

        order_items = cursor.fetchall()


        # ---------------- CREATE PDF BUFFER ----------------
        pdf_buffer = BytesIO()


        # ---------------- CREATE DOCUMENT ----------------
        doc = SimpleDocTemplate(

            pdf_buffer,

            pagesize=A4,

            rightMargin=30,

            leftMargin=30,

            topMargin=30,

            bottomMargin=20
        )


        styles = getSampleStyleSheet()

        elements = []


        # ---------------- TITLE ----------------
        title = Paragraph(

            "<b>BUYROUTE INVOICE</b>",

            styles['Title']
        )

        elements.append(title)

        elements.append(Spacer(1, 15))


        # ---------------- ORDER DETAILS ----------------
        order_info = f"""

        <b>Order ID:</b> {order_data[0]} <br/>

        <b>Razorpay Order ID:</b> {order_data[1]} <br/>

        <b>Payment ID:</b> {order_data[2]} <br/>

        <b>Order  status:</b> {order_data[7]} <br/>

        """


        order_para = Paragraph(

            order_info,

            styles['BodyText']
        )

        elements.append(order_para)

        elements.append(Spacer(1, 10))

        elements.append(HRFlowable(width="100%"))

        elements.append(Spacer(1, 15))


        # ---------------- TABLE DATA ----------------
        table_data = [[

            'Item Name',

            'Category',

            'Price',

            'Quantity',

            'Subtotal'
        ]]


        for item in order_items:

            table_data.append([

                item[0][0:20],

                item[4],

                f"₹{float(item[1])}",

                str(item[2]),

                f"₹{float(item[3])}"
            ])


        # ---------------- CREATE TABLE ----------------
        table = Table(

            table_data,

                              colWidths=[180, 100, 80, 70, 80]
        )


        # ---------------- TABLE STYLE ----------------
        table.setStyle(

            TableStyle([

                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0d6efd')),

                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),

                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),

                ('FONTSIZE', (0, 0), (-1, -1), 10),

                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),

                ('GRID', (0, 0), (-1, -1), 1, colors.black),

                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),

                ('ALIGN', (2, 1), (-1, -1), 'CENTER')
            ])
        )

        elements.append(table)

        elements.append(Spacer(1, 20))


        # ---------------- SUMMARY ----------------
        summary = f"""

        <b>Items Total:</b> ₹{float(order_data[3])}<br/><br/>

        <b>Delivery:</b> ₹{float(order_data[4])}<br/><br/>

        <b>Tax:</b> ₹{float(order_data[5])}<br/><br/>

        <b>Grand Total:</b> ₹{float(order_data[6])}

        """


        summary_para = Paragraph(

            summary,

            styles['Heading3']
        )

        elements.append(summary_para)

        elements.append(Spacer(1, 25))


        # ---------------- FOOTER ----------------
        footer = Paragraph(

            "Thank you for shopping with BUYROUTE",

            styles['Italic']
        )

        elements.append(footer)


        # ---------------- BUILD PDF ----------------
        doc.build(elements)

        pdf_buffer.seek(0)


        # ---------------- RESPONSE ----------------
        response = make_response(

            pdf_buffer.getvalue()
        )

        response.headers['Content-Type'] = 'application/pdf'

        response.headers['Content-Disposition'] = (

            f'attachment; filename=invoice_{ord_id}.pdf'
        )

        return response


    except Exception as e:

        print(f'Invoice Error: {e}')

        return jsonify({

            'status': 'failed',

            'message': str(e)

        }), 500


    finally:

        if cursor:
            cursor.close()
@app.route('/user/forgotpassword', methods=['POST'])
def forgotpassword():

    data = request.get_json()
    f_email = data.get('email')

    cursor = mydb.cursor(buffered=True)

    cursor.execute(
        'select count(*) from userdata where user_email=%s',
        [f_email]
    )

    count_email = cursor.fetchone()

    if count_email[0] == 1:

        reset_link = f"{url_for('resetpassword',token=endata(f_email),_external=True)}"

        subject = "Reset Password Link"
        body = f"Click the link to reset password:\n{reset_link}"

        send_mail(
            to=f_email,
            subject=subject,
            body=body
        )

        return {
            "status": "success",
            "message": "Reset link sent successfully"
        }, 200

    return {
        "status": "error",
        "message": "Email not found"
    }, 404
@app.route('/user/resetpassword/<token>', methods=['GET', 'POST'])
def resetpassword(token):

    if request.method == 'GET':
        return redirect(
            f"http://localhost:5173/new-password?token={token}"
        )

    if request.method == 'POST':

        data = request.get_json()

        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')

        if not new_password or not confirm_password:
            return {
                "status": "error",
                "message": "Please enter both passwords"
            }, 400

        if new_password != confirm_password:
            return {
                "status": "error",
                "message": "Passwords do not match"
            }, 400
        try:
            email = dndata(token)

            cursor = mydb.cursor(buffered=True)

            cursor.execute(
                "SELECT COUNT(*) FROM userdata WHERE user_email=%s",
                [email]
            )

            result = cursor.fetchone()
            print(result[0])
            if result[0] != 1:
                return {
                    "status": "error",
                    "message": "Invalid email"
                }, 404

            # Hash password before storing it
            hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')

            cursor.execute(
                "UPDATE userdata SET user_userpassword=%s WHERE user_email=%s",
                [hashed_password, email]
            )

            mydb.commit()

            return {
                "status": "success",
                "message": "Password changed successfully"
            }, 200

        except Exception as e:
            print(str(e))
            mydb.rollback()

            return {
                "status": "error",
                "message": "Invalid or expired reset link"
            }, 400

if __name__=="__main__":
    app.run(0)