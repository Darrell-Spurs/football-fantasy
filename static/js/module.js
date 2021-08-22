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