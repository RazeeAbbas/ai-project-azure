# ------------------------------------------ #
# AI Knowledge Copilot - Terraform Prod      #
# ------------------------------------------ #

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.112.0"
    }
    azuread = {
      source  = "hashicorp/azuread"
      version = "~> 2.52.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6.0"
    }
  }
}

provider "azurerm" {
  features {}
}

resource "random_string" "suffix" {
  length  = 6
  special = false
  upper   = false
}

locals {
  name_prefix = "aicopilot-prod"
  safe_prefix = "aicopprd${random_string.suffix.result}"
}

module "resource_group" {
  source              = "../../modules/resource-group"
  resource_group_name = "${local.name_prefix}-rg"
  location            = var.location
  environment         = "prod"
  tags                = var.common_tags
}

module "networking" {
  source               = "../../modules/networking"
  resource_group_name  = module.resource_group.resource_group_name
  location             = module.resource_group.location
  environment          = "prod"
  virtual_network_name = "${local.name_prefix}-vnet"
  subnets = [
    { name = "aks-subnet", cidr = "10.2.1.0/24" },
    { name = "app-subnet", cidr = "10.2.2.0/24" }
  ]
  tags = var.common_tags
}

module "acr" {
  source              = "../../modules/acr"
  registry_name       = substr(replace("${local.safe_prefix}acr", "-", ""), 0, 48)
  resource_group_name = module.resource_group.resource_group_name
  location            = module.resource_group.location
  environment         = "prod"
  sku                 = "Premium"
  admin_enabled       = true
  tags                = var.common_tags
}

module "aks" {
  source              = "../../modules/aks"
  aks_name            = "${local.name_prefix}-aks"
  resource_group_name = module.resource_group.resource_group_name
  location            = module.resource_group.location
  kubernetes_version  = var.kubernetes_version
  node_count          = var.node_count
  agent_node_vm_size  = var.agent_node_vm_size
  vnet_subnet_id      = module.networking.subnet_ids["aks-subnet"]
  tags                = var.common_tags
}

resource "azurerm_role_assignment" "aks_acr_pull" {
  scope                = module.acr.registry_id
  role_definition_name = "AcrPull"
  principal_id         = module.aks.kubelet_identity_object_id
}

module "app_service" {
  source                = "../../modules/app-service"
  app_service_plan_name = "${local.name_prefix}-asp"
  app_service_name      = "${local.name_prefix}-app"
  resource_group_name   = module.resource_group.resource_group_name
  location              = module.resource_group.location
  app_service_plan_sku  = "P1v2"
  app_settings = {
    "ENVIRONMENT" = "prod"
  }
  tags = var.common_tags
}

module "database" {
  source                 = "../../modules/database"
  postgresql_name        = "${local.name_prefix}-psql"
  resource_group_name    = module.resource_group.resource_group_name
  location               = module.resource_group.location
  administrator_login    = "copilotadmin"
  administrator_password = var.db_admin_password
  sku_name               = "GP_Standard_D2ds_v4"
  tags                   = var.common_tags
}

module "storage" {
  source               = "../../modules/storage"
  storage_account_name = substr(replace("${local.safe_prefix}sa", "-", ""), 0, 24)
  resource_group_name  = module.resource_group.resource_group_name
  location             = module.resource_group.location
  container_name       = "documents"
  tags                 = var.common_tags
}

module "key_vault" {
  source              = "../../modules/key-vault"
  key_vault_name      = substr(replace("${local.safe_prefix}kv", "-", ""), 0, 24)
  resource_group_name = module.resource_group.resource_group_name
  location            = module.resource_group.location
  tags                = var.common_tags
}

module "monitoring" {
  source              = "../../modules/monitoring"
  app_insights_name   = "${local.name_prefix}-ai"
  resource_group_name = module.resource_group.resource_group_name
  location            = module.resource_group.location
  tags                = var.common_tags
}

