class ApplicationController < ActionController::Base
  protect_from_forgery with: :exception
  
  before_action :set_current_user
  
  private
  
  def set_current_user
    # Здесь будет логика аутентификации пользователя
    @current_user = nil
  end
  
  def authenticate_user!
    redirect_to root_path unless @current_user
  end
end
