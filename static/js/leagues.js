// // var leagues = []
// $(".league-name").each(function(){
//     let league_name = $(this).text()
//     let league = db.collection("leagues").doc(league_name).get()
//     let email = $("#hidden-email").text().split("@")[0]
//     league.then(league_data=>{
//         let this_user = league_data.data()[email]
//         console.log(this_user)
//         $(this).parent().append(
//             `<td>${this_user.name}</td>
//             <td>Head to head</td>
//             <td>0-0-0</td>
//             `
//         )
//     })
// })
// // console.log(leagues)

$(".home-table").on("click",".ln",function(){
    let ln = $(this).text();
    let h_email = $("#h-email").text()
    console.log(ln)
    db.collection("users").doc(h_email).update({"current_league": ln}).then(
        res=>{location.reload()}
    )
})

$("#join-lg").submit(event=>{
    event.preventDefault()
    var h_email = $("#h-email").text()
    console.log(h_email)
    let str = $("#lg-name").val()
    console.log(str)
    var lns = []
    db.collection("leagues").get().then(res=>{
        var docs = res.docs
        docs.forEach(doc=>{
            lns.push(doc.id)
        })
        console.log(lns)
        if(lns.includes(str)){
            db.collection("users").doc(h_email).get().then(res=>{
            let your_leagues = res.data()["leagues"]
            if(!your_leagues.includes(str)){
                console.log("found it")
                axios.post("/leagues",{"ln":str})
                window.location = "/main"}
            else{
                console.log("You are already in this league!")
                $(".alert-content").append("You are already in this league!")
                $(".alert-ok").append(`<button id='ok'>Ok</button>`)
                $(".alert").removeClass("alert-hide")
            }})}
        else{
            console.log("not found")
            $(".alert-content").append("League Not Found")
            $(".alert-ok").append(`<button id='ok'>Ok</button>`)
            $(".alert").removeClass("alert-hide")
        }
    })})

    $(".alert").on("click",".alert-ok>button",function(){
        $(".alert").addClass("alert-hide")
        $(".alert-content").empty()
        $(".alert-ok").empty()
    })