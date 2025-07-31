// === ЭЛЕМЕНТЫ DOM ===
const adSlider = document.getElementById('adSlider');
const shawarmaIcon = document.getElementById('shawarmaIcon');
const priceTag = document.getElementById('priceTag');
const wowBadge = document.getElementById('wowBadge');
const dailyPrice = document.getElementById('dailyPrice');
const reachCount = document.getElementById('reachCount');
const paymentButton = document.getElementById('paymentButton');
const paymentModal = document.getElementById('paymentModal');
const closeModal = document.getElementById('closeModal');
const confirmPayment = document.getElementById('confirmPayment');
const totalAmount = document.getElementById('totalAmount');

// === ДАННЫЕ ДЛЯ УРОВНЕЙ РЕКЛАМЫ ===
const adLevels = {
    1: { price: 50, reach: 500, dailyPrice: '50₽', totalPrice: '1 500₽' },
    2: { price: 100, reach: 1200, dailyPrice: '100₽', totalPrice: '3 000₽' },
    3: { price: 200, reach: 2500, dailyPrice: '200₽', totalPrice: '6 000₽' },
    4: { price: 350, reach: 5000, dailyPrice: '350₽', totalPrice: '10 500₽' },
    5: { price: 500, reach: 8000, dailyPrice: '500₽', totalPrice: '15 000₽' }
};

// === УТИЛИТЫ ===
const isTouchDevice = () => 'ontouchstart' in window || navigator.maxTouchPoints > 0;

// === ОСНОВНЫЕ ФУНКЦИИ ===

// Обновление маркера на карте
function updateMapMarker(level) {
    const data = adLevels[level];
    
    // Обновляем размер иконки и добавляем вращение для максимального тарифа
    if (level === 5) {
        shawarmaIcon.className = `shawarma-icon size-${level}`;
        shawarmaIcon.style.animation = 'spin 1.5s linear infinite';
        wowBadge.style.display = 'block';
        console.log('Применена анимация вращения');
    } else {
        shawarmaIcon.className = `shawarma-icon size-${level}`;
        shawarmaIcon.style.animation = 'float 2s ease-in-out infinite';
        wowBadge.style.display = 'none';
        console.log('Применена обычная анимация');
    }
    
    // Обновляем цену
    priceTag.textContent = `${data.price}₽`;
    
    // Анимация для feedback
    if (!isTouchDevice()) {
        animateElement(shawarmaIcon, 'scale(1.2)', 200);
        animateElement(priceTag, 'scale(1.1)', 200);
        if (level === 5) {
            animateElement(wowBadge, 'scale(1.2)', 200);
        }
    }
}

// Обновление интерфейса
function updateAdLevel(level) {
    const data = adLevels[level];
    
    // Обновляем информацию
    dailyPrice.textContent = data.dailyPrice;
    reachCount.textContent = `~${data.reach.toLocaleString()} человек`;
    totalAmount.textContent = data.totalPrice;
    
    // Обновляем маркер
    updateMapMarker(level);
    
    // Объявляем изменение для screen readers
    announceToScreenReader(`Уровень рекламы ${level}. Стоимость ${data.dailyPrice} в день. Охват ${data.reach} человек.`);
}



// Анимация элемента
function animateElement(element, transform, duration = 200) {
    const originalTransform = element.style.transform;
    element.style.transform = transform;
    
    setTimeout(() => {
        element.style.transform = originalTransform;
    }, duration);
}

// Объявление для screen readers
function announceToScreenReader(message) {
    const announcement = document.createElement('div');
    announcement.setAttribute('aria-live', 'polite');
    announcement.setAttribute('aria-atomic', 'true');
    announcement.style.position = 'absolute';
    announcement.style.left = '-10000px';
    announcement.style.width = '1px';
    announcement.style.height = '1px';
    announcement.style.overflow = 'hidden';
    
    document.body.appendChild(announcement);
    announcement.textContent = message;
    
    setTimeout(() => {
        document.body.removeChild(announcement);
    }, 1000);
}

// === ОБРАБОТЧИКИ СОБЫТИЙ ===

// Ползунок
adSlider.addEventListener('input', function() {
    const level = parseInt(this.value);
    updateAdLevel(level);
    
    // Визуальная обратная связь
    if (!isTouchDevice()) {
        animateElement(this.parentElement, 'scale(1.02)', 150);
    }
});

// Модальное окно - открытие
paymentButton.addEventListener('click', function() {
    paymentModal.classList.add('active');
    paymentModal.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';
    
    // Фокус на кнопку закрытия для accessibility
    setTimeout(() => closeModal.focus(), 100);
});

// Модальное окно - закрытие
function closePaymentModal() {
    paymentModal.classList.remove('active');
    paymentModal.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = 'auto';
    
    // Возвращаем фокус на кнопку открытия
    paymentButton.focus();
}

closeModal.addEventListener('click', closePaymentModal);

// Закрытие по Escape
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape' && paymentModal.classList.contains('active')) {
        closePaymentModal();
    }
});

// Закрытие при клике вне модального окна
paymentModal.addEventListener('click', function(e) {
    if (e.target === paymentModal) {
        closePaymentModal();
    }
});

// Подтверждение оплаты
confirmPayment.addEventListener('click', function() {
    // Состояние загрузки
    this.innerHTML = '<span style="animation: spin 1s linear infinite;">⏳</span> Обработка...';
    this.disabled = true;
    this.setAttribute('aria-busy', 'true');
    
    // Имитация процесса оплаты
    setTimeout(() => {
        this.innerHTML = '✅ Оплата успешна!';
        this.style.background = 'var(--success-green)';
        this.setAttribute('aria-busy', 'false');
        
        setTimeout(() => {
            showSuccessNotification();
            animateSuccessOnMap();
            
            // Закрытие модального окна
            closePaymentModal();
            
            // Сброс кнопки
            setTimeout(() => {
                this.innerHTML = 'Подтвердить оплату';
                this.disabled = false;
                this.style.background = '';
            }, 1000);
            
        }, 1500);
    }, 2000);
});

// === АНИМАЦИИ И ЭФФЕКТЫ ===

// Анимация успеха на карте
function animateSuccessOnMap() {
    if (shawarmaIcon && priceTag) {
        // Эффект успеха
        shawarmaIcon.style.transform = 'scale(1.5)';
        shawarmaIcon.style.filter = 'drop-shadow(0 0 20px var(--success-green))';
        shawarmaIcon.style.transition = 'all 0.5s ease';
        
        priceTag.style.background = 'var(--success-green)';
        priceTag.style.transform = 'scale(1.2)';
        priceTag.style.transition = 'all 0.5s ease';
        
        // Анимация WOW-бейджа если он виден
        if (wowBadge.style.display === 'block') {
            wowBadge.style.background = 'linear-gradient(135deg, var(--success-green), #00a085)';
            wowBadge.style.transform = 'scale(1.3)';
            wowBadge.style.transition = 'all 0.5s ease';
        }
        
        setTimeout(() => {
            shawarmaIcon.style.transform = 'scale(1)';
            shawarmaIcon.style.filter = 'drop-shadow(0 4px 8px rgba(0, 0, 0, 0.3))';
            
            priceTag.style.background = 'var(--accent-red)';
            priceTag.style.transform = 'scale(1)';
            
            if (wowBadge.style.display === 'block') {
                wowBadge.style.background = 'linear-gradient(135deg, #ff6b6b, #ff5722)';
                wowBadge.style.transform = 'scale(1)';
            }
        }, 1000);
    }
}

// Уведомление об успехе
function showSuccessNotification() {
    const notification = document.createElement('div');
    notification.innerHTML = `
        <div style="
            position: fixed;
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: linear-gradient(135deg, var(--success-green), var(--success-green-dark));
            color: var(--bg-white);
            padding: var(--space-md) var(--space-lg);
            border-radius: var(--radius-md);
            box-shadow: var(--shadow-lg);
            z-index: 10000;
            font-weight: 600;
            animation: slideDown 0.3s ease;
            max-width: 90vw;
            text-align: center;
        ">
            🎉 Реклама активирована! Ваш ларек теперь более заметен на карте.
        </div>
    `;
    
    document.body.appendChild(notification);
    
    // CSS анимации
    if (!document.getElementById('notification-styles')) {
        const style = document.createElement('style');
        style.id = 'notification-styles';
        style.textContent = `
            @keyframes slideDown {
                from { transform: translateX(-50%) translateY(-100%); opacity: 0; }
                to { transform: translateX(-50%) translateY(0); opacity: 1; }
            }
            @keyframes slideUp {
                from { transform: translateX(-50%) translateY(0); opacity: 1; }
                to { transform: translateX(-50%) translateY(-100%); opacity: 0; }
            }
            @keyframes spin {
                from { transform: rotate(0deg); }
                to { transform: rotate(360deg); }
            }
        `;
        document.head.appendChild(style);
    }
    
    // Объявляем для screen readers
    announceToScreenReader('Оплата успешна! Реклама активирована.');
    
    // Убираем уведомление
    setTimeout(() => {
        notification.firstElementChild.style.animation = 'slideUp 0.3s ease forwards';
        setTimeout(() => {
            if (document.body.contains(notification)) {
                document.body.removeChild(notification);
            }
        }, 300);
    }, 4000);
}

// === ЭФФЕКТЫ ДЛЯ ДЕСКТОПА ===
if (!isTouchDevice()) {
    // Эффекты наведения на иконку карты
    shawarmaIcon.addEventListener('mouseenter', function() {
        this.style.transform = 'scale(1.1) rotate(10deg)';
    });

    shawarmaIcon.addEventListener('mouseleave', function() {
        this.style.transform = 'scale(1) rotate(0deg)';
    });

    // Пульсация кнопки оплаты
    let pulseInterval;
    paymentButton.addEventListener('mouseenter', function() {
        pulseInterval = setInterval(() => {
            animateElement(this, 'scale(1.02)', 100);
        }, 1000);
    });

    paymentButton.addEventListener('mouseleave', function() {
        clearInterval(pulseInterval);
        this.style.transform = 'scale(1)';
    });
}

// === ИНИЦИАЛИЗАЦИЯ ===

// Инициализация при загрузке
function initApp() {
    updateAdLevel(1);
    
    // Плавное появление элементов
    const elements = document.querySelectorAll('.organization-card');
    elements.forEach((el, index) => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            el.style.transition = 'opacity 0.6s cubic-bezier(0.4, 0, 0.2, 1), transform 0.6s cubic-bezier(0.4, 0, 0.2, 1)';
            el.style.opacity = '1';
            el.style.transform = 'translateY(0)';
        }, index * 200);
    });
}

// Обработчики загрузки и изменения размера
window.addEventListener('load', initApp);
document.addEventListener('DOMContentLoaded', initApp); 