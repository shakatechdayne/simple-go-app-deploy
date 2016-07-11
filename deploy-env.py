from boto3.session import Session
from botocore.exceptions import ClientError
import boto3, logging, os, getpass, subprocess, validators, time, jenkins, httplib

""" Logging Configuration """
logging.basicConfig(filename="goAppEnvDeployment.log",
					format= '%(asctime)s - %(levelname)s: %(message)s',
					level=logging.DEBUG)
					
"""
Defines our GO application environment and provides necessary functions to
validate
"""
class goAppEnv ():
	def __init__ (self, strCloud, strCloudKey, strCloudPass, strRegion):
		self.strCloud = strCloud
		self.strCloudKey = strCloudKey
		self.strCloudPass = strCloudPass
		self.strRegion = strRegion
		self.keyPair = ""
		self.vpcId = ""
		self.Subnet = ""
		self.webPort = "80"
		self.appPort = "8585"
		self.buildPort = "8080"
		self.appUrl = ""
		self.amiId = ""
		self.invDir = ""
		self.jenkinsUser = ""
		self.jenkinsPass = ""
		self.jenkinsBuildName = ""
		self.appSrv1Ip = ""
		self.appSrv2Ip = ""
		self.webSrvIp = ""
		self.buildSrvIp = ""
		self.srvUser = ""
		self.session = Session(
			aws_access_key_id = self.strCloudKey,
			aws_secret_access_key = self.strCloudPass,
			region_name = self.strRegion)

	""" Validates the provided AWS Access key, Secret key and SSH Key Pair """
	def validateAwsKeyPair (self, strKeyPair, strDir):
		self.keyPair = strKeyPair

		try:
			ec2 = self.session.resource('ec2')
			key_pair_info = ec2.KeyPair(self.keyPair)
			key_pair_info.load()

			"""
			If the private key exists in the running directory and the key pair
			exists within AWS account, then pass.
			"""
			privateKeyFile = strDir + "/" + self.keyPair + ".pem"

			if os.path.isfile(privateKeyFile):
				logging.info("The '%s' key pair fingerprint is: %s" % (self.keyPair, key_pair_info.key_fingerprint))
				print("The key pair exists!")
				print("The '%s' key pair fingerprint is: %s" % (self.keyPair, key_pair_info.key_fingerprint))
				logging.info("The private key file (%s.pem) exists!" % self.keyPair)
				return True
			else:
				logging.error("The private key file (%s.pem) is not available!" % self.keyPair)
				print("The private key file (%s.pem) is not available!" % self.keyPair)
				return False

		except Exception, e:
			logging.error("Could not find the key pair '%s' due to the following error: %s" %(self.keyPair, e))
			print("Could not find the key pair '%s' due to the following error: %s" %(self.keyPair, e))

			return False

	""" Validates the provided VPC ID and Subnet information """
	def validateAwsVpcId (self, strVpc, strSubnet):
		self.vpcId = strVpc
		self.Subnet = strSubnet
		try:
			foundSubnet = False
			ec2 = self.session.resource('ec2')
			vpc = ec2.Vpc(self.vpcId)
			vpc.load()

			logging.info("Current VPC state: %s" % vpc.state)
			vpcSubnets = vpc.subnets.all()

			for subnet in vpcSubnets:
				if self.Subnet == subnet.id:
					logging.info("The subnet with id (%s) exists!" % (self.Subnet))
					print("The subnet with id (%s) exists!" % (self.Subnet))
					foundSubnet = True
				else:
					logging.error("The subnet with id ()%s) does not exist!" % (self.Subnet))
					print("The subnet with id ()%s) does not exist!" % (self.Subnet))
					foundSubnet = False
			return foundSubnet
		except Exception, e:
			logging.error("Could not find the VPC or Subnet due to the following error: %s" % e)
			print("Could not find the VPC (%s) or Subnet (%s) due to the following error: %s" % (self.vpcId, self.Subnet, e))
			return False

	def validateAwsAmiId (self, strAmiId):
		self.amiId = strAmiId
		try:
			ec2 = self.session.resource('ec2')
			image = ec2.Image(self.amiId)

			if image.state == 'available':
				logging.info("Found available image (%s)" % self.amiId)
				print("Found available image (%s)" % self.amiId)
				return True
			else:
				logging.error("The supplied image (%s) is not available!" % self.amiId)
				print("The supplied image (%s) is not available!" % self.amiId)
				return False
		except Exception, e:
			logging.error("Could not find the image (%s) due to the following error: %s" % (self.amiId, e))
			print("Could not find the image (%s) due to the following error: %s" % (self.amiId, e))
			return False

	def buildAwsInf (self):
		""" Change working directory """
		os.chdir(os.getcwd() + "/terraform/aws")
		outcome = False
		try:
			""" Create variable file """
			varFile = open('create-env.tvars', 'w')
			varFile.truncate()
			varFile.write('awsKey="%s"\n' % self.strCloudKey)
			varFile.write('awsSecret="%s"\n' % self.strCloudPass)
			varFile.write('region="%s"\n' % self.strRegion)
			varFile.write('vpcId="%s"\n' % self.vpcId)
			varFile.write('subnetId="%s"\n' % self.Subnet)
			varFile.write('webPort="%s"\n' % self.webPort)
			varFile.write('appPort="%s"\n' % self.appPort)
			varFile.write('buildPort="%s"\n' % self.buildPort)
			varFile.write('amiId="%s"\n' % self.amiId)
			varFile.write('keyPair="%s"\n' % self.keyPair)
			varFile.write('inventoryDir="%s"\n' % self.invDir)
			varFile.close()
			varFile = None
		except Exception, e:
			logging.error("An error occured while trying to create the terraform vars file: %s" % e)
			print("An error occured while trying to create the terraform vars file: %s" % e)
			return False

		try:
			print("")
			print("Creating terraform plan for go app environment: ")
			result = subprocess.call(['terraform', 'plan', '-var-file=create-env.tvars'])
			if result == 1:
				return False
			else:
				outcome = True
		except Exception, e:
			logging.error("An error occured while trying to create the terraform plan: %s" % e)
			print("An error occured while trying to create the terraform plan: %s" % e)
			return False

		try:
			print("")
			print("Applying terraform plan: ")
			result = subprocess.call(['terraform', 'apply', '-var-file=create-env.tvars'])
			if result == 1:
				return False
			else:
				outcome = True
		except Exception, e:
			logging.error("An error occured while trying to apply the terraform plan: %s" % e)
			print("An error occured while trying to apply the terraform plan: %s" % e)
			return False

		try:
			print("")
			print("Retrieving the server IPs: ")
			self.appSrv1Ip = subprocess.check_output(['terraform', 'output', 'appNode1ip']).rstrip('\n')
			self.appSrv2Ip = subprocess.check_output(['terraform', 'output', 'appNode2ip']).rstrip('\n')
			self.webSrvIp = subprocess.check_output(['terraform', 'output', 'webNodeIp']).rstrip('\n')
			self.buildSrvIp = subprocess.check_output(['terraform', 'output', 'buildNodeIp']).rstrip('\n')
			outcome = True
		except Exception, e:
			logging.error("An error occured while retrieving the server IPs: %s" % e)
			print("An error occured while retrieving the server IPs: %s" % e)
			return False

		return outcome

	def configSrvViaAnsible (self, strPlayBook, strInventory, dictVars ):
		""" Change the working directory """
		os.chdir(self.invDir)
		outcome = False

		""" Format the list of extra variables for the play """
		extraVars = "--extra-vars='{"
		keyCount = 0
		dictVarsSize = len(dictVars)
		for key, var in dictVars.iteritems():
			keyCount += 1
			if keyCount == dictVarsSize:
				extraVars += key + ": " + var
			else:
				extraVars += key  + ": " + var + ", "

		extraVars += "}'"
		command = "export ANSIBLE_HOST_KEY_CHECKING=False && ansible-playbook -vvvv -i " + strInventory + " " + extraVars + " " + strPlayBook
		print("Calling command: %s" % command)
		try:
			result = subprocess.call([command], shell=True)
			#if result == 1:
			#	return False
			#else:
			#	outcome = True
			return True
		except Exception, e:
			logging.error("An error occured while applying the playbook (%s): %s" % (strPlayBook, e))
			print("An error occured while applying the playbook (%s): %s" % (strPlayBook, e))
			return False

		return outcome

	def kickOffGoAppBuild (self):
		try:
			jenkinsSrvUrl = "http://" + self.buildSrvIp + ":" + self.buildPort
			server = jenkins.Jenkins(jenkinsSrvUrl, username=self.jenkinsUser, password=self.jenkinsPass)
			server.build_job(self.jenkinsBuildName)
			time.sleep(20)
			buildData = server.get_build_info(name=self.jenkinsBuildName, number=1)
			result = buildData['result']

			if not result == 'SUCCESS':
				return False
			else:
				return True
		except Exception, e:
			logging.error("An error occured while trying to kick off the (%s) build: %s" %(self.jenkinsBuildName, e))
			print("An error occured while trying to kick off the (%s) build: %s" %(self.jenkinsBuildName, e))
			return False

	def testGoAppLB (self):
		try:
			testUrl = self.webSrvIp + ":" + self.webPort
			conn = httplib.HTTPConnection(testUrl)
			conn.request('GET', '/')
			firstReq = conn.getresponse()
			data1 = firstReq.read()
			print data1
			conn.request('GET', '/')
			secondReq = conn.getresponse()
			data2 = secondReq.read()
			print data2

			if data1 == data2:
				#print("Responses are equal!")
				return False
			else:
				#print("Responses are not equal!")
				return True
		except Exception, e:
			logging.error("The following error occured while trying to test the GO App via the balancer: %s" % e)
			print("The following error occured while trying to test the GO App via the balancer: %s" % e)
			return False
		finally:
			conn.close()

def main():

	# Get Running Directory
	runningDir = os.getcwd()

	# Get the environment details
	accessKey = str(raw_input('Please provide the AWS Access Key: '))
	secretKey = str(raw_input('Please provide the AWS Secret Key: '))
	region = str(raw_input('What is the region you want to deploy to: '))

	# Create our environment object and validate
	myApp = goAppEnv('AWS', accessKey, secretKey, region)
	sshKeyPair = str(raw_input('Please provide the SSH keypair name to use: '))
	valid = myApp.validateAwsKeyPair(sshKeyPair, runningDir)

	if not valid:
		os._exit(1)

	# Get the AWS VPC, Subnet and AMI ID and Validate
	vpcId = str(raw_input('Please supply the VPC ID to deploy to: '))
	subnetId = str(raw_input('What is the subnet ID to deploy in: '))
	valid = myApp.validateAwsVpcId(vpcId,subnetId)

	if not valid:
		os._exit(1)

	amiId = str(raw_input('What is the ami ID for the OS image to deploy: '))
	valid = myApp.validateAwsAmiId(amiId)

	if not valid:
		os._exit(1)

	# Get the OS Sudo User
	myApp.srvUser = str(raw_input('Please supply the username of the sudo user for the OS on %s: ' % amiId))
	if myApp.srvUser == "":
		logging.error("The sudo user for the OS on %s cannot be empty!" % amiId)
		print("The sudo user for the OS on %s cannot be empty!" % amiId)
		os._exit(1)

	# Set the directory for the environment inventory
	myApp.invDir = os.getcwd()

	# Start building the environment
	buildStatus = myApp.buildAwsInf()
	if not buildStatus:
		logging.error("Failed to build the AWS infrastructure!")
		os._exit(1)

	print("Waiting for servers to become available....")
	time.sleep(120)

	# Configure the App Servers
	print("")
	print("Configuring the GO App Servers: ")
	appConfig = myApp.configSrvViaAnsible(myApp.invDir + '/ansible/build-goserver.yml', myApp.invDir+'/inventory.ini',
										{'"sshUser"' : '"' + myApp.srvUser + '"'})

	if not appConfig:
		logging.error("Failed to configure the GO App Servers!")
		os._exit(1)

	# Configure the Web Balancer Server
	print("")
	print("Configuring the Web Load Balancer: ")

	# Get the application url
	appUrl = str(raw_input("Please supply a valid domain name for the app url (e.g www.domain.com) : "))
	while not validators.domain(appUrl):
		print("The domain name supplied is invalid!")
		appUrl = str(raw_input("Please supply a valid domain name for the app url (e.g www.domain.com) : "))

	myApp.appUrl = appUrl
	webConfig = myApp.configSrvViaAnsible(myApp.invDir + '/ansible/build-balancer.yml', myApp.invDir + '/inventory.ini',
										{'"sshUser"': '"' + myApp.srvUser + '"', '"appUrl"': '"' + myApp.appUrl + '"', '"appNode1ip"': '"' + myApp.appSrv1Ip + '"',
										'"appNode2ip"': '"' + myApp.appSrv2Ip + '"', '"appPort"': myApp.appPort})

	if not webConfig:
		logging.error("Failed to configure the Web Balancer Server!")
		os._exit(1)

	# Configure the Jenkins Build Server
	print("")
	print("Configuring the Jenkins Build Server: ")

	# Set the username, password, job name and GitHub URL for the build server
	userName = str(raw_input("Please provide a username for the build server: "))
	if userName == "":
		logging.error("Build server username cannot be empty!")
		print("The build server username cannot be empty!")
		os._exit(1)

	myApp.jenkinsUser = userName

	passWord = getpass.getpass(prompt='Please provide a password for username (%s) :' % userName)
	if passWord == "":
		logging.error("Build server password for user (%s) cannot be empty!" % userName)
		print("The build server password for user (%s) cannot be empty!" % userName)
		os._exit(1)

	myApp.jenkinsPass = passWord

	jobName = str(raw_input("Please supply the name of the GO App Build Job in Jenkins: "))
	if jobName == "":
		logging.error("GO App build job name cannot be empty!")
		print("Go App build job name cannot be empty!")
		os._exit(1)

	myApp.jenkinsBuildName = jobName

	gitUrl = str(raw_input("Please supply the GitHub URL for the GO App public repo: "))
	while not validators.url(gitUrl):
		print("The url supplied is invalid!")
		gitUrl = str(raw_input("Please supply a valid GitHub URL for the Go App public repo: "))

	buildConfig = myApp.configSrvViaAnsible(myApp.invDir + '/ansible/build-jenkins.yml', myApp.invDir + '/inventory.ini',
											{'"sshUser"': '"' + myApp.srvUser + '"', '"ipList"' : "[" + '"' + myApp.appSrv1Ip + '"' + "," + '"' + myApp.appSrv2Ip + '"' + "]",
											'"buildUser"': '"' + myApp.jenkinsUser + '"', '"buildPass"': '"' + myApp.jenkinsPass + '"', '"gitUrl"': '"' + gitUrl + '"',
											'"buildJobName"': '"' + myApp.jenkinsBuildName + '"'})

	if not buildConfig:
		logging.error("Failed to configure the Jenkins Build Server!")
		os._exit(1)

	# Starting the build on the build server
	print("Waiting for build server to restart: ")
	time.sleep(20)
	print("")
	print("Scheduling the first build of the (%s) build job on %s:" % (myApp.jenkinsBuildName, myApp.buildSrvIp))
	buildJobResult = myApp.kickOffGoAppBuild()

	if not buildJobResult:
		print("Failed to start the build of the (%s) build job on %s. Please check the logs!" % (myApp.jenkinsBuildName, myApp.buildSrvIp))
		os._exit(1)

	# Test the Go App was successfully deployed and load balanced by the web balancer
	appDeployResult = myApp.testGoAppLB()

	if not appDeployResult:
		print("The test of the GO App deployment failed. Please check the logs!")
		os._exit(1)
	else:
		logging.info("Successfully deployed and tested the (%s) application!" % myApp.jenkinsBuildName)
		print("The deployment of the %s application was successful!" % myApp.jenkinsBuildName)
		print("Please ensure that you point the %s domain name to %s IP." % (myApp.appUrl, myApp.webSrvIp))
main()
