// function show_scoring_settings(selected){
//     let s_types=["H2H","Roto","Points"]
// var scoring_form = $(`#scoring_${$("#score_type").val()}`)
// }
$("#create-league").submit(event=>{
    event.preventDefault()
    let submitter = event.originalEvent.submitter.id
    if(submitter==="add_scoring"){
        $("#scoring").removeClass("hide")
        $("#add_scoring").remove()
    }
    else if(submitter==="add_rostering"){
        $("#roster").removeClass("hide")
        $("#add_rostering").remove()
    }
    else if(submitter==="submit"){
        let cl_form = $("#create-league").serializeArray()
        // console.log(cl_form)
        let new_dict={"positions":[],"rosters":[]}
        cl_form.forEach(item=>{
            if(item["name"]=="positions" || item["name"]=="rosters"){
                new_dict[item["name"]].push(item["value"])
            }
            else{
                new_dict[item["name"]]=item["value"]
            }
        })
        console.log(new_dict)

        db.collection("leagues").get().then(res=>{
            const ids=[]
            docs = res.docs
            docs.forEach(doc=>{
                ids.push(doc.id)
            })
            console.log(ids,new_dict["league_name"])
            //check if it is a duplicate name
            if(ids.includes(new_dict["league_name"])){
                alert("League Name Taken!")
            }
            else{
                axios
                .post("/create_league",new_dict)
                .then(window.location = "/leagues")
            }
        })}
    })
    