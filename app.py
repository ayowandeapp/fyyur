#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import sys
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_migrate import Migrate

import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# TODO: connect to a local postgresql database
migrate = Migrate(app, db)
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#




# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

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
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  data=[]
  parents= Venue.query.with_entities(Venue.state,Venue.city,Venue.id).distinct()
  for p in parents:
    city_state = {
        "city" : p.city,
        "state": p.state,
        "venues":[]
    } 
    venues = Venue.query.filter_by(state = p.state).filter_by(city = p.city).all()
    # to format each venues
    format_venues = []
    for v in venues:
      format_venues.append({
        "id": v.id,
        "name":v.name,
        "num_upcoming_shows": len(list(filter(lambda x: x.start_time > datetime.now(), v.shows)))
        })
    city_state['venues'] = format_venues
    data.append(city_state)

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  get_search = request.form.get('search_term','')
  venues = (db.session.query(Venue).filter( Venue.name.ilike(f"%{get_search}%") |
   Venue.city.ilike(f"%{get_search}%") | Venue.state.ilike(f"%{get_search}%")).all()) 
  response = { 
      "count": len(venues), 
      "data": [] 
      } 

  for venue in venues: 
    temp = {} 
    temp["id"] = venue.id
    temp["name"] = venue.name 
    num_upcoming_shows = 0  

    for show in venue.shows:
      if show.start_time > datetime.now(): 
        num_upcoming_shows =+ 1
      temp["num_upcoming_shows"] = num_upcoming_shows

    response["data"].append(temp)
  return render_template('pages/search_venues.html', results=response, search_term=get_search)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  get_venue = Venue.query.get(venue_id)
  setattr(get_venue, "genres", get_venue.genres.split(","))
  #iterate to get the past shows
  get_past_shows= db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).filter(Show.start_time < datetime.now()).all()
  past_shows = [] 
  for show in get_past_shows:
    temp = {} 
    temp["artist_id"] = show.artist_id 
    temp["artist_name"] = show.artists.name
    temp["artist_image_link"] = show.artists.image_link 
    temp["start_time"] = show.start_time.strftime("%m/%d/%Y, %H:%M:%S") 
    past_shows.append(temp) 
  
    setattr(get_venue, "past_shows", past_shows) 
    setattr(get_venue,"past_shows_count", len(past_shows)) 

    #get furure shows
    get_upcoming_shows = db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).filter(Show.start_time > datetime.now()).all() 
    upcoming_shows = [] 
    for show in upcoming_shows: 
      temp = {} 
      temp["artist_id"] = show.artist_id
      temp["artist_name"] = show.artist.name 
      temp["artist_image_link"] = show.artist.image_link 
      temp["start_time"] = show.start_time.strftime("%m/%d/%Y, %H:%M:%S") 
      upcoming_shows.append(temp) 
  
    setattr(get_venue, "upcoming_shows", upcoming_shows)  
    setattr(get_venue,"upcoming_shows_count", len(upcoming_shows)) 


  #data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  return render_template('pages/show_venue.html', venue=get_venue)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm(request.form)
  if form.validate:
    try:
      venue = Venue(
        name=request.form['name'],
        city=request.form['city'], 
        state=request.form['state'],
        address=request.form['address'],
        phone=request.form['phone'],
        genres=", ".join(request.form.get('genres')), 
        image_link=request.form['image_link'],
        facebook_link=request.form['facebook_link'], 
        website_link=request.form['website_link'],
        seeking_venue=request.form.get('seeking_venue'),
        seeking_description=request.form['seeking_description'
        ])
      db.session.add(venue)
      db.session.commit();
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except:
      db.session.rollback()
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')    
    finally:
      db.session.close()
  else:
    flash('An error occurred. Venue ')
  return render_template('pages/home.html')
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  #flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  #return render_template('pages/home.html')

@app.route('/venues/<venue_id>/delete', methods=['GET'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  error=False
  try:
    #the two tables are linked togeather
    get_venue=Venue.query.get(venue_id)
    db.session.delete(get_venue)
    db.session.commit()
  except:
    error=True
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    flash('An error occurred')
    abort(500)
  else:
    flash('Deleted Successfully')
    return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data= db.session.query(Artist).all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  get_search = request.form.get('search_term','')
  artists = (db.session.query(Artist).filter( Artist.name.ilike(f"%{get_search}%") |
   Artist.city.ilike(f"%{get_search}%") | Artist.state.ilike(f"%{get_search}%")).all()) 
  response = { "count": len(artists), "data": [] } 

  for artist in artists: 
    temp = {} 
    temp["id"] = artist.id
    temp["name"] = artist.name 
    upcoming_shows = 0  

    for show in artist.shows:
      if show.start_time > datetime.now(): 
        upcoming_shows =+ 1
      temp["upcoming_shows"] = upcoming_shows
    response["data"].append(temp)

  return render_template('pages/search_artists.html', results=response, search_term=get_search)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  get_artist = Artist.query.get(artist_id)
  #split the string where there is a comma
  setattr(get_artist, "genres", get_artist.genres.split(","))
  #get the past shows
  past_shows= db.session.query(Show).join(Artist).filter(Show.artist_id==artist_id).filter(Show.start_time < datetime.now()).all()
  list_shows = []
  for show in past_shows:
    temp = {}
    temp["venue_name"] = show.venues.name
    temp["venue_id"] = show.venues.id
    temp["venue_image_link"] = show.venues.image_link
    temp["start_time"] = show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
    list_shows.append(temp)
  setattr(get_artist, "past_shows", list_shows)
  setattr(get_artist, "past_shows_count", len(list_shows))

  #get the upcoming shows
  upcoming_shows = db.session.query(Show).join(Artist).filter(Show.artist_id==artist_id).filter(Show.start_time > datetime.now()).all()
  list_shows = []
  for show in upcoming_shows:
    temp = {}
    temp["venue_name"] = show.venues.name
    temp["venue_id"] = show.venues.id
    temp["venue_image_link"] = show.venues.image_link
    temp["start_time"] = show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
    list_shows.append(temp)
  setattr(get_artist, "upcoming_shows", list_shows)
  setattr(get_artist, "upcoming_shows_count", len(list_shows))
  return render_template('pages/show_artist.html', artist=get_artist)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  # TODO: populate form with fields from artist with ID <artist_id>
  get_artist = Artist.query.get(artist_id)
  form.genres.data = get_artist.genres.split(",")
  return render_template('forms/edit_artist.html', form=form, artist=get_artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  form = ArtistForm(request.form)
  if form.validate:
    try:
      artist = Artist.query.get(artist_id)
      if request.form.get('seeking_venue'):
        seeking_venue=1
      else:
        seeking_venue = 0
      artist.name = request.form['name']
      artist.city=request.form['city']
      artist.state=request.form['state']
      artist.phone=request.form['phone']
      artist.image_link=request.form['image_link']
      artist.facebook_link=request.form['facebook_link']
      artist.website_link=request.form['website_link']
      artist.seeking_venue=seeking_venue
      artist.seeking_description=request.form['seeking_description']
      artist.genres=", ".join(request.form.get('genres'))
      db.session.commit()
      flash('Artist ' + request.form['name'] + ' was successfully Updated!')
    except:
      db.session.rollback()
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
    finally:
      db.session.close()
  else:
    flash('An error occurred.')
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  # TODO: populate form with values from venue with ID <venue_id>
  venue = Venue.query.get(venue_id)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  form = VenueForm(request.form)
  if form.validate:
    try:
      venue = Venue.query.get(venue_id)
      if request.form.get('seeking_venue'):
        seeking_venue=1
      else:
        seeking_venue = 0
      venue.name = request.form['name']
      venue.address=request.form['address']
      venue.city=request.form['city']
      venue.state=request.form['state']
      venue.phone=request.form['phone']
      venue.image_link=request.form['image_link']
      venue.facebook_link=request.form['facebook_link']
      venue.website_link=request.form['website_link']
      venue.seeking_venue=seeking_venue
      venue.seeking_description=request.form['seeking_description']
      venue.genres=", ".join(request.form.get('genres'))
      db.session.commit()
      flash('Venue ' + request.form['name'] + ' was successfully Updated!')
    except:
      db.session.rollback()
      flash('An error occurred. could not be edited')
    finally:
      db.session.close()
  else:
    flash('An error occurred. Venue ')
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
  # TODO: insert form data as a new Venue record in the db, instead
  form = ArtistForm(request.form)
  if form.validate:
    try:
      artist = (Artist(
        name=form.name.data,
        city=form.city.data,
        state=form.state.data,
        phone=form.phone.data,
        image_link=form.image_link.data,
        facebook_link=form.facebook_link.data,
        website_link=form.website_link.data,
        seeking_venue=form.seeking_venue.data,
        seeking_description=form.seeking_description.data,
        genres=", ".join(form.genres.data)
        ))
      db.session.add(artist)
      db.session.commit();
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except:
      db.session.rollback()
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
    finally:
      db.session.close()
  else:
    flash('An error occurred.')
  return render_template('pages/home.html')



#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  data = []
  get_shows = Show.query.all()
  for show in get_shows:
    temp={}
    temp['venue_id'] = show.venues.id
    temp['venue_name'] = show.venues.name
    temp['artist_id'] = show.artists.id
    temp['artist_name'] = show.artists.name
    temp['artist_image_link'] = show.artists.image_link
    temp["start_time"] = show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
    data.append(temp)
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
  get_artist = db.session.query(Artist).filter(Artist.id==request.form.get('artist_id')).count()
  get_venue = db.session.query(Venue).filter(Venue.id==request.form.get('venue_id')).count()
  form = ShowForm(request.form)
  if form.validate:
    if get_artist == 0 or get_venue ==0:
      flash('An error occurred. Venue ID or Artist ID does not exist.')
    else:
      try:
        shows = Show(artist_id=request.form.get('artist_id'),venue_id=request.form.get('venue_id'),start_time=request.form.get('start_time'))
        db.session.add(shows)
        db.session.commit();
        flash('Show was successfully listed!')
      except:
        db.session.rollback()
        flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
      finally:
        db.session.close()
  else:
    flash('An error occurred.')    
  return render_template('pages/home.html')

  # on successful db insert, flash success
  #flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  #return render_template('pages/home.html')

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
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
