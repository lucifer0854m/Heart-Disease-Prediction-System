from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from health.views import *
from .apirep import routerep

urlpatterns = [
    path('api/v1/', include(routerep.urls)),
    path('admin/', admin.site.urls),

    # Public Pages
    path('', home, name="home"),
    path('about/', about, name="about"),
    path('contact/', contact, name="contact"),
    path('gallery/', gallery, name="gallery"),

    # Authentication
    path('login/', login_user, name="login"),
    path('login_admin/', login_admin, name="login_admin"),
    path('signup/', signup_user, name="signup"),
    path('logout/', logout_user, name="logout"),
    path('change_password/', change_password, name="change_password"),

    # Home Views
    path('patient_home/', user_home, name="patient_home"),
    path('doctor_home/', doctor_home, name="doctor_home"),
    path('admin_home/', admin_home, name="admin_home"),

    # Doctor Management
    path('view_doctor/', view_doctor, name="view_doctor"),
    path('add_doctor/', add_doctor, name="add_doctor"),
    path('change_doctor/<int:pid>/', add_doctor, name="change_doctor"),
    path('edit_doctor/<int:pid>/', edit_doctor, name="edit_doctor"),
    path('delete_doctor/<int:pid>/', delete_doctor, name="delete_doctor"),
    path('assign_status/<int:pid>/', assign_status, name="assign_status"),

    # Patient Management
    path('view_patient/', view_patient, name="view_patient"),
    path('delete_patient/<int:pid>/', delete_patient, name="delete_patient"),

    # Heart Disease Prediction
    path('add_heartdetail/', add_heartdetail, name="add_heartdetail"),
    path('predict_disease/<str:pred>/<str:accuracy>/', predict_disease, name="predict_disease"),
    path('view_search_pat/', view_search_pat, name="view_search_pat"),
    path('delete_searched/<int:pid>/', delete_searched, name="delete_searched"),

    # Feedback
    path('view_feedback/', view_feedback, name="view_feedback"),
    path('delete_feedback/<int:pid>/', delete_feedback, name="delete_feedback"),
    path('sent_feedback/', sent_feedback, name="sent_feedback"),

    # Profile Management
    path('edit_profile/', edit_my_detail, name="edit_profile"),
    # urls.py
    

    path('profile_doctor/', view_my_detail, name="profile_doctor"),
]

# Media Files
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
