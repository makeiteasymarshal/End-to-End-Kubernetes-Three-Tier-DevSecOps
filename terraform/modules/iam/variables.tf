variable "name_prefix" {
  type = string
}

variable "github_repository" {
  type = string
}

variable "ecr_repo_arns" {
  type = list(string)
}
