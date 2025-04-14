from django.db import migrations

def setup_admin_security(apps, schema_editor):
    AdminSecurity = apps.get_model('hostel', 'AdminSecurity')
    AdminSecurity.objects.create(
        security_key='secretpassword',
        is_configured=True
    )

class Migration(migrations.Migration):
    dependencies = [
        ('hostel', '0018_remove_adminsecurity_user_and_more'),
    ]

    operations = [
        migrations.RunPython(setup_admin_security),
    ] 