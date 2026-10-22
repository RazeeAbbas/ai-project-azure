# ------------------------------------------ #
# AI Knowledge Copilot - App Service Module    #
# ------------------------------------------ #

variable "app_service_plan_name" {
  description = "Name of the App Service plan"
  type        = string
}

variable "app_service_name" {
  description = "Name of the App Service"
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

variable "app_service_plan_sku" {
  description = "SKU for the App Service plan (e.g. B1, P1v2)"
  type        = string
  default     = "F1"
}

variable "app_settings" {
  description = "App settings map"
  type        = map(string)
  default     = {}
}

variable "tags" {
  description = "Tags for the App Service"
  type        = map(string)
  default     = {}
}

resource "azurerm_service_plan" "main" {
  name                = var.app_service_plan_name
  resource_group_name = var.resource_group_name
  location            = var.location
  os_type             = "Linux"
  sku_name            = var.app_service_plan_sku
  tags                = var.tags
}

resource "azurerm_linux_web_app" "main" {
  name                = var.app_service_name
  resource_group_name = var.resource_group_name
  location            = var.location
  service_plan_id     = azurerm_service_plan.main.id

  site_config {
    always_on = var.app_service_plan_sku == "F1" ? false : true
    application_stack {
      python_version = "3.11"
    }
  }

  app_settings = var.app_settings

  identity {
    type = "SystemAssigned"
  }

  tags = var.tags
}

output "app_service_name" {
  value = azurerm_linux_web_app.main.name
}

output "app_service_id" {
  value = azurerm_linux_web_app.main.id
}

output "app_service_url" {
  value = azurerm_linux_web_app.main.default_hostname
}

output "app_service_plan_id" {
  value = azurerm_service_plan.main.id
}

output "identity_principal_id" {
  value = length(azurerm_linux_web_app.main.identity) > 0 ? azurerm_linux_web_app.main.identity[0].principal_id : ""
}
