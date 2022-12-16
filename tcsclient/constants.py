"""
Copyright (C) 2022 Intel Corporation
SPDX-License-Identifier: BSD-3-Clause

"""
import os


TCS_CLIENT_CONF_DIR=os.getenv('TCS_CLIENT_CONF_DIR', '/etc/tcs-client')
TCS_CLIENT_LOG_DIR=os.getenv('TCS_CLIENT_LOG_DIR', '/var/log/tcs-client')
TCS_CLIENT_LOG_FILE=os.getenv('TCS_CLIENT_LOG_FILE', TCS_CLIENT_LOG_DIR+'/tcs-client.log')
TCS_CLIENT_APP_DIR=os.getenv('TCS_CLIENT_APP_DIR', '/opt/tcs-client')
TCS_CLIENT_CONF_PATH=os.getenv('TCS_CLIENT_CONF_PATH', '/etc/tcs-client/config.yml')
TCS_CLIENT_SCRIPT=os.getenv('TCS_CLIENT_SCRIPT', '/usr/local/bin/tcs-client')
TCS_CLIENT_DEFAULT_LOG=os.getenv('TCS_CLIENT_DEFAULT_LOG', 'info')
TCS_CLIENT_VERION=os.getenv('TCS_CLIENT_VERION', '0.1')
TCS_CLIENT_LOCK_FILE=os.getenv('TCS_CLIENT_LOCK_FILE', '/opt/tcs-client/app.lock')
TCS_CLIENT_DEFAULT_TIMER_MINS=10

#TCS Client Exit Code
EXIT_CODE_SUCCESS=0
EXIT_CODE_ERROR=1

#DB Variables
ENV_DB_HOST='TC_DB_HOST'
ENV_DB_NAME='TC_DB_NAME'
ENV_DB_USER='TC_DB_USER'
ENV_DB_PASSWD='TC_DB_PASSWD'
ENV_LOG_LEVEL='LOG_LEVEL'

#Application Variables
ENV_Admin_Name='VCENTER_ADMIN_NAME'
ENV_Admin_Password='VCENTER_ADMIN_PASSWORD'
ENV_RegistrationURL='REGISTRATION_URL'
ENV_VCenterIP='VCENTER_IP'
ENV_VCenterPort='VCENTER_PORT'
ENV_TCSURL='TCS_URL'
ENV_SessionURL='SESSION_URL'
ENV_TaskURL='TASK_URL'
ENV_TIMER_MINS='TIMER_MINS'
HOST_ID='host_id'
API_SESSIONID='vmware-api-session-id'
PPID='ppid'
SUCCESS_STATUS="SUCCEEDED"
CERT_PATH="/etc/vmware_certs"
