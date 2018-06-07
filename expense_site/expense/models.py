# coding= utf-8
# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
#  manage.py inspectdb --database=expense > expense_site/models.py

from __future__ import unicode_literals

from django.db import models
from django.db.models import Sum
import re


class Category(models.Model):
    id = models.AutoField(blank=False, primary_key=True )
    name = models.TextField(blank=True, null=True)

    def __str__(self):
        if self.name:
            return self.name
        else:
            return 'None'

    class Meta:
        managed = False
        db_table = 'category'


class Files(models.Model):
    id = models.IntegerField(blank=True, primary_key=True)
    file_name = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.file_name

    def get_file_total(self):
        return self.expense_set.aggregate(sum=Sum('charge'))['sum']

    def get_file_expenses_link(self):
        return '<a href="/admin/expense/expense/?q=%s">%s</a>' % (self.file_name, "See Details")

    get_file_expenses_link.allow_tags = True

    class Meta:
        managed = False
        db_table = 'files'


class Names(models.Model):
    name = models.TextField(blank=True, primary_key=True)
    cat = models.ForeignKey(Category,db_column='cat')

    class Meta:
        managed = False
        db_table = 'names'

    def __str__(self):
        return self.name

class Expense(models.Model):
    id = models.IntegerField(primary_key=True)
    file = models.ForeignKey(Files)
    date = models.DateField(blank=True, null=True)
    name = models.ForeignKey(Names, db_column='name')
    total = models.FloatField(blank=True, null=True)
    charge = models.FloatField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    charge_number = models.IntegerField()
    total_charges = models.IntegerField()

    def __str__(self):
        return "%12s: %30s [%6.2f/%6.2f] %s" % (self.date, self.name_id, self.charge, self.total, self.notes)

    def get_cat(self):
        return self.name.cat

    def get_file_name(self):
        return self.file.file_name


    class Meta:
        managed = False
        db_table = 'expense'



