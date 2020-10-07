#!/usr/bin/env bash
# echo "Initializing Packaging tool"
if ! command -v pyenv &> /dev/null
then
    if [ ! -d "~/.pyenv" ]; then
        curl https://pyenv.run | bash
    fi
    export PATH="$HOME/.pyenv/bin:$PATH"
    eval "$(pyenv init -)"
    eval "$(pyenv virtualenv-init -)"
fi
for line in `cat .python-version`; do pyenv install -s "$line"; done
# echo "Installing Virtual Environment"
pip3 install virtualenv > /dev/null
if [ ! -d "./.venv" ]; then
python3 -m virtualenv .venv -p python3 > /dev/null
fi
source .venv/bin/activate
echo "Virtual Environment Installed and Activated"
# echo "Installing Dependencies"
pip3 install -r requirements_dev.txt --upgrade

PACKAGE_ID=$(crudini --get package/default/app.conf id name)

BUILD_DIR=build/source/$PACKAGE_ID

export VERSION_SPLUNK=$(dunamai from git --no-metadata --style semver)
export PACKAGE_BUILD=$(date +%s)
rm -rf build || true
rm -rf output || true
mkdir -p $BUILD_DIR

ucc-gen --ta-version $VERSION_SPLUNK
cp -r output/$PACKAGE_ID/* $BUILD_DIR/
rm -rf $BUILD_DIR/samples
rm -rf $BUILD_DIR/default/eventgen.conf
crudini --set $BUILD_DIR/default/app.conf launcher version $VERSION_SPLUNK
crudini --set $BUILD_DIR/default/app.conf id version $VERSION_SPLUNK
crudini --set $BUILD_DIR/default/app.conf install build ${PACKAGE_BUILD}
cp -r LICENSES $BUILD_DIR/

slim generate-manifest $BUILD_DIR --update >/tmp/app.manifest   || true
cp  /tmp/app.manifest  $BUILD_DIR/app.manifest
mkdir -p build/package/splunkbase
mkdir -p build/package/deployment
slim package -o build/package/splunkbase $BUILD_DIR 

mkdir -p build/package/deployment
PACKAGE=$(ls build/package/splunkbase/*)
slim validate $PACKAGE