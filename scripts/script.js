function loadResults(data) {
    let inside = ``;
    
    if (data.length > 0) {
        data.forEach(d => {
            let divId = d.sub_ids.join("-");
            inside +=
                `<div class='resultDisabled'>
                    <div class='name'>${d.title_en}</div>
                    <div class='subName'>${d.title}</div>
                    <div class='odcinki'>${d.episodes_txt ? "Dostępne odcinki: " + d.episodes_txt : "Film/OVA"}</div>
                    <div class='down'><button onclick='download([${d.sub_ids}])'>Pobierz paczkę</button></div>
                    <div class='progress-bar' name='${divId}-m'><div name='${divId}' class='inner-progres'></div></div>
                    <div class='bottomRow'>
                        <div class='autor'>Autor: <a href='http://animesub.info/osoba.php?id=${d.author_id}'>${d.author}</a></div>
                        <div class='data'>${d.date}</div>
                    </div>
                </div>`
        })
    } else {
        inside +=
            `<div class='resultDisabled'>
                <div class='name'>Nie znaleziono żadnego wyniku!</div>
                <div class='details'>Spróbuj wyszukać coś innego - użyj angielskich lub japońskich nazw.</div>
            </div>`
    }

    // wczytanie do html
    document.getElementById('results').innerHTML = inside;
    requestAnimationFrame(() => {
        requestAnimationFrame(() => {
            let elements = document.querySelectorAll(".resultDisabled");
            elements.forEach((element) => {
                element.classList.add("result")
                element.classList.remove("resultDisabled")
            });
        });
    });
}

function sortby(mode){
    element = document.getElementById("select");
    element.innerHTML = `<select id="select_sort" onchange="sortby(this.value)">
                    <option id='s-default' value="default">najlepsze dopasowanie</option>
                    <option id='s-count' value="count">najwięcej odcinków</option>
                    <option id='s-date' value="date">najnowsze</option>
                </select>`
    document.getElementById(`s-${mode}`).setAttribute("selected" ,"");
    switch (mode){
        case "default":
            loadResults(data_global)
            break
        case "count":
            loadResults(data_global.sort((a, b) => b.episodes.length - a.episodes.length))
            break
        case "date":
            loadResults(data_global.sort((a, b) => new Date(b.date) - new Date(a.date)))
            break
    }
}