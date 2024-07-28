# Generated by Django 5.0.7 on 2024-07-28 19:16

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("game", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Event",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("date", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.RemoveIndex(
            model_name="characterinvitation",
            name="game_charac_date_882223_idx",
        ),
        migrations.RemoveIndex(
            model_name="combatinitialization",
            name="game_combat_date_1b2c1a_idx",
        ),
        migrations.RemoveIndex(
            model_name="gamestart",
            name="game_gamest_date_edf9a6_idx",
        ),
        migrations.RemoveIndex(
            model_name="message",
            name="game_messag_date_bac6ca_idx",
        ),
        migrations.RemoveIndex(
            model_name="questupdate",
            name="game_questu_date_73d038_idx",
        ),
        migrations.RemoveIndex(
            model_name="roll",
            name="game_roll_date_201db4_idx",
        ),
        migrations.RemoveIndex(
            model_name="rollrequest",
            name="game_rollre_date_d85969_idx",
        ),
        migrations.RemoveField(
            model_name="characterinvitation",
            name="date",
        ),
        migrations.RemoveField(
            model_name="characterinvitation",
            name="game",
        ),
        migrations.RemoveField(
            model_name="characterinvitation",
            name="id",
        ),
        migrations.RemoveField(
            model_name="combatinitialization",
            name="date",
        ),
        migrations.RemoveField(
            model_name="combatinitialization",
            name="game",
        ),
        migrations.RemoveField(
            model_name="combatinitialization",
            name="id",
        ),
        migrations.RemoveField(
            model_name="gamestart",
            name="date",
        ),
        migrations.RemoveField(
            model_name="gamestart",
            name="game",
        ),
        migrations.RemoveField(
            model_name="gamestart",
            name="id",
        ),
        migrations.RemoveField(
            model_name="message",
            name="date",
        ),
        migrations.RemoveField(
            model_name="message",
            name="game",
        ),
        migrations.RemoveField(
            model_name="message",
            name="id",
        ),
        migrations.RemoveField(
            model_name="questupdate",
            name="date",
        ),
        migrations.RemoveField(
            model_name="questupdate",
            name="game",
        ),
        migrations.RemoveField(
            model_name="questupdate",
            name="id",
        ),
        migrations.RemoveField(
            model_name="roll",
            name="date",
        ),
        migrations.RemoveField(
            model_name="roll",
            name="game",
        ),
        migrations.RemoveField(
            model_name="roll",
            name="id",
        ),
        migrations.RemoveField(
            model_name="rollrequest",
            name="date",
        ),
        migrations.RemoveField(
            model_name="rollrequest",
            name="game",
        ),
        migrations.RemoveField(
            model_name="rollrequest",
            name="id",
        ),
        migrations.AddField(
            model_name="event",
            name="game",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="game.game"
            ),
        ),
        migrations.AddField(
            model_name="characterinvitation",
            name="event_ptr",
            field=models.OneToOneField(
                auto_created=True,
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                parent_link=True,
                primary_key=True,
                serialize=False,
                to="game.event",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="combatinitialization",
            name="event_ptr",
            field=models.OneToOneField(
                auto_created=True,
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                parent_link=True,
                primary_key=True,
                serialize=False,
                to="game.event",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="gamestart",
            name="event_ptr",
            field=models.OneToOneField(
                auto_created=True,
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                parent_link=True,
                primary_key=True,
                serialize=False,
                to="game.event",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="message",
            name="event_ptr",
            field=models.OneToOneField(
                auto_created=True,
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                parent_link=True,
                primary_key=True,
                serialize=False,
                to="game.event",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="questupdate",
            name="event_ptr",
            field=models.OneToOneField(
                auto_created=True,
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                parent_link=True,
                primary_key=True,
                serialize=False,
                to="game.event",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="roll",
            name="event_ptr",
            field=models.OneToOneField(
                auto_created=True,
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                parent_link=True,
                primary_key=True,
                serialize=False,
                to="game.event",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="rollrequest",
            name="event_ptr",
            field=models.OneToOneField(
                auto_created=True,
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                parent_link=True,
                primary_key=True,
                serialize=False,
                to="game.event",
            ),
            preserve_default=False,
        ),
        migrations.AddIndex(
            model_name="event",
            index=models.Index(fields=["-date"], name="game_event_date_707313_idx"),
        ),
    ]
