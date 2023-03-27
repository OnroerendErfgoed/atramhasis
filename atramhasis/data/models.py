import enum

from skosprovider_sqlalchemy.models import ConceptScheme
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Enum
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import JSON
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()


class IDGenerationStrategy(enum.Enum):
    NUMERIC = enum.auto()
    GUID = enum.auto()
    MANUAL = enum.auto()


class ExpandStrategy(enum.Enum):
    RECURSE = 'recurse'
    VISIT = 'visit'


class ConceptschemeVisitLog(Base):
    __tablename__ = 'conceptscheme_visit_log'
    id = Column(Integer, primary_key=True, autoincrement=True)
    conceptscheme_id = Column(String(25), nullable=False)
    visited_at = Column(DateTime, default=func.now(), nullable=False)
    origin = Column(String(25), nullable=False)


class ConceptVisitLog(Base):
    __tablename__ = 'concept_visit_log'
    id = Column(Integer, primary_key=True, autoincrement=True)
    concept_id = Column(Integer, nullable=False)
    conceptscheme_id = Column(String(25), nullable=False)
    visited_at = Column(DateTime, default=func.now(), nullable=False)
    origin = Column(String(25), nullable=False)


class ConceptschemeCounts(Base):
    __tablename__ = 'conceptscheme_counts'
    id = Column(Integer, primary_key=True, autoincrement=True)
    conceptscheme_id = Column(String(25), nullable=False)
    counted_at = Column(DateTime, default=func.now(), nullable=False)
    triples = Column(Integer, nullable=False)
    conceptscheme_triples = Column(Integer, nullable=False)
    avg_concept_triples = Column(Integer, nullable=False)


class Provider(Base):
    __tablename__ = 'provider'

    id = Column(String, primary_key=True)
    conceptscheme_id = Column(
        Integer,
        ForeignKey(ConceptScheme.id),
        nullable=False,
    )
    uri_pattern = Column(Text, nullable=False)
    meta = Column('metadata', JSON, nullable=False)  # metadata is reserved in sqlalchemy
    expand_strategy = Column(Enum(ExpandStrategy))

    conceptscheme = relationship(
        ConceptScheme, uselist=False, single_parent=True, cascade='all, delete-orphan',
    )

    @hybrid_property
    def default_language(self):
        return self.meta.get('default_language')

    @default_language.setter
    def default_language(self, value):
        self.meta['default_language'] = value

    @hybrid_property
    def force_display_language(self):
        return self.meta.get('atramhasis.force_display_language')

    @force_display_language.setter
    def force_display_language(self, value):
        self.meta['atramhasis.force_display_language'] = value

    @hybrid_property
    def id_generation_strategy(self):
        return IDGenerationStrategy[self.meta.get('atramhasis.id_generation_strategy')]

    @id_generation_strategy.setter
    def id_generation_strategy(self, value):
        self.meta['atramhasis.id_generation_strategy'] = value.name

    @hybrid_property
    def subject(self):
        return self.meta.get('subject')

    @subject.setter
    def subject(self, value):
        self.meta['subject'] = value
