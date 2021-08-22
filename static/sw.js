const CACHE_NAME = 'static-cache-0.1.37'
const DYNAMIC_CACHE_NAME = 'dynamic-cache-0.1.37'
const FILES_TO_CACHE=[
    //routes
    "/",
    "/offline",
    // //icons
    // "/static/favicon.ico",
    "/static/manifest.json",
    "/static/images/icon_92.png",
    "/static/images/icon_96.png",
    "/static/images/icon_120.png",
    "/static/images/icon_152.png",
    "/static/images/icon_167.png",
    "/static/images/icon_180.png",
    "/static/images/icon_192.png",
    "/static/images/icon_512.png",
    "/static/images/background.jpg",
    "/static/fontawesome/plus-circle-solid.png",
    // //js
    "/static/js/main.js",
    "/static/js/roster.js",
    "/static/js/transactions.js",
    "/static/js/user.js",
    // //templates and stylesheets
    "/static/templates/module.html",
    "/static/stylesheets/module.css",
    "/static/templates/signup.html",
    "/static/stats/templates/roster.html",
    "/static/stats/stylesheets/roster.css"
]

//cache size limit function
const limitCacheSize = (name, size) => {
    caches.open(name).then(cache => {
      cache.keys().then(keys => {
        if(keys.length > size){
          cache.delete(keys[0]).then(limitCacheSize(name, size));
        }
      });
    });
  };

//Install event
self.addEventListener('install',(evt)=>{
    console.log('[Service Worker]: Install');
    evt.waitUntil(
        caches.open(CACHE_NAME)
        .then((cache)=>{
            console.log('[Service Worker]: Pre-caching offline page');
            cache.addAll(FILES_TO_CACHE)
        })
        .catch((err)=>{
            console.error('[Cache add error]',err)
        })
    );
    self.skipWaiting()
});


self.addEventListener("activate",(evt)=>{
    console.log('[Service Worker] Activate')
    evt.waitUntil(
        caches.keys().then((keyList)=>{
            return Promise.all(keyList
                .filter(key => key !== CACHE_NAME && key !== DYNAMIC_CACHE_NAME)
                .map(key => caches.delete(key))
            )
        }));
    self.clients.claim()
});

// // Fetch event
// self.addEventListener('fetch', (event) =>{
//     console.log("[From Service Worker]", event)
//     //Make sure not to cache the response that's from firestore api 
//     if(event.request.url.indexOf('firestore.googleapis.com')===-1){
//         event.respondWith(
//             caches.match(event.request).then(cacheRes=>{
//                 return cacheRes || fetch(event.request).then(
//                     fetchRes=>{
//                         caches.open(DYNAMIC_CACHE_NAME).then(cache=>{
//                             cache.put(event.request.url, fetchRes.clone())
//                             limitCacheSize(DYNAMIC_CACHE_NAME,100)
//                             return fetchRes
//                         })
//                     }
//                 )
//             }).catch(()=>{
//                 if(event.request.url.indexOf(".html")>-1){
//                     return caches.match("/offline")}
//                 }
//             ))
//         }
//     })

function nonexistance(string,target){
    var good = 1;
    target.forEach(element => {
        if(string.indexOf(element)!==-1){
            good = 0;
        }
    });
    return good;
}

// Fetch event
self.addEventListener('fetch', (event) =>{
    console.log("[From Service Worker]", event)
    //Make sure not to cache the response that's from firestore api 
    event.respondWith(
        caches.open(DYNAMIC_CACHE_NAME).then(function(cache){
            return fetch(event.request).then(function(response){
                if(nonexistance(event.request.url,["asdbfbb"])){
                    if(!(event.request.method=="POST")){
                        cache.put(event.request,response.clone())
                    }
                }
                return response
            })
        })
    )})