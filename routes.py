from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import random
from flask import jsonify, make_response, request, send_file
from sqlalchemy import extract, func
from datetime import datetime, timedelta
from database import Cycle, Days, Notes, Partner, Period, Sleep, Symptons,app,db,User



@app.route('/get_user', methods=['POST'])
def check_email():
    data = request.json
    email_to_check = data.get('email')
    password = data.get('password')
    print(email_to_check)
    print(password)

    

    if email_to_check:
        user = User.query.filter_by(email=email_to_check,password = password).first()
        if user:
            if(user.partner == "True"):
                partner = Partner.query.filter_by(uid = user.uid).first()
                print(user.cycleRange)
                user = {
                'userID':user.uid,
                'name':user.firstName,
                "lastname":user.lastName,
                "email":user.email,
                "dob":user.dob,
                "phone":user.mobileno,
                "cycleRange":user.cycleRange,
                "partner":True,
                "periodRange":user.periodRange,
                "partnerName":partner.firstName,
                "partnerLastName":partner.lastName,
                "partnerMobileno":partner.mobileno,
                "partnerEmail":partner.email,
                "periodStartDate":user.periodStartDate,
                "periodEndDate":user.periodEndDate,
                "cycleDate":user.cycleStartDate,
                "cycleEndDate":user.cycleEndDate,

                }
            else:
                user = {
                'userID':user.uid,
                'name':user.firstName,
                "lastname":user.lastName,
                "email":user.email,
                "dob":user.dob,
                "phone":user.mobileno,
                "cycleRange":user.cycleRange,
                "partner":False,
                "periodRange":user.periodRange,
                "periodStartDate":user.periodStartDate,
                "periodEndDate":user.periodEndDate,
                "cycleDate":user.cycleStartDate,
                "cycleEndDate":user.cycleEndDate,
                }





            return jsonify({'exists': True, 'message': 'Email exists in the database','user':user}), 200
        
        else : 
            return jsonify({'exists': False, 'message': 'Email does not exist in the database'}), 200
    else:
        return jsonify({'error': 'Email not provided in the request'}), 400



@app.route("/partnerLogin",methods=['POST'])
def partnerLogin():
   
    data = request.json
    
    email = data.get("email")
    password = data.get("password")
    partner = Partner.query.filter_by(email = email, password = password).first()
    if partner:
        user = User.query.filter_by(uid = partner.uid).first()
        user = {
                'userID':user.uid,
                'name':user.firstName,
                "lastname":user.lastName,
                "email":user.email,
                "dob":user.dob,
                "phone":user.mobileno,
                "cycleRange":user.cycleRange,
                "partner":True,
                "periodRange":user.periodRange,
                "partnerName":partner.firstName,
                "partnerLastName":partner.lastName,
                "partnerMobileno":partner.mobileno,
                "partnerEmail":partner.email,
                "periodStartDate":user.periodStartDate[0:11],
                "periodEndDate":user.periodEndDate[0:11],
                "cycleDate":user.cycleStartDate[0:11],
                "cycleEndDate":user.cycleEndDate[0:11],

                }
        


        return jsonify({'exists': True, 'message': 'Email does exist in the database','user':user}), 200
    else : 
        return jsonify({'exists': False, 'message': 'Email does not exist in the database'}), 200

    



'''
"firstName": name,
      "lastName": lastName,
      "email": email,
      "mobileno": phone,
      "dob": dob,
        "cycleStartDate": cycleStartDate,
        "cycleEndDate": cycleEndDate,
        "cycleRange": cycleRange,
        "periodStartDate": periodStartDate,
        "periodEndDate": periodEndDate,
        "periodRange": periodRange
'''

def create_user_and_cycle_period(data):
    try:
        # Extract user information
        user_data = {
            'firstName': data['firstName'],
            'lastName': data['lastName'],
            'email': data['email'],
            'password':data['password'],
            'mobileno': data.get('mobileno'),
            'dob': datetime.strptime(data['dob'], '%b %d, %Y'),
            'cycleRange': data.get('cycleRange'),
            'periodRange': data.get('periodRange'),
            'partner': data.get('partner'),
            "periodStartDate":data['userPeriodEndDate'],
             "periodEndDate":data['userPeriodEndDate'],
            "cycleStartDate":data['userCycleStartDate'], 
             "cycleEndDate":data['userCycleEndDate'],
}


        # Create User
        new_user = User(**user_data)
        db.session.add(new_user)
        db.session.flush()

        cycle_data = {
            'uid': new_user.uid,
            'startdate': datetime.strptime(data['cycleStartDate'], '%Y-%m-%dT%H:%M:%S.%f'),  
             'enddate': datetime.strptime(data['cycleEndDate'], '%Y-%m-%dT%H:%M:%S.%f'),# Corrected format
            'range': data['cycleRange']
        }

        # Create 100 Cycles
        csd = cycle_data['startdate']
        ced = cycle_data['enddate']
        


        for _ in range(2):
            ran = random.randint(2,5)
            psd = csd  
            ped = psd + timedelta(days = ran)
            cycledata = {
            'uid': new_user.uid,
            'startdate': csd, 
            'enddate' : ced,
            'range': ((ced - csd)).days
            }
            new_cycle = Cycle(**cycledata)
            db.session.add(new_cycle)
            db.session.flush()

            period_data = {
                 'uid': new_user.uid,
                'cID': new_cycle.cID,
                'startdate': psd,  
                'enddate':ped,
                'range': (ped - psd).days
            }
            new_period = Period(**period_data)
            db.session.add(new_period)
            r = ((ced - csd)).days
            csd = ced 
            ced = ced + timedelta(days=r)


     
        db.session.commit()

        

        return True, new_user.uid  
    except Exception as e:
        print(f"Error: {str(e)}")
        db.session.rollback()
        return False, None  



@app.route('/cycle_range', methods=['GET'])
def get_current_month_data():
    try:
        uid = request.args.get('uID')
        
        current_date = datetime.now()
        start_date = datetime(current_date.year, current_date.month, 1)
        end_date = datetime(current_date.year, current_date.month + 1, 1) - timedelta(days=1)
        previous_start_date = start_date - timedelta(days=1)  # Adjusted for the previous month
        previous_end_date = start_date - timedelta(days=1)

        previous_cycle = Cycle.query.filter(Cycle.uid == uid, Cycle.startdate <= previous_end_date, Cycle.enddate >= previous_start_date).first()
        previous_period = Period.query.join(Cycle).filter(Period.uid == uid, Cycle.startdate <= previous_end_date, Cycle.enddate >= previous_start_date).first()

        cycle = Cycle.query.filter(Cycle.uid == uid,Cycle.startdate <= end_date, Cycle.enddate >= start_date).first()
        period = Period.query.join(Cycle).filter(Period.uid == uid,Cycle.startdate <= end_date, Cycle.enddate >= start_date).first()

        if previous_cycle is None and previous_period is None:
            result = {
                'cycles': {'start_date': cycle.startdate, 'end_date': cycle.enddate, 'range': cycle.range+1, 'variation': 0},
                'periods': {'start_date': period.startdate, 'end_date': period.enddate, 'range': 1+ period.range, 'variation': 0}
            }
        else:
            result = {
                'cycles': {'start_date': cycle.startdate, 'end_date': cycle.enddate, 'range': cycle.range+1, 'variation': cycle.range - previous_cycle.range},
                'periods': {'start_date': period.startdate, 'end_date': period.enddate, 'range': period.range+1, 'variation': period.range - previous_period.range}
            }
        
        a = result['cycles']
        print(a['range']);

        return jsonify(result), 200

    except Exception as e:
        # Log the error using a logging library
        print(f"Error: {str(e)}")
        return jsonify({'error': 'Internal Server Error'}), 500




# @app.route('/updateperiods', methods=['POST'])
# def update_periods():
#     data = request.json
#     start_date = data['periodStartDate']
#     end_date = data['periodEndDate']
#     userid = data['userID']
#     range = data['periodRange']
#     print(start_date)
#     print(end_date)


#     cycle_data = {
#             'uid': userid,
#             'startdate': datetime.strptime(start_date, '%Y-%m-%dT%H:%M:%S.%f'),  
#              'enddate': datetime.strptime(start_date, '%Y-%m-%dT%H:%M:%S.%f')+timedelta(days=28),
#             'range': 28
#         }
    
#     new_cycle = Cycle(**cycle_data)
#     db.session.add(new_cycle)
#     db.session.flush()

#     period_data = {
#                  'uid': userid,
#                 'cID': new_cycle.cID,
#                 'startdate': datetime.strptime(start_date, '%Y-%m-%dT%H:%M:%S.%f'),  
#                 'enddate':datetime.strptime(end_date, '%Y-%m-%dT%H:%M:%S.%f'),
#                 'range': range
#             }
#     new_period = Period(**period_data)
#     db.session.add(new_period)

#     db.session.commit()

#     return jsonify({'result': True}),201



@app.route('/updateperiods', methods=['POST'])
def update_period():
    # Get user input
    new_start_date = request.json.get('periodStartDate')
    new_end_date = request.json.get('periodEndDate')
    user_id = request.json.get("userID")
    range = request.json.get('periodRange')
    
    new_start_date = datetime.strptime(new_start_date, '%Y-%m-%dT%H:%M:%S.%f')
    new_end_date = datetime.strptime(new_end_date, '%Y-%m-%dT%H:%M:%S.%f')

    start_range = new_start_date - timedelta(days=5)
    end_range = new_end_date + timedelta(days=5)

    existing_period = Period.query.filter(Period.startdate >= start_range, Period.enddate <= end_range, Period.uid==user_id).first()
    print(existing_period)
    if existing_period:
        # Update existing period
        existing_period.startdate = new_start_date
        existing_period.enddate = new_end_date
        db.session.commit()
        return jsonify({'message': 'Existing period updated successfully'}), 200
    else:
        # Create a new period
        cycle_data = {
            'uid': user_id,
            'startdate': new_start_date,
            'enddate': new_end_date + timedelta(days=28),  # Assuming a 28-day cycle
            'range': 28  # Assuming a 28-day cycle
        }
     
        new_cycle = Cycle(**cycle_data)
        db.session.add(new_cycle)
        db.session.flush()
        new_period = Period(uid=user_id, cID=new_cycle.cID, range=range, startdate=new_start_date, enddate=new_end_date)
        db.session.add(new_period)
        db.session.commit()
        return jsonify({'message': 'New period added successfully'}), 201
    


@app.route('/users', methods=['POST'])
def create_user():
    data = request.json
    result, uid = create_user_and_cycle_period(data)
    
    if result:
        return jsonify({'result': result, 'message': 'User created successfully', 'uid': uid}),201
    else:
        return jsonify({'result': result, 'message': 'Failed to create user'}),201



@app.route('/delete', methods=['GET'])
def delete_all_data():
    try:
        # Delete all records from each table
        db.session.query(User).delete()
        db.session.query(Cycle).delete()
        db.session.query(Period).delete()
        db.session.query(Days).delete()
        db.session.query(Notes).delete()
        db.session.query(Symptons).delete()
        db.session.query(Partner).delete()

        # Commit the changes
        db.session.commit()

        return jsonify({'message': 'All data deleted successfully'}), 200
    except Exception as e:
        print(f"Error: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to delete data'}), 500
    

@app.route('/create_note', methods=['POST'])
def create_note():
    try:
        data = request.json
        uid = data.get('uid')
        date = data.get('date')
        note_text = data.get('note')

        user = User.query.get(uid)
        if user:
            new_note = Notes(uid=uid, date=date, note=note_text)
            db.session.add(new_note)
            db.session.commit()
            return jsonify({'result': True, 'message': 'Note created successfully'}), 201  # 201 Created
        else:
            return jsonify({'result': False, 'message': 'User not found'}), 404  # 404 Not Found

    except Exception as e:
        print(f"Error: {str(e)}")
        db.session.rollback()
        return jsonify({'result': False, 'message': f'Failed to create note. Error: {str(e)}'}), 500  






@app.route('/get_notes', methods=['GET'])
def get_notes():
    uid = request.args.get('uID')
    date = request.args.get('date')

    try:
        notes = Notes.query.filter_by(uid = uid,date = date).all()
        note_list = [note.note for note in notes]
        return jsonify({'result': True, 'notes': note_list})
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'result': False, 'message': 'Failed to get notes'})


@app.route("/delete_note", methods=['POST'])
def deleteNote():
    data = request.json
    uid = data.get('uid')
    date = data.get('date')
    note = data.get('note')

    note = Notes.query.filter_by(uid=uid, date=date, note = note).first()
    if note:
        db.session.delete(note)
        db.session.commit()
        return jsonify({'result': True, 'message': 'note deleted successfully'}), 201
    else:
        return jsonify({'result': False, 'message': 'note not found'}), 404

@app.route("/delete_symptoms", methods=['POST'])
def deleteSymptoms():
    data = request.json
    uid = data.get('uid')
    date = data.get('date')
    symptoms = data.get('sympton')

    symptom = Symptons.query.filter_by(uid=uid, date=date, symptons=symptoms).first()
    if symptom:
        db.session.delete(symptom)
        db.session.commit()
        return jsonify({'result': True, 'message': 'Symptoms deleted successfully'}), 201
    else:
        return jsonify({'result': False, 'message': 'Symptoms not found'}), 404
    

@app.route('/add_sleep', methods=['POST'])
def add_sleep():
    data = request.json

    uid = data.get('uid')
    date = data.get('date')
    sleep = data.get('sleep')

    try:
        new_sleep = Sleep(uid=uid, date=date, sleep=sleep)
        db.session.add(new_sleep)
        db.session.commit()

        return jsonify({'result': True, 'message': 'Symptoms added successfully'}), 201
    except Exception as e:
        print(f"Error: {str(e)}")
        db.session.rollback()
        return jsonify({'result': False, 'message': 'Failed to add symptoms'}), 500


@app.route('/add_symptoms', methods=['POST'])
def add_symptoms():
    data = request.json

    uid = data.get('uid')
    date = data.get('date')
    symptons = data.get('sympton')

    try:
    

        new_symptom = Symptons(uid=uid, date=date, symptons=symptons)
        db.session.add(new_symptom)
        db.session.commit()

        return jsonify({'result': True, 'message': 'Symptoms added successfully'}),201
    except Exception as e:
        print(f"Error: {str(e)}")
        db.session.rollback()
        return jsonify({'result': False, 'message': 'Failed to add symptoms'}),500




@app.route('/get_symptoms', methods=['GET'])
def get_symptoms():
    uid = request.args.get('uID')
    date = request.args.get('date')
   

    try:
        symptons = Symptons.query.filter_by(uid = uid,date = date).all()
        symptons_list = [sympton.symptons for sympton in symptons]
        
        return jsonify({'result': True, 'symptoms':symptons_list})
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'result': False, 'message': 'Failed to get notes'})
    

   

@app.route('/get_sleep', methods=['GET'])
def get_sleep():
    uid = request.args.get('uID')
    date = request.args.get('date')

    try:
        sleep_records = Sleep.query.filter_by(uid=uid, date=date).all()
        sleep_list = [record.sleep for record in sleep_records]

        return jsonify({'result': True, 'symptoms': sleep_list})
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'result': False, 'message': 'Failed to get sleep records'})





# Read all users
@app.route('/users', methods=['GET'])
def get_all_users():
    users = User.query.all()
    user_list = [{'uid': user.uid, 'firstName': user.firstName, 'lastName': user.lastName, 'email': user.email,
                  'mobileno': user.mobileno} for user in users]
    return jsonify({'users': user_list})

# Read a specific user
@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get(user_id)
    if user:
        user_data = {'uid': user.uid, 'firstName': user.firstName, 'lastName': user.lastName, 'email': user.email,
                     'mobileno': user.mobileno}
        return jsonify({'user': user_data})
    return jsonify({'message': 'User not found'}), 404



@app.route('/get_periods', methods=['GET'])
def get_periods():
    uid = request.args.get('uID')
    periods = Period.query.filter_by(uid = uid).all()
    periods_data = []
    for period in periods:
        periods_data.append({
            'startdate': period.startdate,
            'enddate': period.enddate
        })
    # print(periods_data)
    return jsonify(periods_data),200



# Update a user
@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = User.query.get(user_id)
    if user:
        data = request.json
        user.firstName = data.get('firstName', user.firstName)
        user.lastName = data.get('lastName', user.lastName)
        user.email = data.get('email', user.email)
        user.mobileno = data.get('mobileno', user.mobileno)
        db.session.commit()
        return jsonify({'message': 'User updated successfully'})
    return jsonify({'message': 'User not found'}), 404

# Delete a user
@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'User deleted successfully'})
    return jsonify({'message': 'User not found'}), 404


@app.route('/update_profile', methods=['POST'])
def update_profile():
    try:
        data = request.json
        name = data.get('name')
        lastname = data.get('lastname')
        dob = data.get('dob')
        phone = data.get('phone')
        userid = data.get('userID')
        
        user = User.query.filter_by(uid=userid).first()
        user.firstName = name
        user.lastName = lastname
        user.dob = dob
        user.mobileno = phone
        db.session.commit()

        return jsonify({'result': True}), 200

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': 'Internal Server Error'}), 500


@app.route('/add_partner', methods=['POST'])
def add_partner():
    try:
        data = request.json
        name = data.get('name')
        lastname = data.get('lastname')
        email = data.get('email')
        phone = data.get('phone')
        userid = data.get('userID')
        password = data.get('password')

        user = User.query.filter_by(uid = userid).first()
        user.partner = "True"

        partner = Partner(uid = userid,firstName = name,lastName = lastname,email = email,mobileno = phone,password = password)
        db.session.add(partner)
        db.session.commit()

        return jsonify({'result': True}), 200

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': 'Internal Server Error'}), 500
    
@app.route('/update_partner', methods=['POST'])
def update_partner():
    try:
        data = request.json
        name = data.get('name')
        lastname = data.get('lastname')
        email = data.get('email')
        phone = data.get('phone')
        userid = data.get('userID')
        password = data.get('password')
        
        partner = Partner.query.filter_by(uid=userid).first()
        partner.firstName = name
        partner.lastName = lastname
        partner.email = email
        partner.mobileno = phone
        partner.password = password
        db.session.commit()

        return jsonify({'result': True}), 200

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': 'Internal Server Error'}), 500
    




@app.route('/add_day', methods=['POST'])
def add_day():
    data = request.get_json()

    new_day = Days(
        uid=data['uid'],
        day=data['day'],
        date=data['endDate'],
        today=data['date'],
        symptons=data['symptons'],
        description=data['description'],
        cycleUpdate1=data['cycleUpdate1'],
        cycleUpdate2=data['cycleUpdate2'],
        ovdays = data["ovdays"],
        nextPeriods = data['nextPeriods']
    )

    db.session.add(new_day)
    db.session.commit()

    return jsonify({'message': 'Day added successfully'}), 201         
            
@app.route('/get_date', methods=['GET'])
def get_day():
    uid = request.args.get('uID')
    date = request.args.get('date')

    print(date == "2024-02-04")

    try:
        day = Days.query.filter_by(uid = uid,today = date).first()
        print(day.day)
        return  jsonify({
            'message': 'Day details retrieved successfully',
            'day': {
                'uid': day.uid,
                'day': day.day,
                'date': day.date,
                'today': day.today,
                'symptons': day.symptons,
                'description': day.description,
                'cycleUpdate1': day.cycleUpdate1,
                'cycleUpdate2': day.cycleUpdate2,
                "ovdays":day.ovdays,
                "nextPeriods":day.nextPeriods
            }
        }), 200
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'result': False, 'message': 'Failed to get notes'})

@app.route("/delete_sleep", methods=['POST'])
def deleteSleep():
    data = request.json
    uid = data.get('uid')
    date = data.get('date')
    sleep = data.get('sympton')

    symptom = Sleep.query.filter_by(uid=uid, date=date, sleep= sleep).first()
    if symptom:
        db.session.delete(symptom)
        db.session.commit()
        return jsonify({'result': True, 'message': 'Symptoms deleted successfully'}), 201
    else:
        return jsonify({'result': False, 'message': 'Symptoms not found'}), 404
    

@app.route('/report_symptoms', methods=['GET'])
def get_symptoms_for_current_month():
    current_month = datetime.now().month
    current_year = datetime.now().year
    symptoms = Symptons.query.filter(
        func.strftime('%m', Symptons.date) == str(current_month).zfill(2),
        func.strftime('%Y', Symptons.date) == str(current_year)
    ).all()
    symptom_list = [symptom.symptons for symptom in symptoms]
    return jsonify(symptom_list)


@app.route('/report_notes', methods=['GET'])
def report_notes():
    # Fetch notes for the current month
    current_month = datetime.now().strftime('%Y-%m')
    notes = Notes.query.filter(Notes.date.startswith(current_month)).all()

    # Format notes as a list of strings
    notes_list = [note.note for note in notes]

    return jsonify(notes_list)


@app.route('/report_sleep', methods=['GET'])
def report_sleep():
    # Fetch sleep data for the current month
    current_month = datetime.now().strftime('%Y-%m')
    sleep_data = Sleep.query.filter(Sleep.date.startswith(current_month)).all()

    # Format sleep data as a list of strings
    sleep_list = [data.sleep for data in sleep_data]

    return jsonify(sleep_list)


@app.route('/generate_report', methods=['POST'])
def generate_report():
    # Get data from request
    data = request.json
    name = data.get('name', 'Unknown')
    period_range = data.get('period_range', 0)
    cycle_range = data.get('cycle_range', 0)
    symptoms = data.get('symptoms', [])
    notes = data.get('notes', [])
    sleep = data.get('sleep', [])

    # Create PDF
    pdf_file = 'report.pdf'
    c = canvas.Canvas(pdf_file, pagesize=letter)
    c.drawString(100, 750, f"Name: {name}")
    c.drawString(100, 730, f"Period Range: {period_range}")
    c.drawString(100, 710, f"Cycle Range: {cycle_range}")
    c.drawString(100, 690, "Symptoms:")
    for i, symptom in enumerate(symptoms, start=1):
        c.drawString(120, 670 - i * 20, f"{i}. {symptom}")
    c.drawString(100, 450, "Notes:")
    for i, note in enumerate(notes, start=1):
        c.drawString(120, 430 - i * 20, f"{i}. {note}")
    c.drawString(100, 210, "Sleep:")
    for i, s in enumerate(sleep, start=1):
        c.drawString(120, 190 - i * 20, f"{i}. {s}")
    c.save()

    return send_file(pdf_file, as_attachment=True)