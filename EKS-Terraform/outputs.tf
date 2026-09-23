output "cluster_name" {
  description = "Feed this to: aws eks update-kubeconfig --name <this>"
  value       = aws_eks_cluster.eks.name
}

output "cluster_endpoint" {
  value = aws_eks_cluster.eks.endpoint
}

output "rds_endpoint" {
  description = "Host portion goes into k8s-base/app-secret.yml as DB_HOST"
  value       = aws_db_instance.mysql.address
}

output "redis_endpoint" {
  description = "Goes into k8s-base/app-config.yml as REDIS_HOST"
  value       = aws_elasticache_cluster.redis.cache_nodes[0].address
}

output "bastion_public_ip" {
  description = "SSH here to run kubectl against the cluster"
  value       = aws_instance.eks_client.public_ip
}

output "ecr_registry" {
  description = "Base URI for all pushed images"
  value       = "${data.aws_caller_identity.current.account_id}.dkr.ecr.${var.aws_region}.amazonaws.com"
}

data "aws_caller_identity" "current" {}
