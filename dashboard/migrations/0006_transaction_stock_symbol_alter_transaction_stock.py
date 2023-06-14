# Generated by Django 4.2.1 on 2023-06-10 14:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0005_transaction_purchase'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='stock_symbol',
            field=models.CharField(default='', max_length=10),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='stock',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='dashboard.stock'),
        ),
    ]