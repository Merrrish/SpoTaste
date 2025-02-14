document.addEventListener("DOMContentLoaded", function () {
    // Загружаем контент для первой вкладки (например, "statistics") при загрузке страницы
    loadContent('statistics');
});

function loadContent(tab) {
    const contentDiv = document.getElementById("content");

    // Показываем, что идет загрузка
    contentDiv.innerHTML = '<div class="text2">Loading...</div>';

    axios.get(`/${tab}?fragment=true`)
        .then(response => {
            contentDiv.innerHTML = response.data; // Вставляем новый контент
        })
        .catch(error => {
            console.error("Error loading content:", error);
            contentDiv.innerHTML = '<div class="text2">Error loading content. Please try again.</div>';
        });
}

let currentTab = 'statistics';  // Текущая активная вкладка
let currentTimePeriod = 'short_term';  // Текущий временной диапазон

function changeTimePeriod(timePeriod) {
    currentTimePeriod = timePeriod;
    loadContent(currentTab);  // Обновляем текущую вкладку
}

function loadContent(tab) {
    currentTab = tab;
    const contentDiv = document.getElementById("content");

    // Показываем, что идет загрузка
    contentDiv.innerHTML = '<div class="text2">Loading...</div>';

    // Отправляем запрос на сервер с указанием временного диапазона
    axios.get(`/${tab}?fragment=true&time_period=${currentTimePeriod}`)
        .then(response => {
            contentDiv.innerHTML = response.data; // Вставляем новый контент
        })
        .catch(error => {
            console.error("Error loading content:", error);
            contentDiv.innerHTML = '<div class="text2">Error loading content. Please try again.</div>';
        });
}
