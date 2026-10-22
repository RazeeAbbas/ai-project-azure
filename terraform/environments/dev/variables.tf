# ------------------------------------------ #
# AI Knowledge Copilot - Dev Variables         #
# ------------------------------------------ #

variable "environment" {
  description = "Deployment environment name"
  type        = string
  default     = "dev"
}

variable "location" {
  description = "Azure region for deployment"
  type        = string
  default     = "eastus"
}

variable "kubernetes_version" {
  description = "Kubernetes version for AKS (null for default stable)"
  type        = string
  default     = null
}

variable "node_count" {
  description = "Number of agent nodes in AKS"
  type        = number
  default     = 1
}

variable "agent_node_vm_size" {
  description = "VM size for agent nodes"
  type        = string
  default     = "Standard_B2s"
}

variable "app_service_plan_sku" {
  description = "SKU for App Service plan"
  type        = string
  default     = "B1"
}

variable "db_sku" {
  description = "Database SKU"
  type        = string
  default     = "B_Standard_B1ms"
}

variable "db_storage_mb" {
  description = "Database storage in MB"
  type        = number
  default     = 32768
}

variable "db_admin_username" {
  description = "Database administrator username"
  type        = string
  default     = "copilotadmin"
}

variable "db_admin_password" {
  description = "Database administrator password"
  type        = string
  sensitive   = true
  default     = "P@ssw0rdDev2026!#"
}

variable "common_tags" {
  description = "Common tags for all resources"
  type        = map(string)
  default = {
    Project     = "AI Knowledge Copilot"
    Environment = "Dev"
    ManagedBy   = "Terraform"
    Owner       = "DevOps Team"
  }
}
