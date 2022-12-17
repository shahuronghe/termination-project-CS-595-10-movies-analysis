function close_tab() {
    window.close()
}

imdb_url = ""
tmdb_id = ""

var url = "http://127.0.0.1:5001/";

function display_suggestions(data) {
    const container = document.getElementById("permas");
    var content = ""
    data.forEach(result => {
        content += '<img src=https://image.tmdb.org/t/p/original' + result.poster_path + ' onclick="open_movie_dialog(\'' + result.id + '\')" > '
    });
    // data.forEach(result => {
    //     content += '<img src=https://image.tmdb.org/t/p/original' + result.poster_path + ' onclick="open_movie_dialog(\'' + result.id + '\')" > '
    // });
    container.innerHTML += content
}

function get_similar_movie() {
    var similar_url = url + "similar?movie_id=" + tmdb_id
    fetch(similar_url, {
        method: 'GET',
        headers: {
            'Content-type': 'application/json; charset=UTF-8',
        }
    }).then(response => {
        return response.json();
    }).then(data => {
        display_suggestions(data);
    }).catch(err => {
    });
}

function setObject(type2, str2) {
    if (type2 === "imdb_url") {
        imdb_url = str2;
        if (imdb_url === "") {
            document.getElementById("imdb_btn").style.visibility = "hidden";
        }
    }
    if (type2 === "tmdb_id") {
        tmdb_id = str2;
        get_similar_movie();
    }
}


function gotoIMDB() {
    if (imdb_url !== "") {
        window.open(imdb_url, "_blank");
    }
}

function open_movie_dialog(obj_id) {
    console.log(obj_id);
    window.open(url + "get_movie_details?movie_id=" + obj_id, "_self");

}

