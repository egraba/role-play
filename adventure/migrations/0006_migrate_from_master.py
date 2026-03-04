from django.db import migrations


def copy_campaigns_forward(apps, schema_editor):
    try:
        MasterCampaign = apps.get_model("master", "Campaign")
    except LookupError:
        return  # master app not present — nothing to migrate

    AdventureCampaign = apps.get_model("adventure", "Campaign")
    User = apps.get_model("user", "User")

    # Use the first superuser as a placeholder owner for migrated campaigns.
    # Real campaigns should have owners assigned after migration.
    default_owner = User.objects.filter(is_superuser=True).first()
    if default_owner is None:
        default_owner = User.objects.first()
    if default_owner is None:
        return  # No users yet (fresh install) — nothing to migrate

    for master_campaign in MasterCampaign.objects.all():
        AdventureCampaign.objects.get_or_create(
            slug=master_campaign.slug,
            defaults={
                "title": master_campaign.title,
                "synopsis": master_campaign.synopsis,
                "main_conflict": master_campaign.main_conflict,
                "objective": master_campaign.objective,
                "owner": default_owner,
            },
        )


def copy_campaigns_backward(apps, schema_editor):
    try:
        MasterCampaign = apps.get_model("master", "Campaign")
    except LookupError:
        return  # master app not present — nothing to reverse

    # Reverse: remove adventure campaigns that were created from master
    AdventureCampaign = apps.get_model("adventure", "Campaign")
    master_slugs = set(MasterCampaign.objects.values_list("slug", flat=True))
    AdventureCampaign.objects.filter(slug__in=master_slugs).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("adventure", "0005_alter_encounter_options_encounter_order_and_more"),
        ("user", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(copy_campaigns_forward, copy_campaigns_backward),
    ]
