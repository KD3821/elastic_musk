from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired



class SearchForm(FlaskForm):
    name_s = StringField("придумайте имя запроса", validators=[DataRequired()])
    body_s = TextAreaField("тело запроса без 'body='", validators=[DataRequired()])
    submit = SubmitField("run search")