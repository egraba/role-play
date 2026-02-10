# Update FK references from character.SpellSettings to magic.SpellSettings.
# State-only migration: the DB columns already point to the correct tables.

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("game", "0008_add_concentration_events"),
        ("magic", "0001_initial"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AlterField(
                    model_name="concentrationbroken",
                    name="spell",
                    field=models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="broken_concentration_events",
                        to="magic.spellsettings",
                    ),
                ),
                migrations.AlterField(
                    model_name="concentrationsaverequired",
                    name="spell",
                    field=models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="concentration_check_events",
                        to="magic.spellsettings",
                    ),
                ),
                migrations.AlterField(
                    model_name="concentrationsaveresult",
                    name="spell",
                    field=models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="concentration_result_events",
                        to="magic.spellsettings",
                    ),
                ),
                migrations.AlterField(
                    model_name="concentrationstarted",
                    name="spell",
                    field=models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="started_concentration_events",
                        to="magic.spellsettings",
                    ),
                ),
                migrations.AlterField(
                    model_name="spellcast",
                    name="spell",
                    field=models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="cast_events",
                        to="magic.spellsettings",
                    ),
                ),
                migrations.AlterField(
                    model_name="spellconditionapplied",
                    name="spell",
                    field=models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="condition_events",
                        to="magic.spellsettings",
                    ),
                ),
                migrations.AlterField(
                    model_name="spelldamagedealt",
                    name="spell",
                    field=models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="damage_events",
                        to="magic.spellsettings",
                    ),
                ),
                migrations.AlterField(
                    model_name="spellhealingreceived",
                    name="spell",
                    field=models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="healing_events",
                        to="magic.spellsettings",
                    ),
                ),
                migrations.AlterField(
                    model_name="spellsavingthrow",
                    name="spell",
                    field=models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="saving_throw_events",
                        to="magic.spellsettings",
                    ),
                ),
            ],
            database_operations=[],
        ),
    ]
