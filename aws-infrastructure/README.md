# Deploying the EKS cluster and associated infratructure using CDK

We are going to use the [AWS Cloud Development Kit (CDK)](https://docs.aws.amazon.com/cdk/index.html) in Python to deploy our environment in AWS.

There are two CDK Stacks in `infrastructure-stacks.py`

- `AWSInfrastructureStack` which creats the VPC and EKS Cluster including deploying a few Helm charts to it once it has been provisioned.
- `AWSAppResourcesPipeline` which creates a CodePipeline and CodeBuild to have a GitOps managed MySQL RDS to form the back-end for our Ghost applicaiton

## Prerequistes
In order to deploy this you'll need
- Access to an AWS account via IAM User or Role with sufficient IAM privleges
- The ability to use the AWS CLI as that User/Role on an EC2 Instance or on your local machine to invoke the CDK
- A registered domain name that is set up in Route53 as a public hosted zone.
    - For AWS employees investigate getting your [your_login].people.aws.dev domain for this purpose
- A validated certificate in ACM covering either ghost.[yourdomain] or *.[yourdomain].
- A GitHub account
- Installation of the [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html) and [CDK](https://docs.aws.amazon.com/cdk/latest/guide/getting_started.html#getting_started_install)
- Installation of [kubectl](https://docs.aws.amazon.com/eks/latest/userguide/install-kubectl.html)
- Installation of [fluxctl](https://docs.fluxcd.io/en/1.21.1/references/fluxctl/)

## Deployment Steps

1. Fork this project to your own GitHub account
1. Create a personal access token on your GitHub account - https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token
1. Create a secret in AWS Secrets Manager called `github-token`.
    1. Choose "Other type of secrets" as well as Plaintext. Clear out the box completely (removing the {"": ""}) and then paste in your token.
1. `git clone` down your fork of `k8s-plus-aws-gitops`
1. `cd k8s-plus-aws-gitops/aws-infrastructure/`
1. Edit `infrastructure-stacks.py` to change from my GitHub repo to yours:
    1. Update the flux Helm chart values to point at your git repo
    1. Update the owner on the Soure pipeline stage to your GitHub username
1. Run `pip install -r requirements.txt` to add the necessary python components for CDK.
1. Run `cdk boostrap` to create the S3 artifact bucket etc. into the account
1. Run `cdk deploy AWSInfrastructureStack` and answer y to the confirmation
1. Look at the Outputs of the AWSInfrastructureStack CloudFormation stack for the aws eks update-kubeconfig command to set up the ~/.kube/config so that your kubectl command will work. Run that command.
1. Run `kubectl get nodes` to confirm everything is working
1. Run `cdk deploy AWSAppResourcesPipeline` and answer y to the confirmation
1. Run `fluxctl identity --k8s-fwd-ns kube-system`
1. Take the ssh key output from that command and [add it as a deploy key on the repo on GitHub](https://docs.fluxcd.io/en/1.21.1/tutorials/get-started/#giving-write-access)