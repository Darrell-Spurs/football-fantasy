//render roster list

const roster = document.querySelector(".roster")
const renderRoster = (data, id) =>{
    const name = id.replace(/_/," ")
    const html = `
        <tr class="player-profile" data-id="${id}">
            <td>${name}</td>
            <td>${data.position}</td>
            <td>${data.team}</td>
            <td>${data.nation}</td>
        </tr>
        <tr data-id="${id}">
            <td>1</td>
            <td><button class="cut" id="${id}">Del</button></td>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
        </tr>
    `
    roster.innerHTML += html
}

const removeRoster = (id) =>{
    deleted = document.querySelectorAll(`tr[data-id=${id}]`)
    deleted.forEach(element => {
        element.remove()
    });
}