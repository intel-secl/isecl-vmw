#!/bin/bash
arg1=$1
arg2=$2

uflag=0
pflag=0
rCode=0
cd /opt/tcs-client/
source bin/activate 
env_file=tcs-client.env
if [ -n $env_file ]; then
    source $env_file
    env_file_exports=$(cat $env_file | grep -E '^[a-zA-Z0-9_]+\s*=' | cut -d = -f 1)
    if [ -n "$env_file_exports" ]; then eval export $env_file_exports; fi
else
    echo No .env file found
fi

case $arg1 in
   start)
      python daemon_main.py --StartDaemon 
      rCode=$?
      ;;
   run)
      python daemon_main.py --RunDaemon 
      rCode=$?
      ;;
   stop)
      python daemon_main.py --StopDaemon
      ;;
   status)
      python daemon_main.py --StatusDaemon
      rCode=$?
      ;;
   uninstall)
      python daemon_main.py --UninstallDaemon
      systemctl disable tcs-client
      uflag=1
      if [ "$arg2" = "--purge" ]; then
	pflag=1
      fi
      ;;
   version|-v|--version)
      python daemon_main.py --Version
      ;;
   restart)
      python daemon_main.py --StopDaemon
      systemctl start tcs-client
      ;;
   help|-h|--help)
      python daemon_main.py --Help
      ;;
   *)
      python daemon_main.py --Help
      ;;
esac
deactivate

if [ $uflag -eq 1 ]; then
      rm -rf /opt/tcs-client
      rm -rf /usr/local/bin/tcs-client
      if [ $pflag -eq 1 ]; then
	 rm -rf /etc/tcs-client
      fi
fi

exit $rCode
