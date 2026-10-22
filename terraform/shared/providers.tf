terraform {
  required_version = ">= 1.5.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.100"
    }
    azuread = {
      source  = "hashicorp/azuread"
      version = "~> 2.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
  }
}

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.100"
    }
    azuread = {
      source  = "hashicorp/azuread"
      version = "~> 2.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
  }
}


# ------------------------------------------ #
# AI Knowledge Copilot - Terraform Modules     #
# ------------------------------------------ #

# Terraform modules for Azure infrastructure

# Resource Group Module
# Provider configuration
terraform {
  required_version = ">= 1.5.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "= 3.112.0"
    }
    azuread = {
      source  = "hashicorp/azuread"
      version = "= 2.52.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "= 3.6.3"
    }
  }

  backend "azurerm" {
    resource_group_name  = "tfstate-resource-group"
    storage_account_name = "tfstateaccount"
    container_name       = "tfstate"
    key                  = "ai-knowledge-copilot.tfstate"
  }
}

provider "azurerm" {
  features {}
}

provider "azuread" {
  features {}
}
