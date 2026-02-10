#!/bin/bash

# Redirect all output and errors to a log file
exec > >(tee -a /var/log/user_data.log | logger -t user_data) 2>&1
echo "$(date) - Starting user_data script for Train-Ticket"
echo "$(date) - instance_index is set to: ${instance_index}"
echo "The random suffix is: ${RANDOM_SUFFIX}"
echo "Using bucket name: ${BUCKET_NAME}"

# Common setup tasks for all instances
common_setup() {
  # Update and install required packages
apt update
apt install snapd -y
echo "$(date) - Snapd installed successfully"

# Install MicroK8s
snap install microk8s --classic
echo "$(date) - MicroK8s installed successfully"

# Wait for MicroK8s to be ready
microk8s status --wait-ready
echo "$(date) - MicroK8s is ready"

# Add user to MicroK8s group
usermod -a -G microk8s ubuntu
chown -f -R ubuntu ~/.kube
echo "$(date) - User permissions updated for MicroK8s"

# Install AWS CLI
snap install aws-cli --classic
echo "$(date) - AWS CLI installed successfully"
}

# Function to set up the master node
setup_master_node() {
if [ ${instance_index} -eq 0 ]; then
  echo "$(date) - Configuring master node"
  # Install Terraform on the first instance
  apt-get update && apt-get install -y gnupg software-properties-common
  wget -O- https://apt.releases.hashicorp.com/gpg | gpg --dearmor | sudo tee /usr/share/keyrings/hashicorp-archive-keyring.gpg
  echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
  apt-get update && apt-get install -y terraform

  # Generate MicroK8s config and set KUBECONFIG on the first instance
  microk8s config > /home/ubuntu/microk8s-config
  chown ubuntu:ubuntu /home/ubuntu/microk8s-config
  export KUBECONFIG=/home/ubuntu/microk8s-config
  echo "export KUBECONFIG=/home/ubuntu/microk8s-config" >> /home/ubuntu/.bashrc
  source ~/.bashrc

  # Initialize the master node and generate join commands for worker node 1
  microk8s add-node > /home/ubuntu/${AWS_INSTANCE_PREFIX}-output-worker1.txt
  grep -oP 'microk8s join.*--worker' /home/ubuntu/${AWS_INSTANCE_PREFIX}-output-worker1.txt > /home/ubuntu/${AWS_INSTANCE_PREFIX}-join-command-worker1.txt

  # Initialize the master node and generate join commands for worker node 2
  microk8s add-node > /home/ubuntu/${AWS_INSTANCE_PREFIX}-output-worker2.txt
  grep -oP 'microk8s join.*--worker' /home/ubuntu/${AWS_INSTANCE_PREFIX}-output-worker2.txt > /home/ubuntu/${AWS_INSTANCE_PREFIX}-join-command-worker2.txt

  # Initialize the master node and generate join commands for worker node 3
  microk8s add-node > /home/ubuntu/${AWS_INSTANCE_PREFIX}-output-worker3.txt
  grep -oP 'microk8s join.*--worker' /home/ubuntu/${AWS_INSTANCE_PREFIX}-output-worker3.txt > /home/ubuntu/${AWS_INSTANCE_PREFIX}-join-command-worker3.txt

  # Upload join command files to the new S3 bucket
  aws s3 cp /home/ubuntu/${AWS_INSTANCE_PREFIX}-join-command-worker1.txt s3://${BUCKET_NAME}/${AWS_INSTANCE_PREFIX}-join-command-worker1.txt
  aws s3 cp /home/ubuntu/${AWS_INSTANCE_PREFIX}-join-command-worker2.txt s3://${BUCKET_NAME}/${AWS_INSTANCE_PREFIX}-join-command-worker2.txt
  aws s3 cp /home/ubuntu/${AWS_INSTANCE_PREFIX}-join-command-worker3.txt s3://${BUCKET_NAME}/${AWS_INSTANCE_PREFIX}-join-command-worker3.txt

  microk8s kubectl label nodes $(hostname) role=node1
  echo "$(date) - node 1 labelled"
  echo "$(date) - Master node configuration completed"

  # Create the .conf.env file with New Relic credentials
  echo "NEW_RELIC_LICENSE_KEY=${NEW_RELIC_LICENSE_KEY}" > /home/ubuntu/.conf.env
  echo "NEW_RELIC_API_KEY=${NEW_RELIC_API_KEY}" >> /home/ubuntu/.conf.env
  echo "NEW_RELIC_ACCOUNT_ID=${NEW_RELIC_ACCOUNT_ID}" >> /home/ubuntu/.conf.env
  echo "NEW_RELIC_REGION=${NEW_RELIC_REGION}" >> /home/ubuntu/.conf.env
  echo "NEW_RELIC_BROWSER_KEY=${NEW_RELIC_BROWSER_KEY}" >> /home/ubuntu/.conf.env
  echo "GITHUB_USERNAME=${GITHUB_USERNAME}" >> /home/ubuntu/.conf.env
  echo "GITHUB_PAT=${GITHUB_PAT}" >> /home/ubuntu/.conf.env

  # Set ownership and permissions for the .conf.env file
  chown ubuntu:root /home/ubuntu/.conf.env  # Set owner to ubuntu and group to root
  chmod 640 /home/ubuntu/.conf.env
  echo "$(date) - .conf.env file created and permissions set successfully"

  # Enable Ingress
  echo "$(date) - Enabling Ingress"
  microk8s enable ingress
  if [ $? -eq 0 ]; then
    echo "$(date) - Ingress enabled successfully"
  else
    echo "$(date) - Failed to enable Ingress" >&2
  fi

else
  echo "$(date) - Configuring worker node ${instance_index}"
fi
}

# Function to configure worker nodes
setup_worker_node() {
  if [ ${instance_index} -eq 1 ]; then
    # First worker node
    while [ ! -f /home/ubuntu/${AWS_INSTANCE_PREFIX}-join-command-worker1.txt ]; do
      aws s3 cp s3://${BUCKET_NAME}/${AWS_INSTANCE_PREFIX}-join-command-worker1.txt /home/ubuntu/${AWS_INSTANCE_PREFIX}-join-command-worker1.txt || sleep 20
    done
    JOIN_COMMAND=$(cat /home/ubuntu/${AWS_INSTANCE_PREFIX}-join-command-worker1.txt | grep 'microk8s join')
    eval $JOIN_COMMAND

    # Save hostname to a file and upload to S3
    echo "$(hostname)" > /home/ubuntu/${AWS_INSTANCE_PREFIX}-worker1-hostname.txt
    aws s3 cp /home/ubuntu/${AWS_INSTANCE_PREFIX}-worker1-hostname.txt s3://${BUCKET_NAME}/${AWS_INSTANCE_PREFIX}-worker1-hostname.txt || sleep 10

    echo "$(date) - Worker node ${instance_index} configuration completed"

  elif [ ${instance_index} -eq 2 ]; then
    # Second worker node
    while [ ! -f /home/ubuntu/${AWS_INSTANCE_PREFIX}-join-command-worker2.txt ]; do
      aws s3 cp s3://${BUCKET_NAME}/${AWS_INSTANCE_PREFIX}-join-command-worker2.txt /home/ubuntu/${AWS_INSTANCE_PREFIX}-join-command-worker2.txt || sleep 20
    done
    JOIN_COMMAND=$(cat /home/ubuntu/${AWS_INSTANCE_PREFIX}-join-command-worker2.txt | grep 'microk8s join')
    eval $JOIN_COMMAND

    # Save hostname to a file and upload to S3
    echo "$(hostname)" > /home/ubuntu/${AWS_INSTANCE_PREFIX}-worker2-hostname.txt
    aws s3 cp /home/ubuntu/${AWS_INSTANCE_PREFIX}-worker2-hostname.txt s3://${BUCKET_NAME}/${AWS_INSTANCE_PREFIX}-worker2-hostname.txt || sleep 10

    echo "$(date) - Worker node ${instance_index} configuration completed"

  elif [ ${instance_index} -eq 3 ]; then
    # Third worker node
    while [ ! -f /home/ubuntu/${AWS_INSTANCE_PREFIX}-join-command-worker3.txt ]; do
      aws s3 cp s3://${BUCKET_NAME}/${AWS_INSTANCE_PREFIX}-join-command-worker3.txt /home/ubuntu/${AWS_INSTANCE_PREFIX}-join-command-worker3.txt || sleep 20
    done
    JOIN_COMMAND=$(cat /home/ubuntu/${AWS_INSTANCE_PREFIX}-join-command-worker3.txt | grep 'microk8s join')
    eval $JOIN_COMMAND

    # Save hostname to a file and upload to S3
    echo "$(hostname)" > /home/ubuntu/${AWS_INSTANCE_PREFIX}-worker3-hostname.txt
    aws s3 cp /home/ubuntu/${AWS_INSTANCE_PREFIX}-worker3-hostname.txt s3://${BUCKET_NAME}/${AWS_INSTANCE_PREFIX}-worker3-hostname.txt || sleep 10

    echo "$(date) - Worker node ${instance_index} configuration completed"
  fi
}

# Function to label worker nodes
label_worker_nodes() {
  if [ ${instance_index} -eq 0 ]; then
  echo "$(date) - Configuring node labels"

  # Copy the hostname files from S3 to the first instance
  while [ ! -f /home/ubuntu/${AWS_INSTANCE_PREFIX}-worker1-hostname.txt ]; do
  aws s3 cp s3://${BUCKET_NAME}/${AWS_INSTANCE_PREFIX}-worker1-hostname.txt /home/ubuntu/${AWS_INSTANCE_PREFIX}-worker1-hostname.txt || sleep 30
  done
  while [ ! -f /home/ubuntu/${AWS_INSTANCE_PREFIX}-worker2-hostname.txt ]; do
  aws s3 cp s3://${BUCKET_NAME}/${AWS_INSTANCE_PREFIX}-worker2-hostname.txt /home/ubuntu/${AWS_INSTANCE_PREFIX}-worker2-hostname.txt || sleep 30
  done
  while [ ! -f /home/ubuntu/${AWS_INSTANCE_PREFIX}-worker3-hostname.txt ]; do
  aws s3 cp s3://${BUCKET_NAME}/${AWS_INSTANCE_PREFIX}-worker3-hostname.txt /home/ubuntu/${AWS_INSTANCE_PREFIX}-worker3-hostname.txt || sleep 30
  done

  echo "$(date) - Copied worker hostname files to the first instance"

  # Label the worker nodes with appropriate roles using the file content directly
  if [ -s /home/ubuntu/${AWS_INSTANCE_PREFIX}-worker1-hostname.txt ]; then
    microk8s kubectl label node $(cat /home/ubuntu/${AWS_INSTANCE_PREFIX}-worker1-hostname.txt | tr -d '\n') role=node2
    echo "$(date) - Labeled $(cat /home/ubuntu/${AWS_INSTANCE_PREFIX}-worker1-hostname.txt | tr -d '\n') as role=node2"
  fi

  if [ -s /home/ubuntu/${AWS_INSTANCE_PREFIX}-worker2-hostname.txt ]; then
    microk8s kubectl label node $(cat /home/ubuntu/${AWS_INSTANCE_PREFIX}-worker2-hostname.txt | tr -d '\n') role=node3
    echo "$(date) - Labeled $(cat /home/ubuntu/${AWS_INSTANCE_PREFIX}-worker2-hostname.txt | tr -d '\n') as role=node3"
  fi

  if [ -s /home/ubuntu/${AWS_INSTANCE_PREFIX}-worker3-hostname.txt ]; then
    microk8s kubectl label node $(cat /home/ubuntu/${AWS_INSTANCE_PREFIX}-worker3-hostname.txt | tr -d '\n') role=node4
    echo "$(date) - Labeled $(cat /home/ubuntu/${AWS_INSTANCE_PREFIX}-worker3-hostname.txt | tr -d '\n') as role=node4"
  fi
  echo "$(date) - Worker node labeling completed"
fi
}

# Cleanup: Delete the join command files from S3 after all nodes are initialized
cleanup_s3() {
  if [ ${instance_index} -eq 0 ]; then
  sleep 180 # Wait for all nodes to initialize
  aws s3 rm s3://${BUCKET_NAME}/${AWS_INSTANCE_PREFIX}-join-command-worker1.txt
  aws s3 rm s3://${BUCKET_NAME}/${AWS_INSTANCE_PREFIX}-join-command-worker2.txt
  aws s3 rm s3://${BUCKET_NAME}/${AWS_INSTANCE_PREFIX}-join-command-worker3.txt
  aws s3 rm s3://${BUCKET_NAME}/${AWS_INSTANCE_PREFIX}-worker1-hostname.txt
  aws s3 rm s3://${BUCKET_NAME}/${AWS_INSTANCE_PREFIX}-worker2-hostname.txt
  aws s3 rm s3://${BUCKET_NAME}/${AWS_INSTANCE_PREFIX}-worker3-hostname.txt
  echo "$(date) - S3 bucket cleanup completed"
fi
}

cloneAndConfigureTrainTicket() {
if [ ${instance_index} -eq 0 ]; then
  cd /home/ubuntu/
  # Load environment variables from .conf.env
  if [ -f /home/ubuntu/.conf.env ]; then
  export $(grep -v '^#' /home/ubuntu/.conf.env | xargs)
  echo "$(date) - Loaded environment variables from .conf.env"
  else
  echo "$(date) - .conf.env file not found. Exiting." >&2
  exit 1
  fi

  echo "$(date) - Writing git clone command to a file"
  echo "git clone https://${GITHUB_USERNAME}:${GITHUB_PAT}@github.com/FudanSELab/train-ticket.git /home/ubuntu/train-ticket" > /home/ubuntu/clone_command.txt

  # Change ownership of the file to the ubuntu user
  chown ubuntu:ubuntu /home/ubuntu/clone_command.txt
  echo "$(date) - Changed ownership of clone_command.txt to ubuntu"

  # Read and execute the command from the file
  echo "$(date) - Executing the git clone command from the file"
  bash -c "$(cat /home/ubuntu/clone_command.txt)"
  if [ $? -eq 0 ]; then
    echo "$(date) - Repository cloned successfully"
  else
    echo "$(date) - Failed to clone repository" >&2
  fi
  # Wait for 60 seconds
  sleep 60

  # move .conf.env to train-ticket directory
  sudo mv .conf.env /home/ubuntu/train-ticket/

  # Change permissions for the `configure` file and run configure script
  sudo chown -R ubuntu:ubuntu /home/ubuntu/train-ticket
  cd /home/ubuntu/train-ticket
  sudo chmod +x ./configure
  echo "$(date) - Running the configure script"
  ./configure
  if [ $? -eq 0 ]; then
    echo "$(date) - Configure script executed successfully"
  else
    echo "$(date) - Failed to execute configure script" >&2
  fi
fi
echo "$(date) - configure script completed successfully"
}

# Main script logic
common_setup
setup_master_node
setup_worker_node
label_worker_nodes
cloneAndConfigureTrainTicket
cleanup_s3

echo "$(date) - user_data script completed successfully for Train-Ticket"
