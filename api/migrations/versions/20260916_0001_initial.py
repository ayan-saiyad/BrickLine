"""initial tables"""

import sqlalchemy as sa
from alembic import op

revision = "20260916_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "lego_sets",
        sa.Column("set_number", sa.String(24), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("theme", sa.String(100), nullable=False),
        sa.Column("piece_count", sa.Integer()),
        sa.Column("image_url", sa.Text()),
        sa.Column("status", sa.String(24), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_lego_sets_theme", "lego_sets", ["theme"])
    op.create_index("ix_lego_sets_status", "lego_sets", ["status"])

    op.create_table(
        "import_runs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source_name", sa.String(120), nullable=False),
        sa.Column("source_url", sa.Text(), nullable=False),
        sa.Column("state", sa.String(20), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True)),
        sa.Column("imported_count", sa.Integer(), nullable=False),
        sa.Column("rejected_count", sa.Integer(), nullable=False),
        sa.Column("error", sa.Text()),
    )
    op.create_index("ix_import_runs_source_name", "import_runs", ["source_name"])
    op.create_index("ix_import_runs_state", "import_runs", ["state"])

    op.create_table(
        "release_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "set_number",
            sa.String(24),
            sa.ForeignKey("lego_sets.set_number", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("event_type", sa.String(20), nullable=False),
        sa.Column("event_date", sa.Date(), nullable=False),
        sa.Column("confidence", sa.String(20), nullable=False),
        sa.Column("source_name", sa.String(120), nullable=False),
        sa.Column("source_url", sa.Text(), nullable=False),
        sa.Column("import_run_id", sa.Integer(), sa.ForeignKey("import_runs.id"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("set_number", "event_type"),
    )
    op.create_index("ix_release_events_set_number", "release_events", ["set_number"])
    op.create_index("ix_release_events_event_type", "release_events", ["event_type"])
    op.create_index("ix_release_events_event_date", "release_events", ["event_date"])

    op.create_table(
        "set_changes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("set_number", sa.String(24), nullable=False),
        sa.Column("import_run_id", sa.Integer(), sa.ForeignKey("import_runs.id"), nullable=False),
        sa.Column("changed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("changes", sa.JSON(), nullable=False),
    )
    op.create_index("ix_set_changes_set_number", "set_changes", ["set_number"])


def downgrade() -> None:
    op.drop_table("set_changes")
    op.drop_table("release_events")
    op.drop_table("import_runs")
    op.drop_table("lego_sets")
