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

    // 🔹 Obtener boletos actuales
    const resBoletos = await fetch('/api/boletos');
    const boletos = await resBoletos.json();

    // 🔹 Filtrar solo disponibles
    const disponibles = boletos
        .filter(b => b[1] !== 'vendido')
        .map(b => b[0]);

    if (disponibles.length === 0) {
        alert("Boletos agotados");
        return;
    }

    let contador = 0;

    // 🔹 Animación usando SOLO números disponibles
    const intervalo = setInterval(() => {

        const randomIndex = Math.floor(Math.random() * disponibles.length);
        ruleta.innerText = disponibles[randomIndex];

        ruleta.style.transform = "scale(1.3)";
        setTimeout(() => {
            ruleta.style.transform = "scale(1)";
        }, 100);

        contador++;

        if (contador > 25) {
            clearInterval(intervalo);
        }

    }, 80);


    // 🔹 Confirmar número real desde backend
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