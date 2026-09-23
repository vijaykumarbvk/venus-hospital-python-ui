terraform {
  backend "s3" {
    bucket       = "venus-hospital-tfstate-vkb"   # <-- CHANGE to a globally-unique bucket
    key          = "venus-hospital/terraform.tfstate"
    region       = "us-east-1"
    use_lockfile = true
  }
}
