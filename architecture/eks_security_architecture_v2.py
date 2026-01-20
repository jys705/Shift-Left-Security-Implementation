#!/usr/bin/env python3
"""
EKS Integrated Security Architecture v2
통합 보안 아키텍처 다이어그램 with Shift-Left, Zero Trust, Advanced Governance
+ Auth0 인증 로그 스트리밍 to Datadog
"""

from diagrams import Diagram, Cluster, Edge
from diagrams.aws.network import Route53, CloudFront, ELB, VPC
from diagrams.aws.security import Shield, WAF, Guardduty, Inspector, SecurityHub, IAM
from diagrams.aws.compute import EKS, Lambda
from diagrams.aws.integration import Eventbridge
from diagrams.onprem.vcs import Github
from diagrams.onprem.monitoring import Datadog
from diagrams.saas.chat import Slack
from diagrams.custom import Custom

# 다이어그램 설정
graph_attr = {
    "fontsize": "16",
    "bgcolor": "white",
    "splines": "ortho",
    "nodesep": "0.8",
    "ranksep": "1.2"
}

with Diagram(
    "EKS Integrated Security Architecture v2",
    filename="eks_security_architecture_v2",
    direction="LR",
    graph_attr=graph_attr,
    show=False
):
    
    # ====== 1. Development (Shift-Left Security) ======
    with Cluster("Development\nShift-Left Security"):
        github = Github("GitHub")
        checkov = Custom("Checkov\nIaC Scanning", "./architecture/checkov.png")
        
        github >> Edge(color="darkblue", style="bold") >> checkov
    
    # ====== 2. Edge Security ======
    with Cluster("Edge Security"):
        route53 = Route53("Global DNS")
        shield = Shield("DDoS Protection")
        cloudfront = CloudFront("CDN")
        waf = WAF("L7 Firewall")
        
        route53 >> shield >> cloudfront >> waf
    
    # ====== 3. Authentication Layer (Zero Trust) ======
    auth0 = Custom("Auth0\n(OIDC/Auth0)", "./architecture/auth0.png")
    
    # ====== 4. VPC & Compute ======
    with Cluster("VPC"):
        with Cluster("Public Subnet"):
            alb = ELB("ALB\n(OIDC/Auth0)")
        
        with Cluster("Private Subnet"):
            eks = EKS("EKS Cluster")
        
        alb >> Edge(color="black") >> eks
    
    # ====== 5. Security Governance ======
    with Cluster("Security Governance\nCentralized Monitoring"):
        guardduty = Guardduty("GuardDuty\nThreat Detection")
        inspector = Inspector("Inspector\nVuln Scanning")
        prowler = Custom("Prowler\nAWS Auditing", "./architecture/prowler.png")
        security_hub = SecurityHub("Security Hub\nCentralized Monitoring")
        
        guardduty >> Edge(color="firebrick") >> security_hub
        inspector >> Edge(color="firebrick") >> security_hub
        prowler >> Edge(color="darkorange", style="dashed") >> security_hub
    
    # ====== 6. Observability & SIEM ======
    with Cluster("Observability\nSIEM & Analytics"):
        datadog = Datadog("Datadog\nSIEM")
    
    # ====== 7. Automation & Response ======
    with Cluster("Auto-Response\nIncident Automation"):
        eventbridge = Eventbridge("EventBridge")
        lambda_func = Lambda("Lambda\nAuto-Response")
        slack = Slack("Slack\nNotification")
    
    # ==========================================
    # 주요 흐름 정의
    # ==========================================
    
    # Development Pipeline: GitHub -> Checkov -> EKS
    checkov >> Edge(color="darkblue", label="IaC Deploy", style="bold") >> eks
    
    # Edge Security Flow
    waf >> Edge(color="black") >> alb
    
    # Zero Trust Authentication: Auth0 <-> ALB
    auth0 >> Edge(color="purple", label="OIDC Auth", style="dashed") >> alb
    
    # *** NEW: Auth0 인증 로그 스트리밍 to Datadog ***
    auth0 >> Edge(color="dodgerblue", label="Auth Logs", style="dotted") >> datadog
    
    # Security Monitoring: EKS -> GuardDuty & Inspector
    eks >> Edge(color="firebrick", style="dotted") >> guardduty
    eks >> Edge(color="firebrick", style="dotted") >> inspector
    
    # Security Hub -> Datadog (SIEM)
    security_hub >> Edge(color="darkorange", label="Findings", style="bold") >> datadog
    
    # Auto-Response Flow: GuardDuty -> EventBridge -> Lambda
    guardduty >> Edge(color="red", label="Threat Event", style="bold") >> eventbridge
    eventbridge >> Edge(color="red", style="bold") >> lambda_func
    
    # Lambda Auto-Block & Notification
    lambda_func >> Edge(color="red", label="Auto-Block/Update IP Set", style="bold") >> waf
    lambda_func >> Edge(color="orange", label="Alert", style="dashed") >> slack

print("✅ EKS Integrated Security Architecture v2 다이어그램이 생성되었습니다!")
print("📊 파일명: eks_security_architecture_v2.png")
print("🆕 추가 기능: Auth0 → Datadog 인증 로그 스트리밍")
