# -snapshotalyzer

Demo project to manage EC2 instance snapshots

## About

This project is a demo, uses boto3 to manaage AWS EC2 instance snaposhots.

## Configuring

shotty uses the configuration file created by the AWS cli. e.g.

`aws configure --profile <username>`

## Running

`pipenv run "python shotty/shotty.py <command> <subcommand>
<--project=PROJECT>"`

*option* --profile is an option that can be set to use a specific AWS profile
*option* --region is an option that can be set to use a specific AWS region
*command* is instances, volumes, or snapshots
*subcommand* - depends on command
*project* is optional
