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


async function search() {
    let anime = document.getElementById("anime").value;
    console.log(anime)
    data = await fetch(`${api_link}/search`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title: (anime.toString()) })
    })
    data = await data.json(); // parsuj JSON
    console.log(data);
    let len = data.length;
    let inside = "";
    for (let i=0; i<len; i++)
    {
        let episodes = [];
        let test = data[i].episodes.sort(function(a, b){return a-b});
        test.push(0);
        let testLen = test.length;
        let first = test[0];	
        for (let i=0;i<testLen; i++ )
        {
            if (i>0)
                if (test[i] != test[i-1]+1)
                {
                    if (test[i-1]!=first)
                        episodes.push(`${first}-${test[i-1]}`);				
                    else
                        episodes.push(`${first}`);
                    first = test[i];	
                                    
                }
        }	
        console.log(episodes);
        episodes = episodes.join(", ");
        inside += `<div class='result'>
                    <div class='name'>${data[i].title}</div>
                    <div class='odcinki'>Dostępne odcinki: ${episodes}</div>
                    <div class='autor'>Autor: <a href='http://animesub.info/osoba.php?id=${data[i].author_id}'>${data[i].author}</a></div>
                </div>`
    }
    document.getElementById('results').innerHTML = inside;
        
}