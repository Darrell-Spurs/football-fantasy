
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

//cats for this league
var cats = []

// roster for this user
var rosters = []

// get the selected league
cur_league = info["current_league"]

// get today and this season
var season = "EPL2021-22"
// var season = "Premier League 2021"
var day = new Date()
var tdate = `${day.getUTCFullYear().toString()}-${(day.getUTCMonth()+1).toString().padStart(2,"0")}-${day.getUTCDate().toString().padStart(2,"0")}`

var abbr = {"Adds":"Adds","assists":"AST","blocks":"BLK","conceded":"CON",
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

function cat_to_abbr(list){
    let r_list = []
    list.forEach(elem=>{
        r_list.push(abbr[elem])
    })
    return r_list
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

function sort_a(arr){
    arr = arr.filter(elem=> elem.includes("MD"))
    let to_sort = []
    arr.forEach(md=>{
        to_sort.push(parseInt(md.replace("MD","")))
    })
    
    var temp = 0;
    for(var j=0;j<to_sort.length;j+=1){
        for(var i=0;i<to_sort.length-j;i+=1){
            if(to_sort[i]>to_sort[i-1]){
                temp = to_sort[i];
                to_sort[i] = to_sort[i-1];
                to_sort[i-1] = temp
            }
        }
    }
    for(var j=0;j<to_sort.length;j+=1){
        to_sort[j] = "MD"+to_sort[j].toString()
    }
    return to_sort
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



//get player (render players)
function get_players(){
    // create json for today's stats
    var stat_total = {}
    // get current user
    db.collection("leagues").doc(cur_league).get().then(function(res){
        var user_roster = res.data()[info["processed_email"]]["roster"]
        //render categories
        cats = res.data()["INFO"]["rosters"]
        cats.forEach(cat=>{stat_total[cat]=0})
        cats.unshift("Rank")
        cats.unshift("Pos")
        renderCats(cat_to_abbr(cats))
        return user_roster
    }).then((user_roster)=>{
    // set rosters to the fetched roster
    rosters = user_roster
    db.collection(season).get().then(res=>{
        res.forEach(doc=>{
            main_data[doc.id.toString()]=doc.data()
        })
        console.log(main_data)
        //iterate through user's players
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
            name.setAttribute("colspan",(cats.length-2).toString())
            name.innerHTML += `<b>${p_name["INFO"]["name"]}</b> - ${p_name["INFO"]["team"]}`
            
            //match row
            let match_row = roster.insertRow(-1)
            if(tdate in p_name){
                let cell = match_row.insertCell(-1)
                cell.setAttribute("class","roster-match")
                cell.setAttribute("colspan",(cats.length-1).toString())
                let status = sub_to_status(p_name[tdate]["sub"])
                cell.innerHTML += `<span class="${status}">${status}</span> ${p_name[tdate]["home"]} vs ${p_name[tdate]["away"]}`
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
            if(tdate in p_name){
                cats.slice(2).forEach(cat=>{
                    let cell = stats_row.insertCell(-1)
                    cell.innerHTML += p_name[tdate][cat]
                    stat_total[cat]+= p_name[tdate][cat]
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
        }

// add date options
function add_dates(){
    $("#now-date").append(`${tdate}`)
    // db.collection('fixtures').onSnapshot((snapshot)=>{
    //     console.log(snapshot)
    //     snapshot.docChanges().forEach(change=>{
    //         change.doc.data()['dates'].forEach(date=>{
    //         $("#sel-date").append(`<option>${date}</option>`)
    //         })
    //     })   
    // })
    
}

// click on player to expand player card
$(".roster-table").on("click",".main-row",function(){
    let this_id = $(this).attr("id")
    let this_data = main_data[this_id]
    console.log(this_data)
    $(".popup-content").removeClass("pop-hide")
    $(".popup-box").removeClass("box-hide")

    $(".popup-content").append
    (`
    <div class="popup-inner">
    <div class="pop-name">${this_data["INFO"]["name"]}</div>
    <div class="pop-info">
    <span>F - ${this_data["INFO"]["team"]} / ${this_data["INFO"]["nationality"]}<br>
    Owner: Free Agent 
    <button class="pop-tab" id="GL" p_id="${this_id}">Game Logs</button>
    <button class="pop-tab" id="OVV" p_id="${this_id}">Overview</button></span>
    <img div class="player_photo2" src="https://media.api-sports.io/football/players/${this_id}.png"></div>
    <hr>
    <div class="pop-stats">
    <table class="pop-table"><thead><tr class="pop-tr">
    </tr></thead></table>
    </div>
    <hr id="bottom-hr">
    <div class="pop-end"><button pname="${this_data["INFO"]["full_name"]}" id="fa-${this_id}" class="player-ctrl FA">Add Player</button></div>
    </div>
    `)

    // select pop stats and add a row of stat titles
    $(".pop-tr").append(`<td>MIN</td>`)
    cats.forEach((cat)=>{
        if(cat!="Pos" && cat!="Rank"){
            $(".pop-tr").append(
                `<td>${abbr[cat]}</td>`)
        }
    })

    // check if it is a MD stats, if it is, add into the array
    let keys = Object.keys(this_data)
    keys = sort_a(keys)
    keys.forEach(key=>{
    if(key.includes("MD")){
        // add a row to stat table with MD name as id
        // add game matchup
        if(this_data[key]["team"]==this_data[key]["away"]){
            $(".pop-table").append(`<tr class="md"><td colspan="7" class="pop-matchup"><span class='${sub_to_status(this_data[key]["status"])}'>${sub_to_status(this_data[key]["status"])}</span>
            Matchday ${key.slice(2)} @ ${this_data[key]["home"]}</td></tr>`)
        }else{
            $(".pop-table").append(`<tr class="md"><td colspan="7" class="pop-matchup"><span class='${sub_to_status(this_data[key]["status"])}'>${sub_to_status(this_data[key]["status"])}</span>
            Matchday ${key.slice(2)} vs. ${this_data[key]["away"]}</td></tr>`)
        }
        $(".pop-table").append(
            `<tr id="${key}"></tr>`)
        $(`#${key}`).append(`<td>${this_data[key]["minutes"]}</td>`)   
        cats.forEach(cat=>{
            if(cat!="Pos" && cat!="Rank"){
                $(`#${key}`).append(`<td>${this_data[key][cat]}</td>`)   
            }})
    }})
})

// click on empty space to hide the hover player info
$(".popup-box").on("click",function(event){
    let targ = event.target.className
    if(targ=="popup-box"){
        $(".popup-content").addClass("pop-hide")
        $(".popup-box").addClass("box-hide")
        $(".popup-content").empty()
    }
})

//switch tab to overview while clicking on tab buttons
$(".popup-box").on("click","#OVV",function(){
    let this_id = $(this).attr("p_id")
    let this_data = main_data[this_id]
    $(".pop-table").empty()
    $(".pop-table").append(`<thead><tr class="pop-tr">
    </tr></thead>`)
    $(".pop-tr").append(`<td>RK</td>`)
    $(".pop-tr").append(`<td>MIN</td>`)
    cats.forEach((cat)=>{
        if(cat!="Pos" && cat!="Rank"){
            $(".pop-tr").append(
                `<td>${abbr[cat]}</td>`)
        }
    })
    // a list for ovv stat titles
    let ovvs = ["Last3","Last3A","Last5","Last5A",
    "Last10","Last10A","Season","SeasonA"]
    let ovv_to_row_title = {
        "Last3":"Last 3 Matchdays Total",
        "Last3A":"Last 3 Matchdays Average",
        "Last5":"Last 5 Matchdays Total",
        "Last5A":"Last 5 Matchdays Average",
        "Last10":"Last 10 Matchdays Total",
        "Last10A":"Last 10 Matchdays Average",
        "Season":"Season Total",
        "SeasonA":"Season Average"
    }
    // ovv = overvall time period
    ovvs.forEach((ovv)=>{
        $(".pop-table").append(`
        <tr class="md"><td colspan="7" class="pop-matchup">${ovv_to_row_title[ovv]}</td></tr>`)
        $(".pop-table").append(
            `<tr id="${ovv}"></tr>`)
        $(`#${ovv}`).append(`<td>RK</td>`)   
        $(`#${ovv}`).append(`<td>${this_data[ovv]["minutes"]}</td>`)   
        cats.forEach(cat=>{
            if(cat!="Pos" && cat!="Rank"){
                $(`#${ovv}`).append(`<td>${this_data[ovv][cat]}</td>`)   
            }})
    })
})

//switch tab to game logs while clicking on tab buttons
$(".popup-box").on("click","#GL",function(){
    let this_id = $(this).attr("p_id")
    let this_data = main_data[this_id]
    console.log("this_data")
    $(".pop-table").empty()

    // add stat table header
    $(".pop-table").append(`<thead><tr class="pop-tr">
    </tr></thead>`)
    $(".pop-tr").append(`<td>MIN</td>`)
    cats.forEach((cat)=>{
        if(cat!="Pos" && cat!="Rank"){
            $(".pop-tr").append(
                `<td>${abbr[cat]}</td>`)
        }
    })

    //add stats for each md
    // check if it is a MD stats, if it is, add into the array
    let keys = Object.keys(this_data)
    keys = sort_a(keys)
    keys.forEach(key=>{
    if(key.includes("MD")){
        // add a row to stat table with MD name as id
        // add game matchup
        if(this_data[key]["team"]==this_data[key]["away"]){
            $(".pop-table").append(`<tr class="md"><td colspan="7" class="pop-matchup"><span class='${sub_to_status(this_data[key]["status"])}'>${sub_to_status(this_data[key]["status"])}</span>
            Matchday ${key.slice(2)} @ ${this_data[key]["home"]}</td></tr>`)
        }else{
            $(".pop-table").append(`<tr class="md"><td colspan="7" class="pop-matchup"><span class='${sub_to_status(this_data[key]["status"])}'>${sub_to_status(this_data[key]["status"])}</span>
            Matchday ${key.slice(2)} vs. ${this_data[key]["away"]}</td></tr>`)
        }
        $(".pop-table").append(
            `<tr id="${key}"></tr>`)
        $(`#${key}`).append(`<td>${this_data[key]["minutes"]}</td>`)   
        cats.forEach(cat=>{
            if(cat!="Pos" && cat!="Rank"){
                $(`#${key}`).append(`<td>${this_data[key][cat]}</td>`)   
            }})
    }})
})

// click add drop
$(".popup-box").on("click",".player-ctrl",function(){
    pid = $(this).attr("id").replace("fa-","")
    let pname = $(this).attr("pname")
    $(".alert-content").append(`Drop Player:<br>${pname}?`)
    $(".alert-ok").append(`<button id='yes' pid='${pid}' pname='${pname}'>Yes</button> <button id='no'>No</button>`)
    $(".alert").removeClass("alert-hide")
})

// click ok on popup
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

// click on date
$("#sel-date").on("click","button",function(){
    let clicked = $(this).text()
    if(clicked==">"){
        day.setDate(day.getDate() + 1)
    }
    else if(clicked=="<"){
        day.setDate(day.getDate() - 1)
    }
    
    // get new date
    tdate = `${day.getUTCFullYear().toString()}-${(day.getUTCMonth()+1).toString().padStart(2,"0")}-${day.getUTCDate().toString().padStart(2,"0")}`

    // update displyed date
    $("#now-date").empty()
    $("#now-date").append(tdate)

    // var for today's stats
    var stat_total = {}

    // set each cat as 0 as initialize
    cats.slice(2).forEach(cat=>{
        stat_total[cat] = 0
    })

    //empty roster field
    $(".roster").empty()
    rosters.forEach(id=>{
        p_name = main_data[parseInt(id)]
        
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
        name.setAttribute("colspan",(cats.length-1).toString())
        if(p_name["INFO"]["status"]!="active"){
            name.innerHTML += `<b>${p_name["INFO"]["name"]}</b> - ${p_name["INFO"]["team"]}
            <span class="inactive">${p_name["INFO"]["status"]}`
        }else{
            name.innerHTML += `<b>${p_name["INFO"]["name"]}</b> - ${p_name["INFO"]["team"]}`
        }    
        
        //match row
        let match_row = roster.insertRow(-1)
        if(tdate in p_name){
            let cell = match_row.insertCell(-1)
            cell.setAttribute("class","roster-match")
            cell.setAttribute("colspan",(cats.length-1).toString())
            let status = sub_to_status(p_name[tdate]["sub"])
            cell.innerHTML += `<span class="${status}">${status}</span> ${p_name[tdate]["home"]} vs ${p_name[tdate]["away"]}`
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
        if(tdate in p_name){
            cats.slice(2).forEach(cat=>{
                let cell = stats_row.insertCell(-1)
                cell.innerHTML += p_name[tdate][cat]
                stat_total[cat]+= p_name[tdate][cat]
            })}
        else{
            cats.slice(2).forEach(cat=>{
                let cell = stats_row.insertCell(-1)
                cell.setAttribute("class","player-stats")
                cell.innerHTML += "-"
            })}       
        })

    //update today's total stats
    $(".today-stats").empty()
    for(var cat in stat_total){
        cell = today_stats_tr.insertCell(-1)
        cell.innerHTML+=`${stat_total[cat]}`
    }
})
add_dates()
get_players()