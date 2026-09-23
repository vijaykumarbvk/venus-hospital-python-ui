############################
# ECR REPOSITORIES
#
# The CI workflow also creates these on demand, but declaring them here
# means `terraform destroy` cleans them up and lifecycle policies are
# version-controlled rather than clicked in the console.
############################

locals {
  ecr_repositories = [
    "venus-user-service",
    "venus-doctor-service",
    "venus-patient-service",
    "venus-appointment-service",
    "venus-api-gateway",
    "venus-streamlit-frontend",
  ]
}

resource "aws_ecr_repository" "services" {
  for_each = toset(local.ecr_repositories)

  name                 = each.value
  image_tag_mutability = "MUTABLE"
  force_delete         = true

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = merge(var.project_tags, { Name = each.value })
}

# Keep the last 10 images per repo; untagged layers expire after a day.
resource "aws_ecr_lifecycle_policy" "services" {
  for_each   = aws_ecr_repository.services
  repository = each.value.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Expire untagged images after 1 day"
        selection = {
          tagStatus   = "untagged"
          countType   = "sinceImagePushed"
          countUnit   = "days"
          countNumber = 1
        }
        action = { type = "expire" }
      },
      {
        rulePriority = 2
        description  = "Keep only the 10 most recent images"
        selection = {
          tagStatus   = "any"
          countType   = "imageCountMoreThan"
          countNumber = 10
        }
        action = { type = "expire" }
      }
    ]
  })
}
