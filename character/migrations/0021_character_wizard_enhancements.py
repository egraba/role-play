from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("character", "0020_alter_monstersettings_name_lairactiontemplate_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="character",
            name="darkvision",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.CreateModel(
            name="CharacterFeature",
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
                ("level_gained", models.PositiveIntegerField(default=1)),
                (
                    "character",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="class_features",
                        to="character.character",
                    ),
                ),
                (
                    "class_feature",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="character_instances",
                        to="character.classfeature",
                    ),
                ),
                (
                    "source_class",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="granted_features",
                        to="character.class",
                    ),
                ),
            ],
            options={
                "ordering": ["source_class", "level_gained", "class_feature__name"],
                "unique_together": {("character", "class_feature")},
            },
        ),
    ]
