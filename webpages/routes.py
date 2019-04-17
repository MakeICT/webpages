from flask import render_template, flash, request, redirect, url_for, send_from_directory, g
from werkzeug.utils import secure_filename
from flask_api import status
import os
import json

from webpages import app, db
from webpages.models import FileInfo

import logging, time, traceback, os, sys
import configparser

from wildapricot_api import WaApiClient


WA_API = WaApiClient()

config = configparser.SafeConfigParser()
config.read('config.ini')


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
                                    "Id": event["Id"],
                                    "Name":event['Name'],
                                    "Date": start_date.strftime('%b %d %Y'),
                                    "Time": start_date.strftime('%I:%M %p'),
                                    "Register":"http://makeict.wildapricot.org/event-" + str(event['Id']),
                                  })

            #       str(event['Id']))
            # print(start_date.strftime('%b %d') + ' | ' + start_date.strftime('%I:%M %p') + 
            #       ' | ' + event['Name'] + ' | ' + '<a href="http://makeict.wildapricot.org/event-' + 
            #       str(event['Id']) + '" target="_blank">Register</a><br />')

    return render_template('events.html', events=event_list)

@app.route("/event/<eventId>")
def event_details(eventId):
    while(not WA_API.ConnectAPI(config['api']["key"])):
        time.sleep(5)

    event = WA_API.GetEventByID(eventId)

    event_details = {
        "Description": event["Details"]["DescriptionHtml"],
        "Instructor": [tag.split(':')[1] for tag in event["Tags"]][0],
    }

    print(event_details)

    return json.dumps(event_details)