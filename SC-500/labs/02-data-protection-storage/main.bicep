// Lab: hardened storage account baseline (teaching template).
// Status: see docs/verification-matrix.md - compile result is recorded there. NOT deployed by the author to a live subscription.
@description('Globally unique name: 3-24 lowercase letters and numbers.')
@minLength(3)
@maxLength(24)
param storageAccountName string

param location string = resourceGroup().location

@description('Keep Disabled unless you have a private endpoint or a firewall rule for your own IP.')
@allowed([
  'Enabled'
  'Disabled'
])
param publicNetworkAccess string = 'Disabled'

resource storage 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: storageAccountName
  location: location
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  properties: {
    supportsHttpsTrafficOnly: true
    minimumTlsVersion: 'TLS1_2'
    allowBlobPublicAccess: false
    allowSharedKeyAccess: false
    defaultToOAuthAuthentication: true
    publicNetworkAccess: publicNetworkAccess
    networkAcls: {
      defaultAction: 'Deny'
      bypass: 'AzureServices'
    }
  }
}

resource blobService 'Microsoft.Storage/storageAccounts/blobServices@2023-05-01' = {
  parent: storage
  name: 'default'
  properties: {
    deleteRetentionPolicy: {
      enabled: true
      days: 7
    }
  }
}

output storageAccountId string = storage.id
