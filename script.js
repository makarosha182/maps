// Элементы DOM
const adSlider = document.getElementById('adSlider');
const sliderThumb = document.getElementById('sliderThumb');
const shawarmaIcon = document.getElementById('shawarmaIcon');
const priceTag = document.getElementById('priceTag');
const dailyPrice = document.getElementById('dailyPrice');
const reachCount = document.getElementById('reachCount');
const paymentButton = document.getElementById('paymentButton');
const paymentModal = document.getElementById('paymentModal');
const closeModal = document.getElementById('closeModal');
const confirmPayment = document.getElementById('confirmPayment');
const totalAmount = document.getElementById('totalAmount');

// Данные для разных уровней рекламы
const adLevels = {
    1: { price: 50, reach: 500, dailyPrice: '50₽', totalPrice: '1 500₽' },
    2: { price: 100, reach: 1200, dailyPrice: '100₽', totalPrice: '3 000₽' },
    3: { price: 200, reach: 2500, dailyPrice: '200₽', totalPrice: '6 000₽' },
    4: { price: 350, reach: 5000, dailyPrice: '350₽', totalPrice: '10 500₽' },
    5: { price: 500, reach: 8000, dailyPrice: '500₽', totalPrice: '15 000₽' }
};

// Функция обновления маркера на статичной карте
function updateMapMarker(level) {
    console.log('Обновление маркера на уровень:', level);
    
    const data = adLevels[level];
    
    // Обновляем размер иконки на карте
    shawarmaIcon.className = `shawarma-icon size-${level}`;
    
    // Обновляем цену на карте
    priceTag.textContent = `${data.price}₽`;
    
    // Анимация иконки на карте
    shawarmaIcon.style.transform = 'scale(1.2)';
    setTimeout(() => {
        shawarmaIcon.style.transform = 'scale(1)';
    }, 200);
    
    // Анимация ценника
    priceTag.style.transform = 'scale(1.1)';
    setTimeout(() => {
        priceTag.style.transform = 'scale(1)';
    }, 200);
    
    console.log(`Маркер обновлен на уровень ${level}: ${data.price}₽`);
}

// Функция обновления интерфейса при изменении ползунка
function updateAdLevel(level) {
    const data = adLevels[level];
    
    // Обновляем информацию в карточке
    dailyPrice.textContent = data.dailyPrice;
    reachCount.textContent = `~${data.reach.toLocaleString()} человек`;
    
    // Обновляем общую стоимость в модальном окне
    totalAmount.textContent = data.totalPrice;
    
    // Обновляем маркер на статичной карте
    updateMapMarker(level);
}

// Функция обновления позиции иконки на ползунке
function updateSliderThumb() {
    const sliderValue = adSlider.value;
    const sliderWidth = adSlider.offsetWidth;
    const thumbWidth = sliderThumb.offsetWidth;
    
    // Рассчитываем позицию (с учетом размера thumb)
    const percentage = (sliderValue - 1) / (5 - 1); // от 0 до 1
    const position = percentage * (sliderWidth - thumbWidth);
    
    sliderThumb.style.left = `${position}px`;
    
    // Обновляем размер иконки на ползунке
    const thumbIcon = sliderThumb.querySelector('.thumb-icon');
    const iconSizes = ['16px', '18px', '20px', '22px', '24px'];
    thumbIcon.style.fontSize = iconSizes[sliderValue - 1];
}

// Обработчик изменения ползунка
adSlider.addEventListener('input', function() {
    const level = parseInt(this.value);
    console.log('Ползунок изменен на уровень:', level); // Отладка
    updateAdLevel(level);
    updateSliderThumb();
    
    // Дополнительная визуальная обратная связь
    const sliderWrapper = this.parentElement;
    sliderWrapper.style.transform = 'scale(1.02)';
    setTimeout(() => {
        sliderWrapper.style.transform = 'scale(1)';
    }, 150);
});

// Функция инициализации статичной карты
function initStaticMap() {
    console.log('Инициализация статичной карты');
    
    // Устанавливаем начальный уровень
    updateAdLevel(1);
    
    console.log('Статичная карта готова');
}

// Обработчик загрузки страницы
window.addEventListener('load', function() {
    updateSliderThumb();
    initStaticMap();
});

// Обработчик изменения размера окна
window.addEventListener('resize', function() {
    updateSliderThumb();
});

// Обработчики модального окна
paymentButton.addEventListener('click', function() {
    paymentModal.classList.add('active');
    document.body.style.overflow = 'hidden';
});

closeModal.addEventListener('click', function() {
    paymentModal.classList.remove('active');
    document.body.style.overflow = 'auto';
});

// Закрытие модального окна при клике вне его
paymentModal.addEventListener('click', function(e) {
    if (e.target === paymentModal) {
        paymentModal.classList.remove('active');
        document.body.style.overflow = 'auto';
    }
});

// Обработчик подтверждения оплаты
confirmPayment.addEventListener('click', function() {
    // Показываем анимацию загрузки
    this.innerHTML = '<span style="animation: spin 1s linear infinite;">⏳</span> Обработка...';
    this.disabled = true;
    
    // Имитируем процесс оплаты
    setTimeout(() => {
        this.innerHTML = '✅ Оплата успешна!';
        this.style.background = 'linear-gradient(135deg, #00b894, #00a085)';
        
        setTimeout(() => {
            // Показываем уведомление об успешной оплате
            showSuccessNotification();
            
            // Анимация на карте при успешной оплате
            if (shawarmaIcon && priceTag) {
                // Эффект "взрыва" успеха
                shawarmaIcon.style.transform = 'scale(1.5)';
                shawarmaIcon.style.filter = 'drop-shadow(0 0 20px #00b894)';
                shawarmaIcon.style.transition = 'all 0.5s ease';
                
                priceTag.style.background = '#00b894';
                priceTag.style.transform = 'scale(1.2)';
                priceTag.style.transition = 'all 0.5s ease';
                
                setTimeout(() => {
                    shawarmaIcon.style.transform = 'scale(1)';
                    shawarmaIcon.style.filter = 'drop-shadow(0 4px 8px rgba(0, 0, 0, 0.3))';
                    
                    priceTag.style.background = '#ff6b6b';
                    priceTag.style.transform = 'scale(1)';
                }, 1000);
            }
            
            // Закрываем модальное окно
            paymentModal.classList.remove('active');
            document.body.style.overflow = 'auto';
            
            // Сбрасываем кнопку
            this.innerHTML = 'Подтвердить оплату';
            this.disabled = false;
            this.style.background = 'linear-gradient(135deg, #00b894, #00a085)';
        }, 1500);
    }, 2000);
});

// Функция показа уведомления об успешной оплате
function showSuccessNotification() {
    const notification = document.createElement('div');
    notification.innerHTML = `
        <div style="
            position: fixed;
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: linear-gradient(135deg, #00b894, #00a085);
            color: white;
            padding: 15px 20px;
            border-radius: 12px;
            box-shadow: 0 8px 25px rgba(0, 184, 148, 0.4);
            z-index: 10000;
            font-weight: 600;
            animation: slideDown 0.3s ease;
        ">
            🎉 Реклама активирована! Ваш ларек теперь более заметен на карте.
        </div>
    `;
    
    document.body.appendChild(notification);
    
    // Добавляем CSS анимацию
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideDown {
            from { transform: translateX(-50%) translateY(-100%); opacity: 0; }
            to { transform: translateX(-50%) translateY(0); opacity: 1; }
        }
        @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }
    `;
    document.head.appendChild(style);
    
    // Убираем уведомление через 4 секунды
    setTimeout(() => {
        notification.style.animation = 'slideUp 0.3s ease forwards';
        setTimeout(() => {
            document.body.removeChild(notification);
            document.head.removeChild(style);
        }, 300);
    }, 4000);
}

// Дополнительные эффекты при наведении на иконку на карте
shawarmaIcon.addEventListener('mouseenter', function() {
    this.style.transform = 'scale(1.1) rotate(10deg)';
});

shawarmaIcon.addEventListener('mouseleave', function() {
    this.style.transform = 'scale(1) rotate(0deg)';
});

// Эффект пульсации для кнопки оплаты
let pulseInterval;
paymentButton.addEventListener('mouseenter', function() {
    pulseInterval = setInterval(() => {
        this.style.transform = 'scale(1.02)';
        setTimeout(() => {
            this.style.transform = 'scale(1)';
        }, 100);
    }, 1000);
});

paymentButton.addEventListener('mouseleave', function() {
    clearInterval(pulseInterval);
    this.style.transform = 'scale(1)';
});

// Инициализация приложения
document.addEventListener('DOMContentLoaded', function() {
    // Добавляем плавное появление элементов
    const elements = document.querySelectorAll('.map-container, .control-card');
    elements.forEach((el, index) => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
            el.style.opacity = '1';
            el.style.transform = 'translateY(0)';
        }, index * 200);
    });
}); 