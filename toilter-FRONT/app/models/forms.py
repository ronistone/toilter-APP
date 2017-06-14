from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField,TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email

class RegisterForm(FlaskForm):
	name = StringField("name", validators=[DataRequired()])
	password = PasswordField("password", validators=[DataRequired()])
	email = StringField("email", validators=[Email()])

class LoginForm(FlaskForm):
	username = StringField('username',validators=[DataRequired()])
	password = PasswordField('password',validators=[DataRequired()])
	remember_me = BooleanField('remember_me')

class TwitForm(FlaskForm):
	content = TextAreaField('content',validators=[DataRequired()])
	submit = SubmitField('Postar')

class SearchForm(FlaskForm):
	search = StringField("search", validators=[DataRequired()])
	submit = SubmitField('Procurar')
