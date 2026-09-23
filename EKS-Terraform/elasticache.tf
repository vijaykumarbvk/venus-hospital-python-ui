############################
# ElastiCache — Redis
#
# Backs two things in the app:
#   1. @cached decorators in doctor/appointment services
#   2. Flask-Limiter's rate-limit counters in the API gateway
#
# Managed Redis rather than an in-cluster pod, so restarting the
# cluster never wipes the rate-limit state.
############################

resource "aws_elasticache_subnet_group" "venus" {
  name       = "${var.cluster_name}-redis-subnet-group"
  subnet_ids = [aws_subnet.private1.id, aws_subnet.private2.id]

  tags = var.project_tags
}

resource "aws_elasticache_cluster" "redis" {
  cluster_id           = "${var.cluster_name}-redis"
  engine               = "redis"
  engine_version       = "7.1"
  node_type            = "cache.t3.micro"
  num_cache_nodes      = 1
  parameter_group_name = "default.redis7"
  port                 = 6379

  subnet_group_name  = aws_elasticache_subnet_group.venus.name
  security_group_ids = [aws_security_group.data_tier.id]

  tags = merge(var.project_tags, { Name = "${var.cluster_name}-redis" })
}
