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
    let len = data.length;
    let inside = "";
    for (let i=0; i<len; i++)
    {
        let episodes = [];
        let test = data[i].episodes.sort(function(a, b){return a-b});
        test.push(0);
        let testLen = test.length;
        let first = test[0];
        if (testLen>1)
        {
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
            episodes = episodes.join(", ");
        }	
        else
            episodes="Film/OVA";
        
        inside += `<div class='resultDisabled'>
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
    console.log(data);
    document.getElementById('results').innerHTML = inside;
    setTimeout(() => {
        let elements = document.getElementsByClassName("resultDisabled");
        let len = elements.length;
        for (let i =0; i<len;i++)
        {
            elements[i].classList.add("result");
            elements[i].classList.remove("resultDisabled");
        }
    }, 500) 
}
