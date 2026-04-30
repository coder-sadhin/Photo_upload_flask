import re
from datetime import datetime
from app import db


class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    slug = db.Column(db.String(80), nullable=False, unique=True, index=True)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @staticmethod
    def slugify(name):
        raw = ' '.join((name or '').strip().split())
        if not raw:
            return None
        slug = re.sub(r'[^a-z0-9]+', '-', raw.lower()).strip('-')
        return (slug or None)[:80]

    @classmethod
    def get_or_create(cls, name, user_id=None):
        raw = ' '.join((name or '').strip().split())
        if not raw:
            return None
        slug = cls.slugify(raw)
        if not slug:
            return None
        row = cls.query.filter_by(slug=slug).first()
        if row:
            return row
        row = cls(name=raw[:80], slug=slug, created_by_id=user_id)
        db.session.add(row)
        db.session.flush()
        return row

    def __repr__(self):
        return f'<Category {self.slug}>'
