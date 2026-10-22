# ------------------------------------------ #
# AI Knowledge Copilot - Key Vault Module      #
# ------------------------------------------ #

variable "key_vault_name" {
  description = "Name of the Key Vault (3-24 characters, alphanumeric and dashes)"
  type        = string
}

variable "resource_group_name" {
  description = "Resource group name"
  type        = string
}

variable "location" {
  description = "Azure region"
  type        = string
}

variable "enabled_for_deployment" {
  description = "Enable for deployment"
  type        = bool
  default     = false
}

variable "enabled_for_disk_encryption" {
  description = "Enable for disk encryption"
  type        = bool
  default     = false
}

variable "enabled_for_template_deployment" {
  description = "Enable for template deployment"
  type        = bool
  default     = false
}

variable "tags" {
  description = "Tags"
  type        = map(string)
  default     = {}
}

data "azurerm_client_config" "current" {}

resource "azurerm_key_vault" "main" {
  name                            = var.key_vault_name
  resource_group_name             = var.resource_group_name
  location                        = var.location
  enabled_for_deployment          = var.enabled_for_deployment
  enabled_for_disk_encryption     = var.enabled_for_disk_encryption
  enabled_for_template_deployment = var.enabled_for_template_deployment
  tenant_id                       = data.azurerm_client_config.current.tenant_id
  soft_delete_retention_days      = 7
  purge_protection_enabled        = false

  sku_name = "standard"
  tags     = var.tags
}

resource "azurerm_key_vault_access_policy" "current" {
  key_vault_id = azurerm_key_vault.main.id
  tenant_id    = data.azurerm_client_config.current.tenant_id
  object_id    = data.azurerm_client_config.current.object_id

  key_permissions     = ["Get", "List", "Create", "Delete"]
  secret_permissions  = ["Get", "List", "Set", "Delete"]
  storage_permissions = ["Get", "List"]
}

output "key_vault_name" {
  value = azurerm_key_vault.main.name
}

output "key_vault_id" {
  value = azurerm_key_vault.main.id
}

output "key_vault_uri" {
  value = azurerm_key_vault.main.vault_uri
}
