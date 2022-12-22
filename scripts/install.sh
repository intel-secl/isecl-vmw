#!/bin/bash
set -x

# Check OS and VERSION
OS=$(cat /etc/os-release | grep ^ID= | cut -d'=' -f2)
temp="${OS%\"}"
temp="${temp#\"}"
OS="$temp"

if [[ $EUID -ne 0 ]]; then 
    echo "This installer must be run as root"
    exit 1
fi

SERVICE_USERNAME=tcsclient
COMPONENT_NAME=tcs-client
PRODUCT_HOME=/opt/$COMPONENT_NAME/
LOG_PATH=/var/log/$COMPONENT_NAME/
CONFIG_PATH=/etc/$COMPONENT_NAME/

echo PWD IS $(pwd)
if [ -f ~/$COMPONENT_NAME.env ]; then
    echo Reading Installation options from `realpath ~/$COMPONENT_NAME.env`
    env_file=~/$COMPONENT_NAME.env
#elif [ -f ./input/$COMPONENT_NAME.env ]; then
#    echo Reading Installation options from `realpath ./input/tcs-client.env`
#    env_file=./input/$COMPONENT_NAME.env
else
	echo "Provide environment variables"
	exit 1
fi

env | grep TC
echo "Installing TCS Client Deamon..."

echo "Setting up TCS Client Linux User..."
id -u $SERVICE_USERNAME 2> /dev/null || useradd --comment "TCS Client Deamon" --home $PRODUCT_HOME --shell /bin/false $SERVICE_USERNAME && groupadd $SERVICE_USERNAME

for directory in $PRODUCT_HOME $LOG_PATH $CONFIG_PATH; do
  mkdir -p $directory
  if [ $? -ne 0 ]; then
    echo "Cannot create directory: $directory"
    exit 1
  fi
  chown -R $SERVICE_USERNAME:$SERVICE_USERNAME $directory
  chmod 700 $directory
done

# Create tcs-client product directory
python -m venv $PRODUCT_HOME
cp -r tcsclient/ $PRODUCT_HOME && cp *.py $PRODUCT_HOME && cp input/*.txt $PRODUCT_HOME && cp input/*.lock $PRODUCT_HOME && chown $SERVICE_USERNAME:$SERVICE_USERNAME $PRODUCT_HOME/*
chmod 740 $PRODUCT_HOME/*
chmod 700 $PRODUCT_HOME/*.lock

if [ -n $env_file ]; then
    cp $env_file $PRODUCT_HOME
    chown $SERVICE_USERNAME:$SERVICE_USERNAME $PRODUCT_HOME/$COMPONENT_NAME.env
    chmod 750 $PRODUCT_HOME/$COMPONENT_NAME.env
else
    echo No .env file found
    TC_NOSETUP="true"
fi

#Get certs for ssl verification. These certificates are valid for 10 years.
source $env_file
auth=`echo -n $VCENTER_ADMIN_NAME:$VCENTER_ADMIN_PASSWORD | base64`
session=`curl -s -X POST -H "Authorization: Basic $auth" https://$VCENTER_IP/api/session -k | cut -d'"' -f 2`

chain=`curl -s -H "vmware-api-session-id: $session" https://$VCENTER_IP/api/vcenter/certificate-management/vcenter/trusted-root-chains -k | cut -d '"' -f 4`

cert=`curl -s -H "vmware-api-session-id: $session" https://$VCENTER_IP/api/vcenter/certificate-management/vcenter/trusted-root-chains/$chain -k`

echo $cert | sed -e 's/\\n/\n/g' | cut -d'[' -f 2 | cut -d'"' -f2  | sed '/-----BEGIN X509 CRL-----/,$d' > /etc/vmware_cert.pem
chmod 644 /etc/vmware_cert.pem

pushd $PRODUCT_HOME
source bin/activate
pip install -r requirements.txt
deactivate
popd

chown $SERVICE_USERNAME:$SERVICE_USERNAME $CONFIG_PATH
chmod 700 $CONFIG_PATH

# Create logging dir in /var/log
mkdir -p $LOG_PATH && chown $SERVICE_USERNAME:$SERVICE_USERNAME $LOG_PATH
chmod 740 $LOG_PATH

cp scripts/bootstrap-tcs-client.sh /usr/local/bin/tcs-client

# Install systemd script
cp input/$COMPONENT_NAME.service $PRODUCT_HOME && chown $SERVICE_USERNAME:$SERVICE_USERNAME $PRODUCT_HOME/$COMPONENT_NAME.service && chown $SERVICE_USERNAME:$SERVICE_USERNAME $PRODUCT_HOME

# Enable systemd service
systemctl disable $COMPONENT_NAME.service > /dev/null 2>&1

systemctl enable $PRODUCT_HOME/$COMPONENT_NAME.service
systemctl daemon-reload

# check if TC_NOSETUP is defined
if [ "${TC_NOSETUP,,}" == "true" ]; then
    echo "Installation completed successfully!"
else 
    systemctl start $COMPONENT_NAME
    echo "Waiting for daemon to settle down before checking status"
    sleep 5
    systemctl status $COMPONENT_NAME 2>&1 > /dev/null
    if [ $? != 0 ]; then
        echo "Installation completed with Errors - $COMPONENT_NAME daemon not started."
        echo "Please check errors in syslog using \`journalctl -u $COMPONENT_NAME\`"
        exit 1
    fi
    systemctl enable $COMPONENT_NAME
    echo "$COMPONENT_NAME daemon is running"
    echo "Installation completed successfully!"
fi
