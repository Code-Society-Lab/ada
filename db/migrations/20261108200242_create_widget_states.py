"""20261108200242 - Create widget states"""

from pelican import migration, create_table, drop_table


@migration.up
def upgrade() -> None:
    with create_table("widget_states") as t:
        t.string("key", primary_key=True)
        t.text("value", nullable=False)


@migration.down
def downgrade() -> None:
    drop_table("widget_states")
