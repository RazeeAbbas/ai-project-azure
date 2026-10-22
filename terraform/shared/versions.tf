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
# AI Knowledge Copilot - Terraform Environment #
# ------------------------------------------ #

# Terraform environment configuration

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
    resource_group_name  = "ai-knowledge-copilot-tfstate-rg"
    storage_account_name = "aiknowledgecopilottfstate"
    container_name       = "tfstate"
    key                  = "ai-knowledge-copilot.tfstate"
  }
}

provider "azurerm" {
  features {
    resource_group {
      prevent_deletion_if_contains_resources = false
    }
  }
}

provider "azuread" {}

provider "random" {}

# Configure backend after init
# To use remote state: terraform init -migrate-state
