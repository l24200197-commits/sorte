async function cargarBoletos() {

    const res = await fetch('/api/boletos');
    const data = await res.json();

    const grid = document.getElementById('grid');
    grid.innerHTML = '';

    data.forEach(b => {

        const div = document.createElement('div');

        div.className = "col-1 boleto " +
            (b.estado === 'vendido' ? 'bg-danger' : 'bg-success');

        div.innerText = b.numero;

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

    const resBoletos = await fetch('/api/boletos');
    const boletos = await resBoletos.json();

    const disponibles = boletos
        .filter(b => b.estado !== 'vendido')
        .map(b => b.numero);

    if (disponibles.length === 0) {
        alert("Boletos agotados");
        return;
    }

    let velocidad = 40;
    let vueltas = 0;
    let maxVueltas = 40;

    function girar() {

        const randomIndex = Math.floor(Math.random() * disponibles.length);
        ruleta.innerText = disponibles[randomIndex];

        vueltas++;

        if (vueltas < maxVueltas) {
            velocidad += 8;
            setTimeout(girar, velocidad);
        } else {
            confirmarNumero();
        }
    }

    async function confirmarNumero() {

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
    }

    girar();
}


cargarBoletos();