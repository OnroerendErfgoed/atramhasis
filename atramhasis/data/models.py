from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime)
from sqlalchemy.sql import (
    func
)

Base = declarative_base()


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
