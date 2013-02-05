#!/usr/bin/env bash

function usage() {
    local MODE=${1}
    echo "Usage"
    echo
    echo "  ${0} -v python_version"
    echo
    echo "Required parameters"
    echo "  -u pypi_username  : Your PyPI account username"
    echo "  -p pypi_password  : Your PyPI account password"
    echo "  -v python version : The virtualenv Python version to use."
    echo "Optional parameters"
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
PYPI_USERNAME=""
PYPI_PASSWORD=""

# Parse the options
OPTSTRING=hp:u:v:
while getopts ${OPTSTRING} OPT
do
    case ${OPT} in
        h) usage;;
        p) PYPI_PASSWORD=${OPTARG};;
        u) PYPI_USERNAME=${OPTARG};;        
        v) VIRTVER=${OPTARG};;
        *) usage;;
    esac
done
shift "$(( $OPTIND - 1 ))"

if [ -z "${PYPI_USERNAME}" ] || [ -z "${PYPI_PASSWORD}" ]; then
    echo "ERROR! You must provide your PyPI username and password."
    exit 1
fi

VIRTENV=${WORKSPACE}/.py${VIRTVER}

# Check the virtualenv exists
if [ ! -f ${VIRTENV}/bin/python${VIRTVER} ]; then
    echo "ERROR! Couldn't find the virtualenv : ${VIRTENV}"
    exit 1
fi

# Enter the virtualenv
. ${VIRTENV}/bin/activate

# Enter the Jenkins workspace
cd ${WORKSPACE}

# Get the tag.
TAG_BUILD=`grep tag_build ${WORKSPACE}/setup.cfg | cut -d'=' -f2 | sed 's/ //g'`

# If the build is tagged, in any way, it will not be published on PyPI
if [ -n "${TAG_BUILD}" ]; then
    echo "This build is tagged : ${TAG_BUILD}"
    echo "Therefore it will NOT be published on PyPI"
else   
    echo "[distutils]"                  >  ~/.pypirc
    echo "index-servers ="              >> ~/.pypirc
    echo "    pypi"                     >> ~/.pypirc
    echo                                >> ~/.pypirc
    echo "[pypi]"                       >> ~/.pypirc
    echo "username:${PYPI_USERNAME}" >> ~/.pypirc
    echo "password:${PYPI_PASSWORD}" >> ~/.pypirc
 
    # Publish to PyPI
    python setup.py sdist upload

    # Upload the Sphinx documentation to PyPI
    # First make sure setup.cfg is configured for Sphinx upload
    UPLOAD_SPHINX=`grep upload_sphinx setup.cfg`    
    if [ $? -eq 0 ]; then
        # Make sure there is something to upload
        if [ -f ${WORKSPACE}/doc/build/html/index.html ]; then        
          python setup.py upload_sphinx
        fi
    else
        echo "This build is NOT configured to upload docs to PyPI"
    fi        
fi
