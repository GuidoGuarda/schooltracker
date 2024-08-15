$(document).ready(function() {
    $('#money').inputmask('currency', { 
        prefix: 'R$ ',
        allowMinus: false,
        autoUnmask: true,
        rightAlign: false,
        digits: 2,  
        digitsOptional: false,
        decimalSeparator: ',',
        groupSeparator: '.',
        removeMaskOnSubmit: true
    });

    // Aplica a máscara ao campo RA para permitir apenas números e limitar a 8 dígitos
    $('#ra').inputmask({
        mask: '99999999',  // Define a máscara para permitir até 8 dígitos numéricos
        definitions: {
            '9': {
                validator: '[0-9]',
                cardinality: 1
            }
        },
        placeholder: '',  // Remove o placeholder padrão
        autoUnmask: true,
        rightAlign: false,
        removeMaskOnSubmit: true
    });

    // Adiciona uma validação adicional para garantir que o campo RA tenha no máximo 8 dígitos
    $('#ra').on('input', function() {
        var value = $(this).val().replace(/\D/g, ''); // Remove todos os caracteres não numéricos
        if (value.length > 8) {
            $(this).val(value.slice(0, 8)); // Limita o valor a 8 dígitos
        }
    });
    
});
