import boto3
import botocore
import click

#default profile settings, can be overwritten with the --profile option
session = boto3.Session(profile_name='snapshotalyzer')
ec2 = session.resource('ec2')


def filter_instances(project):
    instances = []

    if project:
        filters = [{'Name':'tag:Project', 'Values':[project]}]
        instances = ec2.instances.filter(Filters=filters)
    else:
        instances = ec2.instances.all()

    return instances

def has_pending_snapshot(volume):
    snapshots = list(volume.snapshots.all())
    pending_snapshots = []
    #the pending snapshot is not always at the same index, must search for it
    for s in volume.snapshots.all():
        if s.state == 'pending':
            pending_snapshots.append(s)
    return pending_snapshots

@click.group()
@click.option('--profile', default=None,
        help="Set the AWS profile name to use, otherwise will default to snapshotalyzer")
def cli(profile):
    """Shotty manages snapshots"""
    try:
        if profile == None:
            session = boto3.Session(profile_name='snapshotalyzer')
            ec2 = session.resource('ec2')
        else:
            session = boto3.Session(profile_name=profile)
            ec2 = session.resource('ec2')
    except botocore.exceptions.ProfileNotFound as e:
        print(" Could not set profile. " +str(e))
        exit()

@cli.group('snapshots')
def snapshots():
    """Commands for snapshots"""

@snapshots.command('list')
@click.option('--project', default=None,
        help="Only snapshots for project(tag Project:<name>)")
@click.option('--all', 'list_all', default=False, is_flag=True,
        help="List all snapshots for each volume, not just the most recent")

def list_snapshots(project, list_all):
    "List EC2 snapshots"
    
    instances = filter_instances(project)

    for i in instances:
        for v in i.volumes.all():
            for s in v.snapshots.all():
                print(', '.join((
                    s.id,
                    v.id,
                    i.id,
                    s.state,
                    s.progress,
                    s.start_time.strftime("%c")
                )))

                #only show the the most recent completed snapshot
                if list_all == False:
                    if s.state == 'completed': break

    return

@cli.group('volumes')
def volumes():
    """Commands for volumes"""


@volumes.command('list')
@click.option('--project', default=None,
        help="Only volumes for project(tag Project:<name>)")
def list_volumes(project):
    "List EC2 volumes"
    
    instances = filter_instances(project)

    for i in instances:
        for v in i.volumes.all():
            print(', '.join((
                v.id,
                i.id,
                v.state,
                str(v.size) + "GB",
                v.encrypted and "Encrypted" or "Not Encrypted"
            )))

    return

@cli.group('instances')
def instances():
    """Commands for instances"""

@instances.command('snapshot',
    help="Create snapshots of all volumes")
@click.option('--project', default=None,
    help="Only instances for project (tag Project:<name>)")
@click.option('--force', default=False, is_flag=True,
        help="Required if the project is undefined and running command on all instances")
def create_snapshots(project, force):
    "Create snapshots for EC2 instances"

    if project == None and force == False:
        print("Error either set the project with the --project option or")
        print("  if wanting to run on all instances use the --force option")
        return

    instances = filter_instances(project)

    for i in instances:

        print("Stopping {0}...".format(i.id))
        
        i.stop()
        #use EC2 waiter, will poll every 15 seconds until stopped
        i.wait_until_stopped()
        
        for v in i.volumes.all():
            if has_pending_snapshot(v):
                print("   Skipping {0}, snapshot already in progress".format(v.id))
                continue

            print("   Creating snapshot of {0}".format(v.id))
            try:
                v.create_snapshot(Description="Created by Snapshotalyzer")
            except botocore.exceptions.ClientError as e:
                print("  Could not create snapshot {0}. ".format(i.id) + str(e))
                continue
        
        print("Starting {0}...".format(i.id))
        i.start()
        #assuming that it is ideal to do one snapshot at a time to minimize
        #downtime impact of servers, wait until running before going on to next
        i.wait_until_running()

    print("Job done")

    return

@instances.command('list')
@click.option('--project', default=None,
    help="Only instances for project (tag Project:<name>)")
def list_instances(project):
    "List EC2 instances"
    
    instances = filter_instances(project)

    for i in instances:
        tags = {} 
        # Convert list of dictionaries, to a single dictionary of tags
        if i.tags != None:
            for t in i.tags:
                tags[t['Key']] = t['Value']

        print(', '.join((
            i.id,
            i.instance_type,
            i.public_ip_address,
            i.placement['AvailabilityZone'],
            i.state['Name'],
            i.public_dns_name,
            tags.get('Project','<no project>')
            )))

    return

@instances.command('start')
@click.option('--project', default=None,
        help="Only instances for project (tag Project:<name>)")
@click.option('--force', default=False, is_flag=True,
        help="Required if the project is undefined and running command on all instances")
def start_instances(project, force):
    "Start EC2 instances"

    if project == None and force == False:
        print("Error either set the project with the --project option or")
        print("  if wanting to run on all instances use the --force option")
        return

    instances = filter_instances(project)
    
    for i in instances:
        print("Starting {0}...".format(i.id))
        try:
            i.start()
        except botocore.exceptions.ClientError as e:
            print(" Could not start {0}. ".format(i.id) + str(e))
            continue

    return


@instances.command('stop')
@click.option('--project', default=None,
        help="Only instances for project (tag Project:<name>)")
@click.option('--force', default=False, is_flag=True,
        help="Required if the project is undefined and running command on all instances")
def stop_instances(project, force):
    "Stop EC2 instances"
    
    if project == None and force == False:
        print("Error either set the project with the --project option or")
        print("  if wanting to run on all instances use the --force option")
        return

    instances = filter_instances(project)
    
    for i in instances:
        print("Stopping {0}...".format(i.id))
        try:
            i.stop()
        except botocore.exceptions.ClientError as e:
            print(" Could not stop {0}. ".format(i.id) + str(e))
            continue

    return

@instances.command('reboot')
@click.option('--project', default=None,
        help="Only instances for project (tag Project:<name>)")
@click.option('--force', default=False, is_flag=True,
        help="Required if the project is undefined and running command on all instances")
def reboot_instances(project, force):
    "Reboot EC2 instances"

    if project == None and force == False:
        print("Error either set the project with the --project option or")
        print("  if wanting to run on all instances use the --force option")
        return

    instances = filter_instances(project)
    
    for i in instances:
        print("Rebooting {0}...".format(i.id))
        try:
            i.reboot()
        except botocore.exceptions.ClientError as e:
            print(" Could not reboot {0}. ".format(i.id) + str(e))
            continue

    return

if __name__=='__main__':
#    print(sys.argv)
    cli()
