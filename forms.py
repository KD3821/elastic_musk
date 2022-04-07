from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired



class SearchForm(FlaskForm):
    name_s = StringField("Choose index", validators=[DataRequired()])
    body_s = TextAreaField("Enter your request {...}", validators=[DataRequired()])
    submit = SubmitField("run search")