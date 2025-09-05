# 🌯 Яндекс Карты - Размещение рекламы (Rails)

## 🚀 Развертывание на Rails

### 1. Установка зависимостей

```bash
# Установка Ruby (если нет)
brew install ruby

# Установка Rails
gem install rails

# Установка bundler
gem install bundler

# Установка зависимостей проекта
bundle install
```

### 2. Настройка базы данных

```bash
# Создание и настройка базы данных
rails db:create
rails db:migrate
rails db:seed
```

### 3. Запуск сервера

```bash
# Development сервер
rails server

# Production сервер
RAILS_ENV=production rails server
```

### 4. Деплой на Heroku

```bash
# Установка Heroku CLI
brew install heroku/brew/heroku

# Логин в Heroku
heroku login

# Создание приложения
heroku create yandex-maps-ads

# Установка Ruby buildpack
heroku buildpacks:set heroku/ruby

# Деплой
git push heroku main

# Миграции на Heroku
heroku run rails db:migrate
```

### 5. Деплой на Railway

```bash
# Установка Railway CLI
npm install -g @railway/cli

# Логин в Railway
railway login

# Инициализация проекта
railway init

# Деплой
railway up
```

## 📱 API Endpoints

### Основные маршруты
- `GET /` - Главная страница с картой
- `POST /ads/:id/purchase` - Покупка рекламы
- `GET /api/v1/ads` - API для мобильного приложения
- `POST /api/v1/ads/:id/purchase` - API покупки

### Пример API запроса

```javascript
// Покупка рекламы
fetch('/api/v1/ads/1/purchase', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRF-Token': document.querySelector('[name="csrf-token"]').content
  },
  body: JSON.stringify({
    level: 5,
    organization_id: 1,
    duration: 30
  })
})
.then(response => response.json())
.then(data => console.log(data));
```

## 🛠 Технологии

- **Backend**: Ruby on Rails 7.0
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **База данных**: SQLite (development), PostgreSQL (production)
- **Деплой**: Heroku, Railway, DigitalOcean

## 📝 Модели данных

```ruby
# app/models/organization.rb
class Organization < ApplicationRecord
  has_many :ads
  
  validates :name, presence: true
  validates :address, presence: true
  validates :rating, inclusion: { in: 0.0..5.0 }
end

# app/models/ad.rb
class Ad < ApplicationRecord
  belongs_to :organization
  
  validates :level, inclusion: { in: 1..5 }
  validates :price, presence: true
  validates :status, inclusion: { in: %w[active inactive expired] }
end
```

## 🔧 Настройки окружения

```bash
# .env файл для development
RAILS_ENV=development
SECRET_KEY_BASE=your_secret_key
DATABASE_URL=sqlite3:db/development.sqlite3

# .env файл для production
RAILS_ENV=production
SECRET_KEY_BASE=production_secret_key
DATABASE_URL=postgresql://user:password@localhost/yandex_maps_ads_production
```

## 📊 Мониторинг

- Логи: `tail -f log/development.log`
- Консоль: `rails console`
- Тесты: `rails test`
- Coverage: `rails test:coverage`
