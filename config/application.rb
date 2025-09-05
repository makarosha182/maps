require_relative "boot"

require "rails/all"

Bundler.require(*Rails.groups)

module YandexMapsAds
  class Application < Rails::Application
    config.load_defaults 7.0
    
    # Настройки для API
    config.api_only = false
    
    # Настройки CORS для мобильного приложения
    config.middleware.insert_before 0, Rack::Cors do
      allow do
        origins '*'
        resource '*', headers: :any, methods: [:get, :post, :patch, :put, :delete, :options, :head]
      end
    end if defined?(Rack::Cors)
    
    # Настройки для статических файлов
    config.assets.compile = true
    config.assets.digest = true
    
    # Настройки безопасности
    config.force_ssl = false # Для development
  end
end
