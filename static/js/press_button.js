document.querySelector('.press-button').addEventListener('click', function() {
    // Agregar el icono de espera al botón
    this.innerHTML = '<div style="display: inline-flex;"><i class="material-icons spinner" style="height: 2.5vh; width:2.5vh;">cached</i> <span>&nbsp; Espere </span></div>';
    // Deshabilitar el botón
    this.disabled = true;
});


var forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
    var submitButton = form.querySelector('button[type="submit"]');
    if (submitButton) {
        submitButton.addEventListener('click', function() {
        // Ejecutar el submit del formulario
        form.submit();
        });
    }
});