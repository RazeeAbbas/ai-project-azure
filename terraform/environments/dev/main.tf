# ------------------------------------------ #
# AI Knowledge Copilot - Terraform Dev Config  #
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
  name_prefix = "aicopilot-${var.environment}"
  safe_prefix = "aicop${var.environment}${random_string.suffix.result}"
}

# 1. Resource Group
module "resource_group" {
  source = "../../modules/resource-group"

  resource_group_name = "${local.name_prefix}-rg"
  location            = var.location
  environment         = var.environment
  tags                = var.common_tags
}

# 2. Networking
module "networking" {
  source = "../../modules/networking"

  resource_group_name  = module.resource_group.resource_group_name
  location             = module.resource_group.location
  environment          = var.environment
  virtual_network_name = "${local.name_prefix}-vnet"
  subnets = [
    {
      name = "aks-subnet"
      cidr = "10.0.1.0/24"
    },
    {
      name = "app-subnet"
      cidr = "10.0.2.0/24"
    }
  ]
  tags = var.common_tags
}

# 3. Azure Container Registry
module "acr" {
  source = "../../modules/acr"

  registry_name       = substr(replace("${local.safe_prefix}acr", "-", ""), 0, 48)
  resource_group_name = module.resource_group.resource_group_name
  location            = module.resource_group.location
  environment         = var.environment
  sku                 = "Basic"
  admin_enabled       = true
  tags                = var.common_tags
}

# 4. Azure Kubernetes Service (AKS)
module "aks" {
  source = "../../modules/aks"

  aks_name            = "${local.name_prefix}-aks"
  resource_group_name = module.resource_group.resource_group_name
  location            = module.resource_group.location
  kubernetes_version  = var.kubernetes_version
  node_count          = var.node_count
  agent_node_vm_size  = var.agent_node_vm_size
  vnet_subnet_id      = module.networking.subnet_ids["aks-subnet"]
  tags                = var.common_tags
}

# ACR Pull Role Assignment for AKS Kubelet Identity
resource "azurerm_role_assignment" "aks_acr_pull" {
  scope                = module.acr.registry_id
  role_definition_name = "AcrPull"
  principal_id         = module.aks.kubelet_identity_object_id
}

# 5. App Service (Plan & Linux Web App)
module "app_service" {
  source = "../../modules/app-service"

  app_service_plan_name = "${local.name_prefix}-asp"
  app_service_name      = "${local.name_prefix}-app"
  resource_group_name   = module.resource_group.resource_group_name
  location              = module.resource_group.location
  app_service_plan_sku  = var.app_service_plan_sku
  app_settings = {
    "WEBSITES_ENABLE_APP_SERVICE_STORAGE"   = "false"
    "ENVIRONMENT"                           = var.environment
    "APPLICATIONINSIGHTS_CONNECTION_STRING" = module.monitoring.connection_string
  }
  tags = var.common_tags
}

# 6. PostgreSQL Flexible Server
module "database" {
  source = "../../modules/database"

  postgresql_name        = "${local.name_prefix}-psql"
  resource_group_name    = module.resource_group.resource_group_name
  location               = module.resource_group.location
  administrator_login    = var.db_admin_username
  administrator_password = var.db_admin_password
  sku_name               = var.db_sku
  storage_mb             = var.db_storage_mb
  database_name          = "aikcopilot"
  tags                   = var.common_tags
}

# 7. Blob Storage Account
module "storage" {
  source = "../../modules/storage"

  storage_account_name = substr(replace("${local.safe_prefix}sa", "-", ""), 0, 24)
  resource_group_name  = module.resource_group.resource_group_name
  location             = module.resource_group.location
  container_name       = "documents"
  tags                 = var.common_tags
}

# 8. Key Vault
module "key_vault" {
  source = "../../modules/key-vault"

  key_vault_name      = substr(replace("${local.safe_prefix}kv", "-", ""), 0, 24)
  resource_group_name = module.resource_group.resource_group_name
  location            = module.resource_group.location
  tags                = var.common_tags
}

# 9. Monitoring (Application Insights & Log Analytics)
module "monitoring" {
  source = "../../modules/monitoring"

  app_insights_name   = "${local.name_prefix}-ai"
  resource_group_name = module.resource_group.resource_group_name
  location            = module.resource_group.location
  tags                = var.common_tags
}
