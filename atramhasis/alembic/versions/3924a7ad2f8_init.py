"""init

Revision ID: 3924a7ad2f8
Revises: None
Create Date: 2014-04-10 15:37:26.804103

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "3924a7ad2f8"
down_revision = None
branch_labels = ("atramhasis",)


def upgrade():
    op.create_table(
        "labeltype",
        sa.Column("name", sa.String(length=20), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("name"),
    )
    op.create_table(
        "language",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "conceptscheme",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("uri", sa.String(length=512), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "notetype",
        sa.Column("name", sa.String(length=20), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("name"),
    )
    op.create_table(
        "label",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("label", sa.String(length=512), nullable=False),
        sa.Column("labeltype_id", sa.String(length=20), nullable=False),
        sa.Column("language_id", sa.String(length=64), nullable=True),
        sa.ForeignKeyConstraint(
            ["labeltype_id"],
            ["labeltype.name"],
        ),
        sa.ForeignKeyConstraint(
            ["language_id"],
            ["language.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_label_labeltype_id", "label", ["labeltype_id"], unique=False)
    op.create_index("ix_label_language_id", "label", ["language_id"], unique=False)
    op.create_table(
        "note",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("note", sa.Text(), nullable=False),
        sa.Column("notetype_id", sa.String(length=20), nullable=False),
        sa.Column("language_id", sa.String(length=64), nullable=True),
        sa.ForeignKeyConstraint(
            ["language_id"],
            ["language.id"],
        ),
        sa.ForeignKeyConstraint(
            ["notetype_id"],
            ["notetype.name"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_note_language_id", "note", ["language_id"], unique=False)
    op.create_index("ix_note_notetype_id", "note", ["notetype_id"], unique=False)
    op.create_table(
        "concept",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("type", sa.String(length=30), nullable=True),
        sa.Column("concept_id", sa.Integer(), nullable=False),
        sa.Column("uri", sa.String(length=512), nullable=True),
        sa.Column("conceptscheme_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["conceptscheme_id"],
            ["conceptscheme.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_concept_concept_id", "concept", ["concept_id"], unique=False)
    op.create_index(
        "ix_concept_conceptscheme_id", "concept", ["conceptscheme_id"], unique=False
    )
    op.create_table(
        "collection_concept",
        sa.Column("collection_id", sa.Integer(), nullable=False),
        sa.Column("concept_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["collection_id"],
            ["concept.id"],
        ),
        sa.ForeignKeyConstraint(
            ["concept_id"],
            ["concept.id"],
        ),
        sa.PrimaryKeyConstraint("collection_id", "concept_id"),
    )
    op.create_table(
        "conceptscheme_note",
        sa.Column("conceptscheme_id", sa.Integer(), nullable=False),
        sa.Column("note_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["conceptscheme_id"],
            ["conceptscheme.id"],
        ),
        sa.ForeignKeyConstraint(
            ["note_id"],
            ["note.id"],
        ),
        sa.PrimaryKeyConstraint("conceptscheme_id", "note_id"),
    )
    op.create_table(
        "conceptscheme_label",
        sa.Column("conceptscheme_id", sa.Integer(), nullable=False),
        sa.Column("label_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["conceptscheme_id"],
            ["conceptscheme.id"],
        ),
        sa.ForeignKeyConstraint(
            ["label_id"],
            ["label.id"],
        ),
        sa.PrimaryKeyConstraint("conceptscheme_id", "label_id"),
    )
    op.create_table(
        "visitation",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("lft", sa.Integer(), nullable=False),
        sa.Column("rght", sa.Integer(), nullable=False),
        sa.Column("depth", sa.Integer(), nullable=False),
        sa.Column("conceptscheme_id", sa.Integer(), nullable=False),
        sa.Column("concept_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["concept_id"],
            ["concept.id"],
        ),
        sa.ForeignKeyConstraint(
            ["conceptscheme_id"],
            ["conceptscheme.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_visitation_concept_id", "visitation", ["concept_id"], unique=False
    )
    op.create_index(
        "ix_visitation_conceptscheme_id",
        "visitation",
        ["conceptscheme_id"],
        unique=False,
    )
    op.create_index("ix_visitation_depth", "visitation", ["depth"], unique=False)
    op.create_index("ix_visitation_lft", "visitation", ["lft"], unique=False)
    op.create_index("ix_visitation_rght", "visitation", ["rght"], unique=False)
    op.create_table(
        "concept_note",
        sa.Column("concept_id", sa.Integer(), nullable=False),
        sa.Column("note_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["concept_id"],
            ["concept.id"],
        ),
        sa.ForeignKeyConstraint(
            ["note_id"],
            ["note.id"],
        ),
        sa.PrimaryKeyConstraint("concept_id", "note_id"),
    )
    op.create_table(
        "concept_related_concept",
        sa.Column("concept_id_from", sa.Integer(), nullable=False),
        sa.Column("concept_id_to", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["concept_id_from"],
            ["concept.id"],
        ),
        sa.ForeignKeyConstraint(
            ["concept_id_to"],
            ["concept.id"],
        ),
        sa.PrimaryKeyConstraint("concept_id_from", "concept_id_to"),
    )
    op.create_table(
        "concept_hierarchy_concept",
        sa.Column("concept_id_broader", sa.Integer(), nullable=False),
        sa.Column("concept_id_narrower", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["concept_id_broader"],
            ["concept.id"],
        ),
        sa.ForeignKeyConstraint(
            ["concept_id_narrower"],
            ["concept.id"],
        ),
        sa.PrimaryKeyConstraint("concept_id_broader", "concept_id_narrower"),
    )
    op.create_table(
        "concept_hierarchy_collection",
        sa.Column("concept_id_broader", sa.Integer(), nullable=False),
        sa.Column("collection_id_narrower", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["collection_id_narrower"],
            ["concept.id"],
        ),
        sa.ForeignKeyConstraint(
            ["concept_id_broader"],
            ["concept.id"],
        ),
        sa.PrimaryKeyConstraint("concept_id_broader", "collection_id_narrower"),
    )
    op.create_table(
        "concept_label",
        sa.Column("concept_id", sa.Integer(), nullable=False),
        sa.Column("label_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["concept_id"],
            ["concept.id"],
        ),
        sa.ForeignKeyConstraint(
            ["label_id"],
            ["label.id"],
        ),
        sa.PrimaryKeyConstraint("concept_id", "label_id"),
    )


def downgrade():
    op.drop_table("concept_label")
    op.drop_table("concept_hierarchy_collection")
    op.drop_table("concept_hierarchy_concept")
    op.drop_table("concept_related_concept")
    op.drop_table("concept_note")
    op.drop_index("ix_visitation_rght", table_name="visitation")
    op.drop_index("ix_visitation_lft", table_name="visitation")
    op.drop_index("ix_visitation_depth", table_name="visitation")
    op.drop_index("ix_visitation_conceptscheme_id", table_name="visitation")
    op.drop_index("ix_visitation_concept_id", table_name="visitation")
    op.drop_table("visitation")
    op.drop_table("conceptscheme_label")
    op.drop_table("conceptscheme_note")
    op.drop_table("collection_concept")
    op.drop_index("ix_concept_conceptscheme_id", table_name="concept")
    op.drop_index("ix_concept_concept_id", table_name="concept")
    op.drop_table("concept")
    op.drop_index("ix_note_notetype_id", table_name="note")
    op.drop_index("ix_note_language_id", table_name="note")
    op.drop_table("note")
    op.drop_index("ix_label_language_id", table_name="label")
    op.drop_index("ix_label_labeltype_id", table_name="label")
    op.drop_table("label")
    op.drop_table("notetype")
    op.drop_table("conceptscheme")
    op.drop_table("language")
    op.drop_table("labeltype")
