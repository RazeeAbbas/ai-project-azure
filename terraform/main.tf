# ------------------------------------------ #
# AI Knowledge Copilot - Terraform Root Config #
# ------------------------------------------ #

# Root terraform configuration

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
  }
}

provider "azurerm" {
  features {}
}

provider "azuread" {}

# Backend configuration should be specified in each environment
# For remote state, configure backend in the environment
