# ------------------------------------------ #
# AI Knowledge Copilot - Monitoring Module     #
# ------------------------------------------ #

variable "app_insights_name" {
  description = "Name of Application Insights"
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

variable "workspace_name" {
  description = "Name of Log Analytics Workspace"
  type        = string
  default     = ""
}

variable "tags" {
  description = "Tags"
  type        = map(string)
  default     = {}
}

locals {
  workspace_name = var.workspace_name != "" ? var.workspace_name : "${var.app_insights_name}-law"
}

resource "azurerm_log_analytics_workspace" "main" {
  name                = local.workspace_name
  location            = var.location
  resource_group_name = var.resource_group_name
  sku                 = "PerGB2018"
  retention_in_days   = 30
  tags                = var.tags
}

resource "azurerm_application_insights" "main" {
  name                 = var.app_insights_name
  resource_group_name  = var.resource_group_name
  location             = var.location
  application_type     = "web"
  workspace_id         = azurerm_log_analytics_workspace.main.id
  daily_data_cap_in_gb = 2
  tags                 = var.tags
}

output "app_insights_name" {
  value = azurerm_application_insights.main.name
}

output "app_insights_id" {
  value = azurerm_application_insights.main.id
}

output "instrumentation_key" {
  value     = azurerm_application_insights.main.instrumentation_key
  sensitive = true
}

output "connection_string" {
  value     = azurerm_application_insights.main.connection_string
  sensitive = true
}

output "workspace_id" {
  value = azurerm_log_analytics_workspace.main.id
}
