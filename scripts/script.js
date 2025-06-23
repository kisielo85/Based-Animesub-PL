const api_link = "https://basedanimesub.153070065.xyz"

/*function download(){
    fetch(`${api_link}/download`)
    .then(res => res.blob())
    .then(blob => {
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = "plik.zip";
        a.click();
        URL.revokeObjectURL(url);
    });
}*/


function search() {
    fetch(`${api_link}/search`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title: "steins gate" })
    }).then(res => res.json())         // parsuj JSON
        .then(data => {
            console.log(data);
        })
}