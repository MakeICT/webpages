from flask import render_template, flash, request, redirect, url_for, send_from_directory, g
from werkzeug.utils import secure_filename
from flask_api import status
import os


from webpages import app, db
from webpages.models import FileInfo

import logging, time, traceback, os, sys
import configparser

from wildapricot_api import WaApiClient


WA_API = WaApiClient()

config = configparser.SafeConfigParser()
config.read('config.ini')

selected_file = None

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']
           # filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def main():
    return render_template('main.html', selected_file=get_active_file()[0])

@app.route('/events', methods=['GET'])
def upcoming_events():

    while(not WA_API.ConnectAPI(config['api']["key"])):
        time.sleep(5)

    upcoming_events = WA_API.GetUpcomingEvents()
    upcoming_events = sorted(upcoming_events, key=lambda event: event['StartDate'])
    event_list = []
    for event in upcoming_events:
        if not event['AccessLevel'] == 'AdminOnly':
            if event['RegistrationsLimit']:
                # print(event['RegistrationsLimit'], event['ConfirmedRegistrationsCount'])
                spots_available = event['RegistrationsLimit'] - event['ConfirmedRegistrationsCount']
                spots = None
                if spots_available > 0:
                    spots = str(spots_available) + 'Register'
                else:
                    spots = 'FULL'
            start_date = WA_API.WADateToDateTime(event['StartDate'])
            if 'test' not in event['Name'].lower():
                event_list.append({
                                    "Name":event['Name'],
                                    "Date": start_date.strftime('%b %d'),
                                    "Time": start_date.strftime('%I:%M %p'),
                                    "Register":"http://makeict.wildapricot.org/event-" + str(event['Id']),
                                  })

            #       str(event['Id']))
            # print(start_date.strftime('%b %d') + ' | ' + start_date.strftime('%I:%M %p') + 
            #       ' | ' + event['Name'] + ' | ' + '<a href="http://makeict.wildapricot.org/event-' + 
            #       str(event['Id']) + '" target="_blank">Register</a><br />')

    return render_template('events.html', events=event_list)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

@app.route('/check_file/<filename>')
def check_file(filename):
    if filename in os.listdir('./uploads'):
        return "Found file: " + filename, status.HTTP_200_OK
    else:
        return "File not found", status.HTTP_404_NOT_FOUND

@app.route('/set_active_file/<filename>', methods=['POST'])
def set_active_file(filename):
    if filename == None or check_file(filename)[1] == status.HTTP_200_OK:
        db.session.add(FileInfo(selected_file = filename))
        db.session.commit()
        print("setting active file:",filename)
        return "OKAY", status.HTTP_200_OK

    else:
        return "File not found", status.HTTP_404_NOT_FOUND

@app.route('/get_active_file')
def get_active_file():
    print("returning active file")
    try:
        file = FileInfo.query.all()[-1].selected_file
    except:
        file = "No file selected"
    if file == None:
        file = "No file selected"
    return file, status.HTTP_200_OK

@app.route('/delete/<filename>', methods=['POST'])
def delete_file(filename):
    if filename in os.listdir('./uploads'):
        if(allowed_file(filename)):
            os.remove("./uploads/" + filename)
            print(get_active_file())
            if filename == get_active_file()[0]:
                print("setting active file to None")
                set_active_file(None)
    return redirect(url_for('upload_file'))

@app.route('/delete_all', methods=['POST'])
def delete_all():
    for file in os.listdir('./uploads'):
        delete_file(file)
    return redirect(url_for('upload_file'))