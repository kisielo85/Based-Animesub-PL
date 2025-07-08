let elements = [];

// otwieranie i zamykanie karty z opisem
function switchPos(i) {
    let el = document.getElementsByName("desc-" + i)[0];
    let arrow = document.getElementsByName("back-" + i)[0];
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
    let el = document.getElementsByName("desc-" + i)[0]
    if (elements[i]) return

    el.style.left = (mouse_in) ? "var(--d-hover)" : "var(--d-default)"
}

function loadResults(data) {
    let inside = ``;
    let len = data.length;
    if (len > 0) {
        for (let i = 0; i < len; i++) {
            let d = data[i];
            let divId = d.sub_ids.join("-");
            let desc = d.descriptions[0].replaceAll("\n", "<br>");
            elements.push(false);
            inside +=
                `<div class='resultDisabled'>
                    <div class='name'>${d.title_en}</div>
                    <div class='subName'>${d.title}</div>
                    <div class='odcinki'>${d.episodes_txt ? "Dostępne odcinki: " + d.episodes_txt : "Film/OVA"}</div>
                    <div class='down'><button onclick='download([${d.sub_ids}])'>Pobierz paczkę</button></div>
                    <div class='progress-bar' name='${divId}-m'><div name='${divId}' class='inner-progres'></div></div>
                    <div style='display: flex;'>
                        <div>Autor: <a href='http://animesub.info/osoba.php?id=${d.author_id}'>${d.author}</a></div>
                        <div class='date'>${d.date}</div>
                    </div>
                    <div class='description' onClick='switchPos(${i})' onmouseover='mouse_hover(${i},true)' onmouseout='mouse_hover(${i},false)' name='desc-${i}'>
                        <div class='back' name='back-${i}'><</div>
                        <div>
                            <div class='name'>Opis</div>
                        </div>
                        <div class='description-text'">${desc}</div>
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

function sortby(mode) {
    document.getElementById("select_sort").style.display = ""
    switch (mode) {
        case "default":
            loadResults(data_global)
            break
        case "count":
            loadResults([...data_global].sort((a, b) => b.episodes.length - a.episodes.length))
            break
        case "date":
            loadResults([...data_global].sort((a, b) => new Date(b.date) - new Date(a.date)))
            break
    }
}