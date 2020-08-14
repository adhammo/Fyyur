import json
import dateutil.parser
import babel
import re
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import distinct, func, or_, and_
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from flask_wtf.csrf import CSRFProtect
from forms import *

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
app.config.from_object('config')

db = SQLAlchemy(app)
moment = Moment(app)
migrate = Migrate(app, db)
csrf = CSRFProtect(app)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(120), nullable=True)
    genres = db.Column(db.String(500), nullable=False)
    image_link = db.Column(db.String(500), nullable=False)
    website_link = db.Column(db.String(120), nullable=True)
    facebook_link = db.Column(db.String(120), nullable=True)
    seeking_talent = db.Column(db.Boolean(), nullable=False)
    seeking_description = db.Column(db.String(), nullable=True)
    created_date = db.Column(db.DateTime(), nullable=False, default=datetime.utcnow)
    shows = db.relationship('Show', backref='venue', lazy=True, cascade='delete')
    

class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=True)
    genres = db.Column(db.String(500), nullable=False)
    image_link = db.Column(db.String(500), nullable=False)
    website_link = db.Column(db.String(120), nullable=True)
    facebook_link = db.Column(db.String(120), nullable=True)
    albums = db.Column(db.String(500), nullable=True)
    seeking_venue = db.Column(db.Boolean(), nullable=False)
    seeking_description = db.Column(db.String(), nullable=True)
    available_times = db.Column(db.Boolean(), nullable=False)
    available_start = db.Column(db.DateTime(), nullable=True)
    available_end = db.Column(db.DateTime(), nullable=True)
    created_date = db.Column(db.DateTime(), nullable=False, default=datetime.utcnow)
    shows = db.relationship('Show', backref='artist', lazy=True, cascade='delete')


class Show(db.Model):
    __tablename__ = 'shows'
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.ForeignKey('artists.id'), nullable=False)
    venue_id = db.Column(db.ForeignKey('venues.id'), nullable=False)
    start_time = db.Column(db.DateTime(), nullable=False)
    created_date = db.Column(db.DateTime(), nullable=False, default=datetime.utcnow)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def index():
    now = datetime.utcnow()

    # Get recent venues
    venues = []
    for venue in db.session.query(Venue).order_by(Venue.created_date.desc()).limit(10).all():
        # Calculate upcoming shows count
        upcoming_shows = 0
        for show in venue.shows:
            if show.start_time > now:
                upcoming_shows = upcoming_shows + 1

        # Append venue to venues
        venues.append({
            'id': venue.id,
            'name': venue.name,
            'num_upcoming_shows': upcoming_shows
        })

    # Get recent artists
    artists = []
    for artist in db.session.query(Artist).order_by(Artist.created_date.desc()).limit(10).all():
        # Calculate upcoming shows count
        upcoming_shows = 0
        for show in artist.shows:
            if show.start_time > now:
                upcoming_shows = upcoming_shows + 1

        # Append artist to artists
        artists.append({
            'id': artist.id,
            'name': artist.name,
            'num_upcoming_shows': upcoming_shows
        })
    
    return render_template('pages/home.html', artists=artists, venues=venues)


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    areas = []

    # Get areas
    for area in db.session.query(Venue.city, Venue.state).distinct().order_by(Venue.city, Venue.state).all():
        venues = []
        now = datetime.utcnow()

        # Get venues in area
        for venue in db.session.query(Venue).filter(Venue.city == area.city, Venue.state == area.state).order_by(Venue.name).all():
            # Calculate upcoming shows count
            upcoming_shows = 0
            for show in venue.shows:
                if show.start_time > now:
                    upcoming_shows = upcoming_shows + 1

            # Append venue to area.venues
            venues.append({
                'id': venue.id,
                'name': venue.name,
                'num_upcoming_shows': upcoming_shows
            })

        # Append area to areas
        areas.append({
            'city': area.city,
            'state': area.state,
            'venues': venues
        })

    # Render venues
    return render_template('pages/venues.html', areas=areas)


@app.route('/venues/search', methods=['POST'])
@csrf.exempt
def search_venues():
    venues = []
    now = datetime.utcnow()

    # Search venues
    term = request.form.get('search_term', '')
    by_city = request.form.get('search_city', False)
    if not by_city:
        for venue in db.session.query(Venue).filter(Venue.name.ilike(f'%{term}%')).order_by(Venue.name).all():
            # Calculate upcoming shows count
            upcoming_shows = 0
            for show in venue.shows:
                if show.start_time > now:
                    upcoming_shows = upcoming_shows + 1

            # Add venue to venues
            venues.append({
                'id': venue.id,
                'name': venue.name,
                'num_upcoming_shows': upcoming_shows
            })
    else:
        city = term.split(', ')[0]
        state = term.split(', ')[1]
        for venue in db.session.query(Venue).filter(and_(Venue.city.ilike(f'%{city}%'), Venue.state.ilike(f'%{state}%'))).order_by(Venue.name).all():
            # Calculate upcoming shows count
            upcoming_shows = 0
            for show in venue.shows:
                if show.start_time > now:
                    upcoming_shows = upcoming_shows + 1

            # Add venue to venues
            venues.append({
                'id': venue.id,
                'name': venue.name,
                'num_upcoming_shows': upcoming_shows
            })

    # Render venues
    return render_template('pages/search_venues.html', results={'count': len(venues), 'data': venues}, search_term=term)


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    now = datetime.utcnow()

    # Get venue
    venue = db.session.query(Venue).filter(Venue.id == venue_id).first()

    # Check if venue exists
    if venue:
        # Get upcoming and past shows
        past_shows = []
        upcoming_shows = []
        for show in venue.shows:
            if show.start_time < now:
                past_shows.append({
                    'artist_id': show.artist.id,
                    'artist_name': show.artist.name,
                    'artist_image_link': show.artist.image_link,
                    'start_time': show.start_time.strftime("%Y-%m-%dT%H:%M")
                })
            else:
                upcoming_shows.append({
                    'artist_id': show.artist.id,
                    'artist_name': show.artist.name,
                    'artist_image_link': show.artist.image_link,
                    'start_time': show.start_time.strftime("%Y-%m-%dT%H:%M")
                })

        # Render venue
        return render_template('pages/show_venue.html', venue={
            'id': venue.id,
            'name': venue.name,
            'genres': map(lambda genre: Genre[genre].value, venue.genres.split(',')[:-1]),
            'address': venue.address,
            'city': venue.city,
            'state': venue.state,
            'phone': venue.phone,
            'image_link': venue.image_link,
            'website_link': venue.website_link,
            'facebook_link': venue.facebook_link,
            'seeking_talent': venue.seeking_talent,
            'seeking_description': venue.seeking_description if venue.seeking_talent == True else None,
            'past_shows': past_shows[::-1],
            'upcoming_shows': upcoming_shows,
            'past_shows_count': len(past_shows),
            'upcoming_shows_count': len(upcoming_shows)
        })
    else:
        # Venue was not found
        return render_template('errors/404.html'), 404

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    # Create venue form
    form = VenueForm()

    # Render venue form
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # Get venue form
    form = VenueForm(request.form)

    # Validate venue form
    valid = form.validate()
    if form.phone.data.strip() != '' and not re.match(r'^[0-9]{3}-[0-9]{3}-[0-9]{4}$', form.phone.data.strip()):
        form.phone.errors = ['Phone must be in the form (xxx-xxx-xxxx).']
        valid = False

    if form.website_link.data.strip() != '' and not re.match(r"^[a-z]+://(?P<host>[^\/\?:]+)(?P<port>:[0-9]+)?(?P<path>\/.*?)?(?P<query>\?.*)?$", form.website_link.data.strip()):
        form.website_link.errors = ['Website link must be an URL.']
        valid = False

    if form.facebook_link.data.strip() != '' and not re.match(r"^[a-z]+://(?P<host>[^\/\?:]+)(?P<port>:[0-9]+)?(?P<path>\/.*?)?(?P<query>\?.*)?$", form.facebook_link.data.strip()):
        form.facebook_link.errors = ['Website link must be an URL.']
        valid = False

    # Check if venue form is valid
    if valid:
        # Create venue
        venue = Venue()
        venue.name = form.name.data.strip()
        genres = ''
        for genre in form.genres.data:
            genres = genres + genre + ','
        venue.genres = genres
        venue.address = form.address.data.strip() if form.address.data.strip() != '' else None
        venue.city = form.city.data.strip()
        venue.state = form.state.data
        venue.phone = form.phone.data.strip() if form.phone.data.strip() != '' else None
        venue.image_link = form.image_link.data.strip()
        venue.website_link = form.website_link.data.strip() if form.website_link.data.strip() != '' else None
        venue.facebook_link = form.facebook_link.data.strip() if form.facebook_link.data.strip() != '' else None
        venue.seeking_talent = form.seeking_talent.data
        venue.seeking_description = form.seeking_description.data.strip() if form.seeking_talent.data == True else None

        # Add venue
        try:
            db.session.add(venue)
            db.session.commit()
            flash(f'Venue {venue.name} was successfully listed!')
        except:
            db.session.rollback()
            flash('An error occurred. Venue could not be listed.')
        finally:
            db.session.close()

        # Render home
        return render_template('pages/home.html')
    else:
        # Venue form is not valid
        return render_template('forms/new_venue.html', form=form)


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    # Get venue
    venue = Venue.query.filter(Venue.id == venue_id).first()

    # Check if venue exists
    if venue:
        # Create venue form from existing venue
        form = VenueForm()
        form.name.data = venue.name
        form.genres.data = venue.genres.split(',')[:-1]
        form.address.data = venue.address if venue.address else ''
        form.city.data = venue.city
        form.state.data = venue.state
        form.phone.data = venue.phone if venue.phone else ''
        form.image_link.data = venue.image_link
        form.website_link.data = venue.website_link if venue.website_link else ''
        form.facebook_link.data = venue.facebook_link if venue.facebook_link else ''
        form.seeking_talent.data = venue.seeking_talent
        form.seeking_description.data = venue.seeking_description if venue.seeking_talent == True else 'We are looking for talent.'

        # Render venue form
        return render_template('forms/edit_venue.html', form=form)
    else:
        # Venue was not found
        return render_template('errors/404.html'), 404


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # Get venue
    venue = Venue.query.filter(Venue.id == venue_id).first()

    # Check if venue exists
    if venue:
        # Get venue form
        form = VenueForm(request.form)

        # Validate venue form
        valid = form.validate()
        if form.phone.data.strip() != '' and not re.match(r'^[0-9]{3}-[0-9]{3}-[0-9]{4}$', form.phone.data.strip()):
            form.phone.errors = ['Phone must be in the form (xxx-xxx-xxxx).']
            valid = False

        if form.website_link.data.strip() != '' and not re.match(r"^[a-z]+://(?P<host>[^\/\?:]+)(?P<port>:[0-9]+)?(?P<path>\/.*?)?(?P<query>\?.*)?$", form.website_link.data.strip()):
            form.website_link.errors = ['Website link must be an URL.']
            valid = False

        if form.facebook_link.data.strip() != '' and not re.match(r"^[a-z]+://(?P<host>[^\/\?:]+)(?P<port>:[0-9]+)?(?P<path>\/.*?)?(?P<query>\?.*)?$", form.facebook_link.data.strip()):
            form.facebook_link.errors = ['Website link must be an URL.']
            valid = False

        # Check if venue form is valid
        if valid:
            # Edit venue
            venue.name = form.name.data.strip()
            genres = ''
            for genre in form.genres.data:
                genres = genres + genre + ','
            venue.genres = genres
            venue.address = form.address.data.strip() if form.address.data.strip() != '' else None
            venue.city = form.city.data.strip()
            venue.state = form.state.data
            venue.phone = form.phone.data.strip() if form.phone.data.strip() != '' else None
            venue.image_link = form.image_link.data.strip()
            venue.website_link = form.website_link.data.strip() if form.website_link.data.strip() != '' else None
            venue.facebook_link = form.facebook_link.data.strip() if form.facebook_link.data.strip() != '' else None
            venue.seeking_talent = form.seeking_talent.data
            venue.seeking_description = form.seeking_description.data.strip() if form.seeking_talent.data == True else None

            # Update venue
            try:
                db.session.commit()
                flash(f'Venue {venue.name} was successfully edited!')
            except:
                db.session.rollback()
                flash('An error occurred. Venue could not be edited.')
            finally:
                db.session.close()

            # Redirect to edited venue
            return redirect(url_for('show_venue', venue_id=venue_id))
        else:
            # Venue form is not valid
            return render_template('forms/edit_venue.html', form=form)
    else:
        # Venue was not found
        return render_template('errors/404.html'), 404


@app.route('/venues/<int:venue_id>', methods=['DELETE'])
@csrf.exempt
def delete_venue(venue_id):
    # Get venue
    venue = Venue.query.get(venue_id)
    
    # Check if venue exists
    if venue:
        # Delete venue
        try:
            db.session.delete(venue)
            db.session.commit()
            flash(f'Venue {venue.name} was successfully deleted!')
        except:
            db.session.rollback()
            flash('An error occurred. Venue could not be deleted.')
        finally:
            db.session.close()
        
        # Redirect to home
        return redirect(url_for('index'), code=303)
    else:
        # Venue was not found
        return render_template('errors/404.html'), 404
    

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    artists = []
    now = datetime.utcnow()

    # Get artists
    for artist in db.session.query(Artist).order_by(Artist.name).all():
        # Calculate upcoming shows count
        upcoming_shows = 0
        for show in artist.shows:
            if show.start_time > now:
                upcoming_shows = upcoming_shows + 1

        # Append artist to artists
        artists.append({
            'id': artist.id,
            'name': artist.name,
            'num_upcoming_shows': upcoming_shows
        })

    # Render artists
    return render_template('pages/artists.html', artists=artists)


@app.route('/artists/search', methods=['POST'])
@csrf.exempt
def search_artists():
    artists = []
    now = datetime.utcnow()

    # Search artists
    term = request.form.get('search_term', '')
    by_city = request.form.get('search_city', False)
    if not by_city:
        for artist in db.session.query(Artist).filter(Artist.name.ilike(f'%{term}%')).order_by(Artist.name).all():
            # Calculate upcoming shows count
            upcoming_shows = 0
            for show in artist.shows:
                if show.start_time > now:
                    upcoming_shows = upcoming_shows + 1

            # Add artist to artists
            artists.append({
                'id': artist.id,
                'name': artist.name,
                'num_upcoming_shows': upcoming_shows
            })
    else:
        city = term.split(', ')[0]
        state = term.split(', ')[1]
        for artist in db.session.query(Artist).filter(and_(Artist.city.ilike(f'%{city}%'), Artist.state.ilike(f'%{state}%'))).order_by(Artist.name).all():
            # Calculate upcoming shows count
            upcoming_shows = 0
            for show in artist.shows:
                if show.start_time > now:
                    upcoming_shows = upcoming_shows + 1

            # Add artist to artists
            artists.append({
                'id': artist.id,
                'name': artist.name,
                'num_upcoming_shows': upcoming_shows
            })
    
    # Render artists
    return render_template('pages/search_artists.html', results={'count': len(artists), 'data': artists}, search_term=term)


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    now = datetime.utcnow()

    # Get artist
    artist = db.session.query(Artist).filter(Artist.id == artist_id).first()

    # Check if artist exists
    if artist:
        # Get upcoming and past shows
        past_shows = []
        upcoming_shows = []
        for show in artist.shows:
            if show.start_time < now:
                past_shows.append({
                    'venue_id': show.venue.id,
                    'venue_name': show.venue.name,
                    'venue_image_link': show.venue.image_link,
                    'start_time': show.start_time.strftime("%Y-%m-%dT%H:%M")
                })
            else:
                upcoming_shows.append({
                    'venue_id': show.venue.id,
                    'venue_name': show.venue.name,
                    'venue_image_link': show.venue.image_link,
                    'start_time': show.start_time.strftime("%Y-%m-%dT%H:%M")
                })

        # Get albums
        albums = []
        if artist.albums:
            for album in artist.albums.split('),')[:-1]:
                # Get songs
                songs = []
                for song in album.split('(')[1].split(',')[:-1]:
                    songs.append(song)
                
                # Add album to albums
                albums.append({
                    'name': album.split('(')[0],
                    'songs': songs,
                    'songs_count': len(songs)
                })

        # Render artist
        return render_template('pages/show_artist.html', artist={
            'id': artist.id,
            'name': artist.name,
            'genres': map(lambda genre: Genre[genre].value, artist.genres.split(',')[:-1]),
            'city': artist.city,
            'state': artist.state,
            'phone': artist.phone,
            'image_link': artist.image_link,
            'website_link': artist.website_link,
            'facebook_link': artist.facebook_link,
            'seeking_venue': artist.seeking_venue,
            'seeking_description': artist.seeking_description if artist.seeking_venue == True else None,
            'available_times': artist.available_times,
            'available_start': artist.available_start.strftime("%Y-%m-%dT%H:%M") if artist.available_times == True else None,
            'available_end': artist.available_end.strftime("%Y-%m-%dT%H:%M") if artist.available_times == True else None,
            'albums': albums,
            'albums_count': len(albums),
            'past_shows': past_shows[::-1],
            'upcoming_shows': upcoming_shows,
            'past_shows_count': len(past_shows),
            'upcoming_shows_count': len(upcoming_shows)
        })
    else:
        # Artist was not found
        return render_template('errors/404.html'), 404

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    # Create artist form
    form = ArtistForm()

    # Render artist form
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # Get artist form
    form = ArtistForm(request.form)

    # Validate artist form
    valid = form.validate()
    if form.phone.data.strip() != '' and not re.match(r'^[0-9]{3}-[0-9]{3}-[0-9]{4}$', form.phone.data.strip()):
        form.phone.errors = ['Phone must be in the form (xxx-xxx-xxxx).']
        valid = False

    if form.website_link.data.strip() != '' and not re.match(r"^[a-z]+://(?P<host>[^\/\?:]+)(?P<port>:[0-9]+)?(?P<path>\/.*?)?(?P<query>\?.*)?$", form.website_link.data.strip()):
        form.website_link.errors = ['Website link must be an URL.']
        valid = False

    if form.facebook_link.data.strip() != '' and not re.match(r"^[a-z]+://(?P<host>[^\/\?:]+)(?P<port>:[0-9]+)?(?P<path>\/.*?)?(?P<query>\?.*)?$", form.facebook_link.data.strip()):
        form.facebook_link.errors = ['Website link must be an URL.']
        valid = False

    if form.albums.data.strip() != '' and not re.match(r"^([a-z|A-Z|0-9|.| ]+\(([a-z|A-Z|0-9|.|'| ]+,)*\),)+$", form.albums.data.strip().replace(')', ',)') + ','):
        form.albums.errors = ['Albmus must be in the form [Album1(Song1,Song2),Album2(Song1)].']
        valid = False

    if form.available_times.data == True and form.available_start.data > form.available_end.data:
        form.available_start.errors = ['Start time must be before end time.']
        valid = False

    # Check if artist form is valid
    if valid:
        # Create artist
        artist = Artist()
        artist.name = form.name.data.strip()
        genres = ''
        for genre in form.genres.data:
            genres = genres + genre + ','
        artist.genres = genres
        artist.city = form.city.data.strip()
        artist.state = form.state.data
        artist.phone = form.phone.data.strip() if form.phone.data.strip() != '' else None
        artist.image_link = form.image_link.data.strip()
        artist.website_link = form.website_link.data.strip() if form.website_link.data.strip() != '' else None
        artist.facebook_link = form.facebook_link.data.strip() if form.facebook_link.data.strip() != '' else None
        artist.seeking_venue = form.seeking_venue.data
        artist.seeking_description = form.seeking_description.data.strip() if form.seeking_venue.data == True else None
        artist.available_times = form.available_times.data
        artist.available_start = form.available_start.data if form.available_times.data == True else None
        artist.available_end = form.available_end.data if form.available_times.data == True else None

        # Strip albums
        if form.albums.data.strip() != '':
            albums = ''
            albums_str = form.albums.data.strip().replace(')', ',)') + ','
            for album in albums_str.split('),')[:-1]:
                songs = ''
                for song in album.split('(')[1].split(',')[:-1]:
                    songs = songs + song.strip() + ','
                albums = albums + album.split('(')[0].strip() + f'({songs}),'
            artist.albums = albums
        else:
            artist.albums = None

        # Add artist
        try:
            db.session.add(artist)
            db.session.commit()
            flash(f'Artist {artist.name} was successfully listed!')
        except:
            db.session.rollback()
            flash('An error occurred. Artist could not be listed.')
        finally:
            db.session.close()

        # Render home
        return render_template('pages/home.html')
    else:
        # Artist form is not valid
        return render_template('forms/new_artist.html', form=form)


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    # Get artist
    artist = Artist.query.filter(Artist.id == artist_id).first()

    # Check if artist exists
    if artist:
        # Create artist form from existing artist
        form = ArtistForm()
        form.name.data = artist.name
        form.genres.data = artist.genres.split(',')[:-1]
        form.city.data = artist.city
        form.state.data = artist.state
        form.phone.data = artist.phone if artist.phone else ''
        form.image_link.data = artist.image_link
        form.website_link.data = artist.website_link if artist.website_link else ''
        form.facebook_link.data = artist.facebook_link if artist.facebook_link else ''
        form.albums.data = artist.albums.replace(',)', ')')[:-1] if artist.albums else ''
        form.seeking_venue.data = artist.seeking_venue
        form.seeking_description.data = artist.seeking_description if artist.seeking_venue == True else "I'm looking for venues."
        form.available_times.data = artist.available_times
        form.available_start.data = artist.available_start if artist.available_times == True else datetime.utcnow()
        form.available_end.data = artist.available_end if artist.available_times == True else datetime.utcnow()

        # Render artist form
        return render_template('forms/edit_artist.html', form=form)
    else:
        # Artist was not found
        return render_template('errors/404.html'), 404


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # Get artist
    artist = Artist.query.filter(Artist.id == artist_id).first()

    # Check if artist exists
    if artist:
        # Get artist form
        form = ArtistForm(request.form)

        # Validate artist form
        valid = form.validate()
        if form.phone.data.strip() != '' and not re.match(r'^[0-9]{3}-[0-9]{3}-[0-9]{4}$', form.phone.data.strip()):
            form.phone.errors = ['Phone must be in the form (xxx-xxx-xxxx).']
            valid = False

        if form.website_link.data.strip() != '' and not re.match(r"^[a-z]+://(?P<host>[^\/\?:]+)(?P<port>:[0-9]+)?(?P<path>\/.*?)?(?P<query>\?.*)?$", form.website_link.data.strip()):
            form.website_link.errors = ['Website link must be an URL.']
            valid = False

        if form.facebook_link.data.strip() != '' and not re.match(r"^[a-z]+://(?P<host>[^\/\?:]+)(?P<port>:[0-9]+)?(?P<path>\/.*?)?(?P<query>\?.*)?$", form.facebook_link.data.strip()):
            form.facebook_link.errors = ['Website link must be an URL.']
            valid = False

        if form.albums.data.strip() != '' and not re.match(r"^([a-z|A-Z|0-9|.| ]+\(([a-z|A-Z|0-9|.|'| ]+,)*\),)+$", form.albums.data.strip().replace(')', ',)') + ','):
            form.albums.errors = ['Albmus must be in the form [Album1(Song1,Song2),Album2(Song1)].']
            valid = False

        if form.available_times.data == True and form.available_start.data > form.available_end.data:
            form.available_start.errors = ['Start time must be before end time.']
            valid = False

        # Check if artist form is valid
        if valid:
            # Edit artist
            artist.name = form.name.data.strip()
            genres = ''
            for genre in form.genres.data:
                genres = genres + genre + ','
            artist.genres = genres
            artist.city = form.city.data.strip()
            artist.state = form.state.data
            artist.phone = form.phone.data.strip() if form.phone.data.strip() != '' else None
            artist.image_link = form.image_link.data.strip()
            artist.website_link = form.website_link.data.strip() if form.website_link.data.strip() != '' else None
            artist.facebook_link = form.facebook_link.data.strip() if form.facebook_link.data.strip() != '' else None
            artist.seeking_venue = form.seeking_venue.data
            artist.seeking_description = form.seeking_description.data.strip() if form.seeking_venue.data == True else None
            artist.available_times = form.available_times.data
            artist.available_start = form.available_start.data if form.available_times.data == True else None
            artist.available_end = form.available_end.data if form.available_times.data == True else None

            # Strip albums
            if form.albums.data.strip() != '':
                albums = ''
                albums_str = form.albums.data.strip().replace(')', ',)') + ','
                for album in albums_str.split('),')[:-1]:
                    songs = ''
                    for song in album.split('(')[1].split(',')[:-1]:
                        songs = songs + song.strip() + ','
                    albums = albums + album.split('(')[0].strip() + f'({songs}),'
                artist.albums = albums
            else:
                artist.albums = None

            # Update artist
            try:
                db.session.commit()
                flash(f'Artist {artist.name} was successfully edited!')
            except:
                db.session.rollback()
                flash('An error occurred. Artist could not be edited.')
            finally:
                db.session.close()

            # Redirect to edited artist
            return redirect(url_for('show_artist', artist_id=artist_id))
        else:
            # Artist form is not valid
            return render_template('forms/edit_artist.html', form=form)
    else:
        # Artist was not found
        return render_template('errors/404.html'), 404


@app.route('/artists/<int:artist_id>', methods=['DELETE'])
@csrf.exempt
def delete_artist(artist_id):
    # Get artist
    artist = Artist.query.get(artist_id)
    
    # Check if artist exists
    if artist:
        # Delete artist
        try:
            db.session.delete(artist)
            db.session.commit()
            flash(f'Artist {artist.name} was successfully deleted!')
        except:
            db.session.rollback()
            flash('An error occurred. Artist could not be deleted.')
        finally:
            db.session.close()
        
        # Redirect to home
        return redirect(url_for('index'), code=303)
    else:
        # Artist was not found
        return render_template('errors/404.html'), 404

#  Shows
#  ----------------------------------------------------------------


@app.route('/shows')
def shows():
    now = datetime.utcnow()

    # Get upcoming and past shows
    past_shows = []
    upcoming_shows = []
    for show in db.session.query(Show).order_by(Show.start_time).all():
        if show.start_time < now:
            past_shows.append({
                'id': show.id,
                'venue_id': show.venue.id,
                'venue_name': show.venue.name,
                'artist_id': show.artist.id,
                'artist_name': show.artist.name,
                'artist_image_link': show.artist.image_link,
                'start_time': show.start_time.strftime("%Y-%m-%dT%H:%M")
            })
        else:
            upcoming_shows.append({
                'id': show.id,
                'venue_id': show.venue.id,
                'venue_name': show.venue.name,
                'artist_id': show.artist.id,
                'artist_name': show.artist.name,
                'artist_image_link': show.artist.image_link,
                'start_time': show.start_time.strftime("%Y-%m-%dT%H:%M")
            })
    
    # Render shows
    return render_template('pages/shows.html', shows={
            'past_shows': past_shows[::-1],
            'upcoming_shows': upcoming_shows,
            'past_shows_count': len(past_shows),
            'upcoming_shows_count': len(upcoming_shows)
    })


@app.route('/shows/search', methods=['POST'])
@csrf.exempt
def search_shows():
    shows = []

    # Search shows
    term = request.form.get('search_term', '')
    by_city = request.form.get('search_city', False)
    if not by_city:
        for show in db.session.query(Show).join(Show.artist, Show.venue).filter(or_(Artist.name.ilike(f'%{term}%'), Venue.name.ilike(f'%{term}%'))).order_by(Show.start_time).all():
            # Add show to shows
            shows.append({
                'id': show.id,
                'venue_id': show.venue.id,
                'venue_name': show.venue.name,
                'artist_id': show.artist.id,
                'artist_name': show.artist.name,
                'artist_image_link': show.artist.image_link,
                'start_time': show.start_time.strftime("%Y-%m-%dT%H:%M")
            })
    else:
        city = term.split(', ')[0]
        state = term.split(', ')[1]
        for show in db.session.query(Show).join(Show.artist, Show.venue).filter(or_(and_(Artist.city.ilike(f'%{city}%'), Artist.state.ilike(f'%{state}%')), and_(Venue.city.ilike(f'%{city}%'), Venue.state.ilike(f'%{state}%')))).order_by(Show.start_time).all():
            # Add show to shows
            shows.append({
                'id': show.id,
                'venue_id': show.venue.id,
                'venue_name': show.venue.name,
                'artist_id': show.artist.id,
                'artist_name': show.artist.name,
                'artist_image_link': show.artist.image_link,
                'start_time': show.start_time.strftime("%Y-%m-%dT%H:%M")
            })

    # Render shows
    return render_template('pages/search_shows.html', results={'count': len(shows), 'data': shows}, search_term=term)


@app.route('/shows/create')
def create_shows():
    # Create show form
    form = ShowForm()

    # Render show form
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # Get show form
    form = ShowForm(request.form)

    # Validate show form
    valid = form.validate()

    artist = Artist.query.filter(Artist.id == form.artist_id.data).first()
    if artist is None:
        form.artist_id.errors = [f'No artist found with id {form.artist_id.data}.']
        valid = False
    elif artist.available_times == True and (form.start_time.data < artist.available_start or form.start_time.data > artist.available_end):
        form.start_time.errors = ["Artist isn't avaliable at that time."]
        valid = False

    if Venue.query.filter(Venue.id == form.venue_id.data).first() is None:
        form.venue_id.errors = [f'No venue found with id {form.venue_id.data}.']
        valid = False

    # Check if show form is valid
    if valid:
        # Create show
        show = Show()
        show.artist_id = form.artist_id.data
        show.venue_id = form.venue_id.data
        show.start_time = form.start_time.data

        # Add show
        try:
            db.session.add(show)
            db.session.commit()
            flash(f'Show was successfully listed!')
        except:
            db.session.rollback()
            flash('An error occurred. Show could not be listed.')
        finally:
            db.session.close()

        # Render home
        return render_template('pages/home.html')
    else:
        # Show form is not valid
        return render_template('forms/new_show.html', form=form)


@app.route('/shows/<int:show_id>/edit', methods=['GET'])
def edit_show(show_id):
    # Get show
    show = Show.query.filter(Show.id == show_id).first()

    # Check if show exists
    if show:
        # Create show form from existing show
        form = ShowForm()
        form.artist_id.data = show.artist_id
        form.venue_id.data = show.venue_id
        form.start_time.data = show.start_time

        # Render show form
        return render_template('forms/edit_show.html', form=form)
    else:
        # Show was not found
        return render_template('errors/404.html'), 404


@app.route('/shows/<int:show_id>/edit', methods=['POST'])
def edit_show_submission(show_id):
    # Get show
    show = Show.query.filter(Show.id == show_id).first()

    # Check if show exists
    if show:
        # Get show form
        form = ShowForm(request.form)

        # Validate show form
        valid = form.validate()
        
        if Artist.query.filter(Artist.id == form.artist_id.data).first() is None:
            form.artist_id.errors = [f'No artist found with id {form.artist_id.data}.']
            valid = False

        if Venue.query.filter(Venue.id == form.venue_id.data).first() is None:
            form.venue_id.errors = [f'No venue found with id {form.venue_id.data}.']
            valid = False

        # Check if show form is valid
        if valid:
            # Edit show
            show.artist_id = form.artist_id.data
            show.venue_id = form.venue_id.data
            show.start_time = form.start_time.data

            # Update show
            try:
                db.session.commit()
                flash(f'Show was successfully edited!')
            except:
                db.session.rollback()
                flash('An error occurred. Show could not be edited.')
            finally:
                db.session.close()

            # Redirect to shows
            return redirect(url_for('shows'))
        else:
            # Show form is not valid
            return render_template('forms/edit_show.html', form=form)
    else:
        # Show was not found
        return render_template('errors/404.html'), 404


@app.route('/shows/<int:show_id>', methods=['DELETE'])
@csrf.exempt
def delete_show(show_id):
    # Get show
    show = Show.query.get(show_id)
    
    # Check if show exists
    if show:
        # Delete show
        try:
            db.session.delete(show)
            db.session.commit()
            flash(f'Show was successfully deleted!')
        except:
            db.session.rollback()
            flash('An error occurred. Show could not be deleted.')
        finally:
            db.session.close()
        
        # Redirect to home
        return redirect(url_for('index'), code=303)
    else:
        # Show was not found
        return render_template('errors/404.html'), 404


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
