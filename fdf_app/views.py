from django.shortcuts import render
from string import Template
import smtplib
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart

# Test

# Create your views here.
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from .forms import KursForm, ExerciseForm
from . import models
from . import forms
from .leistungsnachweise import pdf
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.http import HttpResponse
import random
import string
from django.contrib.auth import logout, authenticate, login
from datetime import datetime
import json
from django.utils import timezone
from uuid import uuid4


class ExercisesModel:
    def __init__(
        self,
        new_execution,
        new_name,
        new_dauer,
        new_videoPath,
        new_looping,
        new_added,
        new_instruction,
        new_timer,
        new_required,
        new_imagePath,
        new_appId,
        new_id,
    ):
        self.execution = new_execution
        self.name = new_name
        self.dauer = new_dauer
        self.videoPath = new_videoPath
        self.looping = new_looping
        self.added = new_added
        self.instruction = new_instruction
        self.timer = new_timer
        self.required = new_required
        self.imagePath = new_imagePath
        self.appId = new_appId
        self.id = new_id


def logout_view(request):
    if request.method == "GET":
        logout(request)
        return redirect(
            "login"
        )  # Hier 'login' durch den Namen deiner Login-URL ersetzen
    else:
        # Du könntest hier auch eine eigene Logout-Seite rendern
        # return render(request, 'logout.html')
        pass


def random_string(length=100):
    characters = string.ascii_letters + string.digits + string.punctuation
    random_string = "".join(random.choice(characters) for _ in range(length))
    return random_string


def display_login_code(request, logintoken=None):
    return render(request, "laxout_app/display_code.html", {"login_token": logintoken})


# Create your views here.
@login_required(login_url="login")
def home(request):
    active_admin = models.UserProfile.objects.get(user=request.user)
    active_admin_user = active_admin.user
    print("Active Admin id{}".format(active_admin_user.is_superuser))
    users_filtert = models.LaxoutUser.objects.filter(created_by=request.user)
    user_amount = users_filtert.count()

    active_user_amount = 0
    for user in users_filtert:
        print(str(user.last_login.date) + "Last Login date")
        if days_between_today_and_date(user.last_login) < 14:
            active_user_amount += 1

    programms = models.Kursprogramm.objects.all()
    programm_list = []
    for programm in programms:
        if programm.created_by == request.user:
            programm_list.append(programm)

    context = {
        "users": programm_list,
        "user_amount": user_amount,
        "active_user_amount": active_user_amount,
        "is_superuser": active_admin_user.is_superuser,
    }
    return render(request, "laxout_app/home.html", context)


@login_required(login_url="login")
def create_exercise(request):
    if request.method == "POST":
        try:
            first = request.POST.get("first")
            second = request.POST.get("second")
        except json.JSONDecodeError as e:
            print("Error in Json Decode")

        form = ExerciseForm(request.POST)

        if form.is_valid():
            print("krass")
            exercise_instance = form.save(commit=False)
            exercise_instance.save()

            # Add First and Second instances
            if first is not None:
                exercise_instance.first.add(models.First.objects.create(first=first))
            if second is not None:
                exercise_instance.second.add(
                    models.Second.objects.create(second=second)
                )
            exercise_instance.second.add(models.Second.objects.create(second=7))

            print(exercise_instance)
            return redirect("/")  # Redirect to the exercise list view
    else:
        form = ExerciseForm()

    return render(request, "laxout_app/create_exercise.html", {"form": form})


def set_exercises_user(user_id, predicted_exercises):
    programm = models.Kursprogramm.objects.get(id=user_id)
    for i in predicted_exercises:
        programm.exercises.add(i)
    programm.save()
    print("Hich")
    print(programm.exercises.all())


# anpassen
def send_user_welcome_email(email, vorname, nachname, straße, hausnummer, stadt, postleitzahl, kurs ):
    # SMTP-Verbindungsinformationen
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_username = "laxoutapp@gmail.com"
    smtp_password = "aliy rfnz mtmx xwif"

    # E-Mail-Inhalte
    sender_email = "laxoutapp@gmail.com"
    receiver_email = email
    subject = "Herzlich Willkommen"
    link = kurs
    

    # HTML-Inhalt der E-Mail
    html_template = Template(
        """
    <!DOCTYPE html>
<html lang="de">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Willkommen bei FitdurchFriedrich</title>
    <style>
        .wave {
            position: absolute;
            bottom: 0;
            left: 0;
            width: 100%;
            height: auto;
            z-index: -1;
        }
    </style>
</head>

<body style="font-family: Arial, sans-serif; position: relative;">

    <!-- Wellenförmige Trennlinie -->
    <svg class="wave" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1440 320">
        <path fill="rgb(243, 242, 244)" fill-opacity="1"
            d="M0,224L48,234.7C96,245,192,267,288,240C384,213,480,139,576,138.7C672,139,768,213,864,229.3C960,245,1056,203,1152,170.7C1248,139,1344,117,1392,106.7L1440,96L1440,320L1392,320C1344,320,1248,320,1152,320C1048,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z">
        </path>
    </svg>
    <!-- Firmenlogo -->
    <div style="display: flex; justify-content: center; flex-direction: column; align-items: center;">
        <div style="text-align: center; margin-bottom: 20px;">
            <img src="https://laxoutapp.com/wp-content/uploads/elementor/thumbs/laxoutLogo-qotzscn3a91cexwuwp0vxxolrnp0fd708p9e4ql7cy.png"
                alt="Firmenlogo" style="max-width: 200px;">
        </div>

        <!-- Willkommensnachricht -->
        <div style="text-align: center; margin-bottom: 20px;">
            <h1>Willkommen!</h1>
            <p>Vielen Dank für Ihre Anmeldung beim Kursprogramm von FdF. Wir freuen uns, Sie als Nutzer der App begrüßen
                zu dürfen.
            </p>
            <p>Für die Nutzung der App bitten wir Sie, den in der Rechnung (befindet sich im Anhang) genannten
                Betrag an unser Firmenkonto zu überweisen.</p>
            <p>Dannach können Sie sich die App herunterladen und mit Ihrem Training beginnen!</p>
            <p>Die Kurs ID-welche Sie für das anmelden der App benötigen finden Sie hier:</p>
            <div style="text-align: center; margin: 50px;">
                <button
                    style="height: 50px; width: 140px; border-radius: 10px; background-color: white; border: solid 3px rgb(255, 111, 1); color: black; cursor: pointer;">
                    <a href="" style="text-decoration: none; color: rgb(255, 111, 1);">${link}</a>
                </button>
            </div>
            <p>Viel Spaß wünscht Ihnen</p>
            <br>
            <p>FdF</p>
        </div>

        <!-- Social-Media-Icons -->
        <div style="display: flex; flex-direction: row; margin-bottom: 20px;">

            <div style="display: flex;flex-direction: column; align-items: center;">
                <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" fill="currentColor" class="bi bi-apple"
                    viewBox="0 0 16 16">
                    <path
                        d="M11.182.008C11.148-.03 9.923.023 8.857 1.18c-1.066 1.156-.902 2.482-.878 2.516s1.52.087 2.475-1.258.762-2.391.728-2.43m3.314 11.733c-.048-.096-2.325-1.234-2.113-3.422s1.675-2.789 1.698-2.854-.597-.79-1.254-1.157a3.7 3.7 0 0 0-1.563-.434c-.108-.003-.483-.095-1.254.116-.508.139-1.653.589-1.968.607-.316.018-1.256-.522-2.267-.665-.647-.125-1.333.131-1.824.328-.49.196-1.422.754-2.074 2.237-.652 1.482-.311 3.83-.067 4.56s.625 1.924 1.273 2.796c.576.984 1.34 1.667 1.659 1.899s1.219.386 1.843.067c.502-.308 1.408-.485 1.766-.472.357.013 1.061.154 1.782.539.571.197 1.111.115 1.652-.105.541-.221 1.324-1.059 2.238-2.758q.52-1.185.473-1.282" />
                    <path
                        d="M11.182.008C11.148-.03 9.923.023 8.857 1.18c-1.066 1.156-.902 2.482-.878 2.516s1.52.087 2.475-1.258.762-2.391.728-2.43m3.314 11.733c-.048-.096-2.325-1.234-2.113-3.422s1.675-2.789 1.698-2.854-.597-.79-1.254-1.157a3.7 3.7 0 0 0-1.563-.434c-.108-.003-.483-.095-1.254.116-.508.139-1.653.589-1.968.607-.316.018-1.256-.522-2.267-.665-.647-.125-1.333.131-1.824.328-.49.196-1.422.754-2.074 2.237-.652 1.482-.311 3.83-.067 4.56s.625 1.924 1.273 2.796c.576.984 1.34 1.667 1.659 1.899s1.219.386 1.843.067c.502-.308 1.408-.485 1.766-.472.357.013 1.061.154 1.782.539.571.197 1.111.115 1.652-.105.541-.221 1.324-1.059 2.238-2.758q.52-1.185.473-1.282" />
                </svg>
                <a style="margin-top: 10px;" href="https://testflight.apple.com/join/9gAa2LDT">Download</a>
            </div>

            <div style="width: 50px;">

            </div>

            <div style="display: flex;flex-direction: column; align-items: center;">
                <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" fill="currentColor"
                    class="bi bi-google-play" viewBox="0 0 16 16">
                    <path
                        d="M14.222 9.374c1.037-.61 1.037-2.137 0-2.748L11.528 5.04 8.32 8l3.207 2.96zm-3.595 2.116L7.583 8.68 1.03 14.73c.201 1.029 1.36 1.61 2.303 1.055zM1 13.396V2.603L6.846 8zM1.03 1.27l6.553 6.05 3.044-2.81L3.333.215C2.39-.341 1.231.24 1.03 1.27" />
                </svg>
                <a style="margin-top: 10px;" href="https://play.google.com/store/apps/details?id=com.appprojekt123.laxout">Download</a>

            </div>
        </div>

        <!-- Footer-Text -->
        <small style="text-align: center; margin-bottom: 50px;">©2024 FdF, Steffen Friedrich, Firmensitz:
            Brünnsteinstraße 49, 85435
            Erding. Alle Rechte vorbehalten.</small>
    </div>


</body>

</html>
    """
    )

    # Erstellen der MIME-Multipart-Nachricht
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject

    # Hinzufügen des HTML-Inhalts zur Nachricht
    html_content = html_template.substitute(link=link)
    msg.attach(MIMEText(html_content, "html"))
    billing_model, created = models.BillingCount.objects.get_or_create(id=1)
    billing_count = str(billing_model.billing_count)
    new_billing_count = billing_model.billing_count + 1
    billing_model.billing_count = new_billing_count
    billing_model.save()
    current_billing_id = ""
    how_many_zeros = 12 - len(billing_count)
    for i in range(how_many_zeros):
        current_billing_id += "0"
    current_billing_id += billing_count
    # Produktion
    # /home/dashboardlaxout/backup_laxout/laxout_app/leistungsnachweise/
    # Dev
    # D:/DEV/laxout_backend_development/laxout/laxout_app/leistungsnachweise/
    print(f"Current billing Id {current_billing_id}")
    input_pdf_path = "D:/fdf/fdf_django/fdf/fdf_app/leistungsnachweise/leistungsnachweis_vorlage.pdf"  # Passe den Pfad zur vorhandenen PDF-Datei an D:/DEV/laxout_backend_development/laxout/laxout_app/leistungsnachweise/leistungsnachweis
    output_pdf_path = f"D:/fdf/fdf_django/fdf/fdf_app/leistungsnachweise/leistungsnachweis_{current_billing_id}.pdf"  # Passe den Pfad für die neu erstellte PDF-Datei an
    pdf.modifyPdf(input_pdf_path, output_pdf_path, current_billing_id, vorname, nachname, straße, hausnummer, stadt, postleitzahl)
    # Pfad zur PDF-Datei
    pdf_attachment_path = f"D:/fdf/fdf_django/fdf/fdf_app/leistungsnachweise/leistungsnachweis_{current_billing_id}.pdf"

    # Hinzufügen der PDF-Datei als Anhang
    with open(pdf_attachment_path, "rb") as pdf_attachment:
        part = MIMEApplication(pdf_attachment.read(), "pdf")
        part.add_header(
            "Content-Disposition", f"attachment; filename= {pdf_attachment_path}"
        )
        msg.attach(part)

    # SMTP-Verbindung und Versenden der E-Mail
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())


def generate_code():
    return "".join([str(random.randint(0, 9)) for _ in range(6)])


@login_required(login_url="login")
def create_programm(request):
    active_admin = models.UserProfile.objects.get(user=request.user)
    active_admin_user = active_admin.user
    if request.method == "POST":
        form = KursForm(request.POST)
        if form.is_valid():
            insteance = form.save(commit=False)
            insteance.created_by = request.user
            new_programm_number = generate_code()
            while models.Kursprogramm.objects.filter(
                programm_number=new_programm_number
            ).exists():
                new_programm_number = generate_code()
            insteance.programm_number = new_programm_number
            insteance.save()
            note = request.POST.get("selected_illness")
            if form.cleaned_data.get("note") is "":
                print("Note was None")
                insteance.note = note
            insteance.save()
            exercises = []
            print(f"note{note}")

            ai_training_data = models.AiTrainingData.objects.filter(illness=note).last()
            if ai_training_data != None:
                predicted_exercises_ids = []

                for i in ai_training_data.related_exercises.all():
                    predicted_exercises_ids.append(i.exercise_id)

                for i in predicted_exercises_ids:

                    # es wird geschaut, ob es schon eine Reihenfolge gibt
                    if i != 0 and i < len(models.Uebungen_Models.objects.all()):
                        print("AI predicted exercise")
                        exercise_to_add = models.Laxout_Exercise.objects.create(
                            execution=models.Uebungen_Models.objects.get(
                                id=i
                            ).execution,
                            name=models.Uebungen_Models.objects.get(id=i).name,
                            dauer=models.Uebungen_Models.objects.get(id=i).dauer,
                            videoPath=models.Uebungen_Models.objects.get(
                                id=i
                            ).videoPath,
                            looping=models.Uebungen_Models.objects.get(id=i).looping,
                            added=False,
                            instruction="",
                            timer=models.Uebungen_Models.objects.get(id=i).timer,
                            required=models.Uebungen_Models.objects.get(id=i).required,
                            imagePath=models.Uebungen_Models.objects.get(
                                id=i
                            ).imagePath,
                            appId=models.Uebungen_Models.objects.get(id=i).id,
                            onlineVideoPath=models.Uebungen_Models.objects.get(
                                id=i
                            ).onlineVideoPath,
                        )
                        exercises.append(exercise_to_add)

            set_exercises_user(insteance.id, exercises)
            print(exercises)
            print(insteance.id)
            # print(lax_ai.predict_exercise(note))
            return redirect("/home")

    else:
        ilness_list_obj = models.AiTrainingData.objects.all()
        ilness_list = []
        for i in ilness_list_obj:
            if i.illness not in ilness_list:
                filterd_objects = ilness_list_obj.filter(illness=i.illness)
                item = filterd_objects.last()
                print(item.illness)
                ilness_list.append(item.illness)

        form = KursForm()
        return render(
            request,
            "laxout_app/create_programm.html",
            {
                "form": form,
                "is_superuser": active_admin_user.is_superuser,
                "illness_list": ilness_list,
            },
        )


@login_required(login_url="login")
def create_customer(request):
    active_admin = models.UserProfile.objects.get(user=request.user)
    active_admin_user = active_admin.user
    if request.method == "POST":
        form = forms.CustomerForm(request.POST)
        if form.is_valid():
            vorname = form.cleaned_data["vorname"]
            nachname = form.cleaned_data["nachname"]
            straße = form.cleaned_data["straße"]
            hausnummer = form.cleaned_data["hausnummer"]
            email = form.cleaned_data["email"]
            stadt = form.cleaned_data["stadt"]
            postleitzahl = form.cleaned_data["postleitzahl"]
            kurs_string = form.cleaned_data["kurs"]

        print(f"Kurs String:{kurs_string}")

        selected_programm = models.Kursprogramm.objects.get(name = kurs_string)
        if selected_programm == None:
            print("SCheiße")
        kurs = selected_programm.programm_number
        print(f"Kurs String:{kurs}")
        send_user_welcome_email(email, vorname, nachname, straße, hausnummer, stadt, postleitzahl, kurs )

        return redirect("/home")
    else:
        kurse = models.Kursprogramm.objects.all()
        programm_list = []
        for i in kurse:
            if i.name not in programm_list:
                filterd_objects = kurse.filter(name=i.name)
                item = filterd_objects.last()
                print(item.name)
                programm_list.append(item.name)
        print("TZessafjhasjf")
        print(programm_list)
        form = KursForm()
        return render(
            request,
            "laxout_app/create_customer.html",
            {
                "form": form,
                "is_superuser": active_admin_user.is_superuser,
                "programm_list": programm_list,
            },
        )


@login_required(login_url="login")
def delete_user(request, id=None):
    if id != None:
        object_to_delte = models.LaxoutUser.objects.get(id=id)
        if request.user == object_to_delte.created_by:
            for exercis in object_to_delte.exercises.all():
                exercis.delete()
            for index in models.IndexesLaxoutUser.objects.filter(created_by=id).all():
                index.delete()
            for coupon in object_to_delte.coupons.all():
                coupon.delete()
            for doneWorkout in models.DoneWorkouts.objects.filter(
                laxout_user_id=id
            ).all():
                doneWorkout.delete()
            for skippedExercise in models.SkippedExercises.objects.filter(
                laxout_user_id=id
            ).all():
                skippedExercise.delete()
            for doneExercise in models.DoneExercises.objects.filter(
                laxout_user_id=id
            ).all():
                doneExercise.delete()
            for doneWorkout in models.DoneWorkouts.objects.filter(
                laxout_user_id=id
            ).all():
                doneWorkout.delete()
            for order in models.Laxout_Exercise_Order_For_User.objects.filter(
                laxout_user_id=id
            ).all():
                order.delete()
            for pain in models.LaxoutUserPains.objects.filter(created_by=id).all():
                pain.delete()
            models.SuccessControll.objects.filter(created_by=id).delete()
            object_to_delte.delete()
        return redirect("/home")
    return redirect("/home")


@login_required(login_url="login")
def delete_kursprogramm(request, id=None):
    if id != None:
        object_to_delte = models.Kursprogramm.objects.get(id=id)
        if request.user == object_to_delte.created_by:
            for exercis in object_to_delte.exercises.all():
                exercis.delete()
            for order in models.Laxout_Exercise_Order_For_User.objects.filter(
                laxout_user_id=id
            ).all():
                order.delete()
            object_to_delte.delete()
        return redirect("/home")
    return redirect("/home")


@login_required(login_url="login")
def edit_programm(request, id=None):
    programm = models.Kursprogramm.objects.get(id=id)
    ###skip logik###

    current_exercises = programm.exercises.all()
    if programm.note != "":
        old_training_data = models.AiTrainingData.objects.filter(
            created_for=programm.id
        )
        for i in old_training_data:
            i.related_exercises.all().delete()
        old_training_data.delete()
        ai_training_data = models.AiTrainingData.objects.create(
            illness=programm.note, created_by=request.user.id, created_for=programm.id
        )

    current_order_objects = models.Laxout_Exercise_Order_For_User.objects.filter(
        laxout_user_id=id
    )  # es wird geschaut, ob es schon eine Reihenfolge gibt

    print(f"ids der geradigen order:")
    for i in current_order_objects:
        print(i.laxout_exercise_id)

    if len(current_order_objects) == 0 and len(current_exercises) != 0:
        print("There was a diffenrence")
        order = 1
        for i in current_exercises:
            models.Laxout_Exercise_Order_For_User.objects.create(
                laxout_user_id=id, laxout_exercise_id=i.id, order=order
            )

            order += 1
        print("length")
        print(len(models.Laxout_Exercise_Order_For_User.objects.all()))

    print("LENGTH ORDER OBJECTS{}".format(len(current_order_objects)))

    users_exercises_skipped = []

    list_order_objects = models.Laxout_Exercise_Order_For_User.objects.filter(
        laxout_user_id=id
    )
    # print("LIST Skipped LENGTH {}".format(skipped_exercises))
    sorted_list = sorted(
        list_order_objects, key=lambda x: x.order
    )  # Werden der größe nach Sotiert
    # print("Sorted List {}".format(sorted_list))
    exercise_ids = []

    for i in sorted_list:
        exercise_ids.append(i.laxout_exercise_id)

    for order in sorted_list:
        # print("RELEVANT ERROR ID")
        # print(order.laxout_exercise_id)
        try:
            ai_training_data.related_exercises.add(
                models.AiExercise.objects.create(
                    exercise_id=models.Laxout_Exercise.objects.get(
                        id=order.laxout_exercise_id
                    ).appId
                )
            )
            exercise = models.Laxout_Exercise.objects.get(id=order.laxout_exercise_id)
            users_exercises_skipped.append(
                ExercisesModel(
                    new_added=exercise.added,
                    new_appId=exercise.appId,
                    new_dauer=exercise.dauer,
                    new_execution=exercise.execution,
                    new_imagePath=exercise.imagePath,
                    new_instruction=exercise.instruction,
                    new_looping=exercise.looping,
                    new_name=exercise.name,
                    new_required=exercise.required,
                    new_timer=exercise.timer,
                    new_videoPath=exercise.videoPath,
                    new_id=exercise.id,
                )
            )

        except:
            print("EXEPTION THROUGH DELETE AFTER AI GENERATION OF EXERCISES")

    print(
        "LENGHT EXERCISE LIST {}".format(users_exercises_skipped)
    )  # sie heißen nur skipped weil die skipped logik drinnen steckt, sind aber die ganz normalen Übungen
    print("Exercise ids from user with note:{}".format(programm.note))
    for i in users_exercises_skipped:
        print(i.appId)

    related_customers = models.LaxoutUser.objects.filter(belongs_to_programm_number = programm.programm_number)

    context = {
        "related_customers": related_customers,
        "customer_count":len(related_customers),
        "user": programm,
        "users": programm,
        "workouts": users_exercises_skipped,
        "int": programm.instruction_in_int,
    }

    return render(
        request,
        "laxout_app/edit_programm.html",
        context,
    )


def get_workout_list(first, second):
    to_return = []
    uebungen_to_append = []
    exercises_to_browse = models.Uebungen_Models.objects.all()
    # Nacken
    if first == 0 and second == 0:
        for i in exercises_to_browse:
            all_firsts = i.first.all()
            all_second = i.second.all()
            if (
                all_firsts.filter(first=0).exists()
                and all_second.filter(second=0).exists()
            ):
                to_return.append(i)

    if first == 0 and second == 1:
        for i in exercises_to_browse:
            all_firsts = i.first.all()
            all_second = i.second.all()
            if (
                all_firsts.filter(first=0).exists()
                and all_second.filter(second=1).exists()
            ):
                to_return.append(i)
    if first == 0 and second == 2:
        for i in exercises_to_browse:
            all_firsts = i.first.all()
            all_second = i.second.all()
            if (
                all_firsts.filter(first=0).exists()
                and all_second.filter(second=2).exists()
            ):
                to_return.append(i)
    if first == 0 and second == 7:
        for i in exercises_to_browse:
            all_firsts = i.first.all()
            all_second = i.second.all()
            if (
                all_firsts.filter(first=0).exists()
                and all_second.filter(second=7).exists()
            ):
                to_return.append(i)
    # Schultern
    if first == 1 and second == 0:
        for i in exercises_to_browse:
            all_firsts = i.first.all()
            all_second = i.second.all()
            if (
                all_firsts.filter(first=1).exists()
                and all_second.filter(second=0).exists()
            ):
                to_return.append(i)
    if first == 1 and second == 1:
        for i in exercises_to_browse:
            all_firsts = i.first.all()
            all_second = i.second.all()
            if (
                all_firsts.filter(first=1).exists()
                and all_second.filter(second=1).exists()
            ):
                to_return.append(i)
    if first == 1 and second == 2:
        for i in exercises_to_browse:
            all_firsts = i.first.all()
            all_second = i.second.all()
            if (
                all_firsts.filter(first=1).exists()
                and all_second.filter(second=2).exists()
            ):
                to_return.append(i)
    if first == 1 and second == 7:
        for i in exercises_to_browse:
            all_firsts = i.first.all()
            all_second = i.second.all()
            if (
                all_firsts.filter(first=1).exists()
                and all_second.filter(second=7).exists()
            ):
                to_return.append(i)
    # mittlerer Rücken
    if first == 2 and second == 0:
        for i in exercises_to_browse:
            all_firsts = i.first.all()
            all_second = i.second.all()
            if (
                all_firsts.filter(first=2).exists()
                and all_second.filter(second=0).exists()
            ):
                to_return.append(i)
    if first == 2 and second == 1:
        for i in exercises_to_browse:
            all_firsts = i.first.all()
            all_second = i.second.all()
            if (
                all_firsts.filter(first=2).exists()
                and all_second.filter(second=1).exists()
            ):
                to_return.append(i)
    if first == 2 and second == 2:
        for i in exercises_to_browse:
            all_firsts = i.first.all()
            all_second = i.second.all()
            if (
                all_firsts.filter(first=2).exists()
                and all_second.filter(second=2).exists()
            ):
                to_return.append(i)
    if first == 2 and second == 7:
        for i in exercises_to_browse:
            all_firsts = i.first.all()
            all_second = i.second.all()
            if (
                all_firsts.filter(first=2).exists()
                and all_second.filter(second=7).exists()
            ):
                to_return.append(i)
    # bauch rumpf
    if first == 3 and second == 0:
        uebungen_to_append = []
    if first == 3 and second == 1:
        for i in exercises_to_browse:
            all_firsts = i.first.all()
            all_second = i.second.all()
            if (
                all_firsts.filter(first=3).exists()
                and all_second.filter(second=1).exists()
            ):
                to_return.append(i)
    if first == 3 and second == 2:
        for i in exercises_to_browse:
            all_firsts = i.first.all()
            all_second = i.second.all()
            if (
                all_firsts.filter(first=3).exists()
                and all_second.filter(second=2).exists()
            ):
                to_return.append(i)
    if first == 3 and second == 7:
        for i in exercises_to_browse:
            all_firsts = i.first.all()
            all_second = i.second.all()
            if (
                all_firsts.filter(first=3).exists()
                and all_second.filter(second=7).exists()
            ):
                to_return.append(i)
    # Unterer Rücken
    if first == 4 and second == 0:
        for i in exercises_to_browse:
            all_firsts = i.first.all()
            all_second = i.second.all()
            if (
                all_firsts.filter(first=4).exists()
                and all_second.filter(second=0).exists()
            ):
                to_return.append(i)
    if first == 4 and second == 1:
        for i in exercises_to_browse:
            all_firsts = i.first.all()
            all_second = i.second.all()
            if (
                all_firsts.filter(first=4).exists()
                and all_second.filter(second=1).exists()
            ):
                to_return.append(i)
    if first == 4 and second == 2:
        for i in exercises_to_browse:
            all_firsts = i.first.all()
            all_second = i.second.all()
            if (
                all_firsts.filter(first=4).exists()
                and all_second.filter(second=2).exists()
            ):
                to_return.append(i)

    if first == 4 and second == 7:
        for i in exercises_to_browse:
            all_firsts = i.first.all()
            all_second = i.second.all()
            if (
                all_firsts.filter(first=4).exists()
                and all_second.filter(second=7).exists()
            ):
                to_return.append(i)
    # Beine Füße
    if first == 5 and second == 0:
        for i in exercises_to_browse:
            all_firsts = i.first.all()
            all_second = i.second.all()
            if (
                all_firsts.filter(first=5).exists()
                and all_second.filter(second=0).exists()
            ):
                to_return.append(i)
    if first == 5 and second == 1:
        for i in exercises_to_browse:
            all_firsts = i.first.all()
            all_second = i.second.all()
            if (
                all_firsts.filter(first=5).exists()
                and all_second.filter(second=1).exists()
            ):
                to_return.append(i)
    if first == 5 and second == 2:
        for i in exercises_to_browse:
            all_firsts = i.first.all()
            all_second = i.second.all()
            if (
                all_firsts.filter(first=5).exists()
                and all_second.filter(second=2).exists()
            ):
                to_return.append(i)
    if first == 5 and second == 7:
        for i in exercises_to_browse:
            all_firsts = i.first.all()
            all_second = i.second.all()
            if (
                all_firsts.filter(first=5).exists()
                and all_second.filter(second=7).exists()
            ):
                to_return.append(i)
    # Arme Hände

    if first == 6 and second == 0:
        for i in exercises_to_browse:
            all_firsts = i.first.all()
            all_second = i.second.all()
            if (
                all_firsts.filter(first=6).exists()
                and all_second.filter(second=0).exists()
            ):
                to_return.append(i)
    if first == 6 and second == 1:
        for i in exercises_to_browse:
            all_firsts = i.first.all()
            all_second = i.second.all()
            if (
                all_firsts.filter(first=6).exists()
                and all_second.filter(second=1).exists()
            ):
                to_return.append(i)
    if first == 6 and second == 2:
        for i in exercises_to_browse:
            all_firsts = i.first.all()
            all_second = i.second.all()
            if (
                all_firsts.filter(first=6).exists()
                and all_second.filter(second=2).exists()
            ):
                to_return.append(i)

    if first == 6 and second == 7:
        for i in exercises_to_browse:
            all_firsts = i.first.all()
            all_second = i.second.all()
            if (
                all_firsts.filter(first=6).exists()
                and all_second.filter(second=7).exists()
            ):
                to_return.append(i)

    return to_return


@login_required(login_url="login")
def add_exercises(request, id=None, first=0, second=0):
    print("ececuted")
    workout_list = []
    if request.method == "GET":
        first = request.GET.get("first", 0)
        second = request.GET.get("second", 0)
        print(first)
        print(second)
        workout_list = get_workout_list(int(first), int(second))
        print("handled request")
        print(workout_list)
        return render(
            request, "laxout_app/add_exercises.html", {"workouts": workout_list}
        )
    if request.method == "POST":
        new_execution = request.POST.get("execution")
        new_dauer = request.POST.get("dauer")  # .objects.get(id=new_id)
        new_id = request.POST.get("id")
        print(new_dauer)
        if new_dauer == "":
            new_dauer = models.Uebungen_Models.objects.get(id=new_id).dauer

        programm_instance = models.Kursprogramm.objects.get(id=id)

        current_exercises = programm_instance.exercises.all()
        current_order_objects = models.Laxout_Exercise_Order_For_User.objects.filter(
            laxout_user_id=id
        )  # es wird geschaut, ob es schon eine Reihenfolge gibt
        if len(current_order_objects) == 0 and len(current_exercises) != 0:
            print("There was a diffenrence")
            order = 1
            for i in current_exercises:
                models.Laxout_Exercise_Order_For_User.objects.create(
                    laxout_user_id=id, laxout_exercise_id=i.id, order=order
                )
                order += 1
            print("length")
            print(len(models.Laxout_Exercise_Order_For_User.objects.all()))

        lenght_order_objects_list = len(current_order_objects)

        print("LENGTH ORDER OBJECTS{}".format(len(current_order_objects)))

        exercise_to_add = models.Laxout_Exercise.objects.create(
            execution=new_execution,
            name=models.Uebungen_Models.objects.get(id=new_id).name,
            dauer=new_dauer,
            videoPath=models.Uebungen_Models.objects.get(id=new_id).videoPath,
            looping=models.Uebungen_Models.objects.get(id=new_id).looping,
            added=False,
            instruction="",
            timer=models.Uebungen_Models.objects.get(id=new_id).timer,
            required=models.Uebungen_Models.objects.get(id=new_id).required,
            imagePath=models.Uebungen_Models.objects.get(id=new_id).imagePath,
            appId=new_id,
            onlineVideoPath=models.Uebungen_Models.objects.get(
                id=new_id
            ).onlineVideoPath,
        )
        order_new_exercise = len(current_order_objects) + 1

        print(f"ID der hinzugefügten Übung {exercise_to_add.id}")

        models.Laxout_Exercise_Order_For_User.objects.create(
            laxout_user_id=id,
            laxout_exercise_id=exercise_to_add.id,
            order=order_new_exercise,
        )

        print(exercise_to_add.dauer)
        exercise_to_add.save()
        programm_instance.exercises.add(exercise_to_add)
        if request.user == programm_instance.created_by:
            programm_instance.save()

    workout_list = get_workout_list(0, 0)
    return render(
        request,
        "laxout_app/add_exercises.html",
        {"workouts": workout_list, "userId": id},
    )


@login_required(login_url="login")
def edit_programm_workout(
    request,
    id=None,
):
    if request.method == "POST":
        new_execution = request.POST.get("execution")
        print("new execution:{}".format(new_execution))
        new_dauer = request.POST.get("dauer")  # .objects.get(id=new_id)
        new_id = request.POST.get("id")
        user_id = request.POST.get("userId")
        print("new dauer:{}".format(new_dauer))
        print("new id:{}".format(new_id))
        programm_instance = models.Kursprogramm.objects.get(id=user_id)
        exercise_to_edit = programm_instance.exercises.get(id=new_id)
        if new_execution:
            exercise_to_edit.execution = new_execution
        if new_dauer:
            exercise_to_edit.dauer = new_dauer
        exercise_to_edit.save()
        programm_instance.save()
    return render(
        request,
        "laxout_app/edit_user.html",
    )


@login_required(login_url="login")
def delete_user_exercise(
    request,
    id=None,
):
    if request.method == "POST":
        to_delete_id = request.POST.get("id")
        id = request.POST.get("userId")
        programm_instance = models.Kursprogramm.objects.get(id=id)
        exercise_to_edit = programm_instance.exercises.get(id=to_delete_id)
        if request.user == programm_instance.created_by:
            exercise_to_edit.delete()
            programm_instance.save()
            print("to delete id")
            print(to_delete_id)
            to_delete = models.Laxout_Exercise_Order_For_User.objects.get(
                laxout_exercise_id=to_delete_id, laxout_user_id=id
            )
            to_delete.delete()

            list_order_exercises = models.Laxout_Exercise_Order_For_User.objects.filter(
                laxout_user_id=id
            )
            if len(list_order_exercises) != 0:
                right_order_exercises = []
                for i in list_order_exercises:
                    right_order_exercises.append(
                        models.Laxout_Exercise.objects.get(id=i.laxout_exercise_id)
                    )

                sorted_list = sorted(right_order_exercises, key=lambda x: x.order)
                order = 1
                for i in sorted_list:
                    instance = models.Laxout_Exercise_Order_For_User.objects.get(
                        laxout_exercise_id=i.laxout_exercise_id,
                        laxout_user_id=i.laxout_user_id,
                    ).order = order
                    instance.save()
                    order += 1
            models.SuccessControll.objects.filter(
                created_by=programm_instance.id
            ).delete()
    return render(
        request,
        "laxout_app/edit_user.html",
    )


def days_between_today_and_date(input_datetime):
    # Assuming last_login_2 is stored in the same timezone as the server
    input_datetime = input_datetime.replace(tzinfo=None)  # Make it naive
    current_datetime = datetime.now()

    time_difference = current_datetime - input_datetime
    days_difference = time_difference.days

    return days_difference


@login_required(login_url="login")
def post_user_instruction(request, id=None):
    new_instruction = request.POST.get("instruction")
    user_insance = models.Kursprogramm.objects.get(id=id)
    user_insance.instruction = new_instruction
    user_insance.save()
    return HttpResponse("All clear")


# from . import signals


class UebungList:
    def __init__(
        self,
        looping,
        timer,
        execution,
        name,
        videoPath,
        dauer,
        imagePath,
        added,
        instruction,
        required,
        onlineVidePath,
    ):
        self.looping = looping
        self.timer = timer
        self.execution = execution
        self.name = name
        self.videoPath = videoPath
        self.dauer = dauer
        self.imagePath = imagePath
        self.added = added
        self.instruction = instruction
        self.required = required
        self.onlineVidePath = onlineVidePath


additionalUebungList2 = []


uebungen_to_append00 = []  # Nacken
uebungen_to_append01 = []
uebungen_to_append02 = []
uebungen_to_append07 = []
uebungen_to_append10 = []  # Schultern
uebungen_to_append11 = []
uebungen_to_append12 = []
uebungen_to_append17 = []
uebungen_to_append20 = []  # Mittlerer Rücken
uebungen_to_append21 = []
uebungen_to_append22 = []
uebungen_to_append27 = []
uebungen_to_append30 = []  # Bauch Rumpf
uebungen_to_append31 = []
uebungen_to_append32 = []
uebungen_to_append37 = []
uebungen_to_append40 = []  # Unterer Rücken
uebungen_to_append41 = []
uebungen_to_append42 = []
uebungen_to_append47 = []
uebungen_to_append50 = []  # Beine Füße
uebungen_to_append51 = []
uebungen_to_append52 = []
uebungen_to_append57 = []
uebungen_to_append60 = []  # Arme Hände
uebungen_to_append61 = []
uebungen_to_append62 = []
uebungen_to_append67 = [254, 255, 256, 257]


def inizialize_first_second(
    debugValue,
):  # Falls die Ids in der Datenbank durch löschungen verzogen werden kommt ein debugValue hinzu, der die Ids anpasst ab Übung 210 wird der wert relevant (387)
    for i in uebungen_to_append00:
        instance_exercise = models.Uebungen_Models.objects.get(id=i + debugValue)
        instance_exercise.first.add(models.First.objects.create(first=0))
        instance_exercise.second.add(models.Second.objects.create(second=0))
        instance_exercise.save()
    for i in uebungen_to_append01:
        instance_exercise = models.Uebungen_Models.objects.get(id=i + debugValue)
        instance_exercise.first.add(models.First.objects.create(first=0))
        instance_exercise.second.add(models.Second.objects.create(second=1))
        instance_exercise.save()
    for i in uebungen_to_append02:
        instance_exercise = models.Uebungen_Models.objects.get(id=i + debugValue)
        instance_exercise.first.add(models.First.objects.create(first=0))
        instance_exercise.second.add(models.Second.objects.create(second=2))
        instance_exercise.save()
    for i in uebungen_to_append07:
        instance_exercise = models.Uebungen_Models.objects.get(id=i + debugValue)
        instance_exercise.second.add(models.Second.objects.create(second=7))
        instance_exercise.second.add(models.Second.objects.create(second=7))
        instance_exercise.save()
    for i in uebungen_to_append10:
        instance_exercise = models.Uebungen_Models.objects.get(id=i + debugValue)
        instance_exercise.first.add(models.First.objects.create(first=1))
        instance_exercise.second.add(models.Second.objects.create(second=0))
        instance_exercise.save()
    for i in uebungen_to_append11:
        instance_exercise = models.Uebungen_Models.objects.get(id=i + debugValue)
        instance_exercise.first.add(models.First.objects.create(first=1))
        instance_exercise.second.add(models.Second.objects.create(second=1))
        instance_exercise.save()
    for i in uebungen_to_append12:
        instance_exercise = models.Uebungen_Models.objects.get(id=i + debugValue)
        instance_exercise.first.add(models.First.objects.create(first=1))
        instance_exercise.second.add(models.Second.objects.create(second=2))
        instance_exercise.save()
    for i in uebungen_to_append17:
        instance_exercise = models.Uebungen_Models.objects.get(id=i + debugValue)
        instance_exercise.first.add(models.First.objects.create(first=1))
        instance_exercise.second.add(models.Second.objects.create(second=7))
        instance_exercise.save()
    for i in uebungen_to_append20:
        instance_exercise = models.Uebungen_Models.objects.get(id=i + debugValue)
        instance_exercise.first.add(models.First.objects.create(first=2))
        instance_exercise.second.add(models.Second.objects.create(second=0))
        instance_exercise.save()
    for i in uebungen_to_append21:
        instance_exercise = models.Uebungen_Models.objects.get(id=i + debugValue)
        instance_exercise.first.add(models.First.objects.create(first=2))
        instance_exercise.second.add(models.Second.objects.create(second=1))
        instance_exercise.save()
    for i in uebungen_to_append22:
        instance_exercise = models.Uebungen_Models.objects.get(id=i + debugValue)
        instance_exercise.first.add(models.First.objects.create(first=2))
        instance_exercise.second.add(models.Second.objects.create(second=2))
        instance_exercise.save()
    for i in uebungen_to_append27:
        instance_exercise = models.Uebungen_Models.objects.get(id=i + debugValue)
        instance_exercise.first.add(models.First.objects.create(first=2))
        instance_exercise.second.add(models.Second.objects.create(second=7))
        instance_exercise.save()
    for i in uebungen_to_append30:
        instance_exercise = models.Uebungen_Models.objects.get(id=i + debugValue)
        instance_exercise.first.add(models.First.objects.create(first=3))
        instance_exercise.second.add(models.Second.objects.create(second=0))
        instance_exercise.save()
    for i in uebungen_to_append31:
        instance_exercise = models.Uebungen_Models.objects.get(id=i + debugValue)
        instance_exercise.first.add(models.First.objects.create(first=3))
        instance_exercise.second.add(models.Second.objects.create(second=1))
        instance_exercise.save()
    for i in uebungen_to_append32:
        instance_exercise = models.Uebungen_Models.objects.get(id=i + debugValue)
        instance_exercise.first.add(models.First.objects.create(first=3))
        instance_exercise.second.add(models.Second.objects.create(second=2))
        instance_exercise.save()
    for i in uebungen_to_append37:
        instance_exercise = models.Uebungen_Models.objects.get(id=i + debugValue)
        instance_exercise.first.add(models.First.objects.create(first=3))
        instance_exercise.second.add(models.Second.objects.create(second=7))
        instance_exercise.save()
    for i in uebungen_to_append40:
        instance_exercise = models.Uebungen_Models.objects.get(id=i + debugValue)
        instance_exercise.first.add(models.First.objects.create(first=4))
        instance_exercise.second.add(models.Second.objects.create(second=0))
        instance_exercise.save()
    for i in uebungen_to_append41:
        instance_exercise = models.Uebungen_Models.objects.get(id=i + debugValue)
        instance_exercise.first.add(models.First.objects.create(first=4))
        instance_exercise.second.add(models.Second.objects.create(second=1))
        instance_exercise.save()
    for i in uebungen_to_append42:
        instance_exercise = models.Uebungen_Models.objects.get(id=i + debugValue)
        instance_exercise.first.add(models.First.objects.create(first=4))
        instance_exercise.second.add(models.Second.objects.create(second=2))
        instance_exercise.save()
    for i in uebungen_to_append47:
        instance_exercise = models.Uebungen_Models.objects.get(id=i + debugValue)
        instance_exercise.first.add(models.First.objects.create(first=4))
        instance_exercise.second.add(models.Second.objects.create(second=7))
        instance_exercise.save()
    for i in uebungen_to_append50:
        instance_exercise = models.Uebungen_Models.objects.get(id=i + debugValue)
        instance_exercise.first.add(models.First.objects.create(first=5))
        instance_exercise.second.add(models.Second.objects.create(second=0))
        instance_exercise.save()
    for i in uebungen_to_append51:
        instance_exercise = models.Uebungen_Models.objects.get(id=i + debugValue)
        instance_exercise.first.add(models.First.objects.create(first=5))
        instance_exercise.second.add(models.Second.objects.create(second=1))
        instance_exercise.save()
    for i in uebungen_to_append52:
        instance_exercise = models.Uebungen_Models.objects.get(id=i + debugValue)
        instance_exercise.first.add(models.First.objects.create(first=5))
        instance_exercise.second.add(models.Second.objects.create(second=2))
        instance_exercise.save()
    for i in uebungen_to_append57:
        instance_exercise = models.Uebungen_Models.objects.get(id=i + debugValue)
        instance_exercise.first.add(models.First.objects.create(first=5))
        instance_exercise.second.add(models.Second.objects.create(second=7))
        instance_exercise.save()
    for i in uebungen_to_append60:
        instance_exercise = models.Uebungen_Models.objects.get(id=i + debugValue)
        instance_exercise.first.add(models.First.objects.create(first=6))
        instance_exercise.second.add(models.Second.objects.create(second=0))
        instance_exercise.save()
    for i in uebungen_to_append61:
        instance_exercise = models.Uebungen_Models.objects.get(id=i + debugValue)
        instance_exercise.first.add(models.First.objects.create(first=6))
        instance_exercise.second.add(models.Second.objects.create(second=1))
        instance_exercise.save()
    for i in uebungen_to_append62:
        instance_exercise = models.Uebungen_Models.objects.get(id=i + debugValue)
        instance_exercise.first.add(models.First.objects.create(first=6))
        instance_exercise.second.add(models.Second.objects.create(second=2))
        instance_exercise.save()
    for i in uebungen_to_append67:
        instance_exercise = models.Uebungen_Models.objects.get(id=i + debugValue)
        instance_exercise.first.add(models.First.objects.create(first=6))
        instance_exercise.second.add(models.Second.objects.create(second=7))
        instance_exercise.save()


@login_required(login_url="login")
def admin_power(request):
    ##Update Executions
    # id = 1
    # all_exercises = models.Uebungen_Models.objects.all()
    # print("Test")
    # print(len(uebungen))
    # print(len(all_exercises))
    # for i in uebungen:
    #     exercise = models.Uebungen_Models.objects.get(id=id)
    #     exercise.execution = i.execution
    #     exercise.save()
    #     id += 1
    # print("done")

    # Create new Exercises
    for i in additionalUebungList2:
        models.Uebungen_Models.objects.create(
            looping=i.looping,
            timer=i.timer,
            execution=i.execution,
            name=i.name,
            videoPath=i.videoPath,
            dauer=i.dauer,
            imagePath=i.imagePath,
            added=i.added,
            instruction=i.instruction,
            required=i.required,
            onlineVideoPath=i.onlineVidePath,
        )
    inizialize_first_second(
        0
    )  # auf pythonanywhere ist dieser wert aktuell 387 erklärung bei 'def' inizialize..

    # models.Uebungen_Models.objects.all().delete()
    # models.First.objects.all().delete()
    # models.Second.objects.all().delete()

    # from . import signals
    # for i in signals.uebungen:
    #             Uebungen_Models.objects.create(
    #                 looping=i.looping,
    #                 timer=i.timer,
    #                 execution=i.execution,
    #                 name=i.name,
    #                 videoPath=i.videoPath,
    #                 dauer=i.dauer,
    #                 imagePath=i.imagePath,
    #                 added=i.added,
    #                 instruction=i.instruction,
    #                 required=i.required,
    #                 onlineVideoPath = i.onlineVidePath

    #             )
    # inizialize_first_second()

    # for i in models.LaxoutUser.objects.all():
    #     laxout_tree = models.LaxTree.objects.create()
    #     i.lax_tree_id = laxout_tree.id
    #     i.save()

    return HttpResponse("all clear")


@login_required(login_url="login")
def move_up(request, id=None):
    try:
        exercise_id = request.POST.get("exercise_id")
        user = models.Kursprogramm.objects.get(id=id)
        item_to_move_up = models.Laxout_Exercise_Order_For_User.objects.get(
            laxout_user_id=id, laxout_exercise_id=exercise_id
        )
        if item_to_move_up.order == 1:
            return HttpResponse("INVALID MOVE UP: FIRST ITEM IN LIST")
        order_to_move_up = item_to_move_up.order
        order_to_move_down = item_to_move_up.order - 1
        item_to_move_down = models.Laxout_Exercise_Order_For_User.objects.get(
            laxout_user_id=id, order=order_to_move_down
        )
        item_to_move_up.order = order_to_move_down
        item_to_move_up.save()
        item_to_move_down.order = order_to_move_up
        item_to_move_down.save()

        context = {"exercises": user.exercises.all()}
        return render(request, "laxout_app/edit_user.html", context)
    except:
        print(Exception)
        return HttpResponse("ERROR INTERNAL 4_0_4")


@login_required(login_url="login")
def move_down(request, id=None):
    try:
        exercise_id = request.POST.get("exercise_id")
        user = models.Kursprogramm.objects.get(id=id)
        item_to_move_down = models.Laxout_Exercise_Order_For_User.objects.get(
            laxout_user_id=id, laxout_exercise_id=exercise_id
        )
        if item_to_move_down.order == len(
            models.Laxout_Exercise_Order_For_User.objects.filter(laxout_user_id=id)
        ):
            return HttpResponse("INVALID MOVE UP: FIRST ITEM IN LIST")

        order_to_move_down = item_to_move_down.order
        order_to_move_up = item_to_move_down.order + 1

        item_to_move_up = models.Laxout_Exercise_Order_For_User.objects.get(
            laxout_user_id=id, order=order_to_move_up
        )

        item_to_move_up.order = order_to_move_down
        item_to_move_up.save()

        item_to_move_down.order = order_to_move_up
        item_to_move_down.save()

        context = {"exercises": user.exercises.all()}
        return render(request, "laxout_app/edit_user.html", context)
    except:
        print(Exception)
        return HttpResponse("ERROR INTERNAL 4_0_4")


@login_required(login_url="login")
def set_instruction_int(request):
    try:
        user = models.Kursprogramm.objects.get(id=request.POST.get("id"))
        print(user.id)
        instruction_int = request.POST.get("int")
        print(instruction_int)
        user.instruction_in_int = instruction_int
        user.save()
        return HttpResponse("OK 2_0_0")
    except:
        print(Exception)
        print("Kacke")
        return HttpResponse("ERROR INTERNAL 4_0_4")


@login_required(login_url="login")
def chats(request):
    users = models.LaxoutUser.objects.filter(created_by=request.user.id)
    return render(request, "laxout_app/chats.html", {"users": users})


@login_required(login_url="login")
def personal_chat(request, id=None):
    user = models.LaxoutUser.objects.get(id=id)
    personal_chat = models.ChatDataModel.objects.filter(created_by=id)
    print(f"Länge des Chats{len(personal_chat)}")
    return render(
        request,
        "laxout_app/personal-chat.html",
        {"user": user, "personal_chat": personal_chat},
    )


@login_required(login_url="login")
def post_message(request, id=None):
    user = models.LaxoutUser.objects.get(id=id)
    message = request.POST.get("message")
    is_sender = request.POST.get("is_sender")
    user.user_has_seen_chat = False
    user.save()
    models.ChatDataModel.objects.create(
        message=message, is_sender=False, created_by=id, admin_id=request.user.id
    )
    return HttpResponse("OK")


@login_required(login_url="login")
def admin_has_seen(request, id=None):
    user = models.LaxoutUser.objects.get(id=id)
    user.admin_has_seen_chat = True
    user.save()
    return HttpResponse("OK")
