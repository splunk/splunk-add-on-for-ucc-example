#!/bin/bash

add_common_dependencies() {
    pip install pip==20.2
    if [ -f package/lib/requirements.txt ]; then
        pip install -r package/lib/requirements.txt
    fi

    # Below two lines are added to create specific path required by splunktalib to create log file.
    # Once fix is avalible(ADDON-32060) in splunktalib, remove these lines.
    mkdir -p /opt/splunk/var/log/splunk
    chmod -R 777 /opt/splunk/var/log/splunk
}

add_per_python_version_dependencies() {
    version=$(python -V 2>&1 | sed 's/.* \([0-9]\).\([0-9]\).*/\1\2/')
    if [[ -z "${version}" ]]; then
        echo "Install Python to run tests"
        exit 1
    fi
    if [[ "$version" -gt "30" ]]; then
        echo "Installing dependencies for Python 3.x"
        pip install -r requirements_dev.txt
        if [ -f package/lib/py3/requirements.txt ]; then
            pip install -r package/lib/py3/requirements.txt
        fi
    elif [[ "$version" -gt "20" ]]; then
        echo "Installing dependencies for Python 2.x"
        pip install -r requirements_py2_dev.txt
        if [ -f package/lib/py2/requirements.txt ]; then
            pip install -r package/lib/py2/requirements.txt
        fi
    else
        echo "Not supported Python version"
    fi
}

run_tests() {
    echo "Running tests with pytest"
    coverage run --source=./package/bin -m pytest -c tests/unit/pytest-ci.ini tests/unit
}

main() {
    add_common_dependencies
    add_per_python_version_dependencies
    run_tests
}

main
