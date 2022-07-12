from memoapp import db

from datetime import datetime


class User(db.Model):
    id = db.Column(db.String(12), unique=True, primary_key=True)
    
    password = db.Column(db.String(60), unique=False, nullable=False)
    email = db.Column(db.String(50), unique=False, nullable=False)
    name = db.Column(db.String(50), unique=False, nullable=False)
    used_bytes = db.Column(
        db.BigInteger, unique=False, nullable=False, default=0)

    create_time = db.Column(
        db.DateTime, unique=False, nullable=False, default=datetime.now)

    memos = db.relationship("Memo", back_populates="parent")
    directories = db.relationship("Directory", back_populates="parent")


class Memo(db.Model):
    id = db.Column(db.String(12), unique=True, primary_key=True)

    name = db.Column(db.String(50), unique=False, nullable=False)
    content = db.Column(db.Text, unique=False, nullable=True)
    preview = db.Column(db.String(50), unique=False, nullable=True)

    version = db.Column(db.String(8), unique=False, nullable=False)
    create_time = db.Column(
        db.DateTime, unique=False, nullable=False, default=datetime.now)
    edit_time = db.Column(db.DateTime, unique=False, nullable=True)

    owner = db.relationship("User", back_populates="memos")
    owner_id = db.Column(db.String(12), db.ForeignKey("user.id"))
    parent = db.relationship("Directory", back_populates="memos")
    parent_id = db.Column(db.String(12), db.ForeignKey("directory.id"))


class Directory(db.Model):
    id = db.Column(db.String(12), unique=True, primary_key=True)

    name = db.Column(db.String(50), unique=False, nullable=False)

    version = db.Column(db.String(8), unique=False, nullable=False)
    create_time = db.Column(
        db.DateTime, unique=False, nullable=False, default=datetime.now)
    edit_time = db.Column(db.DateTime, unique=False, nullable=True)

    owner = db.relationship("User", back_populates="directories")
    owner_id = db.Column(db.String(12), db.ForeignKey("user.id"))
    parent = db.relationship(
        "Directory", back_populates="directories", remote_side=['id'])
    parent_id = db.Column(db.String(12), db.ForeignKey("directory.id"))

    memos = db.relationship("Memo", back_populates="parent")
    directories = db.relationship("Directory", back_populates="parent")
