resource "random_password" "db_master" {
  length           = 24
  special          = true
  override_special = "!*-_=+"
}

resource "aws_secretsmanager_secret" "rds_credentials" {
  name                    = "${var.name_prefix}/rds/credentials"
  recovery_window_in_days = 0
}

resource "aws_secretsmanager_secret_version" "rds_credentials" {
  secret_id = aws_secretsmanager_secret.rds_credentials.id
  secret_string = jsonencode({
    username     = var.db_username
    password     = random_password.db_master.result
    dbname       = var.db_name
    engine       = "postgresql"
    port         = 5432
    host         = aws_db_instance.this.address
    database_url = "postgresql://${var.db_username}:${urlencode(random_password.db_master.result)}@${aws_db_instance.this.address}:5432/${var.db_name}?sslmode=require"
  })
}

resource "aws_db_subnet_group" "this" {
  name       = "${var.name_prefix}-db-subnet-group"
  subnet_ids = var.private_db_subnet_ids

  tags = {
    Name = "${var.name_prefix}-db-subnet-group"
  }
}

resource "aws_db_instance" "this" {
  identifier             = "${var.name_prefix}-postgres"
  engine                 = "postgres"
  engine_version         = "16.4"
  instance_class         = var.db_instance_class
  allocated_storage      = 20
  max_allocated_storage  = 50
  storage_type           = "gp3"
  storage_encrypted      = true
  db_name                = var.db_name
  username               = var.db_username
  password               = random_password.db_master.result
  db_subnet_group_name   = aws_db_subnet_group.this.name
  vpc_security_group_ids = [var.rds_security_group_id]
  publicly_accessible    = false
  multi_az               = false
  skip_final_snapshot    = true
  deletion_protection    = false

  tags = {
    Name = "${var.name_prefix}-postgres"
  }
}
