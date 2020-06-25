# -snapshotalyzer

Demo project to manage EC2 instance snapshots

## About

This project is a demo, uses boto3 to manaage AWS EC2 instance snaposhots.

## Configuring

shotty uses the configuration file created by the AWS cli. e.g.

`aws configure --profile <username>`

## Running

`pipenv run "python shotty/shotty.py <command>
<--project=PROJECT>"`

*command* is list, start, or stop
*project* is optional
