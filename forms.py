from datetime import datetime
from flask_wtf import FlaskForm as Form
from wtforms import StringField, BooleanField, SelectField, SelectMultipleField, DateTimeField
from wtforms.fields.html5 import URLField, IntegerField, DateTimeLocalField
from wtforms.validators import DataRequired, Regexp, AnyOf, URL, Length
from enums import State, Genre


class ShowForm(Form):
    artist_id = IntegerField(
        'artist_id',
        validators=[DataRequired('Artist id is required.')]
    )
    venue_id = IntegerField(
        'venue_id',
        validators=[DataRequired('Venue id is required.')]
    )
    start_time = DateTimeLocalField(
        'start_time',
        validators=[DataRequired('Start time is required.')],
        default=datetime.utcnow,
        format='%Y-%m-%dT%H:%M'
    )


class VenueForm(Form):
    name = StringField(
        'name',
        validators=[DataRequired('Name is required.')]
    )
    city = StringField(
        'city',
        validators=[DataRequired('City is required.'), Length(0, 120)]
    )
    state = SelectField(
        'state',
        validators=[DataRequired('State is required.')],
        choices=State.choices()
    )
    address = StringField(
        'address',
        validators=[Length(0, 120)]
    )
    phone = StringField(
        'phone'
    )
    genres = SelectMultipleField(
        'genres',
        validators=[DataRequired('At least one genre is required.')],
        choices=Genre.choices()
    )
    image_link = URLField(
        'image_link',
        validators=[DataRequired('Image link is required.'), URL(message='Image link must be an URL.'), Length(0, 500)]
    )
    website_link = URLField(
        'website_link',
        validators=[Length(0, 120)]
    )
    facebook_link = URLField(
        'facebook_link',
        validators=[Length(0, 120)]
    )
    seeking_talent = BooleanField(
        'seeking_talent',
        default='checked'
    )
    seeking_description = StringField(
        'seeking_description',
        default='We are looking for talent.'
    )


class ArtistForm(Form):
    name = StringField(
        'name',
        validators=[DataRequired('Name is required.')]
    )
    city = StringField(
        'city',
        validators=[DataRequired('City is required.'), Length(0, 120)]
    )
    state = SelectField(
        'state',
        validators=[DataRequired('State is required.')],
        choices=State.choices()
    )
    phone = StringField(
        'phone'
    )
    genres = SelectMultipleField(
        'genres',
        validators=[DataRequired('At least one genre is required.')],
        choices=Genre.choices()
    )
    image_link = URLField(
        'image_link',
        validators=[DataRequired('Image link is required.'), URL(message='Image link must be an URL.'), Length(0, 500)]
    )
    website_link = URLField(
        'website_link',
        validators=[Length(0, 120)]
    )
    facebook_link = URLField(
        'facebook_link',
        validators=[Length(0, 120)]
    )
    albums = StringField(
        'albums',
        validators=[Length(0, 500)]
    )
    seeking_venue = BooleanField(
        'seeking_venue',
        default='checked'
    )
    seeking_description = StringField(
        'seeking_description',
        default="I'm looking for venues."
    )
    available_times = BooleanField(
        'available_times'
    )
    available_start = DateTimeLocalField(
        'available_start',
        default=datetime.utcnow,
        format='%Y-%m-%dT%H:%M'
    )
    available_end = DateTimeLocalField(
        'available_end',
        default=datetime.utcnow,
        format='%Y-%m-%dT%H:%M'
    )
