const api_link = "https://basedanimesub.153070065.xyz"
// const api_link = "http://localhost:8986"

var IDsMap = new Map();
const delay = ms => new Promise(res => setTimeout(res, ms));
var data_global=[]

async function checkDownloadProgress(id)
{
    
    progress = 0
    divId = IDsMap.get(id).toString();
    element =document.getElementsByName(divId)[0];
    element2 =document.getElementsByName(`${divId}-m`)[0];
    element.style.opacity = '100%';
    element2.style.opacity = '100%';
    while (progress < 100) {
        data = await fetch(`${api_link}/download_progress`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ job_id: id })
        })
        data = await data.json()
        progress = data['progress']
        element.style.width= `${progress}%`;
        await delay(500)
    }
    element.style.opacity = '0%';
    element2.style.opacity = '0%';
}

async function download(ids) {
    // wysłanie id do pobrania, i odebranie job_id
    data = await fetch(`${api_link}/download_start`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ sub_ids: ids })
    });
    data = await data.json();
    const job_id = data['job_id'];
    let id = ids.join("-");
    IDsMap.set(job_id, id);

    // sprawdzanie postępu w tworzeniu .zip
    await checkDownloadProgress(job_id);

    // pobranie gotowego pliku
    data = await fetch(`${api_link}/download`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ job_id: job_id })
    })

    let filename = "plik_BasedAnimesubInfo.zip"; // fallback

    // nazwa pliku z headerów
    const disposition = data.headers.get("Content-Disposition");
    if (disposition && disposition.includes("filename=")) {
        const match = disposition.match(/filename="?([^"]+)"?/);
        if (match)
            filename = match[1];
    }

    // pobieranie .zip
    const blob = await data.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
}

async function search(e) {
    e.preventDefault();
    let anime = document.getElementById("anime").value;

    data = await fetch(`${api_link}/search`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title: (anime.toString()) })
    })
    data = await data.json();
    data_global = data

    data.forEach(d => {
        let episodes = [];
        d.episodes = d.episodes.sort(function (a, b) { return a - b });

        if (d.episodes.length > 0) {
            // zmiana listy odc. na czytelne zakresy
            let first = d.episodes[0];
            for (let i = 1; i < d.episodes.length + 1; i++) {
                if (d.episodes[i] != d.episodes[i - 1] + 1) {
                    if (d.episodes[i - 1] != first)
                        episodes.push(`${first}-${d.episodes[i - 1]}`);
                    else
                        episodes.push(`${first}`);
                    first = d.episodes[i];
                }
            }
            d['episodes_txt'] = episodes.join(", ");
        }
        else
            d['episodes_txt'] = false;
    })

    try
    {
        value = document.getElementById("select_sort").value;
    }
    catch
    {
        value = "default";
    }
    finally
    {
        sortby(value);
    }
    

}