#!/usr/bin/env bash

log_level="info"
opereto_host=
opereto_user=
opereto_pass=
agent_os_user=$USER
agent_os_group=$agent_os_user
agent_name=`hostname`

OS=$(lsb_release -si)
if [ -f /etc/redhat-release ];then
    OSREL=$(cat /etc/redhat-release)
elif [ -f /etc/os-release ];then
    OSREL=$(cat /etc/os-release)
fi


if [[ $OS == *"buntu"* ]]; then
  os_platform="ubuntu"
elif [[ $OS == *"RedHat"* ]]; then
  os_platform="rh"
elif [[ $OS == *"entos"* ]]; then
  os_platform="centos"
elif [[ $OSREL == *"Red Hat"* ]]; then
  os_platform="rh"
elif [[ $OSREL == *"entos"* ]]; then
  os_platform="centos"
elif [[ $OSREL == *"CentOS"* ]]; then
  os_platform="centos"
elif [[ $OSREL == *"buntu"* ]]; then
  os_platform="ubuntu"
elif [[ $OSREL == *"Amazon"* ]]; then
  os_platform="rh"
fi

if [ -z "$os_platform" ]; then
    echo "Cannot identify OS platform."
    exit 1;
fi


while getopts b:u:p:n:o:g:l:d opt; do
  case $opt in
  b)
      opereto_host=$OPTARG
      ;;
  u)
      opereto_user=$OPTARG
      ;;
  p)
      opereto_pass=$OPTARG
      ;;
  n)
      agent_name=$OPTARG
      ;;
  o)
      agent_os_user=$OPTARG
      ;;
  g)
      agent_os_group=$OPTARG
      ;;
  l)
      log_level=$OPTARG
      ;;
  esac
done
shift $((OPTIND - 1))

function usage {
	echo `basename $0` -b BOXURL -u USER -p PASS [-n AGENTNAME] [-o OSUSER] [-g OSGROUP] [-l LOGLEVEL]
	echo ""
	echo ""
	echo "BOX_URL    : the address of opereto server (e.g. https:/192.168.0.1)"
	echo "USER       : the user to login into the OperetoBox"
	echo "PASS       : the password to use for login into the OperetoBox"
	echo "AGENT_NAME : the agent identifier (optional, default is the hostname)"
	echo "OS_USER    : the os user to run the agent (optional, default is current user)"
	echo "OS_GROUP   : the os group to run the agent (optional, default is current group)"
	echo "LOGLEVEL   : the agent log level (optional, default: info)"
}

if [[ -z "$opereto_host" || -z "$opereto_user" || -z "$opereto_pass" ]] ; then
	usage
	exit 1
fi


# install java if not installed
if type -p java; then
    echo found java executable in PATH
    _java=java
elif [[ -n "$JAVA_HOME" ]] && [[ -x "$JAVA_HOME/bin/java" ]];  then
    echo found java executable in JAVA_HOME
    _java="$JAVA_HOME/bin/java"
elif [ "$os_platform" == "ubuntu" ]; then
    sudo apt-get update -y
    sudo apt-get install -y default-jre
    _java=java
elif [ "$os_platform" == "centos" ]; then
    #sudo yum update -y
    sudo yum install -y java-1.7.0-openjdk
    _java=java
elif [ "$os_platform" == "rh" ]; then
    #sudo yum update -y
    sudo yum install -y java-1.7.0-openjdk
    _java=java
fi

# remove the tty requirements if exists
sudo sed --in-place /requiretty/d /etc/sudoers
sudo sed -i 's/^mesg n$/tty -s \&\& mesg n/g' /root/.profile

# run agent if not running
agent_cmd="java $javaParams -jar opereto-agent.jar -host $opereto_host -name $agent_name -u $opereto_user -p $opereto_pass -loglevel $log_level &"

`ps -ef | grep opereto-agent | grep -v grep`
if [ $? -ne 0 ]; then
    echo "Agent is not running.. running it now.."
    $SHELL -c "$agent_cmd"
fi

exit $?