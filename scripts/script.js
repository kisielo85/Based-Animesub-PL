const api_link = "https://basedanimesub.153070065.xyz"

function download(ids) {
    console.log("download:", data)

    fetch(`${api_link}/download`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ sub_ids: ids })
    })
        .then(async res => {
            let filename = "plik_BasedAnimesubInfo.zip"; // fallback

            // nazwa pliku z headerów
            const disposition = res.headers.get("Content-Disposition");
            if (disposition && disposition.includes("filename=")) {
                const match = disposition.match(/filename="?([^"]+)"?/);
                if (match)
                    filename = match[1];
            }

            // pobieranie .zip
            const blob = await res.blob();
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            a.click();
            URL.revokeObjectURL(url);
        });
}


async function search() {
    let anime = document.getElementById("anime").value;
    console.log("search:", anime)

    data = await fetch(`${api_link}/search`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title: (anime.toString()) })
    })
    data = await data.json();

    let inside = "";
    for (let i = 0; i < data.length; i++) {
        let episodes = [];
        let test = data[i].episodes.sort(function (a, b) { return a - b });
        let testLen = test.length;
        let first = test[0];
        if (testLen > 0) {
            // zmiana listy odc. na czytelne zakresy
            for (let i = 1; i < testLen + 1; i++) {
                if (test[i] != test[i - 1] + 1) {
                    if (test[i - 1] != first)
                        episodes.push(`${first}-${test[i - 1]}`);
                    else
                        episodes.push(`${first}`);
                    first = test[i];
                }
            }
            episodes = episodes.join(", ");
        }
        else
            episodes = "Film/OVA";

        inside +=
            `<div class='resultDisabled'>
                <div class='name'>${data[i].title_en}</div>
                <div class='subName'>${data[i].title}</div>
                <div class='odcinki'>Dostępne odcinki: ${episodes}</div>
                <div class='down'><button onclick='download([${data[i].sub_ids}])'>Pobierz paczkę</button></div>
                <div class='bottomRow'>
                    <div class='autor'>Autor: <a href='http://animesub.info/osoba.php?id=${data[i].author_id}'>${data[i].author}</a></div>
                    <div class='data'>${data[i].date}</div>
                </div>
            </div>`
    }

    // wczytanie do html
    document.getElementById('results').innerHTML = inside;
    requestAnimationFrame(() => {
        let elements = document.querySelectorAll(".resultDisabled");
        elements.forEach((element) => {
            element.classList.add("result")
            element.classList.remove("resultDisabled")
        });
    });
}