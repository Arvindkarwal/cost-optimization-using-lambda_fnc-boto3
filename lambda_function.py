import boto3
from botocore.exceptions import ClientError

# Initialize AWS clients
s3 = boto3.client('s3')
ec2 = boto3.client('ec2')

def delete_empty_s3_buckets():
  """Deletes empty S3 buckets."""
  try:
    # List all S3 buckets
    response = s3.list_buckets()
    buckets = response.get('Buckets', [])

    for bucket in buckets:
      bucket_name = bucket['Name']
      try:
        # Check if the bucket is empty
        objects = s3.list_objects_v2(Bucket=bucket_name)
        if objects.get('Contents') is None:
          # Bucket is empty, delete it
          s3.delete_bucket(Bucket=bucket_name)
          print(f"Deleted empty S3 bucket: {bucket_name}")
        else:
          print(f"S3 bucket {bucket_name} is not empty. Skipping...")
      except ClientError as e:
        print(f"Error accessing S3 bucket {bucket_name}: {e}")
  except ClientError as e:
    print(f"Failed to list S3 buckets: {e}")

def delete_unused_ebs_snapshots():
  """Deletes unused EBS snapshots if their volume does not exist."""
  try:
    # Get all snapshots owned by the account
    snapshots = ec2.describe_snapshots(OwnerIds=['self'])['Snapshots']

    for snapshot in snapshots:
      snapshot_id = snapshot['SnapshotId']
      volume_id = snapshot.get('VolumeId')  # Get the volume ID from the snapshot metadata

      # Check snapshot state
      if snapshot.get('State') == 'completed':
        try:
          # Check if the volume exists
          if volume_id:
            try:
              ec2.describe_volumes(VolumeIds=[volume_id])  # If the volume exists, skip deletion
              print(f"Snapshot {snapshot_id} belongs to an existing volume {volume_id}. Skipping...")
              continue
            except ClientError as e:
              if e.response['Error']['Code'] == 'InvalidVolume.NotFound':
                # Volume does not exist, safe to delete snapshot
                pass
              else:
                print(f"Error checking volume {volume_id} for snapshot {snapshot_id}: {e}")
                continue

          # Delete the snapshot if the volume does not exist
          ec2.delete_snapshot(SnapshotId=snapshot_id)
          print(f"Deleted unused EBS snapshot: {snapshot_id}")

        except ClientError as e:
          print(f"Error deleting snapshot {snapshot_id}: {e}")
      else:
        print(f"EBS snapshot {snapshot_id} is not in a deletable state. Skipping...")
  except ClientError as e:
    print(f"Failed to list EBS snapshots: {e}")


def release_unused_eips():
  """Releases unused Elastic IPs."""
  try:
    # Describe all Elastic IP addresses
    addresses = ec2.describe_addresses()['Addresses']
    for address in addresses:
      # For VPC allocated addresses, check for 'AssociationId'
      allocation_id = address.get('AllocationId')
      association_id = address.get('AssociationId')
      public_ip = address.get('PublicIp')

      # If there's no association, the IP is not in use
      if not association_id:
        try:
          # Release the Elastic IP using the allocation ID (for VPC)
          if allocation_id:
            ec2.release_address(AllocationId=allocation_id)
            print(f"Released unused Elastic IP with AllocationId: {allocation_id}")
          else:
            # For EC2-Classic, release by PublicIp
            ec2.release_address(PublicIp=public_ip)
            print(f"Released unused Elastic IP with PublicIp: {public_ip}")
        except ClientError as e:
          print(f"Error releasing Elastic IP {public_ip}: {e}")
      else:
        print(f"Elastic IP {public_ip} is currently in use. Skipping...")
  except ClientError as e:
    print(f"Failed to describe Elastic IP addresses: {e}")

def lambda_handler(event, context):
  """
  AWS Lambda handler to:
    - Delete empty S3 buckets,
    - Delete unused EBS snapshots, and
    - Release unused Elastic IPs.
  """
  delete_empty_s3_buckets()
  delete_unused_ebs_snapshots()
  release_unused_eips()

  return {
    'statusCode': 200,
    'body': 'Cleanup of empty S3 buckets, unused EBS snapshots, and unused Elastic IPs completed successfully.'
  }
