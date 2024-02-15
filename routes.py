
from flask import jsonify, request
from sqlalchemy.orm.exc import NoResultFound
import razorpay
from datetime import datetime, timedelta
from database import Cycle, Days, Notes, Partner, Period, Symptons,app,db,User



@app.route('/get_user', methods=['POST'])
def check_email():
    data = request.json
    email_to_check = data.get('email')
    password = data.get('password')

    print(email_to_check)
    print(password)
    

    if email_to_check:
        user = User.query.filter_by(email=email_to_check,password = password).first()
        print(user)
        partner = Partner.query.filter_by(email = email_to_check,password = password).first()
        if user:
            if(user.partner == "True"):
                partner = Partner.query.filter_by(uid = user.uid).first()
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
                "partnerEmail":partner.email

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
                }





            return jsonify({'exists': True, 'message': 'Email exists in the database','user':user}), 200
        elif partner:
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
                "partnerEmail":partner.email

                }
        


            return jsonify({'exists': True, 'message': 'Email does not exist in the database','user':user}), 200
        else : 
            return jsonify({'exists': False, 'message': 'Email does not exist in the database'}), 200
    else:
        return jsonify({'error': 'Email not provided in the request'}), 400





# Fighter on 31 Jan ticket booking done

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
            'partner': data.get('partner')
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
        


        for _ in range(100):

            psd = csd
            ped = psd + timedelta(days=data['periodRange'])
            cycledata = {
            'uid': new_user.uid,
            'startdate': csd, 
            'enddate' : ced,
            'range': data['cycleRange']
            }
            new_cycle = Cycle(**cycledata)
            db.session.add(new_cycle)
            db.session.flush()

            period_data = {
                 'uid': new_user.uid,
                'cID': new_cycle.cID,
                'startdate': psd,  
                'enddate':ped,
                'range': data['periodRange']
            }
            new_period = Period(**period_data)
            db.session.add(new_period)
            csd = ced
            ced = ced + timedelta(days=data['cycleRange'])


        # Commit changes
        db.session.commit()

        

        return True, new_user.uid  # Data added successfully, return uid
    except Exception as e:
        print(f"Error: {str(e)}")
        db.session.rollback()
        return False, None  # Failed to add data to the database



@app.route('/cycle_range', methods=['GET'])
def get_current_month_data():
    try:
        current_date = datetime.now()
        start_date = datetime(current_date.year, current_date.month, 1)
        end_date = datetime(current_date.year, current_date.month + 1, 1) - timedelta(days=1)

        print(start_date)
        print(end_date)

        previous_start_date = start_date - timedelta(days=1)  # Adjusted for the previous month
        previous_end_date = start_date - timedelta(days=1)

        previous_cycle = Cycle.query.filter(Cycle.startdate <= previous_end_date, Cycle.enddate >= previous_start_date).first()
        previous_period = Period.query.join(Cycle).filter(Cycle.startdate <= previous_end_date, Cycle.enddate >= previous_start_date).first()

        cycle = Cycle.query.filter(Cycle.startdate <= end_date, Cycle.enddate >= start_date).first()
        period = Period.query.join(Cycle).filter(Cycle.startdate <= end_date, Cycle.enddate >= start_date).first()

        if previous_cycle is None and previous_period is None:
            result = {
                'cycles': {'start_date': cycle.startdate, 'end_date': cycle.enddate, 'range': cycle.range, 'variation': 0},
                'periods': {'start_date': period.startdate, 'end_date': period.enddate, 'range': period.range, 'variation': 0}
            }
        else:
            result = {
                'cycles': {'start_date': cycle.startdate, 'end_date': cycle.enddate, 'range': cycle.range, 'variation': cycle.range - previous_cycle.range},
                'periods': {'start_date': period.startdate, 'end_date': period.enddate, 'range': period.range, 'variation': period.range - previous_period.range}
            }
        
        a = result['cycles']
        print(a['range']);

        return jsonify(result), 200

    except Exception as e:
        # Log the error using a logging library
        print(f"Error: {str(e)}")
        return jsonify({'error': 'Internal Server Error'}), 500

    except Exception as e:
        # Log the error using a logging library
        print(f"Error: {str(e)}")
        return jsonify({'error': 'Internal Server Error'}), 500



@app.route('/updateperiods', methods=['POST'])
def update_periods():
    data = request.json
    start_date = data['periodStartDate']
    end_date = data['periodEndDate']
    userid = data['userID']
    range = data['periodRange']
    print(start_date)
    print(end_date)


    cycle_data = {
            'uid': userid,
            'startdate': datetime.strptime(start_date, '%Y-%m-%dT%H:%M:%S.%f'),  
             'enddate': datetime.strptime(start_date, '%Y-%m-%dT%H:%M:%S.%f')+timedelta(days=28),
            'range': 28
        }
    
    new_cycle = Cycle(**cycle_data)
    db.session.add(new_cycle)
    db.session.flush()

    period_data = {
                 'uid': userid,
                'cID': new_cycle.cID,
                'startdate': datetime.strptime(start_date, '%Y-%m-%dT%H:%M:%S.%f'),  
                'enddate':datetime.strptime(end_date, '%Y-%m-%dT%H:%M:%S.%f'),
                'range': range
            }
    new_period = Period(**period_data)
    db.session.add(new_period)

    db.session.commit()

    return jsonify({'result': True}),201


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



@app.route('/add_symptoms', methods=['POST'])
def add_symptoms():
    data = request.json

    uid = data.get('uid')
    date = data.get('date')
    symptons = data.get('sympton')

    try:
        # Assuming you have a User model
        # You should perform necessary validations here, such as checking if the user exists
        # and handling other error scenarios

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
        print(symptons_list)
        return jsonify({'result': True, 'symptoms':symptons_list})
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'result': False, 'message': 'Failed to get notes'})



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
        cycleUpdate2=data['cycleUpdate2']
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
                'cycleUpdate2': day.cycleUpdate2
            }
        }), 200
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'result': False, 'message': 'Failed to get notes'})

