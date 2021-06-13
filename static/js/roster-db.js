// //offline data
// db.enablePersistence()
//     .catch(err=>{
//         if(err.code == "failed-precondition"){
//             // multiple tabs
//             console.log("Persistence failed")
//         }
//         else if(err.code == "unimplemented"){
//             //lack of browser support
//             console.log("Persistence unavailable")
//         }
//     })

// db.collection('roster').onSnapshot((snapshot)=>{
//     // console.log(snapshot.docChanges())
//     snapshot.docChanges().forEach(change=>{
//         // console.log(change,change.doc.data(),change.doc.id)
//         console.log(change)
//         if(change.type=="added"){
//             renderRoster(change.doc.data(),change.doc.id)
//         }
//         else if(change.type=="removed"){
//             removeRoster(change.doc.id)
//             console.log("REMOVED")
//         }
//     })
// })

// // add new player
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

// //delete player
// const roster_table = document.querySelector(".roster-table")
// roster_table.addEventListener('click',event=>{
//     console.log(event)
//     if(event.target.className=="cut"){
//         const id = event.target.getAttribute("id")
//         db.collection('roster').doc(id).delete()
//     }
// })

// db.collection('NATIONAL FRIENDLIES 2021').onSnapshot((snapshot)=>{
//     // console.log(snapshot.docChanges())
//     snapshot.docChanges().forEach(change=>{
//         // console.log(change,change.doc.data(),change.doc.id)
//         console.log(change)
//         if(change.type=="added"){
//             renderTransferList(change.doc.data(),change.doc.id)
//         }
//         else if(change.type=="removed"){
//             removeTransfer(change.doc.id)
//             console.log("REMOVED")
//         }
//     })
// })