//render roster list

// roster content field ref
const roster = document.querySelector(".roster-table").getElementsByTagName("tbody")[0]
// table header field ref
const cats_head_tr = document.querySelector(".stat-cats")
const today_cats_tr = document.querySelector(".today-cats")
const today_stats_tr = document.querySelector(".today-stats")
// all player from db
var main_data = {}

//get the hidden user data
var info = $("#user").text().replaceAll("\'","\"")
info = JSON.parse(info)
var cats = []
cur_league = info["current_league"]


const removeRoster = (id) =>{
    deleted = document.querySelectorAll(`tr[data-id=${id}]`)
    deleted.forEach(element => {
        element.remove()
    });
}

// add the header for the form
function renderCats(cats){
    // add cats row
    cats.forEach((cat)=>{
        let cell = cats_head_tr.insertCell(-1)

        if(cat=="Pos"||cat=="Rank"){
            cell.setAttribute("class","split")
            cell.innerHTML+=cat
        }
        else{
            let tcat = today_cats_tr.insertCell(-1)
            cell.setAttribute("class","else-split")
            cell.innerHTML+=cat
            tcat.setAttribute("class","else-split")
            tcat.innerHTML+=cat
        }
    })
}

//Get league name
function getLeague(){
    return "Premier League"
}

var rosters = []
// function getCats(){

// }

//set stats value to shown texts
function cat_to_abbr(list){
    let abbr = {"Pos":"Pos","assists":"AST","blocks":"BLK","conceded":"CON",
                "dribbles":"DRI","dribbles_won":"D-W",
                "duels":"DUE","duels_won":"2-W",
                "fouls":"FOU","fouls_drawn":"FOD",
                "goals":"GOA","interceptions":"INT",
                "key_passes":"KEP","minutes":"MIN",
                "offsides":"OFF","passes":"PAS",
                "Rank":"Rank","rating":"RAT",
                "red_cards":"RDC","saves":"SV",
                "shot_on_goals":"SOG","shots":"SHO",
                "tackles":"TAC","yellow_cards":"YLC"
                }
    let r_list = []
    list.forEach(elem=>{
        r_list.push(abbr[elem])
    })
    return r_list
}

//set player's status
function sub_to_status(sub){
    if(sub==="starting"){
        return "△"
    }
    else if(sub==="substitute"){
        return "✓"
    }
    else{
        return "✖"
    }
}


//offline data
db.enablePersistence()
    .catch(err=>{
        if(err.code == "failed-precondition"){
            // multiple tabs
            console.log("Persistence failed")
        }
        else if(err.code == "unimplemented"){
            //lack of browser support
            console.log("Persistence unavailable")
        }
    })


//get player

function get_players(){
    // create json for today's stats
    var stat_total = {}
    db.collection("leagues").doc(cur_league).get().then(function(res){
        var user_roster = res.data()[info["processed_email"]]["roster"]
        cats = res.data()["INFO"]["rosters"]
        cats.forEach(cat=>{stat_total[cat]=0})
        cats.unshift("Rank")
        cats.unshift("Pos")
        renderCats(cat_to_abbr(cats))
        return user_roster
    }).then((user_roster)=>{
    console.log(user_roster)
    db.collection('roster').onSnapshot((snapshot)=>{
        snapshot.docChanges().forEach(
            change=>{
                main_data = change.doc.data()
                console.log(main_data)
                user_roster.forEach(id=>{
                    p_name = main_data[parseInt(id)]
                    // renderRoster(p_name,id)
                    
                    //add player pos
                    let main_row = roster.insertRow(-1)
                    main_row.setAttribute("id",p_name["INFO"]["id"])
                    main_row.setAttribute("class","main-row")
                    let player_pos = main_row.insertCell(0)
                    player_pos.setAttribute("rowspan","2")
                    player_pos.setAttribute("class","player_pos")
                    player_pos.innerHTML += `<span>FW</span>`

                    //add player photo
                    let photo = main_row.insertCell(1)
                    photo.setAttribute("rowspan","2")
                    photo.setAttribute("class","player_photo")
                    photo.innerHTML += `<img src="${p_name["INFO"]["photo"]}">`
                    
                    // add player name/ team
                    let name = main_row.insertCell(2)
                    name.setAttribute("class","roster-info")
                    name.setAttribute("colspan","4")
                    name.innerHTML += `<b>${p_name["INFO"]["name"]}</b> - ${p_name["INFO"]["team"]}`
                    
                    //match row
                    let match_row = roster.insertRow(-1)
                    if("2021-04-10" in p_name){
                        let cell = match_row.insertCell(-1)
                        cell.setAttribute("class","roster-match")
                        cell.setAttribute("colspan",(cats.length-1).toString())
                        let status = sub_to_status(p_name["2021-04-10"]["sub"])
                        cell.innerHTML += `<span class="${status}">${status}</span> ${p_name["2021-04-10"]["home"]} vs ${p_name["2021-04-10"]["away"]}`
                        }
                    else{
                        let cell = match_row.insertCell(-1)
                        cell.setAttribute("class","roster-match")
                        cell.setAttribute("colspan",(cats.length-1).toString())
                        cell.innerHTML += "No Game"
                    }
                    
                    //stats row
                    let stats_row = roster.insertRow(-1)
                    stats_row.setAttribute("class","player-stats")
                    let rank = stats_row.insertCell(-1)
                    // cell.innerHTML += p_name[filter_time]["rank"]
                    let adds = stats_row.insertCell(-1) 
                    rank.innerHTML += "?"
                    if("2021-04-10" in p_name){
                        cats.slice(2).forEach(cat=>{
                            let cell = stats_row.insertCell(-1)
                            cell.innerHTML += p_name["2021-04-10"][cat]
                            stat_total[cat]+= p_name["2021-04-10"][cat]
                        })}
                    else{
                        cats.slice(2).forEach(cat=>{
                            let cell = stats_row.insertCell(-1)
                            cell.setAttribute("class","player-stats")
                            cell.innerHTML += "-"
                        })}       
            })
        })
        //after iteration of players, add stats total stats field
        console.log(stat_total)
        for(var cat in stat_total){
            cell = today_stats_tr.insertCell(-1)
            cell.innerHTML+=`${stat_total[cat]}`
        }
        })
        })  
    }

$(".roster-table").on("click",".main-row",function(){
    let this_id = $(this).attr("id")
    let this_data = main_data[this_id]
    console.log(this_data)
    $(".popup-content").removeClass("pop-hide")
    $(".popup-box").removeClass("box-hide")

    $(".popup-content").append
    (`
    <div class="popup-inner">
    <div class="pop-name">${this_data["INFO"]["full_name"]}</div>
    <div class="pop-info">
    <span>Forward<br>
    ${this_data["INFO"]["team"]} / ${this_data["INFO"]["nationality"]}<br>
    Owner: Free Agent </span>
    <img div class="player_photo2" src="https://media.api-sports.io/football/players/${this_id}.png"></div>
    <hr>
    <div class="pop-stats">Goal</div>
    <hr>
    <div class="pop-end"><button pname="${this_data["INFO"]["full_name"]}" id="fa-${this_id}" class="player-ctrl DP">DROP</button></div>
    </div>
    `)
})

$(".popup-box").on("click",function(event){
    let targ = event.target.className
    if(targ=="popup-box"){
        $(".popup-content").addClass("pop-hide")
        $(".popup-box").addClass("box-hide")
        $(".popup-content").empty()
    }
})

$(".popup-box").on("click",".player-ctrl",function(){
    pid = $(this).attr("id").replace("fa-","")
    let pname = $(this).attr("pname")
    $(".alert-content").append(`Drop Player:<br>${pname}?`)
    $(".alert-ok").append(`<button id='yes' pid='${pid}' pname='${pname}'>Yes</button> <button id='no'>No</button>`)
    $(".alert").removeClass("alert-hide")
})
$(".alert").on("click",".alert-ok>button",function(){
    let yid = $(this).attr("id")
    let pid = $(this).attr("pid")
    let pname = $(this).attr("pname")
    if(yid=="yes"){
        console.log("DROP",pid, cur_league)
        let p_email = `${info["processed_email"]}.roster`
        let to_db = {}
        to_db[`${p_email}`] = firebase.firestore.FieldValue.arrayRemove(pid)
        db.collection("leagues").doc(cur_league).update(to_db)
        $(".alert-content").empty()
        $(".alert-ok").empty()
        $(".alert-content").append(`Successfully Dropped:<br>${pname}!`)
        $(".alert-ok").append(`<button id="okk">OK</button>`)    
        $(`#${pid}`).next().remove()
        $(`#${pid}`).next().remove()
        $(`#${pid}`).remove()  
    }
    else{
        $(".alert").addClass("alert-hide")
        $(".alert-content").empty()
        $(".alert-ok").empty()
        $(".popup-content").addClass("pop-hide")
        $(".popup-box").addClass("box-hide")
        $(".popup-content").empty()
    }
})
get_players()


// add new player
// const add_form = document.querySelector(".add-form")
// add_form.addEventListener("submit",event=>{
//     event.preventDefault()
//     const name= add_form.name.value
//     const to_add = {
//         name: add_form.name.value,
//         league: add_form.league.value,
//     }
//     db.collection('roster').doc(name.replace(/ /,"_")).set(to_add)
    
//     add_form.reset()
// }) 

//delete player
// const roster_table = document.querySelector(".roster-table")
// roster_table.addEventListener('click',event=>{
//     console.log(event)
//     if(event.target.className=="cut"){
//         const id = event.target.getAttribute("id")
//         db.collection('roster').doc(id).delete()
//     }
// })



// $(".add_button").on("click",function(event){

// })