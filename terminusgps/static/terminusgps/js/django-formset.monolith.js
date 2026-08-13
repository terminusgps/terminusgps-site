"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
require("@ungap/custom-elements");
require("requestidlecallback");
var DjangoFormset_1 = require("./django-formset/DjangoFormset");
var helpers_1 = require("./django-formset/helpers");
// remember to always reflect imports below here also in django-formset.ts
var DjangoSelectize_1 = require("./django-formset/DjangoSelectize");
var DjangoSelectizeCountry_1 = require("./django-formset/DjangoSelectizeCountry");
var SortableSelect_1 = require("./django-formset/SortableSelect");
var DualSelector_1 = require("./django-formset/DualSelector");
var DecimalUnit_1 = require("./django-formset/DecimalUnit");
var PhoneNumber_1 = require("./django-formset/PhoneNumber");
var RichtextArea_1 = require("./django-formset/RichtextArea");
var DjangoSlug_1 = require("./django-formset/DjangoSlug");
var Calendar_1 = require("./django-formset/Calendar");
var DateTime_1 = require("./django-formset/DateTime");
var FormDialog_1 = require("./django-formset/FormDialog");
var StepperCollection_1 = require("./django-formset/StepperCollection");
function handleDOMLoaded() {
    var customElementNames = Array();
    var promises = Array();
    helpers_1.StyleHelpers.attachPseudoStyles();
    window.customElements.define('django-selectize', DjangoSelectize_1.DjangoSelectizeElement, { extends: 'select' });
    customElementNames.push('django-selectize');
    window.customElements.define('django-selectize-country', DjangoSelectizeCountry_1.CountrySelectizeElement, { extends: 'select' });
    customElementNames.push('django-selectize-country');
    window.customElements.define('django-sortable-select', SortableSelect_1.SortableSelectElement);
    customElementNames.push('django-sortable-select');
    window.customElements.define('django-dual-selector', DualSelector_1.DualSelectorElement, { extends: 'select' });
    customElementNames.push('django-dual-selector');
    window.customElements.define('django-decimal-unit', DecimalUnit_1.DecimalUnitElement, { extends: 'input' });
    customElementNames.push('django-decimal-unit');
    window.customElements.define('django-phone-number', PhoneNumber_1.PhoneNumberElement, { extends: 'input' });
    customElementNames.push('django-phone-number');
    window.customElements.define('django-richtext', RichtextArea_1.RichTextAreaElement, { extends: 'textarea' });
    customElementNames.push('django-richtext');
    window.customElements.whenDefined('django-richtext').then(function () {
        var textareaElements = document.querySelectorAll('textarea[is="django-richtext"]');
        textareaElements.forEach(function (textareaElement) {
            promises.push(new Promise(function (resolve) {
                // RichtextArea connects asynchronously, so we need to wait until it is connected to the DOM
                textareaElement.addEventListener('connected', function () { return resolve(undefined); }, { once: true });
            }));
        });
    });
    window.customElements.define('django-slug', DjangoSlug_1.DjangoSlugElement, { extends: 'input' });
    customElementNames.push('django-slug');
    window.customElements.define('django-datefield', DateTime_1.DateFieldElement, { extends: 'input' });
    customElementNames.push('django-datefield');
    window.customElements.define('django-datecalendar', Calendar_1.DateCalendarElement, { extends: 'input' });
    customElementNames.push('django-datecalendar');
    window.customElements.define('django-datepicker', DateTime_1.DatePickerElement, { extends: 'input' });
    customElementNames.push('django-datepicker');
    window.customElements.define('django-datetimefield', DateTime_1.DateTimeFieldElement, { extends: 'input' });
    customElementNames.push('django-datetimefield');
    window.customElements.define('django-datetimecalendar', Calendar_1.DateTimeCalendarElement, { extends: 'input' });
    customElementNames.push('django-datetimecalendar');
    window.customElements.define('django-datetimepicker', DateTime_1.DateTimePickerElement, { extends: 'input' });
    customElementNames.push('django-datetimepicker');
    window.customElements.define('django-daterangefield', DateTime_1.DateRangeFieldElement, { extends: 'input' });
    customElementNames.push('django-daterangefield');
    window.customElements.define('django-daterangecalendar', Calendar_1.DateRangeCalendarElement, { extends: 'input' });
    customElementNames.push('django-daterangecalendar');
    window.customElements.define('django-daterangepicker', DateTime_1.DateRangePickerElement, { extends: 'input' });
    customElementNames.push('django-daterangepicker');
    window.customElements.define('django-datetimerangefield', DateTime_1.DateTimeRangeFieldElement, { extends: 'input' });
    customElementNames.push('django-datetimerangefield');
    window.customElements.define('django-datetimerangecalendar', Calendar_1.DateTimeRangeCalendarElement, { extends: 'input' });
    customElementNames.push('django-datetimerangecalendar');
    window.customElements.define('django-datetimerangepicker', DateTime_1.DateTimeRangePickerElement, { extends: 'input' });
    customElementNames.push('django-datetimerangepicker');
    window.customElements.define('django-form-dialog', FormDialog_1.FormDialogElement, { extends: 'dialog' });
    customElementNames.push('django-form-dialog');
    window.customElements.define('django-stepper-collection', StepperCollection_1.StepperCollectionElement);
    customElementNames.push('django-stepper-collection');
    var foundIds = new Set();
    document.querySelectorAll('django-formset [id]').forEach(function (element) {
        var foundId = element.getAttribute('id');
        if (foundIds.has(foundId))
            throw new Error("There are at least two elements with attribute id=\"".concat(foundId, "\""));
        foundIds.add(foundId);
    });
    promises.push.apply(promises, customElementNames.map(function (name) { return window.customElements.whenDefined(name); }));
    Promise.all(promises).then(function () {
        window.customElements.define('django-formset', DjangoFormset_1.DjangoFormsetElement);
    }).catch(function (error) { return console.error("Failed to initialize django-formset: ".concat(error)); });
}
if (document.readyState === 'loading') {
    window.addEventListener('DOMContentLoaded', handleDOMLoaded);
}
else {
    handleDOMLoaded();
}
