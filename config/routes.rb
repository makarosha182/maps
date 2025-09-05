Rails.application.routes.draw do
  root 'ads#index'
  
  resources :ads, only: [:index, :show] do
    member do
      post :purchase
    end
  end
  
  # API routes для мобильного приложения
  namespace :api do
    namespace :v1 do
      resources :ads do
        member do
          post :purchase
          get :analytics
        end
      end
    end
  end
end
