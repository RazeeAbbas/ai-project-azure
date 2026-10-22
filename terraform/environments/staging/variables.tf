# ------------------------------------------ #
# AI Knowledge Copilot - Staging Variables     #
# ------------------------------------------ #

variable "location" {
  type    = string
  default = "eastus"
}

variable "kubernetes_version" {
  type    = string
  default = null
}

variable "node_count" {
  type    = number
  default = 2
}

variable "agent_node_vm_size" {
  type    = string
  default = "Standard_B2s"
}

variable "db_admin_password" {
  type      = string
  sensitive = true
  default   = "StgSecurePass2026!#"
}

variable "common_tags" {
  type = map(string)
  default = {
    Project     = "AI Knowledge Copilot"
    Environment = "Staging"
    ManagedBy   = "Terraform"
  }
}

