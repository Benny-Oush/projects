async function getRandomJoke() {
    const response = await fetch("https://icanhazdadjoke.com/", {headers : {
        Accept: "application/json"
    }}) 
    return await response.json()
}

async function getJokeById(id) {
    const response = await fetch(`https://icanhazdadjoke.com/j/${id}`, {headers : {
        Accept: "application/json"
    }})
    return await response.json() 
}

export {getRandomJoke, getJokeById}