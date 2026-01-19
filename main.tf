# main.tf (일부러 취약하게 작성된 샘플)
resource "aws_s3_bucket" "insecure_bucket" {
  bucket = "my-devsecops-project-bucket-2026"
  # 취약점: 버전 관리가 꺼져 있음
  # 취약점: 암호화 설정이 없음
  # 취약점: 퍼블릭 액세스 차단이 없음
}

resource "aws_security_group" "insecure_sg" {
  name = "insecure-sg"
  # 취약점: SSH(22번) 포트가 전세계(0.0.0.0/0)에 열려 있음
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}