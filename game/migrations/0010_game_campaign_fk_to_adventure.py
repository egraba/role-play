# Re-point game.Game.campaign FK from master.Campaign to adventure.Campaign.
# Uses SeparateDatabaseAndState to avoid Django autodetector noise from the
# game models that are not yet exported via game/models/__init__.py.
#
# NOTE: The state_operations are a no-op on fresh installs (game/0001 was
# updated to point directly to adventure.campaign when master/ was deleted).
# The database_operations are guarded with IF EXISTS / conditional logic so
# they are idempotent on both fresh installs and existing databases.

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("adventure", "0006_migrate_from_master"),
        ("game", "0009_update_spell_fks"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AlterField(
                    model_name="game",
                    name="campaign",
                    field=models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="adventure.campaign",
                    ),
                ),
            ],
            database_operations=[
                migrations.RunSQL(
                    sql="""
                        DO $$
                        BEGIN
                            IF EXISTS (
                                SELECT 1 FROM information_schema.table_constraints
                                WHERE constraint_name = 'game_game_campaign_id_a8fc2a9b_fk_master_campaign_id'
                                  AND table_name = 'game_game'
                            ) THEN
                                ALTER TABLE game_game
                                DROP CONSTRAINT game_game_campaign_id_a8fc2a9b_fk_master_campaign_id;
                            END IF;

                            IF NOT EXISTS (
                                SELECT 1 FROM information_schema.table_constraints
                                WHERE constraint_name = 'game_game_campaign_id_fk_adventure_campaign_id'
                                  AND table_name = 'game_game'
                            ) THEN
                                ALTER TABLE game_game
                                ADD CONSTRAINT game_game_campaign_id_fk_adventure_campaign_id
                                FOREIGN KEY (campaign_id)
                                REFERENCES adventure_campaign (id)
                                DEFERRABLE INITIALLY DEFERRED;
                            END IF;
                        END $$;
                    """,
                    reverse_sql=migrations.RunSQL.noop,
                ),
            ],
        ),
    ]
