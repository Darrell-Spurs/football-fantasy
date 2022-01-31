var prizes = []
for(var i=1;i<=75;i++){
    prizes.push(i)
}
var this_shuffle = 0
function rand_int(){
    var a = prizes[Math.floor((Math.random()*1000000000)%prizes.length)]
    $(".bingo").empty()
    $(".bingo").append(`${a}`)
    this_shuffle = a
}

$(".bingo").on("click",function(){
    var audio = new Audio("/static/sounds/slot.wav")
    audio.play() 
    for(var i=0;i<43;i+=1){
        setTimeout(() => {rand_int()}, 100*i);
    }
    setTimeout(() => {
        var ind = prizes.indexOf(this_shuffle)
        prizes.splice(ind,1)
        $(".drawn").append(` ${this_shuffle}`)
    }, 4500);
})

