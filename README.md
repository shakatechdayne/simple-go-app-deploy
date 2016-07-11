# Simple GO App Deployment Project

This project provides a deployment of a simple GO application within AWS cloud VPC. It demonstrates, at a simple level, continuous integration through automation. The project uses [Terraform](https://www.terraform.io/) to provision the infrastructure and [Ansible](https://www.ansible.com/) to configure the app, web and build servers. The build server ([Jenkins](https://jenkins.io/)) is configured to build a simple GO application and deploy it to the app servers if the build is stable. The web server is configured to load balance requests in a round-robin fashion to the app servers. Everything is built and configured using one command.

## Requirements

You will require the following to run the project from a control machine:

* [Terraform](https://www.terraform.io/intro/getting-started/install.html)
* [Ansible](http://docs.ansible.com/ansible/intro_installation.html)
* [Python2.7](https://www.python.org/download/releases/2.7/)
* [Pip](https://pip.pypa.io/en/stable/installing/)
* [Boto3](https://boto3.readthedocs.io/en/latest/guide/quickstart.html#installation)
* [Validators](https://validators.readthedocs.io/en/latest/#installation)
* [Python-Jenkins](https://python-jenkins.readthedocs.io/en/latest/install.html)
* [Debian-Jessie AMI](https://wiki.debian.org/Cloud/AmazonEC2Image/Jessie)

This project also assumes that you have an AWS account with a VPC, subnet and key pair available. It has been tested against official `Debian Jessie` EC2 AMIs. Please ensure that you have the private key within the working directory of the project. You will also need the GO App to deploy, which should be located on a public Git repo or you can use the one located here: [sample-go-app](https://github.com/shakatechdayne/sample-go-app)

## How to Run

Once all the requirements are met on your control machine, clone this repository to your working directory:

```
git clone [GITURL]
```
Now run the `deploy-env.py` python script and supply the necessary information when prompted:

```
python deploy-env.py
```

The script will output to a log file `goAppEnvDeployment.log` within the working directory of the script which will give you clues if something goes wrong.
