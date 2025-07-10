let elements = [];

// otwieranie i zamykanie karty z opisem
function switchPos(i) {
    let el = document.getElementById("desc-" + i);
    let arrow = document.getElementById("arrow-" + i);
    if (elements[i]) {
        el.style.left = "var(--d-default)";
        arrow.style.transform = "rotate(0turn)";
        setTimeout(function () { elements[i] = false }, 400);
    }
    else {
        el.style.left = "var(--d-open)";
        arrow.style.transform = "rotate(0.5turn)";
        elements[i] = true;
    }
}

// smol animacja po najechaniu na karte z opisem
function mouse_hover(i, mouse_in) {
    let el = document.getElementById("desc-" + i)
    if (elements[i]) return

    el.style.left = (mouse_in) ? "var(--d-hover)" : "var(--d-default)"
}

function loadResults(data) {
    let inside = ``;
    let len = data.length;
    elements = Array(len).fill(false);
    if (len > 0) {
        for (let i = 0; i < len; i++) {
            let d = data[i];
            let divId = d.sub_ids.join("-");
            let desc = d.descriptions[0]
            inside +=
                `<div class='resultDisabled'>
                    <div class='name'>${d.title_en}</div>
                    <div class='subName'>${d.title}</div>
                    <div class='odcinki'>${d.episodes_txt ? "Dostępne odcinki: " + d.episodes_txt : "Film/OVA"}</div>
                    <div class='down'><button onclick='download([${d.sub_ids}])'>Pobierz paczkę</button></div>
                    <div class='progress-bar' id='${divId}-m'><div id='${divId}' class='inner-progres'></div></div>
                    <div style='display: flex;'>
                        <div>Autor: <a href='http://animesub.info/osoba.php?id=${d.author_id}'>${d.author}</a></div>
                        <div class='date'>${d.date}</div>
                    </div>
                    <div class='description' id='desc-${i}'>
                        <div class='arrow-parent' onClick='switchPos(${i})' onmouseover='mouse_hover(${i},true)' onmouseout='mouse_hover(${i},false)'>
                            <div class='arrow' id='arrow-${i}'><</div>
                            <div class='name'>Opis</div>
                        </div>
                        <div class='pages'>
                            <div id='page-num-${i}'>1/${d.descriptions.length}</div>
                            <button onclick='load_desc(${i}, -1)' style='margin-right: 4px'><</button>
                            <button onclick='load_desc(${i}, 1)'>></button>
                        </div>
                        <div class='description-text' id='desc-txt-${i}' value='0'>${desc}</div>
                    </div>
                </div>`
        }
    } else {
        inside +=
            `<div class='resultDisabled'>
                <div class='name'>Nie znaleziono żadnego wyniku!</div>
                <div class='details'>Spróbuj wyszukać coś innego - użyj angielskich lub japońskich nazw.</div>
            </div>`
    }

    // wczytanie do html
    document.getElementById('results').innerHTML = inside;
    enable_results()
}

// włącza animacje pojawiających sie wyników
function enable_results(){
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

// wczytywanie opisów danych plików
function load_desc(id, val) {
    len = sorted_data_global[id].descriptions.length
    desc_element = document.getElementById('desc-txt-' + id)
    page = parseInt(desc_element.getAttribute('value')) + val

    if (page >= len) page = 0
    else if (page < 0) page = len - 1

    desc_element.setAttribute('value', page)
    document.getElementById('page-num-' + id).innerText = `${page + 1}/${len}`

    desc_element.innerHTML = sorted_data_global[id].descriptions[page]
}

var sorted_data_global = []

function sortby(mode) {
    document.getElementById("select_sort").style.display = ""
    switch (mode) {
        case "default":
            sorted_data_global = data_global
            break
        case "count":
            sorted_data_global = [...data_global].sort((a, b) => b.episodes.length - a.episodes.length)
            break
        case "date":
            sorted_data_global = [...data_global].sort((a, b) => new Date(b.date) - new Date(a.date))
            break
    }
    loadResults(sorted_data_global)
}