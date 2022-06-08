from app import db

from datetime import datetime


class User(db.Model):
    id = db.Column(db.String(12), primary_key=True)
    password = db.Column(db.String(60), unique=False, nullable=False)
    email = db.Column(db.String(320), unique=True, nullable=False)
    name = db.Column(db.String(50), unique=False, nullable=False)

    memos = db.relationship("Memo", back_populates="owner")
    directories = db.relationship("Directory", back_populates="owner")

    total_space = db.Column(db.Integer, unique=False, default=0)
    create_time = db.Column(db.DateTime, unique=False, default=datetime.now)


class Memo(db.Model):
    id = db.Column(db.String(12), primary_key=True)
    name = db.Column(db.String(50), unique=False, nullable=False)
    content = db.Column(db.Text, unique=False, nullable=False)

    owner = db.relationship("User", back_populates="memos")
    owner_id = db.Column(
        db.String(12), db.ForeignKey('user.id'), nullable=False)
    parent = db.relationship("Directory", back_populates="memos")
    parent_id = db.Column(
        db.String(12), db.ForeignKey('directory.id'), nullable=False)

    version = db.Column(db.String(8), unique=False, nullable=False)
    create_time = db.Column(db.DateTime, unique=False, default=datetime.now)
    edit_time = db.Column(db.DateTime, unique=False, nullable=True)

    def to_json(self, strip=False):
        if len(self.content) > 50:
            preview = self.content[:47] + "..."
        else:
            preview = self.content

        return {
            "type": "M",
            "id": self.id,
            "name": self.name,
            "content": self.content if not strip else None,
            "preview": preview,
            "parent": self.parent_id,
            "version": self.version,
            "create_time": self.create_time.timestamp(),
            "edit_time": self.edit_time.timestamp()
        }


class Directory(db.Model):
    id = db.Column(db.String(12), primary_key=True)
    name = db.Column(db.String(50), unique=False, nullable=False)

    memos = db.relationship("Memo", back_populates="parent")
    directories = db.relationship("Directory", back_populates="parent")

    owner = db.relationship("User", back_populates="directories")
    owner_id = db.Column(
        db.String(12), db.ForeignKey('user.id'), nullable=False)
    parent = db.relationship("Directory", back_populates="directories")
    parent_id = db.Column(
        db.String(12), db.ForeignKey('directory.id'), nullable=False)

    version = db.Column(db.String(8), unique=False, nullable=False)
    create_time = db.Column(db.DateTime, unique=False, default=datetime.now)
    edit_time = db.Column(db.DateTime, unique=False, nullable=True)

    def to_json(self, strip=False):
        if not strip:
            memos = [memo.to_json(strip=True) for memo in self.memos]
            dirs = [dir_.to_json(strip=True) for dir_ in self.directories]
        else:
            memos = None
            dirs = None

        return {
            "type": "D",
            "id": self.id,
            "name": self.name,
            "directories": dirs,
            "memos": memos,
            "is_empty": not dirs,
            "parent": self.parent_id,
            "version": self.version,
            "create_time": self.create_time.timestamp(),
            "edit_time": self.edit_time.timestamp()
        }
