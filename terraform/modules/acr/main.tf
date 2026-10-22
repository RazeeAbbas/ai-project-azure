# ------------------------------------------ #
# AI Knowledge Copilot - Azure Container Registry Module #
# ------------------------------------------ #

variable "registry_name" {
  description = "Name of the container registry (alphanumeric only, 5-50 characters)"
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

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}

variable "sku" {
  description = "SKU of the registry (Basic, Standard, Premium)"
  type        = string
  default     = "Basic"
}

variable "admin_enabled" {
  description = "Enable admin credentials on registry"
  type        = bool
  default     = true
}

variable "tags" {
  description = "Tags for the registry"
  type        = map(string)
  default     = {}
}

resource "azurerm_container_registry" "main" {
  name                = var.registry_name
  resource_group_name = var.resource_group_name
  location            = var.location
  sku                 = var.sku
  admin_enabled       = var.admin_enabled
  tags                = var.tags
}

output "registry_name" {
  value = azurerm_container_registry.main.name
}

output "registry_login_server" {
  value = azurerm_container_registry.main.login_server
}

output "registry_id" {
  value = azurerm_container_registry.main.id
}

output "admin_username" {
  value     = var.admin_enabled ? azurerm_container_registry.main.admin_username : ""
  sensitive = false
}

output "admin_password" {
  value     = var.admin_enabled ? azurerm_container_registry.main.admin_password : ""
  sensitive = true
}

