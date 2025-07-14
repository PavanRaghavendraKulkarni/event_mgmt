from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('events', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='timezone',
            field=models.CharField(max_length=64, default='Asia/Kolkata'),
        ),
    ] 