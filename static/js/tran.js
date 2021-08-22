//render roster list

// roster content field ref
const roster = document.querySelector(".roster-table").getElementsByTagName("tbody")[0]
// table header field ref
const cats_head_tr = document.querySelector(".stat-cats")
// all player from db
var main_data = {}
//today's date
var today = "2021-04-10"

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

function get_players(){
     db.collection("leagues").doc(cur_league).get().then(function(res){
        cats = res.data()["INFO"]["rosters"]
        owned = res.data()["owned"]
        cats.unshift("Rank")
        cats.unshift("Adds")
        renderCats(cat_to_abbr(cats))
    }).then(()=>{
    db.collection('roster').onSnapshot((snapshot)=>{
        snapshot.docChanges().forEach(
            change=>{
                main_data = change.doc.data()
                league_json = change.doc.data()
                for(var id in league_json){
                    if(!owned.includes(id)){
                    p_name = league_json[id]
                    
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
                    let cell = stats_row.insertCell(-1)
                    // cell.innerHTML += p_name[filter_time]["rank"]
                    cell.innerHTML += "?"
                    let adds = stats_row.insertCell(-1) 
                    if("2021-04-10" in p_name){
                        cats.slice(2).forEach(cat=>{
                            let cell = stats_row.insertCell(-1)
                            cell.innerHTML += p_name["2021-04-10"][cat]
                        })}
                    else{
                        cats.slice(2).forEach(cat=>{
                            let cell = stats_row.insertCell(-1)
                            cell.innerHTML += "-"
                        })}       
            }}
        })})
        })  
    }

$(".roster-table").on("click",".add_button",function(){
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
    <div class="pop-end"><button pname="${this_data["INFO"]["full_name"]}" id="fa-${this_id}" class="player-ctrl FA">Add Player</button></div>
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
    $(".alert-content").append(`Add Player:<br>${pname}?`)
    $(".alert-ok").append(`<button id='yes' pid='${pid}' pname='${pname}'>Yes</button> <button id='no'>No</button>`)
    $(".alert").removeClass("alert-hide")
})
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
            if(data_array[i][today]==undefined){cur_data=-1
            }else{cur_data = data_array[i][today][col]}
            if(data_array[i+1][today]==undefined){next_data=-1
            }else{next_data = data_array[i+1][today][col]}
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
        if(today in player){
            let cell = match_row.insertCell(-1)
            cell.setAttribute("class","roster-match")
            cell.setAttribute("colspan",(cats.length-1).toString())
            let status = sub_to_status(player[today]["sub"])
            cell.innerHTML += `<span class="${status}">${status}</span> ${player[today]["home"]} vs ${player[today]["away"]}`
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
        if("2021-04-10" in player){
            cats.slice(2).forEach(cat=>{
                let cell = stats_row.insertCell(-1)
                if(cat==key){
                    cell.setAttribute("style","color:red")
                }
                cell.innerHTML += player["2021-04-10"][cat]
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

