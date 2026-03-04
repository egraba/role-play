from django.db import migrations


class Migration(migrations.Migration):
    """Drop the master_campaign table left over from the master/ app."""

    dependencies = [("adventure", "0006_migrate_from_master")]

    operations = [
        migrations.RunSQL(
            sql="DROP TABLE IF EXISTS master_campaign;",
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
