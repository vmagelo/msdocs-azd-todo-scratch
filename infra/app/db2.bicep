param tags object = {}
param location string = resourceGroup().location
param accountName string

@secure()
param postgresPassword string

param postgresUser string
param databaseName string

param keyVaultName string

module postgresServer '../core/database/postgresql/flexibleserver.bicep' = {
  name: 'postgresql'
  scope: resourceGroup()
  params: {
    name: accountName
    location: location
    tags: tags
    sku: {
      name: 'Standard_B1ms'
      tier: 'Burstable'
    }
    storage: {
      storageSizeGB: 32
    }
    version: '14' // 14 is the latest supported version with 15 Coming Soon
    administratorLogin: postgresUser
    administratorLoginPassword: postgresPassword
    databaseNames: [databaseName]
    allowAzureIPsFirewall: true
  }
}

module keyVaultSecrets '../core/security/keyvault-secret.bicep' = {
  name: 'keyvault-secret-AZURE-POSTGRES-CONNECTION-STRING'
  scope: resourceGroup()
  params: {
    keyVaultName: keyVaultName
    name: 'AZURE-POSTGRES-CONN-STRING'
    secretValue: 'postgres://${postgresUser}:${postgresPassword}@${postgresServer.outputs.POSTGRES_DOMAIN_NAME}/${databaseName}'
  }
}

output endpoint string = postgresServer.outputs.POSTGRES_DOMAIN_NAME
output databaseName string = databaseName
output adminLogin string = postgresUser
output connectionString string = 'postgres://${postgresUser}:"VALUEINKEYVAULT"@${postgresServer.outputs.POSTGRES_DOMAIN_NAME}/${databaseName}'