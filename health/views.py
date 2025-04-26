from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
import datetime

from sklearn.ensemble import GradientBoostingClassifier
from .forms import DoctorForm
from .models import *
from django.contrib.auth import authenticate, login, logout
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style('darkgrid')

from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
from sklearn.model_selection import train_test_split
from django.http import HttpResponse

# View for home page
def home(request):
    return render(request, 'carousel.html')

# Admin Home View
@login_required(login_url='login')
def admin_home(request):
    dis = Search_Data.objects.all()
    pat = Patient.objects.all()
    doc = Doctor.objects.all()
    feed = Feedback.objects.all()

    d = {'dis': dis.count(), 'pat': pat.count(), 'doc': doc.count(), 'feed': feed.count()}
    return render(request, 'admin_home.html', d)

# Admin functionality to change doctor status
@login_required(login_url="login")
def assign_status(request, pid):
    doctor = Doctor.objects.get(id=pid)
    if doctor.status == 1:
        doctor.status = 2
        messages.success(request, 'Selected doctor has successfully withdrawn their approval.')
    else:
        doctor.status = 1
        messages.success(request, 'Selected doctor has successfully been approved.')
    doctor.save()
    return redirect('view_doctor')

# User Home View
@login_required(login_url="login")
def user_home(request):
    return render(request, 'patient_home.html')

# Doctor Home View
@login_required(login_url="login")
def doctor_home(request):
    return render(request, 'doctor_home.html')

# About page view
def about(request):
    return render(request, 'about.html')

# Contact page view
def contact(request):
    return render(request, 'contact.html')

# Gallery page view
def gallery(request):
    return render(request, 'gallery.html')

# Login User view
def login_user(request):
    error = ""
    if request.method == "POST":
        u = request.POST['uname']
        p = request.POST['pwd']
        user = authenticate(username=u, password=p)
        sign = ""
        if user:
            try:
                sign = Patient.objects.get(user=user)
            except:
                pass
            if sign:
                login(request, user)
                error = "pat1"
            else:
                pure = False
                try:
                    pure = Doctor.objects.get(status=1, user=user)
                except:
                    pass
                if pure:
                    login(request, user)
                    error = "pat2"
                else:
                    login(request, user)
                    error = "notmember"
        else:
            error = "not"
    return render(request, 'login.html', {'error': error})

# Login Admin view
def login_admin(request):
    error = ""
    if request.method == "POST":
        u = request.POST['uname']
        p = request.POST['pwd']
        user = authenticate(username=u, password=p)
        if user and user.is_staff:
            login(request, user)
            error = "pat"
        else:
            error = "not"
    return render(request, 'admin_login.html', {'error': error})

# User signup view
def signup_user(request):
    error = ""
    if request.method == 'POST':
        f = request.POST['fname']
        l = request.POST['lname']
        u = request.POST['uname']
        e = request.POST['email']
        p = request.POST['pwd']
        d = request.POST['dob']
        con = request.POST['contact']
        add = request.POST['add']
        type = request.POST['type']
        im = request.FILES['image']
        user = User.objects.create_user(email=e, username=u, password=p, first_name=f, last_name=l)
        if type == "Patient":
            Patient.objects.create(user=user, contact=con, address=add, image=im, dob=d)
        else:
            Doctor.objects.create(dob=d, image=im, user=user, contact=con, address=add, status=2)
        error = "create"
    return render(request, 'register.html', {'error': error})

# Logout User view
def logout_user(request):
    logout(request)
    return redirect('home')

# Change Password view
@login_required(login_url="login")
def change_password(request):
    sign = 0
    user = User.objects.get(username=request.user.username)
    error = ""
    try:
        sign = Patient.objects.get(user=user)
        error = "pat"
    except:
        sign = Doctor.objects.get(user=user)
    terror = ""
    if request.method == "POST":
        n = request.POST['pwd1']
        c = request.POST['pwd2']
        o = request.POST['pwd3']
        if c == n:
            u = User.objects.get(username__exact=request.user.username)
            u.set_password(n)
            u.save()
            terror = "yes"
        else:
            terror = "not"
    return render(request, 'change_password.html', {'error': error, 'terror': terror, 'data': sign})

# Function to preprocess inputs for machine learning model
def preprocess_inputs(df, scaler):
    df = df.copy()
    y = df['target'].copy()
    X = df.drop('target', axis=1).copy()
    X = pd.DataFrame(scaler.fit_transform(X), columns=X.columns)
    return X, y

# Predict Heart Disease function
def predict_heart_disease(list_data):
    csv_file = Admin_Helath_CSV.objects.get(id=1)
    df = pd.read_csv(csv_file.csv_file)

    X = df[['age', 'sex', 'cp', 'trestbps', 'chol', 'fbs', 'restecg', 'thalach', 'exang', 'oldpeak', 'slope', 'ca', 'thal']]
    y = df['target']
    X_train, X_test, y_train, y_test = train_test_split(X, y, train_size=0.8, random_state=0)
    nn_model = GradientBoostingClassifier(n_estimators=100, learning_rate=1.0, max_depth=1, random_state=0)
    nn_model.fit(X_train, y_train)
    pred = nn_model.predict([list_data])
    accuracy = nn_model.score(X_test, y_test) * 100
    print(f"Neural Network Accuracy: {accuracy:.2f}%")
    print(f"Predicted Value is: {pred}")
    return accuracy, pred

# Add Doctor view
@login_required(login_url="login")
def add_doctor(request, pid=None):
    doctor = None
    if pid:
        doctor = Doctor.objects.get(id=pid)
    if request.method == "POST":
        form = DoctorForm(request.POST, request.FILES, instance=doctor)
        if form.is_valid():
            new_doc = form.save()
            new_doc.status = 1
            if not pid:
                user = User.objects.create_user(password=request.POST['password'], username=request.POST['username'], first_name=request.POST['first_name'], last_name=request.POST['last_name'])
                new_doc.user = user
            new_doc.save()
            return redirect('view_doctor')
    return render(request, 'add_doctor.html', {'doctor': doctor})

# Add Heart Disease Detail view
@login_required(login_url="login")
def add_heartdetail(request):
    if request.method == "POST":
        list_data = []
        value_dict = eval(str(request.POST)[12:-1])  # Parse POST data
        count = 0
        for key, value in value_dict.items():
            if count == 0:
                count = 1
                continue
            if key == "sex" and value[0] in ["Male", "male", "m", "M"]:
                list_data.append(0)
            else:
                list_data.append(1)
            list_data.append(value[0])

        accuracy, pred = predict_heart_disease(list_data)
        patient = Patient.objects.get(user=request.user)
        Search_Data.objects.create(patient=patient, prediction_accuracy=accuracy, result=pred[0], values_list=list_data)
        rem = int(pred[0])
        pred = "<span style='color:green'>You are healthy</span>" if pred[0] == 0 else "<span style='color:red'>You are Unhealthy, Need to Checkup.</span>"
        return redirect('predict_desease', str(rem), str(accuracy))
    return render(request, 'add_heartdetail.html')

# Predict Disease view
@login_required(login_url="login")
def predict_disease(request, pred, accuracy):
    doctor = Doctor.objects.filter(address__icontains=Patient.objects.get(user=request.user).address)
    return render(request, 'predict_disease.html', {'pred': pred, 'accuracy': accuracy, 'doctor': doctor})

# View for searching patients
@login_required(login_url="login")
def view_search_pat(request):
    doc = None
    try:
        doc = Doctor.objects.get(user=request.user)
        data = Search_Data.objects.filter(patient__address__icontains=doc.address).order_by('-id')
    except:
        try:
            doc = Patient.objects.get(user=request.user)
            data = Search_Data.objects.filter(patient=doc).order_by('-id')
        except:
            data = Search_Data.objects.all().order_by('-id')
    return render(request, 'view_search_pat.html', {'data': data})

# Deleting doctor view
@login_required(login_url="login")
def delete_doctor(request, pid):
    doc = Doctor.objects.get(id=pid)
    doc.delete()
    return redirect('view_doctor')

# Deleting feedback view
@login_required(login_url="login")
def delete_feedback(request, pid):
    doc = Feedback.objects.get(id=pid)
    doc.delete()
    return redirect('view_feedback')

# Deleting patient view
@login_required(login_url="login")
def delete_patient(request, pid):
    doc = Patient.objects.get(id=pid)
    doc.delete()
    return redirect('view_patient')

# Deleting searched record view
@login_required(login_url="login")
def delete_searched(request, pid):
    doc = Search_Data.objects.get(id=pid)
    doc.delete()
    return redirect('view_search_pat')

# View Doctors list
@login_required(login_url="login")
def view_doctor(request):
    doc = Doctor.objects.all()
    return render(request, 'view_doctor.html', {'doc': doc})

# View Patients list
@login_required(login_url="login")
def view_patient(request):
    patient = Patient.objects.all()
    return render(request, 'view_patient.html', {'patient': patient})

# View Feedback list
@login_required(login_url="login")
def view_feedback(request):
    dis = Feedback.objects.all()
    return render(request, 'view_feedback.html', {'dis': dis})

# View My Details page
@login_required(login_url="login")
def view_my_detail(request):
    terror = ""
    user = User.objects.get(id=request.user.id)
    error = ""
    try:
        sign = Patient.objects.get(user=user)
        error = "pat"
    except:
        sign = Doctor.objects.get(user=user)
    return render(request, 'profile_doctor.html', {'error': error, 'pro': sign})

# Edit Doctor details
@login_required(login_url="login")
def edit_doctor(request, pid):
    doc = Doctor.objects.get(id=pid)
    error = ""
    if request.method == 'POST':
        f = request.POST['fname']
        l = request.POST['lname']
        e = request.POST['email']
        con = request.POST['contact']
        add = request.POST['add']
        cat = request.POST['type']
        try:
            im = request.FILES['image']
            doc.image = im
            doc.save()
        except:
            pass
        doc.user.first_name = f
        doc.user.last_name = l
        doc.user.email = e
        doc.contact = con
        doc.category = cat
        doc.address = add
        doc.user.save()
        doc.save()
        error = "create"
    return render(request, 'edit_doctor.html', {'error': error, 'doc': doc})

# Edit Profile details for Doctor or Patient
@login_required(login_url="login")
def edit_my_detail(request):
    terror = ""
    user = User.objects.get(id=request.user.id)
    error = ""
    try:
        sign = Patient.objects.get(user=user)
        error = "pat"
    except:
        sign = Doctor.objects.get(user=user)
    if request.method == 'POST':
        f = request.POST['fname']
        l = request.POST['lname']
        e = request.POST['email']
        con = request.POST['contact']
        add = request.POST['add']
        try:
            im = request.FILES['image']
            sign.image = im
            sign.save()
        except:
            pass
        sign.user.first_name = f
        sign.user.last_name = l
        sign.user.email = e
        sign.contact = con
        if error != "pat":
            cat = request.POST['type']
            sign.category = cat
            sign.save()
        sign.address = add
        sign.user.save()
        sign.save()
        terror = "create"
    return render(request, 'edit_profile.html', {'error': error, 'terror': terror, 'doc': sign})

# Sent Feedback view
@login_required(login_url='login')
def sent_feedback(request):
    terror = None
    if request.method == "POST":
        username = request.POST['uname']
        message = request.POST['msg']
        username = User.objects.get(username=username)
        Feedback.objects.create(user=username, messages=message)
        terror = "create"
    return render(request, 'sent_feedback.html', {'terror': terror})
