"""cascades

Revision ID: 3e9675b35dfc
Revises: cb568ec81000
Create Date: 2020-08-12 14:48:35.592316

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "3e9675b35dfc"
down_revision = "cb568ec81000"


def _get_convention():
    is_sqlite = op.get_bind().dialect.name == "sqlite"
    return (
        {"fk": "FK_%(table_name)s_%(referred_table_name)s"}
        if is_sqlite
        else {"fk": "%(table_name)s_%(column_0_name)s_fkey"}
    )


def upgrade():

    args = [
        ("conceptscheme_source", "conceptscheme", "conceptscheme_id", "id"),
        ("conceptscheme_source", "source", "source_id", "id"),
        ("concept_source", "concept", "concept_id", "id"),
        ("concept_source", "source", "source_id", "id"),
        ("conceptscheme_language", "conceptscheme", "conceptscheme_id", "id"),
        ("match", "concept", "concept_id", "id"),
        ("label", "language", "language_id", "id"),
        ("note", "language", "language_id", "id"),
        ("collection_concept", "concept", "concept_id", "id"),
        ("collection_concept", "concept", "collection_id", "id"),
        ("conceptscheme_note", "conceptscheme", "conceptscheme_id", "id"),
        ("conceptscheme_label", "conceptscheme", "conceptscheme_id", "id"),
        ("visitation", "concept", "concept_id", "id"),
        ("visitation", "conceptscheme", "conceptscheme_id", "id"),
        ("concept_note", "concept", "concept_id", "id"),
        ("concept_note", "note", "note_id", "id"),
        ("concept_related_concept", "concept", "concept_id_from", "id"),
        ("concept_related_concept", "concept", "concept_id_to", "id"),
        ("concept_hierarchy_concept", "concept", "concept_id_narrower", "id"),
        ("concept_hierarchy_concept", "concept", "concept_id_broader", "id"),
        ("concept_hierarchy_collection", "concept", "concept_id_broader", "id"),
        ("concept_hierarchy_collection", "concept", "collection_id_narrower", "id"),
        ("concept_label", "concept", "concept_id", "id"),
        ("concept_label", "label", "label_id", "id"),
    ]
    convention = _get_convention()

    for source_table, referent_table, local_col, remote_col in args:
        with op.batch_alter_table(
            source_table, naming_convention=convention
        ) as batch_op:
            constraint_name = convention["fk"] % {
                "table_name": source_table,
                "referred_table_name": referent_table,
                "column_0_name": local_col,
            }
            batch_op.drop_constraint(constraint_name)
            batch_op.create_foreign_key(
                constraint_name,
                referent_table,
                [local_col],
                [remote_col],
                ondelete="cascade",
            )


def downgrade():
    pass
