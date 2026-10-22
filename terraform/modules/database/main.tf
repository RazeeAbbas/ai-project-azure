# ------------------------------------------ #
# AI Knowledge Copilot - PostgreSQL Flexible Server Module #
# ------------------------------------------ #

variable "postgresql_name" {
  description = "Name of the PostgreSQL Flexible Server"
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

variable "administrator_login" {
  description = "Administrator username"
  type        = string
  default     = "copilotadmin"
}

variable "administrator_password" {
  description = "Administrator password"
  type        = string
  sensitive   = true
}

variable "sku_name" {
  description = "SKU name (e.g. B_Standard_B1ms)"
  type        = string
  default     = "B_Standard_B1ms"
}

variable "storage_mb" {
  description = "Storage capacity in MB"
  type        = number
  default     = 32768
}

variable "backup_retention_days" {
  description = "Backup retention days"
  type        = number
  default     = 7
}

variable "server_version" {
  description = "PostgreSQL version"
  type        = string
  default     = "14"
}

variable "database_name" {
  description = "Database name"
  type        = string
  default     = "aikcopilot"
}

variable "tags" {
  description = "Tags"
  type        = map(string)
  default     = {}
}

resource "azurerm_postgresql_flexible_server" "main" {
  name                   = var.postgresql_name
  resource_group_name    = var.resource_group_name
  location               = var.location
  version                = var.server_version
  administrator_login    = var.administrator_login
  administrator_password = var.administrator_password
  sku_name               = var.sku_name
  storage_mb             = var.storage_mb
  backup_retention_days  = var.backup_retention_days

  tags = var.tags
}

resource "azurerm_postgresql_flexible_server_database" "main" {
  name      = var.database_name
  server_id = azurerm_postgresql_flexible_server.main.id
  collation = "en_US.utf8"
  charset   = "utf8"
}

# Allow Azure internal connections (0.0.0.0)
resource "azurerm_postgresql_flexible_server_firewall_rule" "azure_access" {
  name             = "AllowAzureServices"
  server_id        = azurerm_postgresql_flexible_server.main.id
  start_ip_address = "0.0.0.0"
  end_ip_address   = "0.0.0.0"
}

output "postgresql_server_name" {
  value = azurerm_postgresql_flexible_server.main.name
}

output "postgresql_server_id" {
  value = azurerm_postgresql_flexible_server.main.id
}

output "postgresql_hostname" {
  value = azurerm_postgresql_flexible_server.main.fqdn
}

output "postgresql_database_name" {
  value = azurerm_postgresql_flexible_server_database.main.name
}

output "administrator_login" {
  value = azurerm_postgresql_flexible_server.main.administrator_login
}
