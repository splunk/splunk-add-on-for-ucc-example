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
# echo "Installing Dependencies"
echo install setuptools
pip3 install setuptools --upgrade
pip3 install wheel --upgrade
pip3 install --upgrade pip
pip2 install --upgrade pip
echo install slim
pip3 install https://download.splunk.com/misc/packaging-toolkit/splunk-packaging-toolkit-1.0.1.tar.gz --upgrade
echo install crudini
pip3 install git+ssh://git@github.com/pixelb/crudini.git --upgrade
echo install requirements_dev
pip3 install -r requirements_dev.txt --upgrade

PACKAGE_ID=$(crudini --get package/default/app.conf id name)
VERSION=$(./semtag getcurrent)
BUILD_DIR=build/source/$PACKAGE_ID

export VERSION_SPLUNK=$(python ./splver.py ${VERSION})
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
#slim partition -o build/package/deployment $PACKAGE || true