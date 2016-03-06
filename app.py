from flask import Flask, jsonify, render_template, request, redirect
from flask.ext.mongoengine import MongoEngine
from flask.ext.mongoengine.wtf import model_form
from flask.ext.login import LoginManager, login_required, login_user, logout_user
from wtforms import Form, TextField, PasswordField, validators
from twilio.rest import TwilioRestClient
from backend import config
from backend import form as createForm
from backend import models
from datetime import datetime

app = Flask(__name__)
#app.config['SECRET_KEY'] = config.secret_key
app.secret_key = config.secret_key
app.config['WTF_CSRF_ENABLED'] = config.csrf_enabled
login_manager = LoginManager()
login_manager.init_app(app)
app.config['DEBUG'] = True  # Only include this while you are testing your app
app.config['MONGODB_SETTINGS'] = { 'db': 'subscribers' }
db = MongoEngine(app)

account_sid = config.acct_sid
auth_token = config.token
client = TwilioRestClient(account_sid, auth_token)

class User(db.Document):
    name = db.StringField(required=True,unique=True)
    password = db.StringField(required=True)
    def is_authenticated(self):
        users = User.objects(name=self.name, password=self.password)
        return len(users) != 0
    def is_active(self):
        return True
    def is_anonymous(self):
        return False
    def get_id(self):
        return self.name

@login_manager.user_loader
def load_user(name):
    users = User.objects(name=name)
    if len(users) != 0:
        return users[0]
    else:
        return None

UserForm = model_form(User)
UserForm.password = PasswordField('password')

class MessageForm(Form):
    content = TextField('Blast message', [validators.Length(min=2, max=160)])

class Subscriber(db.Document):
    phone = db.StringField(required=True)
    interactions = db.IntField(min_value=0)
    first = db.DateTimeField(auto_now_add=True)
    last = db.DateTimeField(auto_now=True)

@app.route("/", methods=['GET','POST'])
def login():
    form = UserForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User(name=form.name.data,password=form.password.data)
        login_user(user)
        return redirect('/send')
    return render_template('login.html', form=form)

@app.route("/send", methods=['GET', 'POST'])
def send():
    form = MessageForm(request.form);
    if request.method == 'POST' and form.validate():
        subscribers = Subscriber.objects()
        for sub in subscribers:
            message = client.messages.create(body=form.content.data,
        	to = sub.phone,
        	from_ = config.twilio_num)
        return redirect("/")
    return render_template("send.html", form=form)

@app.route("/subscribe/<phone>")
@login_required
def subscribe(phone):
    timestamp = datetime.now()
    new_sub = Subscriber(phone=phone, interactions=1, first=timestamp, last=timestamp)
    new_sub.save()
    return render_template("confirm.html")

@app.route("/subscribers")
@login_required
def subscribers():
    subscribers = Subscriber.objects()
    return render_template("subscribers.html", subscribers=subscribers)

@app.route("/unsubscribe/<phone>")
@login_required
def unsubscribe(phone):
    sub = Subscriber.objects(phone=phone)
    sub.delete()
    return render_template("confirm.html")

@app.route("/unsubscribe-all")
@login_required
def clear():
    subscribers = Subscriber.objects()
    for sub in subscribers:
        sub.delete()
    return render_template("subscribers.html", subscribers=subscribers)

@app.route("/register", methods=['GET', 'POST'])
def register():
    form = UserForm(request.form)
    if request.method == 'POST' and form.validate():
        form.save()
        return redirect("/login")
    return render_template("register.html", form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")

if __name__ == "__main__":
    app.run(host="0.0.0.0")
