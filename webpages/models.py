from datetime import datetime
from webpages import db

class FileInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    selected_file = db.Column(db.String(120), unique=False, nullable=True)

    def __repr__(self):
        return "FileInfo('{selected_file}')".format(selected_file = self.selected_file)