# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals

from django.db import models
from jsonfield import JSONField


class CompanyManager(models.Manager):
    def get_vacancies(self, company_id):
        return Vacancy.objects.filter(company__id=company_id)


class Company(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    website = models.CharField(max_length=255, blank=True, null=True)
    email = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=255, blank=True, null=True)
    is_managed = models.BooleanField()
    lead_data = JSONField(blank=True, null=True)  # This field type is a guess.
    added = models.DateTimeField()
    objects = CompanyManager()

    class Meta:
        managed = False
        db_table = 'company'


class Errors(models.Model):
    vacancy_link = models.TextField(blank=True, null=True)
    source = models.TextField(blank=True, null=True)
    file_name = models.TextField(blank=True, null=True)
    error_type = models.TextField(blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)
    error_lineno = models.IntegerField(blank=True, null=True)
    error_datetime = models.DateTimeField(blank=True, null=True)
#    id = models.AutoField()

    class Meta:
        managed = False
        db_table = 'errors'


class Vacancy(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True)
    work_schedule = models.CharField(max_length=255, blank=True, null=True)
    required_skills = models.CharField(max_length=255, blank=True, null=True)
    desired_skills = models.CharField(max_length=255, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    date = models.DateTimeField(blank=True, null=True)
    qualification_level = models.CharField(max_length=255, blank=True, null=True)
    source = models.CharField(max_length=255, blank=True, null=True)
    link = models.TextField(blank=True, null=True)
    salary = models.TextField(blank=True, null=True)
    telecommunicate = models.NullBooleanField()
    is_expired = models.NullBooleanField()
    added = models.DateTimeField()
    company = models.ForeignKey(Company, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'vacancy'

