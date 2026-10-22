# ------------------------------------------ #
# AI Knowledge Copilot - Dev Outputs           #
# ------------------------------------------ #

output "resource_group_name" {
  value = module.resource_group.resource_group_name
}

output "acr_name" {
  value = module.acr.registry_name
}

output "acr_login_server" {
  value = module.acr.registry_login_server
}

output "aks_cluster_name" {
  value = module.aks.cluster_name
}

output "aks_fqdn" {
  value = module.aks.fqdn
}

output "app_service_name" {
  value = module.app_service.app_service_name
}

output "app_service_url" {
  value = "https://${module.app_service.app_service_url}"
}

output "database_hostname" {
  value = module.database.postgresql_hostname
}

output "storage_account_name" {
  value = module.storage.storage_account_name
}

output "key_vault_name" {
  value = module.key_vault.key_vault_name
}

output "app_insights_name" {
  value = module.monitoring.app_insights_name
}

