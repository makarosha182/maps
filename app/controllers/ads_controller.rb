class AdsController < ApplicationController
  before_action :set_ad, only: [:show, :purchase]
  
  def index
    # Главная страница с картой и формой размещения рекламы
    @organization = {
      name: 'Ларек с шаурмой',
      address: 'ул. Тверская, 15',
      rating: 3.4,
      emoji: '🌯'
    }
    
    @ad_levels = {
      1 => { price: 50, reach: 500, daily_price: '50₽', total_price: '1 500₽' },
      2 => { price: 100, reach: 1200, daily_price: '100₽', total_price: '3 000₽' },
      3 => { price: 200, reach: 2500, daily_price: '200₽', total_price: '6 000₽' },
      4 => { price: 350, reach: 5000, daily_price: '350₽', total_price: '10 500₽' },
      5 => { price: 500, reach: 8000, daily_price: '500₽', total_price: '15 000₽' }
    }
    
    render 'index'
  end
  
  def show
    # Страница конкретной рекламы
  end
  
  def purchase
    # Обработка покупки рекламы
    level = params[:level].to_i
    
    if level.between?(1, 5)
      # Здесь будет логика оплаты
      flash[:success] = 'Реклама успешно активирована! Ваш ларек теперь более заметен на карте.'
      render json: { 
        status: 'success', 
        message: 'Оплата прошла успешно',
        level: level 
      }
    else
      render json: { 
        status: 'error', 
        message: 'Неверный уровень рекламы' 
      }, status: :bad_request
    end
  end
  
  private
  
  def set_ad
    @ad = params[:id] # В реальном приложении это будет модель
  end
  
  def ad_params
    params.require(:ad).permit(:level, :organization_id, :duration)
  end
end
