# Generated by Django 4.2.23 on 2025-07-25 13:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('employeurs', '0002_alter_candidature_cv_alter_photosentreprise_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='candidature',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='employeurs.candidature'),
        ),
    ]
