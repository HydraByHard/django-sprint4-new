from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_alter_category_options_alter_location_options_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': ('-pub_date',), 'verbose_name': 'Публикация', 'verbose_name_plural': 'Публикации'},
        ),
    ]
