"""20260420133046 - Create messages"""

from pelican import migration, create_table, drop_table


@migration.up
def upgrade() -> None:
    with create_table("message") as t:
        t.integer("id", primary_key=True, autoincrement=True)
        t.string("content", nullable=False)
        t.string("timestamp", nullable=False)
        t.string("sender", nullable=False)
        t.string("event_id", nullable=False)
        t.boolean("is_command", nullable=False)


@migration.down
def downgrade() -> None:
    drop_table("message")
