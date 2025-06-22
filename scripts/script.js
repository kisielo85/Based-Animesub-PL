const api_link="http://127.0.0.1:8986"

function download(){
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
}
