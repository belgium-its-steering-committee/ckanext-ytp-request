ckanext-ytp-request
===================

CKAN extension providing means to control organization member requests, requests history and related operations.

Features
--------

- Users can request to be part of organization
- Organization admins and global admins can approve or reject request
- Request history log

## Compatibility

Tested with CKAN 2.10

## Installation

Install to you ckan virtual environment

```
pip install -e  git+https://github.com/belgium-its-steering-committee/ckanext-ytp-request#egg=ckanext-ytp-request
```

Add to ckan.ini

```
ckan.plugins = ... ytp_request
```

Initialize the database

```
cd /usr/lib/ckan/default/src/ckanext-ytp-request
paster initdb --config=/etc/ckan/default/production.ini
```
