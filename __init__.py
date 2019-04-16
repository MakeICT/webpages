from flask import Flask
# from flask import Flask, render_template, flash, request, redirect, url_for, send_from_directory, g
from flask_sqlalchemy import SQLAlchemy


UPLOAD_FOLDER = './uploads'
# ALLOWED_EXTENSIONS = set(['hpgl', 'plt'])

app = Flask(__name__)
app.config['SECRET_KEY'] = 'you-will-never-guess'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = set(['hpgl', 'plt'])
# app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

db = SQLAlchemy(app)

from webpages import routes