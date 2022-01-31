// document.querySelector("html")
$("#hide-menu").on("click",function(){
    $(".sidebar").addClass("hide")
})

$("#menu").on("click",function(){
    $(".sidebar").removeClass("hide")
})

// $(".alert").on("click",".alert-ok",function(){
//     $(".alert").addClass("alert-hide")
//     $(".alert-content").empty()
// })

// var wooah = {}
// db.collection("Premier League 2021").get().then(res=>{
//     res.forEach(doc=>{
//         wooah[doc.id.toString()]=doc.data()
//     })
//     console.log(wooah)
// })
