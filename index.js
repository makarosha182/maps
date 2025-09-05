const express = require('express');
const path = require('path');
const app = express();
const PORT = process.env.PORT || 3000;

// Статические файлы
app.use(express.static('.'));

// Основной маршрут
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'index.html'));
});

// Все остальные маршруты тоже ведут на index.html (SPA)
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'index.html'));
});

app.listen(PORT, () => {
  console.log(`🌯 Яндекс Карты Реклама запущены на порту ${PORT}`);
  console.log(`🔗 Открыть: http://localhost:${PORT}`);
});
