from flask import render_template, flash, redirect
from app import app
import config
from .forms import LoginForm, MessageForm

@app.route('/', methods=['GET','POST'])
@app.route('/index', methods=['GET','POST'])
def index():
	form = MessageForm()
	return render_template('index.html',
							form = form)

@app.route('/login', methods=['GET','POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		flash('Login requested for password="%s"' %
				(form.password.data))
		if (form.password.data == config.PASSWORD):
			return redirect('/index')
	return render_template('login.html',
							form = form)
