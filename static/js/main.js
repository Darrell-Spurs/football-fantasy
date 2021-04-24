if ('serviceWorker' in navigator) {
    navigator.serviceWorker
    .register('/sw.js',{"scope":"/"})
    .then(function(registration) {
        console.log('Service Worker Registered!',registration.scope);
        return registration;
    })
    .catch(function(err) {
        console.error('Unable to register service worker.', err);
    });
}