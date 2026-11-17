// Mantiene i valori nativi bundled/external e sincronizza i controlli radio.
module.exports = function(ui, group) {
    const inputs = Array.from(group.querySelectorAll('input[type="radio"]'));
    const selection = {
        get value() {
            const checked = inputs.find(input => input.checked);
            return checked ? checked.value : ui.python.value();
        },
        set value(value) {
            inputs.forEach(input => { input.checked = input.value === value; });
        }
    };
    selection.value = ui.python.value();
    group.addEventListener('change', event => {
        if (inputs.includes(event.target) && event.target.checked)
            ui.python.setValue(event.target.value);
    });
    ui.view.model.options.getOption('python').on('valuechanged', () => {
        selection.value = ui.python.value();
    });
    return selection;
};
