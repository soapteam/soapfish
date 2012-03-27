#!/usr/bin/env bash

function usage() {
    local MODE=${1}
    echo "Usage"
    echo
    echo "  ${0} -p package_name -v python_version -l"
    echo
    echo "Required parameters"
    echo "  -p package_name   : The package to test."
    echo "  -v python version : The virtualenv Python version to use."
    echo "Optional parameters"
    echo "  -l                : Enable 'pylint'. By default only 'pyflakes' is used."
    echo "  -h                : This help"
    exit 1
}

# Make sure we are running from within Jenkins
if [ -z "${WORKSPACE}" ]; then
    echo "ERROR! This script is designed to run from within a Jenkins build."
    exit1
fi

# Init the variables
VIRTVER=""
PACKAGE=""

# Parse the options
OPTSTRING=hlp:v:
while getopts ${OPTSTRING} OPT
do
    case ${OPT} in
        h) usage;;
        l) PYLINT=1;;
        p) PACKAGE=${OPTARG};;
        v) VIRTVER=${OPTARG};;
        *) usage;;
    esac
done
shift "$(( $OPTIND - 1 ))"

# Check that the package dir exists.
if [ ! -d ${WORKSPACE}/${PACKAGE} ]; then
    echo "ERROR! Can't find directory ${WORKSPACE}/${PACKAGE}"
    exit 1
fi

# Remove old style virtualenv
if [ -d ${WORKSPACE}/.pyenv ]; then
    rm -rf ${WORKSPACE}/.pyenv
fi

VIRTENV=${WORKSPACE}/.py${VIRTVER}

# Create virtualenv, but only if doesn't exist
if [ ! -f ${VIRTENV}/bin/python${VIRTVER} ]; then
    virtualenv --python=python${VIRTVER} --no-site-packages --distribute ${VIRTENV}
fi

# Enter the virtualenv
. ${VIRTENV}/bin/activate

# Enter the Jenkins workspace
cd ${WORKSPACE}

# Ensure 'pip' uses the internal PyPI server
if [ ! -f ~/.pip/pip.conf ]; then
    mkdir -p ~/.pip/ 2>/dev/null
    echo "[global]"                                                 >  ~/.pip/pip.conf
    echo "index-url = http://pypi.flightdataservices.com/simple/"   >> ~/.pip/pip.conf
fi    

# Ensure 'easy_install' and distutils uses the internal PyPI server
if [ ! -f ~/.pydistutils.cfg ]; then
    echo "[easy_install]"                                           >  ~/.pydistutils.cfg
    echo "index_url = http://pypi.flightdataservices.com/simple/"   >> ~/.pydistutils.cfg
fi    

# Update pip and distribute to the latest versions
pip install --upgrade pip distribute

if [ -f requirements_early.txt ]; then
    pip install --upgrade --requirement=requirements_early.txt
fi    

for REQUIREMENT in `ls -1 requirements*.txt | grep -v early`
do
    if [ -f ${REQUIREMENT} ]; then
        pip install --upgrade --requirement=${REQUIREMENT}
    fi
done

# Run any additional setup steps
if [ -x ${WORKSPACE}/jenkins/setup-extra.sh ]; then
    ${WORKSPACE}/jenkins/setup-extra.sh
fi

# Install runtime requirements.
if [ -f setup.py ]; then
    # Remove 'build' and 'dist' directories to ensure clean builds are made.    
    rm -rf ${WORKSPACE}/dist
    rm -rf ${WORKSPACE}/build    
    python setup.py develop
fi

# Build Sphinx documentation
if [ -f ${WORKSPACE}/doc/Makefile ]; then
    rm -rf ${WORKSPACE}/doc/build/*
    python setup.py build_sphinx
fi

# Remove pre-existing metric output files
rm coverage.xml nosetests.xml pylint.log pep8.log cpd.xml sloccount.log 2>/dev/null

# Run the tests suite and generate coverage reports
if [ -f setup.py ] && [ -d tests ]; then
    python setup.py jenkins
fi

# Pyflakes code quality metric, in Pylint format
pyflakes ${PACKAGE} | awk -F\: '{printf "%s:%s: [E]%s\n", $1, $2, $3}' > pylint.log

# PEP8 code quality metric
pep8 --repeat --ignore=E501 ${PACKAGE} > pep8.log

# Copy and Paste Detector code quality metric
clonedigger --fast --cpd-output --output=cpd.xml ${PACKAGE}

# Count lines of code
sloccount --duplicates --wide --details ${PACKAGE} > sloccount.log
