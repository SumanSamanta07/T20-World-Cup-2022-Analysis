from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, URL
# from flask_ckeditor import CKEditorField


##WTForm
class CreateMatchForm(FlaskForm):
    team1 = StringField("TeamA", validators=[DataRequired()])
    team2 = StringField("TeamB", validators=[DataRequired()])
     # = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    submit = SubmitField("Submit")
