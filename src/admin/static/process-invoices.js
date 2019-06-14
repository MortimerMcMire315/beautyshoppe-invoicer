var Invoicer = {

    printLog: function(res) {
        $('#processing-log').html('<pre>' + res + '</pre>');
    },

    doProcess: function() {
        var self = this;
        $('#processing-log').html('<p>Running...</p>');
        $.ajax({
            url: '/process-invoices/',
            success: function(res) {self.printLog(res);},
            error: function(xhr, status, msg) {alert(msg);}
        });
    },

    init: function() {
        var self = this;
        $('#process-invoices').click(function(e) {
            e.preventDefault();
            self.doProcess();
        });
    },
};

$(document).ready(function() {
    Invoicer.init();
});
