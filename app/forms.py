from flask.ext.wtf import Form
from wtforms import StringField
from wtforms.validators import DataRequired

class LoginForm(Form):
	password = StringField('password', validators=[DataRequired()])

class MessageForm(Form):
	message = StringField('message', validators=[DataRequired()])
