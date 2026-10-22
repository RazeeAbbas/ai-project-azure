# ------------------------------------------ #
# AI Knowledge Copilot - Root terraform files  #
# ------------------------------------------ #

# Terraform root configuration

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
}

provider "azurerm" {
  features {
    resource_group {
      prevent_deletion_if_contains_resources = false
    }
  }
}

provider "azuread" {
  features {}
}

provider "random" {}
