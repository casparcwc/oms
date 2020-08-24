# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals

from django.db import models




class OperationLog(models.Model):
    trigger_job_name = models.CharField(max_length=1024)
    op_environment = models.CharField(max_length=225, blank=True, null=True)
    do_action = models.CharField(max_length=225)
    belong_project = models.CharField(max_length=255, blank=True, null=True)
    diff_item = models.TextField(blank=True, null=True)
    job_name = models.CharField(max_length=1024, blank=True, null=True)
    source_control = models.CharField(max_length=255, blank=True, null=True)
    version = models.CharField(max_length=255, blank=True, null=True)
    deploy_server_address = models.CharField(max_length=255, blank=True, null=True)
    applicant_name = models.CharField(max_length=255, blank=True, null=True)
    publisher_name = models.CharField(max_length=255, blank=True, null=True)
    param1 = models.CharField(max_length=255, blank=True, null=True)
    param2 = models.CharField(max_length=255, blank=True, null=True)
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    mark = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'operation_log'


class PublishLog(models.Model):
    modelname = models.CharField(max_length=255, blank=True, null=True)
    diff_description = models.TextField(blank=True, null=True)
    diff_item = models.TextField(blank=True, null=True)
    function_type = models.CharField(max_length=255, blank=True, null=True)
    applicant = models.CharField(max_length=255, blank=True, null=True)
    publisher = models.CharField(max_length=255, blank=True, null=True)
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    mark = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'publish_log'


class ServerManager(models.Model):
    id = models.IntegerField(primary_key=True)
    ip = models.CharField(max_length=32)
    port = models.CharField(max_length=10, blank=True, null=True)
    username = models.CharField(max_length=32, blank=True, null=True)
    password = models.CharField(max_length=225, blank=True, null=True)
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'server_manager'


class ServiceJobsManager(models.Model):
    env = models.CharField(max_length=15, blank=True, null=True)
    product = models.CharField(max_length=225, blank=True, null=True)
    nickname = models.CharField(max_length=1024, blank=True, null=True)
    service_name = models.CharField(max_length=512)
    install_job_name = models.CharField(max_length=512, blank=True, null=True)
    deploy_job_name = models.CharField(max_length=512, blank=True, null=True)
    pkg_upload_path = models.CharField(max_length=512, blank=True, null=True)
    groupid = models.CharField(db_column='groupId', max_length=25, blank=True, null=True)  # Field name made lowercase.
    src_pkg_path = models.CharField(max_length=225, blank=True, null=True)
    version = models.CharField(max_length=225, blank=True, null=True)
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    dependency_env_info = models.CharField(max_length=512, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'service_jobs_manager'


class ServiceManager(models.Model):
    id = models.BigAutoField(primary_key=True)
    env = models.CharField(max_length=20)
    ip = models.CharField(max_length=255)
    service_name = models.CharField(max_length=512)
    is_active = models.CharField(max_length=2, blank=True, null=True)
    service_subscrible = models.CharField(max_length=512, blank=True, null=True)
    service_port = models.CharField(max_length=25, blank=True, null=True)
    product = models.CharField(max_length=225)
    name_type = models.CharField(max_length=255)
    busi_type = models.CharField(max_length=225, blank=True, null=True)
    load_flag = models.CharField(max_length=255, blank=True, null=True)
    pkg_path = models.CharField(max_length=255, blank=True, null=True)
    backup_path = models.CharField(max_length=255, blank=True, null=True)
    tomcat_path = models.CharField(max_length=255, blank=True, null=True)
    service_deploy_path = models.CharField(max_length=512, blank=True, null=True)
    log_level = models.CharField(max_length=255, blank=True, null=True)
    service_log_path = models.CharField(max_length=512, blank=True, null=True)
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    publish_time = models.DateTimeField(blank=True, null=True)
    version = models.CharField(max_length=20, blank=True, null=True)
    mark = models.CharField(max_length=512, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'service_manager'
        unique_together = (('service_name', 'ip', 'product'),)


class SvnAddressJobsMaps(models.Model):
    trunk_or_branch = models.CharField(max_length=11, blank=True, null=True)
    product = models.CharField(max_length=225)
    nickname = models.CharField(max_length=1024)
    svn_address = models.CharField(max_length=1024, blank=True, null=True)
    best_workspace = models.CharField(max_length=1024)
    fixed_workspace = models.CharField(max_length=1024)
    trunk_workspace = models.CharField(max_length=1024, blank=True, null=True)
    install_job_name = models.CharField(max_length=1024, blank=True, null=True)
    filterfiles = models.CharField(max_length=255, blank=True, null=True)
    trunk_svn_address = models.CharField(max_length=1024, blank=True, null=True)
    branch_svn_address = models.CharField(max_length=1024, blank=True, null=True)
    fixed_svn_address = models.CharField(max_length=1024, blank=True, null=True)
    increment_dir = models.CharField(max_length=255, blank=True, null=True)
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'svn_address_jobs_maps'
