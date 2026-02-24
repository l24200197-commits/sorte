async function cargarBoletos() {

    const res = await fetch('/api/boletos');
    const data = await res.json();

    const grid = document.getElementById('grid');
    grid.innerHTML = '';

    data.forEach(b => {

        const div = document.createElement('div');
        div.className = "col-1 boleto " +
            (b[1] === 'vendido' ? 'bg-danger' : 'bg-success');

        div.innerText = b[0];
        grid.appendChild(div);
    });
}



async function aleatorio() {

    const usuario = document.getElementById('usuario').value;

    if (!usuario) {
        alert("Escribe tu nombre primero");
        return;
    }

    const ruleta = document.getElementById("ruletaNumero");
    let contador = 0;

    // Animación tipo ruleta
    const intervalo = setInterval(() => {

        const randomTemp = Math.floor(Math.random() * 150) + 1;
        ruleta.innerText = randomTemp;

        ruleta.style.transform = "scale(1.3)";
        setTimeout(() => {
            ruleta.style.transform = "scale(1)";
        }, 100);

        contador++;

        if (contador > 25) {
            clearInterval(intervalo);
        }

    }, 80);


    // Después de animación, pedir número real al backend
    setTimeout(async () => {

        const res = await fetch('/api/aleatorio', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({usuario})
        });

        const data = await res.json();

        if (data.numero) {
            ruleta.innerText = data.numero;
            alert("Tu número asignado es: " + data.numero);
        } else {
            ruleta.innerText = "❌";
            alert(data.error);
        }

        cargarBoletos();

    }, 2200);
}


cargarBoletos();