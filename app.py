#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import sys
from sys import exc_info
from sqlalchemy import DateTime
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# TODO: connect to a local postgresql database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://lydia@localhost:5432/new_fyurrapp'

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.Column(db.String(150))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(500))
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.Text())
    shows = db.relationship('Show', backref='venue', lazy=True)

    def __repr__(self):
      return f'<Venue: {self.id}, {self.name}, {self.genres}>'

   
class Artist(db.Model):
    __tablename__ = 'Artist'
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(500))
    seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.Text())
    shows = db.relationship('Show', backref='artist', lazy=True)

    def __repr__(self):
      return f'<Artist: {self.id}, {self.name}, {self.genres}>'
   

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
    __tablename__ = 'Show'
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    start_time = db.Column(db.DateTime(), nullable=False)

    def __repr__(self):
      return f'<Show: {self.id}, {self.start_time}>'

#db.create_all()

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  list_of_venues = Venue.query.all()

  venues_dict = {}

  for venue in list_of_venues:
    key = f'{venue.city}, {venue.state}'

    venues_dict.setdefault(key, []).append({
      'id': venue.id,
      'name': venue.name,
      'city': venue.city,
      'state': venue.state,
    })

  data = []
  for value in venues_dict.values():
    data.append({
      'city': value[0]['city'],
      'state': value[0]['state'],
      'venues': value
    })

  return render_template('pages/venues.html', areas=data)


# TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
# seach for Hop should return "The Musical Hop".
# search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
@app.route('/venues/search', methods=['POST'])
def search_venues():
    search_term = request.form.get('search_term', '')
    venues = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()

    response = {
      'count': len(venues),
      'data': []
    }

    for result in venues:
      response['data'].append({
        'id': result.id,
        'name': result.name,
        'num_upcoming_shows': len(result.shows)
      })
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))
    

# shows the venue page with the given venue_id
# TODO: replace with real venue data from the venues table, using venue_id
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = Venue.query.get(venue_id)
  print(venue)
  past_shows = []
  upcoming_shows = []
  show_details = None

  for show in venue.shows:
    show_details = {
      'artist_id' : show.artist.id,
      'artist_name' : show.artist.name,
      'artist_image_link' : show.artist.image_link,
      'start_time' : show.start_time.strftime('%m/%d/%Y, %H:%M:%S')
    }

    if show.start_time <= datetime.now():
      past_shows.append(show_details)
    else:
      upcoming_shows.append(show_details)    

  data = {
    'id' : venue.id,
    'name' : venue.name,
    'genres' : venue.genres,
    'address' : venue.address,
    'city' : venue.city,
    'state' : venue.state,
    'phone' : venue.phone,
    'website' : venue.website,
    'image_link' : venue.image_link,
    'facebook_link' : venue.facebook_link,
    'seeking_talent' : venue.seeking_talent,
    'seeking_description' : venue.seeking_description,
    'upcoming_shows_count' : len(upcoming_shows),
    'upcoming_shows' : upcoming_shows,
    'past_shows_count' : len(past_shows),
    'past_shows' : past_shows,
  }
  return render_template('pages/show_venue.html', venue=data)


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  try:
    venue = Venue(
      name=request.form['name'],
      city=request.form['city'],
      state=request.form['state'],
      address=request.form['address'],
      phone=request.form['phone'],
      genres=request.form.getlist('genres'),
      facebook_link=request.form['facebook_link']
    )
    db.session.add(venue)
    db.session.commit()
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  except:
    message = 'could not be listed'
    if SQLAlchemyError:
      message = 'already exist'
    flash('Venue ' + request.form['name'] + ' ' + message)
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  return render_template('pages/home.html')      
 


# TODO: Complete this endpoint for taking a venue_id, and using
# SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
# BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
# clicking that button delete it from the db then redirect the user to the homepage
@app.route('/venues/<venue_id>', methods=['POST'])
def delete_venue(venue_id):
  try:
    ven_id = request.form["venue_name"]
    venue_to_delete = Venue.query.get(ven_id)
    db.session.delete(venue_to_delete)
    db.session.commit()
    flash('Venue ' + request.form['venue_name'] + ' was successfully deleted')
  except:
    flash('Venue ' + request.form['venue_name'] + ' could not be deleted')
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()    
  return redirect(url_for('index'))


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  list_of_artists = Artist.query.all()
  artist_dict = {}
  data = []

  for artist in list_of_artists:
    artist_dict = {
      'id': artist.id,
      'name': artist.name
    }
    data.append(artist_dict)

  return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term', '')
  artists = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()

  response = {
    'count': len(artists),
    'data': []
  }

  for result in artists:
    response['data'].append({
      'id': result.id,
      'name': result.name,
      'num_upcoming_shows': len(result.shows)
    })
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))
  

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):  
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  artist = Artist.query.get(artist_id)
  past_shows = []
  upcoming_shows = []
  show_details = None

  for show in artist.shows:
    show_details = {
      'venue_id' : show.venue.id,
      'venue_name' : show.venue.name,
      'venue_image_link' : show.venue.image_link,
      'start_time' : show.start_time.strftime('%m/%d/%Y, %H:%M:%S')
    }

    if show.start_time <= datetime.now():
      past_shows.append(show_details)
    else:
      upcoming_shows.append(show_details)    


  data = {
    'id' : artist.id,
    'name' : artist.name,
    'genres' : artist.genres,
    'city' : artist.city,
    'state' : artist.state,
    'phone' : artist.phone,
    'website' : artist.website,
    'image_link' : artist.image_link,
    'facebook_link' : artist.facebook_link,
    'seeking_venue' : artist.seeking_venue,
    'seeking_description' : artist.seeking_description,
    'upcoming_shows_count' : len(upcoming_shows),
    'upcoming_shows' : upcoming_shows,
    'past_shows_count' : len(past_shows),
    'past_shows' : past_shows,
  }
  return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  # TODO: populate form with fields from artist with ID <artist_id>
  form = ArtistForm()
  artist_to_edit = Artist.query.get(artist_id)
  artist={
    'id': artist_to_edit.id,
    'name': artist_to_edit.name,
    'genres': artist_to_edit.genres,
    'city': artist_to_edit.city,
    'state': artist_to_edit.state,
    'phone': artist_to_edit.phone,
    'website': artist_to_edit.website,
    'facebook_link': artist_to_edit.facebook_link,
    'seeking_venue': artist_to_edit.seeking_venue,
    'seeking_description': artist_to_edit.seeking_description,
    'image_link': artist_to_edit.image_link
  }
  
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  artist = Artist.query.get(artist_id)
  try:
    artist.name = request.form['name']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    artist.genres = request.form.getlist('genres')
    artist.facebook_link = request.form['facebook_link']
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully updated')
  except:
    flash('Artist ' + request.form['name'] + ' could not be updated')
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()    

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  # TODO: populate form with values from venue with ID <venue_id>
  form = VenueForm()
  venue_to_edit = Venue.query.get(venue_id)
  venue={
    'id': venue_to_edit.id,
    'name': venue_to_edit.name,
    'genres': venue_to_edit.genres,
    'address': venue_to_edit.address,
    'city': venue_to_edit.city,
    'state': venue_to_edit.state,
    'phone': venue_to_edit.phone,
    'website': venue_to_edit.website,
    'facebook_link': venue_to_edit.facebook_link,
    'seeking_talent': venue_to_edit.seeking_talent,
    'seeking_description': venue_to_edit.seeking_description,
    'image_link': venue_to_edit.image_link
  }
  
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  venue = Venue.query.get(venue_id)
  try:
    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.address = request.form['address']
    venue.phone = request.form['phone']
    venue.genres = request.form.getlist('genres')
    venue.facebook_link = request.form['facebook_link']
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully updated')
  except:
    flash('Venue ' + request.form['name'] + ' could not be updated')
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()    
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Artist record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  try:
    new_artist = Artist(
      name=request.form['name'],
      city=request.form['city'],
      state=request.form['state'],
      phone=request.form['phone'],
      genres=request.form.getlist('genres'),
      facebook_link=request.form['facebook_link']
    )
    db.session.add(new_artist)
    db.session.commit()
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  except:
    flash('An error occured. Artist ' + request.form['name'] + ' could not be listed!')
    db.session.rollback()
    print(sys.exc_info)
  finally:
    db.session.close()  
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  # num_shows should be aggregated based on number of upcoming shows per venue.
  list_of_shows = Show.query.all()
  show_dict = {}

  data = []
  for show in list_of_shows:
    show_dict = {
      'venue_id': show.venue_id,
      'venue_name': show.venue.name,
      'artist_id': show.artist_id,
      'artist_name': show.artist.name,
      'artist_image_link': show.artist.image_link,
      'start_time': show.start_time.strftime('%m/%d/%Y, %H:%M:%S')
    }
    data.append(show_dict)

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  try:
    new_show = Show(
      artist_id=request.form['artist_id'],
      venue_id=request.form['venue_id'],
      start_time=request.form['start_time']
    )
    db.session.add(new_show)
    db.session.commit()
    # on successful db insert, flash success
    flash('Show was successfully listed!')
  except:
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    flash('An error occured. Show could not be listed.')
    db.session.rollback()
    print(sys.exc_info) 
  finally:
    db.session.close()   

  return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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
    app.run(debug=True)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
