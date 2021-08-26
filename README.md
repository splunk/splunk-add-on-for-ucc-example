## Setup of developer env

Note: Must install docker desktop, vscode or pycharm pro optional

Note2: Appinspect requires libmagic verify this has been installed correctly each time a new workstation/vm is used https://dev.splunk.com/enterprise/docs/releaseapps/appinspect/splunkappinspectclitool/installappinspect

```bash
git clone git@github.com:splunk/<repo slug>.git
cd <repo dir>
git submodule update --init --recursive

poetry shell
poetry install
mkdir -p package/lib
poetry export --without-hashes -o package/lib/requirements.txt
ucc-gen
slim package output/Splunk_TA_UCCExample
```

## Test

Using docker 

```bash
pytest
```

Using external Splunk instance with Eventgen and app pre-installed

```bash
pytest --splunk-type=external --splunk-host=something --splunk-user=foo --splunk-password=something
```
