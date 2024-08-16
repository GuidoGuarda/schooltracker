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

    
    $('#ra').inputmask({
        mask: '99999999',
        definitions: {
            '9': {
                validator: '[0-9]',
                cardinality: 1
            }
        },
        placeholder: 'xxxxxxxx',
        autoUnmask: true,
        rightAlign: false,
        removeMaskOnSubmit: true
    });

    $('#ra').on('input', function() {
        var value = $(this).val().replace(/\D/g, '');
        if (value.length > 8) {
            $(this).val(value.slice(0, 8));
        }
    });
    
});
