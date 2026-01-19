# Shift-Left Security Implementation
> 인프라(IaC)와 애플리케이션 보안을 단일 플랫폼에서 통합 관리하는 DevSecOps 아키텍처 구현

---

## 🎯 프로젝트 개요

GitHub Advanced Security(CodeQL)와 Checkov를 활용하여 **배포 전 단계에서** 인프라 설정 오류와 애플리케이션 코드 취약점을 자동으로 탐지하는 Shift-Left Security 파이프라인입니다.

### 핵심 가치
- 🛡️ **자동화된 보안 게이트**: 취약점 발견 시 배포 자동 차단
- ⚡ **병렬 실행 최적화**: Infrastructure와 Application 스캔 동시 수행
- 📊 **통합 대시보드**: GitHub Security 탭을 통한 Single Pane of Glass 구현
- 🔄 **SARIF 표준 통합**: 이기종 보안 도구 결과의 표준화된 집계

---

## 🏗️ 아키텍처

### 워크플로우 구조
```
┌─────────────────────────────────────────────────┐
│            Git Push/Pull Request                │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│          GitHub Actions Trigger                 │
└─────────────────────────────────────────────────┘
                      ↓
        ┌─────────────────────────────┐
        │    Parallel Execution       │
        ├─────────────┬───────────────┤
        ↓             ↓               
┌──────────────┐  ┌────────────────┐
│ IaC Security │  │ App Security   │
│  (Checkov)   │  │   (CodeQL)     │
└──────────────┘  └────────────────┘
        │             │
        └─────┬───────┘
              ↓
    ┌──────────────────┐
    │  SARIF Upload    │
    │  to Security Tab │
    └──────────────────┘
              ↓
    ┌──────────────────┐
    │ Security Gate    │
    │ (Pass/Fail)      │
    └──────────────────┘
```

### 보안 도구 역할 분담

| 도구 | 대상 | 탐지 항목 | 출력 포맷 |
|------|------|----------|----------|
| **Checkov** | Infrastructure (Terraform) | S3 암호화, Security Group 설정, 리소스 정책 등 | SARIF |
| **CodeQL** | Application (Python) | SQL Injection, 하드코딩된 시크릿, Command Injection 등 | SARIF |

---

## 🔧 구현 상세

### 1️⃣ 보안 게이트 메커니즘

#### 취약점 발견 시 자동 차단
```yaml
jobs:
  iac-security:
    soft_fail: false  # 취약점 발견 시 Job 실패
    
  app-security:
    # CodeQL 분석 실행
```

**동작 방식:**
- Checkov 또는 CodeQL에서 취약점 탐지 → Job 실패
- 전체 워크플로우 상태: ❌ Failed
- 실제 배포 단계 진입 차단 (배포 Job이 추가될 경우)

#### 결과 업로드는 보장
```yaml
- name: Upload Results
  if: always()  # 실패해도 반드시 실행
```

**효과:**
- 스캔 실패 시에도 Security 탭에 상세 내용 기록
- 개발자가 정확한 취약점 위치와 수정 방법 확인 가능

---

### 2️⃣ 병렬 실행 최적화

#### Job 독립성 설계
```yaml
jobs:
  iac-security:    # Job 1: Infrastructure 스캔
  app-security:    # Job 2: Application 스캔 (병렬)
  security-summary: # Job 3: 리포트 (순차)
    needs: [iac-security, app-security]
```

**성능 이점:**
```
순차 실행: Checkov (30s) + CodeQL (60s) = 90s
병렬 실행: max(30s, 60s) = 60s
→ 33% 시간 단축
```

**안정성:**
- Job 1 실패해도 Job 2는 계속 실행
- 모든 보안 검사 완료 보장
- 포괄적인 취약점 탐지

---

### 3️⃣ SARIF 표준 기반 통합

#### 통합 포인트
```yaml
# Checkov → SARIF
output_format: sarif
category: checkov-iac-scan

# CodeQL → SARIF (자동)
category: codeql-python
```

#### GitHub Security 탭 통합 효과

**Before (도구 분리):**
```
Checkov CLI → 터미널 출력 → 수동 확인
CodeQL     → 별도 대시보드 → 수동 확인
→ 보안 가시성 분산, 관리 복잡도 증가
```

**After (통합 대시보드):**
```
모든 취약점 → GitHub Security 탭
→ 단일 화면에서 전체 위험 수준 파악
→ 코드 라인 직접 링크
→ 우선순위별 자동 정렬
```

---

## 🧪 데모용 취약 코드 샘플

### Infrastructure (sample_vulnerable.tf)
```terraform
# 의도적 취약점 10개 포함 (교육 목적)
resource "aws_s3_bucket" "insecure_bucket" {
  bucket = "my-devsecops-project-bucket-2026"
  # ❌ 암호화 미설정
  # ❌ 버전 관리 비활성화
  # ❌ 퍼블릭 액세스 차단 없음
}

resource "aws_security_group" "insecure_sg" {
  # ❌ SSH(22) 전체 공개 (0.0.0.0/0)
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
```

### Application (sample_vulnerable_app.py)
```python
# 의도적 취약점 8개 포함 (교육 목적)
SECRET_KEY = "hardcoded-secret-key-123456"  # ❌ 하드코딩된 시크릿

@app.route('/user')
def get_user():
    user_id = request.args.get('id')
    query = f"SELECT * FROM users WHERE id = '{user_id}'"  # ❌ SQL Injection
    cursor.execute(query)

@app.route('/ping')
def ping_server():
    host = request.args.get('host')
    os.system(f"ping -c 1 {host}")  # ❌ Command Injection
```

> ⚠️ **주의**: 이 파일들은 보안 스캔 데모를 위한 샘플 코드이며, 실제 프로덕션 환경에서 절대 사용하지 마십시오.

---

## 📊 실행 결과

### GitHub Actions
```
DevSecOps-Shift-Left-Scan
Status: ❌ Failed

├─ Infrastructure Security (Checkov)  ❌ Failed
│  └─ 10 vulnerabilities detected
│
├─ Application Security (CodeQL)      ✅ Completed
│  └─ 5-8 vulnerabilities detected
│
└─ Security Scan Summary              ✅ Success
   └─ Report generated
```

### GitHub Security 탭
```
Code scanning alerts: 15-18 total

🔴 Critical (5)
├─ [Checkov] S3 bucket encryption disabled
├─ [Checkov] Security Group allows SSH from 0.0.0.0/0
├─ [CodeQL] SQL injection vulnerability
├─ [CodeQL] Hardcoded credentials
└─ [CodeQL] Command injection vulnerability

🟠 High (8)
🟡 Medium (3)
```

---

## 🎓 기술적 의의

### Shift-Left Security 구현
```
전통적 접근:
개발 → 빌드 → 배포 → [보안 스캔] → 취약점 발견 → 롤백 (비용 高)

Shift-Left 접근:
개발 → [보안 스캔] → 취약점 차단 → 빌드 → 배포 (비용 低)
```

### 확장 가능한 구조
현재 파이프라인에 추가 가능한 단계:
```yaml
jobs:
  iac-security:      # 현재 구현 ✅
  app-security:      # 현재 구현 ✅
  security-summary:  # 현재 구현 ✅
  
  # 확장 가능 (선택사항)
  deploy-staging:    # 스테이징 배포
    needs: [iac-security, app-security]
    if: success()
    
  manual-approval:   # 수동 승인
  deploy-production: # 프로덕션 배포
```

---

## 📖 참고 자료

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Checkov Documentation](https://www.checkov.io/1.Welcome/What%20is%20Checkov.html)
- [CodeQL Documentation](https://codeql.github.com/docs/)
- [SARIF Specification](https://docs.oasis-open.org/sarif/sarif/v2.1.0/sarif-v2.1.0.html)

---

## 📝 결론

본 프로젝트는 **인프라 보안(Checkov)**과 **애플리케이션 보안(CodeQL)**을 GitHub Actions 파이프라인 내에서 **SARIF 표준**을 통해 통합함으로써, 개발팀이 단일 플랫폼(GitHub)에서 전체적인 보안 상태를 모니터링할 수 있는 **Single Pane of Glass** 아키텍처를 구현하였습니다.

이를 통해 보안 검증을 개발 초기 단계로 이동(Shift-Left)시켜, 취약점 수정 비용을 최소화하고 배포 안정성을 극대화하는 현대적인 DevSecOps 체계를 구축하였습니다.
