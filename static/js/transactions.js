const transaction = document.querySelector(".transaction")
const renderTransferList = (data, id) =>{
    const name = id.replace(/_/," ")
    const html = `
        <tr class="player-profile" data-id="${id}">
            <td><button class="cut" id="${id}">-</button></td>
            <td colspan="3">${name}</td>
            <td>${data.Total.Team}</td>
        </tr>
        <tr data-id="${id}">
            <td>${data.Total.Goals}</td>
            <td>${data.Total.Assists}</td>
            <td>0</td>
            <td>0</td>
            <td>0</td>
        </tr>
    `
    transaction.innerHTML += html
}

const removeTransfer = (id) =>{
    deleted = document.querySelectorAll(`tr[data-id=${id}]`)
    deleted.forEach(element => {
        element.remove()
    });
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

db.collection('NATIONAL FRIENDLIES 2021').onSnapshot((snapshot)=>{
    // console.log(snapshot.docChanges())
    snapshot.docChanges().forEach(change=>{
        // console.log(change,change.doc.data(),change.doc.id)
        console.log(change)
        if(change.type=="added"){
            renderTransferList(change.doc.data(),change.doc.id)
        }
        else if(change.type=="removed"){
            removeTransfer(change.doc.id)
            console.log("REMOVED")
        }
    })
})


//delete player
const roster_table = document.querySelector(".transaction-table")
roster_table.addEventListener('click',event=>{
    console.log(event)
    if(event.target.className=="cut"){
        const id = event.target.getAttribute("id")
        db.collection('roster').doc(id).delete()
    }
})