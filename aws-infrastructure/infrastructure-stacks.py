from aws_cdk import (
    aws_codebuild as codebuild,
    aws_iam as iam,
    aws_ec2 as ec2,
    aws_eks as eks,
    aws_ecr as ecr,
    aws_elasticsearch as es,
    core
)
import os

class AWSInfrastructureStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        eks_vpc = ec2.Vpc(
            self, "VPC",
            cidr="10.0.0.0/16"
        )

        # Create IAM Role For EC2 bastion instance to be able to manage the cluster
        bastion_role = iam.Role(
            self, "BastionRole",
            assumed_by=iam.CompositePrincipal(
                iam.ServicePrincipal("ec2.amazonaws.com"),
                iam.AccountRootPrincipal()
            )
        )
        self.bastion_role = bastion_role
        # Create EC2 Instance Profile for that Role
        instance_profile = iam.CfnInstanceProfile(
            self, "InstanceProfile",
            roles=[bastion_role.role_name]            
        )

        # Create SecurityGroup for the Control Plane ENIs
        eks_security_group = ec2.SecurityGroup(
            self, "EKSSecurityGroup",
            vpc=eks_vpc,
            allow_all_outbound=True
        )
        
        eks_security_group.add_ingress_rule(
            ec2.Peer.ipv4('10.0.0.0/16'),
            ec2.Port.all_traffic()
        )    

        # Create an EKS Cluster
        eks_cluster = eks.Cluster(
            self, "cluster",
            vpc=eks_vpc,
            masters_role=bastion_role,
            default_capacity_type=eks.DefaultCapacityType.NODEGROUP,
            default_capacity_instance=ec2.InstanceType("m5.large"),
            default_capacity=2,
            security_group=eks_security_group,
            endpoint_access=eks.EndpointAccess.PUBLIC_AND_PRIVATE,
            version=eks.KubernetesVersion.V1_18
        )

        # Deploy ALB Ingress Controller
        # Create the k8s Service account and corresponding IAM Role mapped via IRSA
        alb_service_account = eks_cluster.add_service_account(
            "aws-load-balancer-controller",
            name="aws-load-balancer-controller",
            namespace="kube-system"
        )

        # Create the PolicyStatements to attach to the role
        # I couldn't find a way to get this to work with a PolicyDocument and there are 10 of these
        alb_policy_statement_json_1 = {
            "Effect": "Allow",
            "Action": [
                "acm:DescribeCertificate",
                "acm:ListCertificates",
                "acm:GetCertificate"
            ],
            "Resource": "*"
        }
        alb_policy_statement_json_2 = {
            "Effect": "Allow",
            "Action": [
                "ec2:AuthorizeSecurityGroupIngress",
                "ec2:CreateSecurityGroup",
                "ec2:CreateTags",
                "ec2:DeleteTags",
                "ec2:DeleteSecurityGroup",
                "ec2:DescribeAccountAttributes",
                "ec2:DescribeAddresses",
                "ec2:DescribeInstances",
                "ec2:DescribeInstanceStatus",
                "ec2:DescribeInternetGateways",
                "ec2:DescribeNetworkInterfaces",
                "ec2:DescribeSecurityGroups",
                "ec2:DescribeSubnets",
                "ec2:DescribeTags",
                "ec2:DescribeVpcs",
                "ec2:ModifyInstanceAttribute",
                "ec2:ModifyNetworkInterfaceAttribute",
                "ec2:RevokeSecurityGroupIngress"
            ],
            "Resource": "*"
        }
        alb_policy_statement_json_3 = {
            "Effect": "Allow",
            "Action": [
                "elasticloadbalancing:AddListenerCertificates",
                "elasticloadbalancing:AddTags",
                "elasticloadbalancing:CreateListener",
                "elasticloadbalancing:CreateLoadBalancer",
                "elasticloadbalancing:CreateRule",
                "elasticloadbalancing:CreateTargetGroup",
                "elasticloadbalancing:DeleteListener",
                "elasticloadbalancing:DeleteLoadBalancer",
                "elasticloadbalancing:DeleteRule",
                "elasticloadbalancing:DeleteTargetGroup",
                "elasticloadbalancing:DeregisterTargets",
                "elasticloadbalancing:DescribeListenerCertificates",
                "elasticloadbalancing:DescribeListeners",
                "elasticloadbalancing:DescribeLoadBalancers",
                "elasticloadbalancing:DescribeLoadBalancerAttributes",
                "elasticloadbalancing:DescribeRules",
                "elasticloadbalancing:DescribeSSLPolicies",
                "elasticloadbalancing:DescribeTags",
                "elasticloadbalancing:DescribeTargetGroups",
                "elasticloadbalancing:DescribeTargetGroupAttributes",
                "elasticloadbalancing:DescribeTargetHealth",
                "elasticloadbalancing:ModifyListener",
                "elasticloadbalancing:ModifyLoadBalancerAttributes",
                "elasticloadbalancing:ModifyRule",
                "elasticloadbalancing:ModifyTargetGroup",
                "elasticloadbalancing:ModifyTargetGroupAttributes",
                "elasticloadbalancing:RegisterTargets",
                "elasticloadbalancing:RemoveListenerCertificates",
                "elasticloadbalancing:RemoveTags",
                "elasticloadbalancing:SetIpAddressType",
                "elasticloadbalancing:SetSecurityGroups",
                "elasticloadbalancing:SetSubnets",
                "elasticloadbalancing:SetWebAcl"
            ],
            "Resource": "*"
        }
        alb_policy_statement_json_4 = {
            "Effect": "Allow",
            "Action": [
                "iam:CreateServiceLinkedRole",
                "iam:GetServerCertificate",
                "iam:ListServerCertificates"
            ],
            "Resource": "*"
        }
        alb_policy_statement_json_5 = {
            "Effect": "Allow",
            "Action": [
                "cognito-idp:DescribeUserPoolClient"
            ],
            "Resource": "*"
        }
        alb_policy_statement_json_6 = {
            "Effect": "Allow",
            "Action": [
                "waf-regional:GetWebACLForResource",
                "waf-regional:GetWebACL",
                "waf-regional:AssociateWebACL",
                "waf-regional:DisassociateWebACL"
            ],
            "Resource": "*"
        }
        alb_policy_statement_json_7 = {
            "Effect": "Allow",
            "Action": [
                "tag:GetResources",
                "tag:TagResources"
            ],
            "Resource": "*"
        }
        alb_policy_statement_json_8 = {
            "Effect": "Allow",
            "Action": [
                "waf:GetWebACL"
            ],
            "Resource": "*"
        }
        alb_policy_statement_json_9 = {
            "Effect": "Allow",
            "Action": [
                "wafv2:GetWebACL",
                "wafv2:GetWebACLForResource",
                "wafv2:AssociateWebACL",
                "wafv2:DisassociateWebACL"
            ],
            "Resource": "*"
        }
        alb_policy_statement_json_10 = {
            "Effect": "Allow",
            "Action": [
                "shield:DescribeProtection",
                "shield:GetSubscriptionState",
                "shield:DeleteProtection",
                "shield:CreateProtection",
                "shield:DescribeSubscription",
                "shield:ListProtections"
            ],
            "Resource": "*"
        }
        
        # Attach the necessary permissions
        alb_service_account.add_to_policy(iam.PolicyStatement.from_json(alb_policy_statement_json_1))
        alb_service_account.add_to_policy(iam.PolicyStatement.from_json(alb_policy_statement_json_2))
        alb_service_account.add_to_policy(iam.PolicyStatement.from_json(alb_policy_statement_json_3))
        alb_service_account.add_to_policy(iam.PolicyStatement.from_json(alb_policy_statement_json_4))
        alb_service_account.add_to_policy(iam.PolicyStatement.from_json(alb_policy_statement_json_5))
        alb_service_account.add_to_policy(iam.PolicyStatement.from_json(alb_policy_statement_json_6))
        alb_service_account.add_to_policy(iam.PolicyStatement.from_json(alb_policy_statement_json_7))
        alb_service_account.add_to_policy(iam.PolicyStatement.from_json(alb_policy_statement_json_8))
        alb_service_account.add_to_policy(iam.PolicyStatement.from_json(alb_policy_statement_json_9))
        alb_service_account.add_to_policy(iam.PolicyStatement.from_json(alb_policy_statement_json_10))

        # Deploy the ALB Ingress Controller from the Helm chart
        eks_cluster.add_helm_chart(
            "aws-load-balancer-controller",
            chart="aws-load-balancer-controller",
            repository="https://aws.github.io/eks-charts",
            namespace="kube-system",
            values={
                "clusterName": eks_cluster.cluster_name,
                "region": self.region,
                "vpcId": eks_vpc.vpc_id,
                "serviceAccount": {
                    "create": False,
                    "name": "aws-load-balancer-controller"
                }
            }
        )

        # Deploy External DNS Controller
        # Create the k8s Service account and corresponding IAM Role mapped via IRSA
        externaldns_service_account = eks_cluster.add_service_account(
            "external-dns",
            name="external-dns",
            namespace="kube-system"
        )

        # Create the PolicyStatements to attach to the role
        externaldns_policy_statement_json_1 = {
        "Effect": "Allow",
            "Action": [
                "route53:ChangeResourceRecordSets"
            ],
            "Resource": [
                "arn:aws:route53:::hostedzone/*"
            ]
        }
        externaldns_policy_statement_json_2 = {
            "Effect": "Allow",
            "Action": [
                "route53:ListHostedZones",
                "route53:ListResourceRecordSets"
            ],
            "Resource": [
                "*"
            ]
        }

        # Add the policies to the service account
        externaldns_service_account.add_to_policy(iam.PolicyStatement.from_json(externaldns_policy_statement_json_1))
        externaldns_service_account.add_to_policy(iam.PolicyStatement.from_json(externaldns_policy_statement_json_2))

        # Deploy the Helm Chart
        eks_cluster.add_helm_chart(
            "external-dns",
            chart="external-dns",
            repository="https://charts.bitnami.com/bitnami",
            namespace="kube-system",
            values={
                "provider": "aws",
                "aws": {
                    "region": self.region
                },
                "serviceAccount": {
                    "create": False,
                    "name": "external-dns"
                },
                "podSecurityContext": {
                    "fsGroup": 65534
                }
            }
        )    

        # Install external secrets controller
        # Create the Service Account
        externalsecrets_service_account = eks_cluster.add_service_account(
            "kubernetes-external-secrets",
            name="kubernetes-external-secrets",
            namespace="kube-system"
        )

        # Define the policy in JSON
        externalsecrets_policy_statement_json_1 = {
        "Effect": "Allow",
            "Action": [
                "secretsmanager:GetResourcePolicy",
                "secretsmanager:GetSecretValue",
                "secretsmanager:DescribeSecret",
                "secretsmanager:ListSecretVersionIds"
            ],
            "Resource": [
                "*"
            ]
        }

        # Add the policies to the service account
        externalsecrets_service_account.add_to_policy(iam.PolicyStatement.from_json(externalsecrets_policy_statement_json_1))

        # Deploy the Helm Chart
        eks_cluster.add_helm_chart(
            "external-secrets",
            chart="kubernetes-external-secrets",            
            repository="https://external-secrets.github.io/kubernetes-external-secrets/",
            namespace="kube-system",
            values={
                "env": {
                    "AWS_REGION": self.region
                },
                "serviceAccount": {
                    "name": "kubernetes-external-secrets",
                    "create": False
                },
                "securityContext": {
                    "fsGroup": 65534
                }
            }
        )

        # Deploy Flux
        # Deploy the Helm Chart
        eks_cluster.add_helm_chart(
            "flux",
            chart="flux",
            repository="https://charts.fluxcd.io",
            namespace="kube-system",
            values={
                "git": {
                    "url": "git@github.com:jasonumiker/k8s-plus-aws-gitops",
                    "path": "k8s-app-resources",
                    "branch": "master"
                }
            }
        )

        # Deploy Prometheus and Grafana
        # TODO Replace this with the new AWS Managed Prometheus and Grafana when available
        eks_cluster.add_helm_chart(
            "metrics",
            chart="kube-prometheus-stack",
            repository="https://prometheus-community.github.io/helm-charts",
            namespace="monitoring",
            values={
                "prometheus": {
                    "prometheusSpec": {
                    "storageSpec": {
                        "volumeClaimTemplate": {
                        "spec": {
                            "accessModes": [
                            "ReadWriteOnce"
                            ],
                            "resources": {
                            "requests": {
                                "storage": "8Gi"
                            }
                            },
                            "storageClassName": "gp2"
                        }
                        }
                    }
                    }
                },
                "alertmanager": {
                    "alertmanagerSpec": {
                    "storage": {
                        "volumeClaimTemplate": {
                        "spec": {
                            "accessModes": [
                            "ReadWriteOnce"
                            ],
                            "resources": {
                            "requests": {
                                "storage": "2Gi"
                            }
                            },
                            "storageClassName": "gp2"
                        }
                        }
                    }
                    }
                },
                "grafana": {
                    "persistence": {
                        "enabled": "true",
                        "storageClassName": "gp2"
                    }
                }
            }          
        )

        # Deploy Fluentbit and Elasticsearch
        # Deploy an ElasticSearch Domain
        es_domain = es.Domain(
            self, "ESDomain",
            version=es.ElasticsearchVersion.V7_9
        )
        # Create the Service Account
        fluentbit_service_account = eks_cluster.add_service_account(
            "fluentbit",
            name="fluentbit",
            namespace="monitoring"
        )

        # Define the policy in JSON
        fluentbit_policy_statement_json_1 = {
        "Effect": "Allow",
            "Action": [
                "es:ESHttp*"
            ],
            "Resource": [
                es_domain.domain_arn
            ]
        }

        # Add the policies to the service account
        fluentbit_service_account.add_to_policy(iam.PolicyStatement.from_json(externalsecrets_policy_statement_json_1))

        # Grant fluentbit access to our ES Domain
        es_domain.grant_write(fluentbit_service_account)

        eks_cluster.add_helm_chart(
            "fluent-bit",
            chart="fluent-bit",
            repository="https://fluent.github.io/helm-charts",
            namespace="monitoring",
            values={
                "serviceAccount": {
                    "create": False,
                    "name": "fluentbit"
                },
                "config": {
                    "outputs": "[OUTPUT]\n    Name            es\n    Match           *\n    Host            "+es_domain.domain_endpoint+"\n    Port            443\n    TLS             On\n    AWS_Auth        On\n    AWS_Region      "+self.region+"\n    Retry_Limit     6\n",
                }
            }
        )    

class AWSAppResourcesPipelineStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create IAM Role For CodeBuild
        # TODO Make this role's policy least privilege
        aws_app_resources_build_role = iam.Role(
            self, "AWSAppResourcesBuildRole",
            assumed_by=iam.ServicePrincipal("codebuild.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AdministratorAccess")
            ]
        )

        # We only want to fire on the master branch and if there is a change in the dockerbuild folder
        git_hub_source = codebuild.Source.git_hub(
            owner="jasonumiker",
            repo="k8s-plus-aws-gitops",
            webhook=True,
            webhook_filters=[
                codebuild.FilterGroup.in_event_of(codebuild.EventAction.PUSH).and_branch_is("master").and_file_path_is("aws-app-resources/*")
            ]
        )

        # Create CodeBuild
        build_project = codebuild.Project(
            self, "AWSAppResourcesBuildProject",
            source=git_hub_source,
            role=aws_app_resources_build_role,
            build_spec=codebuild.BuildSpec.from_source_filename("aws-app-resources/buildspec.yml")
        )

class DockerBuildPipelineStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        
        # Create ECR Repository
        ghost_repo = ecr.Repository(
            self, "GhostRepo",
            repository_name="ghost"
        )

        # Create IAM Role For CodeBuild
        ghost_build_role = iam.Role(
            self, "GhostBuildRole",
            assumed_by=iam.ServicePrincipal("codebuild.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("EC2InstanceProfileForImageBuilderECRContainerBuilds")
            ]
        )

        # We only want to fire on the master branch and if there is a change in the dockerbuild folder
        git_hub_source = codebuild.Source.git_hub(
            owner="jasonumiker",
            repo="k8s-plus-aws-gitops",
            webhook=True,
            webhook_filters=[
                codebuild.FilterGroup.in_event_of(codebuild.EventAction.PUSH).and_branch_is("master").and_file_path_is("dockerbuild/*")
            ]
        )

        # Create CodeBuild
        build_project = codebuild.Project(
            self, "GhostBuildProject",
            source=git_hub_source,
            role=ghost_build_role,
            build_spec=codebuild.BuildSpec.from_source_filename("dockerbuild/buildspec.yml"),
            environment={
                'privileged': True,
            },
            environment_variables={
                'AWS_ACCOUNT_ID': codebuild.BuildEnvironmentVariable(value=self.account),
                'IMAGE_REPO_NAME': codebuild.BuildEnvironmentVariable(value=ghost_repo.repository_name)
            }
        )

app = core.App()
aws_infrastructure_stack = AWSInfrastructureStack(app, "AWSInfrastructureStack")
aws_app_resources_pipeline_stack = AWSAppResourcesPipelineStack(app, "AWSAppResourcesPipelineStack")
docker_build_pipeline_stack = DockerBuildPipelineStack(app, "DockerBuildPipelineStack")
app.synth()