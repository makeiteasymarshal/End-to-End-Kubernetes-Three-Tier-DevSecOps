variable "name_prefix" {
  type = string
}

variable "vpc_cidr" {
  type = string
}

variable "availability_zones" {
  type = list(string)
}

variable "cluster_name" {
  type = string
}

variable "enable_nat_gateway" {
  type    = bool
  default = true
}
