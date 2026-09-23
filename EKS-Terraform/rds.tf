############################
# RDS — MySQL
#
# The app follows database-per-service, but all four logical databases
# live on one RDS instance here to keep cost sane for a dev/demo build.
# Schema isolation is preserved (venus_user_db, venus_doctor_db, ...),
# so splitting them onto separate instances later is a config change,
# not a code change.
#
# CREDENTIALS: hardcoded here rather than passed as a Terraform secret
# variable — same pattern as your previous project's rds.tf
# (username = "admin", password = "Cloud123"). This means no
# DB_PASSWORD GitHub secret and no TF_VAR_db_password to manage.
#
# Trade-off, stated plainly: the password is in this file, in git, in
# plaintext. That's fine for a throwaway dev/demo cluster you can
# `terraform destroy` when you're done — the same trade your previous
# project made. Before this ever holds real data, replace `password`
# below with `manage_master_user_password = true` (RDS-managed password
# in Secrets Manager, zero code changes needed elsewhere) or wire in
# TF_VAR_db_password the way the commented block further down shows.
############################

resource "aws_db_subnet_group" "venus" {
  name       = "${var.cluster_name}-db-subnet-group"
  subnet_ids = [aws_subnet.private1.id, aws_subnet.private2.id]

  tags = merge(var.project_tags, { Name = "${var.cluster_name}-db-subnet-group" })
}

resource "aws_db_instance" "mysql" {
  identifier     = "${var.cluster_name}-mysql"
  engine         = "mysql"
  engine_version = "8.0"
  instance_class = "db.t3.micro"

  allocated_storage     = 20
  max_allocated_storage = 100
  storage_type          = "gp3"
  storage_encrypted     = true

  db_name  = "cloud"
  username = var.db_username # "admin"
  password = "Cloud123"      # same value as your previous project — see note above
  port     = 3306

  # ---- To switch to a secret-backed password instead, delete the line
  # above and uncomment this one (needs the db_password variable back
  # in variables.tf and TF_VAR_db_password set wherever you run terraform):
  # password = var.db_password

  db_subnet_group_name   = aws_db_subnet_group.venus.name
  vpc_security_group_ids = [aws_security_group.data_tier.id]

  # Private only — the pods reach it over the VPC, nothing else can.
  publicly_accessible = false
  multi_az            = false

  backup_retention_period = 7
  skip_final_snapshot     = true
  deletion_protection     = false

  tags = merge(var.project_tags, { Name = "${var.cluster_name}-mysql" })
}
