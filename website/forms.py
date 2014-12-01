from wtforms import Form, DateTimeField, TextAreaField, StringField
from wtforms.validators import InputRequired, Optional
from website import app

class EventForm(Form):
    title = StringField('Event Title', validators=[InputRequired()])
    description = TextAreaField('Description', validators=[Optional()])
    image_url = StringField('Image URL', validators=[Optional()])
    scheduled_date = DateTimeField('Event Date', format='%y/%m/%d')
