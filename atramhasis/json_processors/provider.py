from typing import Mapping

from skosprovider.registry import Registry
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from atramhasis import mappers
from atramhasis.data.datamanagers import ProviderDataManager
from atramhasis.data.models import Provider
from atramhasis.errors import SQLAlchemyProviderNotFoundException
from atramhasis.errors import ValidationError
from atramhasis.scripts.delete_scheme import delete_scheme
from atramhasis.validators import validate_provider_json


def create_provider(json_data: Mapping, session: Session, skos_registry: Registry) -> Provider:
    """Process a provider JSON into a newly stored Provider."""
    for provider in skos_registry.get_providers():
        if provider.get_vocabulary_uri() == json_data["conceptscheme_uri"]:
            raise ValidationError(
                "Provider could not be validated.",
                [{"conceptscheme_uri": "Collides with existing provider."}],
            )
    validate_provider_json(json_data)
    db_provider = mappers.map_provider(json_data)
    if not db_provider.id:
        # Store conceptscheme first so we can copy its id
        session.add(db_provider.conceptscheme)
        session.flush()
        db_provider.id = str(db_provider.conceptscheme.id)

    session.add(db_provider)
    session.flush()

    return db_provider


def update_provider(provider_id: str, json_data: Mapping, session: Session) -> Provider:
    """Process a JSON into to update an existing provider."""
    validate_provider_json(json_data, provider_id)
    manager = ProviderDataManager(session)
    db_provider = manager.get_provider_by_id(provider_id)
    db_provider = mappers.map_provider(json_data, provider=db_provider)
    session.flush()
    return db_provider


def delete_provider(provider_id, session: Session) -> None:
    manager = ProviderDataManager(session)
    try:
        db_provider = manager.get_provider_by_id(provider_id)
    except NoResultFound:
        raise SQLAlchemyProviderNotFoundException(provider_id)
    delete_scheme(session, db_provider.conceptscheme.id)
    session.delete(db_provider)
