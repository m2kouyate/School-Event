/* ... (event_list) ... */

document.addEventListener('DOMContentLoaded', (event) => {
    const itemsPerPage = 10;
    let currentIndex = 10;
    let showOldEvents = false;

    const eventItems = document.querySelectorAll('.event-item');
    const showMoreBtn = document.getElementById('show-more-btn');
    const toggleEventsBtn = document.getElementById('toggle-events-btn');

    let oldEvents = [];
    let currentEvents = [];
    const now = new Date();
    now.setHours(0, 0, 0, 0);

    eventItems.forEach(item => {
        const eventDate = new Date(item.getAttribute('data-date'));
        if (eventDate < now) {
            oldEvents.push(item);
        } else {
            currentEvents.push(item);
        }
        item.style.display = 'none';
    });

    function showEvents(events) {
        for (let i = 0; i < Math.min(currentIndex, events.length); i++) {
            events[i].style.display = '';
        }
        showMoreBtn.style.display = currentIndex < events.length ? '' : 'none';
    }

    function updateVisibility() {
        eventItems.forEach(item => item.style.display = 'none');
        if (showOldEvents) {
            showEvents(oldEvents);
        } else {
            showEvents(currentEvents);
        }
    }

    showMoreBtn.addEventListener('click', () => {
        currentIndex += itemsPerPage;
        updateVisibility();
    });

    toggleEventsBtn.addEventListener('click', () => {
        showOldEvents = !showOldEvents;
        toggleEventsBtn.textContent = showOldEvents ? 'Show Current Events' : 'Show Old Events';
        currentIndex = itemsPerPage;
        updateVisibility();
    });

    updateVisibility();
});

/* ... (event_detail) ... */

document.addEventListener('DOMContentLoaded', (event) => {
    const imageLinks = document.querySelectorAll('.event-images-container a');
    const showMoreImagesBtn = document.createElement('button');
    showMoreImagesBtn.textContent = "Show More";
    showMoreImagesBtn.classList.add('show-more-images-btn');
    let currentIndex = 9;

    imageLinks.forEach((link, index) => {
        if (index >= currentIndex) {
            link.style.display = 'none';
        }
    });

    showMoreImagesBtn.addEventListener('click', () => {
        let maxIndex = Math.min(currentIndex + 9, imageLinks.length);
        for (let i = currentIndex; i < maxIndex; i++) {
            imageLinks[i].style.display = 'inline-block';
        }
        currentIndex = maxIndex;

        if (currentIndex >= imageLinks.length) {
            showMoreImagesBtn.style.display = 'none';
        }
    });

    if (imageLinks.length > 9) {
        document.querySelector('.event-images-container').after(showMoreImagesBtn);
    }
});

