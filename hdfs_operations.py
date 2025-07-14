from hdfs import InsecureClient

# Set up Hadoop client (Replace with actual Hadoop NameNode IP or hostname)
HADOOP_NAMENODE = "localhost"  # Change this to your Hadoop NameNode address
HADOOP_USER = "hadoop-user"    # Replace with your Hadoop user

client = InsecureClient(f'http://{HADOOP_NAMENODE}:50070', user=HADOOP_USER)

# Define HDFS path
hdfs_path = "/crime_data/crime_data.csv"  
local_path = "crime_data.csv"  # Ensure this file exists locally

# Write to HDFS
with client.write(hdfs_path, overwrite=True) as writer:
    with open(local_path, 'rb') as f:
        writer.write(f.read())

print(f"File {local_path} uploaded to HDFS at {hdfs_path}")

# Read from HDFS
with client.read(hdfs_path) as reader:
    data = reader.read()
    print(f"Data read from HDFS:\n{data.decode('utf-8')}")
