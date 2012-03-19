#!/usr/bin/env bash

function usage() {
    local MODE=${1}
    echo "Usage"
    echo
    echo "  ${0} -v python_version"
    echo
    echo "Required parameters"
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

# Parse the options
OPTSTRING=hv:
while getopts ${OPTSTRING} OPT
do
    case ${OPT} in
        h) usage;;
        v) VIRTVER=${OPTARG};;
        *) usage;;
    esac
done
shift "$(( $OPTIND - 1 ))"

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

# Remove previous builds
rm -rf ${WORKSPACE}/dist/*
rm -rf ${WORKSPACE}/doc/build/*

# Make a source distribution
if [ -f setup.py ] && [ -f setup.cfg ]; then

    # Get the tag.
    TAG_BUILD=`grep tag_build ${WORKSPACE}/setup.cfg | cut -d'=' -f2 | sed 's/ //g'`

    # If the build is tagged, in any way, then append the Jenkins build number.
    # If the build is not tagged, it is assumed to be a release.
    if [ -n "${TAG_BUILD}" ]; then
        python setup.py egg_info -b ${TAG_BUILD}.${BUILD_NUMBER} sdist
    else
        python setup.py sdist
    fi

    # Grab the last commit log.
    if [ -d ${WORKSPACE}/.bzr ]; then
        LAST_LOG=`bzr log -l 1`
    elif [ -d ${WORKSPACE}/.git ]; then
        LAST_LOG=`git log -n 1`
    elif [ -d ${WORKSPACE}/.hg ]; then
        LAST_LOG=`hg log -l 1`
    else
        LAST_LOG="None"
    fi

    # Create a build record
    BUILD_RECORD="`ls -1tr ${WORKSPACE}/dist/*.zip | tail -n1`.html"
    echo "<html><head><title>${BUILD_TAG}</title></head><body><h2>${BUILD_ID}</h2><ul><li><a href=\"${BUILD_URL}\" target=\"_blank\">${BUILD_TAG}</a></li></ul><h3>Last Commit Log</h3><pre>${LAST_LOG}</pre></body></html>" > ${BUILD_RECORD}

    # Build sphinx documentation
    if [ -f ${WORKSPACE}/doc/Makefile ]; then
        python setup.py build_sphinx
    fi
fi
