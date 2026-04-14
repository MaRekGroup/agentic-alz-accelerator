# Development Environment Configuration

subscription_id       = "00000000-0000-0000-0000-000000000000" # Replace with dev subscription
location              = "eastus2"
management_group_name = "Sandbox"
profile_name          = "sandbox"
vnet_address_space    = "10.10.0.0/16"
enable_ddos           = false
enable_defender       = true
log_retention_days    = 30

tags = {
  environment = "dev"
  cost_center = "engineering"
}
