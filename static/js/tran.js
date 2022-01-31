//render roster list

// roster content field ref
const roster = document.querySelector(".roster-table").getElementsByTagName("tbody")[0]
// table header field ref
const cats_head_tr = document.querySelector(".stat-cats")
// all player from db
var main_data = {}

// get today and this season
var day = new Date()
// var tdate = `${day.getUTCFullYear().toString()}-${(day.getUTCMonth()+1).toString().padStart(2,"0")}-${day.getUTCDate().toString().padStart(2,"0")}`
var tdate = "2021-08-21"
// var season = "Premier League 2021"
var season = "EPL2021-22"

// user info
var info = $("#user").text().replaceAll("\'","\"")
info = JSON.parse(info)

//all categories
var cats = []
//owned players
var owned = []
cur_league = info["current_league"]

const renderRoster = (data, id) =>{
    // const name = id.replace(/_/," ")
    console.log("Nope")
}

    //         <td><button class="cut" id="${id}">Del</button></td>


const removeRoster = (id) =>{
    deleted = document.querySelectorAll(`tr[data-id=${id}]`)
    deleted.forEach(element => {
        element.remove()
    });
}

function renderCats(cats){
    // add cats row
    cats.forEach((cat)=>{
        let cell = cats_head_tr.insertCell(-1)
        if(cat=="Adds"||cat=="Rank"){
            cell.setAttribute("class","split")
            cell.innerHTML+=cat
        }
        else{
            cell.setAttribute("class","else-split")
            cell.innerHTML+=cat
        }
    })
}

function getLeague(){
    return "Premier League"
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

var rosters = []
// function getCats(){

// }

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

function sub_to_status(sub){
    if(sub==="starting"){
        return "✓"
    }
    else if(sub==="sub"){
        return "△"
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

function get_players(){
     db.collection("leagues").doc(cur_league).get().then(function(res){
        cats = res.data()["INFO"]["rosters"]
        owned = res.data()["owned"]
        cats.unshift("Rank")
        cats.unshift("Adds")
        renderCats(cat_to_abbr(cats))
    }).then(()=>{
        db.collection(season).get().then(res=>{
            res.forEach(doc=>{
                main_data[doc.id.toString()]=doc.data()
            })
        console.log(main_data)
        for(var id in main_data){
            if(!owned.includes(id)){
            p_name = main_data[id]
            
            //add button, photo and name row
            let main_row = roster.insertRow(-1)
            let add_button = main_row.insertCell(0)
            add_button.setAttribute("rowspan","2")
            add_button.setAttribute("class","add_button")
            add_button.setAttribute("id",p_name["INFO"]["id"])
            add_button.innerHTML += `<img src="/static/fontawesome/plus-circle-solid.png">`
            let photo = main_row.insertCell(1)
            photo.setAttribute("rowspan","2")
            photo.setAttribute("class","player_photo")
            photo.innerHTML += `<img src="${p_name["INFO"]["photo"]}">`
            let name = main_row.insertCell(2)
            name.setAttribute("class","roster-info")
            name.setAttribute("colspan",(cats.length-2).toString())
            if(p_name["INFO"]["status"]!="active"){
                name.innerHTML += `<b>${p_name["INFO"]["name"]}</b> - ${p_name["INFO"]["team"]}
                <span class="inactive">${p_name["INFO"]["status"]}</span>`
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
            let cell = stats_row.insertCell(-1)
            // cell.innerHTML += p_name[filter_time]["rank"]
            cell.innerHTML += "?"
            let adds = stats_row.insertCell(-1) 
            if(tdate in p_name){
                cats.slice(2).forEach(cat=>{
                    let cell = stats_row.insertCell(-1)
                    cell.innerHTML += p_name[tdate][cat]
                })}
            else{
                cats.slice(2).forEach(cat=>{
                    let cell = stats_row.insertCell(-1)
                    cell.innerHTML += "-"
                })}       
        }}
    })
    })  
    }

// expand player card
$(".roster-table").on("click",".add_button",function(){
    let this_id = $(this).attr("id")
    let this_data = main_data[this_id]
    console.log(this_data)

    $(".popup-content").removeClass("pop-hide")
    $(".popup-box").removeClass("box-hide")

    $(".popup-content").append
    (`
    <div class="popup-inner">
    <div class="pop-name">${this_data["INFO"]["name"]}
    <div class="pop-info">
    <span>F - ${this_data["INFO"]["team"]} / ${this_data["INFO"]["nationality"]}<br>
    Owner: Free Agent 
    <button class="pop-tab" id="GL" p_id="${this_id}">Game Logs</button>
    <button class="pop-tab" id="OVV" p_id="${this_id}">Overview</button>
    </span>
    <img div class="player_photo2" src="https://media.api-sports.io/football/players/${this_id}.png"></div>
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
        if(cat!="Adds" && cat!="Rank"){
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
            if(cat!="Adds" && cat!="Rank"){
                $(`#${key}`).append(`<td>${this_data[key][cat]}</td>`)   
            }})
    }})
})

// hide player card while clicking outside
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
    console.log("this_data")
    $(".pop-table").empty()
    $(".pop-table").append(`<thead><tr class="pop-tr">
    </tr></thead>`)
    $(".pop-tr").append(`<td>RK</td>`)
    $(".pop-tr").append(`<td>MIN</td>`)
    cats.forEach((cat)=>{
        if(cat!="Adds" && cat!="Rank"){
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
            if(cat!="Adds" && cat!="Rank"){
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
        if(cat!="Adds" && cat!="Rank"){
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
            if(cat!="Adds" && cat!="Rank"){
                $(`#${key}`).append(`<td>${this_data[key][cat]}</td>`)   
            }})
    }})
})


// add/move player
$(".popup-box").on("click",".player-ctrl",function(){
    pid = $(this).attr("id").replace("fa-","")
    let pname = $(this).attr("pname")
    $(".alert-content").append(`Add Player:<br>${pname}?`)
    $(".alert-ok").append(`<button id='yes' pid='${pid}' pname='${pname}'>Yes</button> <button id='no'>No</button>`)
    $(".alert").removeClass("alert-hide")
})

// confirming player move
$(".alert").on("click",".alert-ok>button",function(){
    let yid = $(this).attr("id")
    let pid = $(this).attr("pid")
    let pname = $(this).attr("pname")
    if(yid=="yes"){
        let p_email = `${info["processed_email"]}.roster`
        let to_db = {}
        to_db[`${p_email}`] = firebase.firestore.FieldValue.arrayUnion(pid)
        to_db["owned"] = firebase.firestore.FieldValue.arrayUnion(pid)
        db.collection("leagues").doc(cur_league).update(to_db)
        $(".alert-content").empty()
        $(".alert-ok").empty()
        $(".alert-content").append(`Successfully Added:<br>${pname}!`)
        $(".alert-ok").append(`<button id="okk">OK</button>`) 
        //remove that player row()
        $(`#${pid}`).parent().next().remove()
        $(`#${pid}`).parent().next().remove()
        $(`#${pid}`).parent().remove()   
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

function sortTableSlow(n){
    var table, this_row, next_row, dir, switching, rows, shouldSwitch, switchCount = 0;
    table = document.getElementById("roster-table")
    switching = true
    dir = "des"
    console.log()
    while(switching){
        switching = false
        rows = table.rows
        for(var i=3;i<rows.length-3;i+=3){
            shouldSwitch = false
            this_row = rows[i].getElementsByTagName("TD")[n]
            next_row = rows[i+3].getElementsByTagName("TD")[n]
            var this_num, next_num
            if(this_row.innerHTML=="-"){this_num = -1}
            else{this_num = parseInt(this_row.innerHTML)}
            if(next_row.innerHTML=="-"){next_num = -1}
            else{next_num = parseInt(next_row.innerHTML)}
            if(dir=="des"){
                if(next_num>this_num){
                    shouldSwitch = true
                    break
                }
            }else if(dir=="asc"){
                if(next_num<this_num){
                    shouldSwitch = true
                    break
                }
            }
        }
        if(shouldSwitch){
            console.log("SWITCH")
            rows[i].parentNode.insertBefore(rows[i+1],rows[i-2])
            rows[i].parentNode.insertBefore(rows[i+2],rows[i-1])
            rows[i].parentNode.insertBefore(rows[i+3],rows[i])
            switching = true
            switchCount++
            break
        }else if(switchCount==0 && dir=="asc"){
            dir = "asc"
            switching = true
        }
    }
}

function sortTable(col){
    var data_array = []
    for(var i in main_data){
        data_array.push(main_data[i])
    }
    var swit = true
    var real = 0
    //temp
    //cat to full name
    while(swit){
        swit = false
        for(var i=0; i<data_array.length-1; i++){
            let cur_data, next_data
            if(data_array[i][tdate]==undefined){cur_data=-1
            }else{cur_data = data_array[i][tdate][col]}
            if(data_array[i+1][tdate]==undefined){next_data=-1
            }else{next_data = data_array[i+1][tdate][col]}
            if(cur_data<next_data){
                var temp = data_array[i+1]
                data_array[i+1] = data_array[i]
                data_array[i] = temp
                real++
            }
        }
        if(real){
        real = 0
        swit = true
        }
    }
    console.log("SORTED")
    return data_array
}

$(".stat-cats").on("click","td",function(){
    var this_cat = $(this).parent().children()
    var c;
    for(var i=0; i<this_cat.length; i++){
        this_cat[i].style.color = "black"
        if(this_cat[i].textContent==$(this).text()){
            c = i
        }
    }
    $(this).css("color","red")
    //find the full name of stat
    for(var key in abbr){
        if(abbr[key] == $(this).text())
        break
    }
    var sorted = sortTable(key)
    $(".roster").empty()

    //render players
    sorted.forEach(player=>{
        var id = player["INFO"]["id"].toString()
        if(!owned.includes(id)){
        //add button, photo and name row
        let main_row = roster.insertRow(-1)
        let add_button = main_row.insertCell(0)
        add_button.setAttribute("rowspan","2")
        add_button.setAttribute("class","add_button")
        add_button.setAttribute("id",id)
        add_button.innerHTML += `<img src="/static/fontawesome/plus-circle-solid.png">`
        let photo = main_row.insertCell(1)
        photo.setAttribute("rowspan","2")
        photo.setAttribute("class","player_photo")
        photo.innerHTML += `<img src="${player["INFO"]["photo"]}">`
        let name = main_row.insertCell(2)
        name.setAttribute("class","roster-info")
        name.setAttribute("colspan",(cats.length-2).toString())
        name.innerHTML += `<b>${player["INFO"]["name"]}</b> - ${player["INFO"]["team"]}`
        
        //match row
        let match_row = roster.insertRow(-1)
        if(tdate in player){
            let cell = match_row.insertCell(-1)
            cell.setAttribute("class","roster-match")
            cell.setAttribute("colspan",(cats.length-1).toString())
            let status = sub_to_status(player[tdate]["sub"])
            cell.innerHTML += `<span class="${status}">${status}</span> ${player[tdate]["home"]} vs ${player[tdate]["away"]}`
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
        let cell = stats_row.insertCell(-1)
        // cell.innerHTML += p_name[filter_time]["rank"]
        cell.innerHTML += "?"
        let adds = stats_row.insertCell(-1) 
        if(tdate in player){
            cats.slice(2).forEach(cat=>{
                let cell = stats_row.insertCell(-1)
                if(cat==key){
                    cell.setAttribute("style","color:red")
                }
                cell.innerHTML += player[tdate][cat]
            })}
        else{
            cats.slice(2).forEach(cat=>{
                let cell = stats_row.insertCell(-1)
                if(cat==key){
                    cell.setAttribute("style","color:red")
                }
                cell.innerHTML += "-"
            })}
    }})
})

$("#range").on("change",function(){a
    var selected = [$(this).val().slice(0,-1),$(this).val().slice(-1)]
    console.log(selected)
    $(".roster").empty()
    var range = selected[0]
    if(range="Today"){
        range = tdate
    }
    for(var id in main_data){
        if(!owned.includes(id)){
        p_name = main_data[id]
        
        //add button, photo and name row
        let main_row = roster.insertRow(-1)
        let add_button = main_row.insertCell(0)
        add_button.setAttribute("rowspan","2")
        add_button.setAttribute("class","add_button")
        add_button.setAttribute("id",p_name["INFO"]["id"])
        add_button.innerHTML += `<img src="/static/fontawesome/plus-circle-solid.png">`
        let photo = main_row.insertCell(1)
        photo.setAttribute("rowspan","2")
        photo.setAttribute("class","player_photo")
        photo.innerHTML += `<img src="${p_name["INFO"]["photo"]}">`
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
        let cell = stats_row.insertCell(-1)
        // cell.innerHTML += p_name[filter_time]["rank"]
        cell.innerHTML += "?"
        let adds = stats_row.insertCell(-1) 
        if(range in p_name){
            cats.slice(2).forEach(cat=>{
                let cell = stats_row.insertCell(-1)
                cell.innerHTML += p_name[range][cat]
            })}
        else{
            cats.slice(2).forEach(cat=>{
                let cell = stats_row.insertCell(-1)
                cell.innerHTML += "-"
            })}       
    }}
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

