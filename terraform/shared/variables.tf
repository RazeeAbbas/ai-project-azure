variable "location" {
  description = "Azure region for all resources"
  type        = string
  default     = "East US"
}

variable "common_tags" {
  description = "Common tags applied to all resources"
  type        = map(string)
  default = {
    Project     = "AI Knowledge Copilot"
    Environment = "Dev"
    ManagedBy   = "Terraform"
    Owner       = "DevOps Team"
  }
}

variable "location" {
  description = "Azure region for all resources"
  type        = string
  default     = "East US"
}

variable "common_tags" {
  description = "Common tags applied to all resources"
  type        = map(string)
  default = {
    Project     = "AI Knowledge Copilot"
    Environment = "Dev"
    ManagedBy   = "Terraform"
    Owner       = "DevOps Team"
  }
}


# ------------------------------------------ #
# AI Knowledge Copilot - Terraform Variables   #
# ------------------------------------------ #

# Root variables

variable "location" {
  description = "Azure region for all resources"
  type        = string
  default     = "East US"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
}

variable "common_tags" {
  description = "Common tags for all resources"
  type        = map(string)
  default = {
    Project   = "AI Knowledge Copilot"
    ManagedBy = "Terraform"
  }
}
